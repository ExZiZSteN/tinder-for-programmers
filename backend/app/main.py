from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="Tinder for Programmers",
    version="0.1.0"
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message" : "Tinder for Programmers API"}