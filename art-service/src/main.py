import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.router import router as arts_router
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from asyncio import Task


async def async_lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Artspire-Arts",
    lifespan=async_lifespan,  # noqa
)

app.add_middleware(
    CORSMiddleware, # noqa
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
    uvicorn.run(app, port=8000)
