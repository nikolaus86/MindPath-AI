from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine
from .routers import auth, chat, context, mini_apps, progress, router, sessions, summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
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
def health_check() -> dict[str, str]:
    return {"status": "ok", "project": "MindPath AI"}
