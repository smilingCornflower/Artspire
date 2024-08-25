from fastapi import FastAPI
from api.router import router as auth_router


app = FastAPI(
    title="Artspire-Auth"
)

app.include_router(auth_router)
