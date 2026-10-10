from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend.database import initialize_database
from backend.api.routes import router


@asynccontextmanager
async def lifespan(_app):
    initialize_database()
    yield


app = FastAPI(
    title="Bilbo AI Companion",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(router)


@app.get("/")
def home():

    return {
        "message": "Bilbo backend is running! 🐰"
    }