from fastapi import FastAPI
from routes import router as auth_router

app = FastAPI(
    title="Artspire-Auth"
)

app.include_router(auth_router)
