from contextlib import asynccontextmanager

from . import env as _env  # noqa: F401 — load backend/.env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine
from .routers import auth, chat, context, mini_apps, progress, router, sessions, summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="MindPath AI API",
    description="Backend API for the MindPath AI self-reflection MVP.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(context.router)
app.include_router(router.router)
app.include_router(mini_apps.router)
app.include_router(progress.router)
app.include_router(summary.router)


@app.get("/")
def health_check() -> dict[str, str | bool | None]:
    from .services.llm_service import LlmService

    provider = LlmService.provider()
    return {
        "status": "ok",
        "project": "MindPath AI",
        "llm_provider": provider,
        "llm_configured": LlmService.is_configured(),
        "llm_model": LlmService.model(),
        "ai_gateway_configured": provider == "ai_gateway",
    }
