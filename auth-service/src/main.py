import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rabbit.jwt_server import jwt_server
from api.router import router as auth_router
from contextlib import asynccontextmanager
from config import logger


@asynccontextmanager
async def async_lifespan(app_name: FastAPI):
    app.jwt_task = asyncio.create_task(jwt_server())
    yield
    app.jwt_task.cancel()

app = FastAPI(
    title="Artspire-Auth",
    lifespan=async_lifespan,
)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

if __name__ == "__main__":
    logger.info(f"In __main__")
    uvicorn.run(app=app, port=8001, host="0.0.0.0")
