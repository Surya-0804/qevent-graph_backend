from fastapi import FastAPI
import subprocess
import os
from dotenv import load_dotenv

from app.api.routes import router
from app.api.execution_routes import router as execution_router
from app.api.replay_routes import router as replay_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Event-Graph Quantum Backend")

# Add CORS middleware - origins from environment variable
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(execution_router)
app.include_router(replay_router)

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/status")
def status():
    """
    this function return the last git commit hash """
    try:
        commit_id = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("utf-8")
            .strip()
        )
        return commit_id
    except Exception:
        return "unknown"