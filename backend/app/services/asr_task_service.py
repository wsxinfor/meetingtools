import asyncio
import logging
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.asr_config import AsrConfig
from app.models.asr_task import AsrTask
from app.models.audio import AudioFile
from app.models.meeting import Meeting
from app.models.segment import TranscriptSegment
from app.services.asr.factory import get_asr_provider

logger = logging.getLogger(__name__)


async def recover_stuck_tasks() -> None:
    """Re-queue ASR tasks that were left in 'pending' or 'running' after a restart."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(AsrTask).where(AsrTask.status.in_(["pending", "running"]))
        )
        stuck = list(result.scalars().all())
    if not stuck:
        return
    logger.info("Recovering %d stuck ASR task(s)", len(stuck))
    for task in stuck:
        asyncio.create_task(_run_asr_bg(task.id))


async def create_asr_task(
    db: AsyncSession,
    meeting_id: uuid.UUID,
    audio_file_id: uuid.UUID,
    engine: str,
    asr_config_id: uuid.UUID | None = None,
) -> AsrTask:
    task = AsrTask(
        meeting_id=meeting_id,
        audio_file_id=audio_file_id,
        engine=engine,
        asr_config_id=asr_config_id,
        status="pending",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    asyncio.create_task(_run_asr_bg(task.id))
    return task


async def get_asr_task(db: AsyncSession, task_id: uuid.UUID) -> AsrTask | None:
    result = await db.execute(select(AsrTask).where(AsrTask.id == task_id))
    return result.scalar_one_or_none()


async def _run_asr_bg(task_id: uuid.UUID) -> None:
    try:
        await _execute_asr(task_id)
    except Exception as exc:
        logger.error("ASR task %s failed: %s", task_id, exc)
        await _set_task_failed(task_id, str(exc))


async def _execute_asr(task_id: uuid.UUID) -> None:
    async with async_session_factory() as db:
        task = await db.get(AsrTask, task_id)
        if not task:
            return

        await db.execute(
            AsrTask.__table__.update()
            .where(AsrTask.id == task_id)
            .values(status="running", started_at=datetime.now(timezone.utc))
        )
        await db.commit()

        audio_file = await db.get(AudioFile, task.audio_file_id)
        if not audio_file or not audio_file.normalized_path:
            raise RuntimeError("音频文件未完成预处理")

        # Clear VAD segments so that whole-file transcription can capture
        # speaker diarization from FunASR. VAD segments have no speaker_label
        # and per-clip transcription loses diarization info.
        await db.execute(
            TranscriptSegment.__table__.delete()
            .where(TranscriptSegment.audio_file_id == task.audio_file_id)
        )
        await db.commit()

        # Resolve AsrConfig for remote engine
        asr_config: AsrConfig | None = None
        if task.engine == "remote":
            asr_config = await db.get(AsrConfig, task.asr_config_id) if task.asr_config_id else None
            if not asr_config:
                asr_config = (
                    await db.execute(
                        select(AsrConfig).where(
                            AsrConfig.is_default.is_(True),
                            AsrConfig.is_enabled.is_(True),
                        )
                    )
                ).scalar_one_or_none()

    provider = get_asr_provider(engine=task.engine, asr_config=asr_config)
    await _transcribe_whole_file(task_id, audio_file, provider)


async def _transcribe_segments(
    task_id: uuid.UUID,
    audio_file: AudioFile,
    segments: list[TranscriptSegment],
    provider,
) -> None:
    total = len(segments)
    texts: list[str] = []

    for idx, seg in enumerate(segments):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            clip_path = tmp.name

        await asyncio.to_thread(
            _extract_clip,
            audio_file.normalized_path,
            seg.start_ms,
            seg.end_ms,
            clip_path,
        )
        result = await asyncio.to_thread(provider.transcribe_file, clip_path)
        Path(clip_path).unlink(missing_ok=True)

        text = result.text.strip()
        confidence = result.confidence
        texts.append(f"[{_fmt_ms(seg.start_ms)}-{_fmt_ms(seg.end_ms)}] {text}")

        async with async_session_factory() as db:
            await db.execute(
                TranscriptSegment.__table__.update()
                .where(TranscriptSegment.id == seg.id)
                .values(raw_text=text, confidence=confidence)
            )
            progress = int((idx + 1) / total * 100)
            await db.execute(
                AsrTask.__table__.update()
                .where(AsrTask.id == task_id)
                .values(progress=progress)
            )
            await db.commit()

    raw_text = "\n".join(texts)
    async with async_session_factory() as db:
        await db.execute(
            Meeting.__table__.update()
            .where(Meeting.id == audio_file.meeting_id)
            .values(raw_text=raw_text, status="done")
        )
        await db.execute(
            AsrTask.__table__.update()
            .where(AsrTask.id == task_id)
            .values(
                status="done",
                progress=100,
                finished_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()

    logger.info("ASR task %s done, %d segments", task_id, total)


async def _transcribe_whole_file(
    task_id: uuid.UUID,
    audio_file: AudioFile,
    provider,
) -> None:
    result = await asyncio.to_thread(provider.transcribe_file, audio_file.normalized_path)
    text = result.text.strip()
    duration_ms = int(float(audio_file.duration_seconds or 0) * 1000)

    async with async_session_factory() as db:
        if result.segments:
            # Speaker-diarized segments from provider
            rows = [
                dict(
                    id=uuid.uuid4(),
                    meeting_id=audio_file.meeting_id,
                    audio_file_id=audio_file.id,
                    segment_index=idx,
                    start_ms=seg["start_ms"],
                    end_ms=seg["end_ms"],
                    speaker_label=seg.get("speaker"),
                    raw_text=seg["text"],
                    confidence=result.confidence,
                )
                for idx, seg in enumerate(result.segments)
            ]
            await db.execute(TranscriptSegment.__table__.insert(), rows)
        else:
            await db.execute(
                TranscriptSegment.__table__.insert().values(
                    id=uuid.uuid4(),
                    meeting_id=audio_file.meeting_id,
                    audio_file_id=audio_file.id,
                    segment_index=0,
                    start_ms=0,
                    end_ms=duration_ms,
                    raw_text=text,
                    confidence=result.confidence,
                )
            )
        await db.execute(
            Meeting.__table__.update()
            .where(Meeting.id == audio_file.meeting_id)
            .values(raw_text=text, status="done")
        )
        await db.execute(
            AsrTask.__table__.update()
            .where(AsrTask.id == task_id)
            .values(
                status="done",
                progress=100,
                finished_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()

    logger.info(
        "ASR task %s done (whole file, %d segments)",
        task_id, len(result.segments) if result.segments else 1,
    )


async def _set_task_failed(task_id: uuid.UUID, error_msg: str) -> None:
    try:
        async with async_session_factory() as db:
            await db.execute(
                AsrTask.__table__.update()
                .where(AsrTask.id == task_id)
                .values(
                    status="failed",
                    error_message=error_msg[:500],
                    finished_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()
    except Exception:
        pass


def _extract_clip(input_path: str, start_ms: int, end_ms: int, output_path: str) -> None:
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ss", f"{start_ms / 1000:.3f}",
        "-to", f"{end_ms / 1000:.3f}",
        "-acodec", "pcm_s16le",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg clip failed: {result.stderr[-300:]}")


def _fmt_ms(ms: int) -> str:
    s, millis = divmod(ms, 1000)
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}.{millis:03d}"
