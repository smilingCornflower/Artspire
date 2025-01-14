import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse
from api.routers.router import router as arts_router
from fastapi.middleware.cors import CORSMiddleware
from config import logger
from rabbit.s3_server import s3_add_server, s3_get_server
import asyncio


@asynccontextmanager
async def async_lifespan(app_: FastAPI):
    app_.s3_add_server_task = asyncio.create_task(s3_add_server())
    app_.s3_get_server_task = asyncio.create_task(s3_get_server())
    yield
    app_.s3_add_server_task.cancel()
    app_.s3_get_server_task.cancel()

app = FastAPI(
    title="Artspire-Arts",
    lifespan=async_lifespan,  # noqa
)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(arts_router)


@app.get("/")
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    logger.info(f"In __main__")
    uvicorn.run(app=app, port=8000, host="0.0.0.0")
