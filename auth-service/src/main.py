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
    logger.info(f"{app_name} Started")
    await jwt_server()
    yield


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
    uvicorn.run(app=app, port=8002, host="0.0.0.0")
