import uvicorn
from fastapi import FastAPI
from api.router import router as arts_router

app = FastAPI(
    title="Artspire-Arts"
)

app.include_router(arts_router)
