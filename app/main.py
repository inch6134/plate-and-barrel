from fastapi import FastAPI

from app.api import leaderboard, players

app = FastAPI(title="Plate&Barrel")
app.include_router(players.router)
app.include_router(leaderboard.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
