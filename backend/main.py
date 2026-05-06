import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.asr import router as asr_router
from app.api.exports import router as exports_router
from app.api.llm_configs import router as llm_configs_router
from app.api.summaries import router as summaries_router
from app.api.terms import router as terms_router
from app.api.audio import router as audio_router
from app.api.customers import router as customers_router
from app.api.health import router as health_router
from app.api.meetings import router as meetings_router
from app.api.projects import router as projects_router
from app.api.segments import router as segments_router
from app.api.templates import router as templates_router
from app.core.config import settings

logging.basicConfig(level=settings.log_level)

app = FastAPI(title="MeetingTools API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(customers_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(meetings_router, prefix="/api")
app.include_router(audio_router, prefix="/api")
app.include_router(asr_router, prefix="/api")
app.include_router(segments_router, prefix="/api")
app.include_router(terms_router, prefix="/api")
app.include_router(templates_router, prefix="/api")
app.include_router(llm_configs_router, prefix="/api")
app.include_router(summaries_router, prefix="/api")
app.include_router(exports_router, prefix="/api")
