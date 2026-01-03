from fastapi import FastAPI
import subprocess

app = FastAPI()

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