import asyncio
import logging
import shutil
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.audio import AudioFile
from app.models.segment import TranscriptSegment
from app.services.audio.preprocess import normalize_audio
from app.services.audio.vad import detect_speech_segments

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac"}
MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4 GB


def _meeting_audio_dir(meeting_id: uuid.UUID) -> Path:
    return Path(settings.audio_storage_path) / str(meeting_id)


async def save_audio_file(
    db: AsyncSession,
    meeting_id: uuid.UUID,
    filename: str,
    src_path: Path,
) -> AudioFile:
    audio_dir = _meeting_audio_dir(meeting_id)
    audio_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(filename).suffix.lower()
    dest = audio_dir / f"{uuid.uuid4().hex}{suffix}"
    shutil.move(str(src_path), str(dest))
    file_size = dest.stat().st_size
    logger.info("Audio saved: %s", dest)

    audio_file = AudioFile(
        meeting_id=meeting_id,
        original_filename=filename,
        file_path=str(dest),
        file_size=file_size,
        status="uploaded",
    )
    db.add(audio_file)
    await db.commit()
    await db.refresh(audio_file)

    # 异步触发预处理，使用独立 session，不阻塞上传响应
    asyncio.create_task(_preprocess_task(meeting_id, audio_file.id, str(dest), audio_dir))

    return audio_file


async def _preprocess_task(
    meeting_id: uuid.UUID,
    audio_file_id: uuid.UUID,
    input_path: str,
    audio_dir: Path,
) -> None:
    output_path = str(audio_dir / f"{audio_file_id.hex}_norm.wav")
    try:
        meta = await asyncio.to_thread(normalize_audio, input_path, output_path)
        async with async_session_factory() as session:
            await session.execute(
                AudioFile.__table__.update()
                .where(AudioFile.id == audio_file_id)
                .values(
                    normalized_path=output_path,
                    duration_seconds=meta.duration_seconds,
                    sample_rate=meta.sample_rate,
                    channels=meta.channels,
                    status="preprocessed",
                )
            )
            await session.commit()
        logger.info("Preprocessing done for %s", audio_file_id)

        # VAD: detect speech segments and persist them
        speech_segments = await asyncio.to_thread(detect_speech_segments, output_path)
        logger.info(
            "VAD found %d segments for %s", len(speech_segments), audio_file_id
        )
        if speech_segments:
            rows = [
                {
                    "id": uuid.uuid4(),
                    "meeting_id": meeting_id,
                    "audio_file_id": audio_file_id,
                    "segment_index": i,
                    "start_ms": seg.start_ms,
                    "end_ms": seg.end_ms,
                }
                for i, seg in enumerate(speech_segments)
            ]
            async with async_session_factory() as session:
                await session.execute(TranscriptSegment.__table__.insert(), rows)
                await session.commit()

    except Exception as exc:
        logger.error("Preprocessing failed for %s: %s", audio_file_id, exc)
        try:
            async with async_session_factory() as session:
                await session.execute(
                    AudioFile.__table__.update()
                    .where(AudioFile.id == audio_file_id)
                    .values(status="failed")
                )
                await session.commit()
        except Exception:
            pass


async def get_audio_file(db: AsyncSession, audio_file_id: uuid.UUID) -> AudioFile | None:
    result = await db.execute(select(AudioFile).where(AudioFile.id == audio_file_id))
    return result.scalar_one_or_none()


async def list_audio_files_for_meeting(
    db: AsyncSession, meeting_id: uuid.UUID
) -> list[AudioFile]:
    result = await db.execute(
        select(AudioFile)
        .where(AudioFile.meeting_id == meeting_id)
        .order_by(AudioFile.created_at)
    )
    return list(result.scalars().all())


async def delete_audio_file(db: AsyncSession, audio_file: AudioFile) -> None:
    for attr in ("file_path", "normalized_path"):
        path = getattr(audio_file, attr, None)
        if path:
            p = Path(path)
            if p.exists():
                try:
                    p.unlink()
                except OSError:
                    logger.warning("Failed to delete file: %s", p)
    await db.delete(audio_file)
    await db.commit()
