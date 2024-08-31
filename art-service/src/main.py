import uvicorn
from fastapi import FastAPI
from api.router import router as arts_router
from rabbit.ping_sender import ping_sender
import asyncio
from asyncio import Task


async def async_lifespan(app: FastAPI):
    ping_sender_task: "Task" = asyncio.create_task(ping_sender())
    yield
    ping_sender_task.cancel()

app = FastAPI(
    title="Artspire-Arts",
    lifespan=async_lifespan,    # noqa
)

app.include_router(arts_router)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
