"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import chat, documents, evaluation
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.database import sqlite

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    sqlite.get_connection()  # create tables
    log.info("RAG API starting")
    yield


app = FastAPI(title="RAG From Scratch API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(_, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])
