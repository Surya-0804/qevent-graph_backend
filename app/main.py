from fastapi import FastAPI
import subprocess

from app.api.routes import router
from app.api.execution_routes import router as execution_router


app = FastAPI(title="Event-Graph Quantum Backend")

app.include_router(router)
app.include_router(execution_router)

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