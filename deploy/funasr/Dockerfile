FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first to avoid pulling CUDA dependencies (~2GB+).
# Pin matching versions: aarch64 CPU wheels only go up to torch 2.5.1.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.5.1 torchaudio==2.5.1

# Install remaining Python deps separately so pip doesn't re-resolve torch.
RUN pip install --no-cache-dir \
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
ENV SPK_MODEL=iic/speech_campplus_sv_zh-cn_16k-common
ENV DEVICE=cpu
ENV NCPU=4

EXPOSE 6013

HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=5 \
    CMD curl -f http://localhost:6013/health || exit 1

CMD ["python", "server.py"]
