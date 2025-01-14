import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import settings, logger
from rabbit.similarity_server import similarity_server
from rec import update_similarity_matrix


@asynccontextmanager
async def async_lifespan(app_name: FastAPI):
    app.task = asyncio.create_task(similarity_server())
    yield
    app.task.cancel()


app = FastAPI(
    title="Artspire-Recommendations",
    lifespan=async_lifespan,
)


@app.post("/update-similarity-matrix")
async def update_sim(key_word: str):
    if key_word == settings.update_password:
        logger.info("password is correct")
        await update_similarity_matrix()
    else:
        logger.info("password is incorrect")


if __name__ == "__main__":
    uvicorn.run(app=app, port=8002, host="0.0.0.0")
