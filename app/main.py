from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import leaderboard, players, insights

DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(title="Plate&Barrel")
app.include_router(players.router)
app.include_router(leaderboard.router)
app.include_router(insights.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")
