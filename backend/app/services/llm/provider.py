import logging
import time
from dataclasses import dataclass

from openai import OpenAI

from app.models.llm_config import LlmConfig

logger = logging.getLogger(__name__)


@dataclass
class LlmResult:
    content: str
    model: str
    latency_ms: int


def build_client(config: LlmConfig) -> OpenAI:
    return OpenAI(
        base_url=config.base_url,
        api_key=config.api_key or "ollama",
    )


def generate(config: LlmConfig, prompt: str) -> LlmResult:
    client = build_client(config)
    start = time.monotonic()
    response = client.chat.completions.create(
        model=config.model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    latency_ms = int((time.monotonic() - start) * 1000)
    content = response.choices[0].message.content or ""
    logger.info("LLM generation done model=%s latency_ms=%d", config.model_name, latency_ms)
    return LlmResult(content=content, model=config.model_name, latency_ms=latency_ms)


def test_connection(config: LlmConfig) -> LlmResult:
    client = build_client(config)
    start = time.monotonic()
    response = client.chat.completions.create(
        model=config.model_name,
        messages=[{"role": "user", "content": "你好，请回复一句话。"}],
        max_tokens=50,
        temperature=0.0,
    )
    latency_ms = int((time.monotonic() - start) * 1000)
    content = response.choices[0].message.content or ""
    return LlmResult(content=content, model=config.model_name, latency_ms=latency_ms)
