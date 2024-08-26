from fastapi import FastAPI
from api.router import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Artspire-Auth"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
