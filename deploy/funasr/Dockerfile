FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install all Python deps in one resolver pass so torch + torchaudio are
# always the same version (avoids ABI mismatch from mixing whl indexes).
# On arm64 (Apple Silicon Docker) torch from PyPI is already CPU-only.
RUN pip install --no-cache-dir \
    torch \
    torchaudio \
    funasr \
    fastapi \
    "uvicorn[standard]" \
    python-multipart \
    soundfile \
    modelscope \
    sentencepiece \
    onnxruntime \
    "typing_extensions>=4.12.0"

COPY server.py /app/server.py
WORKDIR /app

# ModelScope caches downloaded models here — mount as a named volume
ENV MODELSCOPE_CACHE=/models
ENV HF_HOME=/models
ENV ASR_MODEL=iic/SenseVoiceSmall
ENV DEVICE=cpu
ENV NCPU=4

EXPOSE 6013

HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=5 \
    CMD curl -f http://localhost:6013/health || exit 1

CMD ["python", "server.py"]
