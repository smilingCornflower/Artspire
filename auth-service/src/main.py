import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from rabbit.jwt_server import jwt_server
from rabbit.users_server import users_server
from api.router import router as auth_router
from contextlib import asynccontextmanager
from config import logger


@asynccontextmanager
async def async_lifespan(app_name: FastAPI):
    app.jwt_rpc_task = asyncio.create_task(jwt_server())
    app.users_rpc_task = asyncio.create_task(users_server())
    yield
    app.jwt_rpc_task.cancel()
    app.users_rpc_task.cancel()


app = FastAPI(
    title="Artspire-Auth",
    lifespan=async_lifespan,
)

# Allow all hosts with 3000 port
REGEX_ORIGINS: str = r".*:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:3000$"
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins_regex=REGEX_ALLOWED_ORIGINS,
)

app.include_router(auth_router)


@app.get("/")
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run(app=app, port=8001, host="0.0.0.0")
