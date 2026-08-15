from fastapi import FastAPI

app = FastAPI(title="Plate&Barrel")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
