from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from .db import init_db
from .routes import reviews, analytics, ingest, search
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Reviews Copilot API",
    description="AI-powered customer review management system",
    version="1.0.0"
)

API_KEY = os.getenv("API_KEY", "dev-key-12345")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return api_key

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(reviews.router, dependencies=[Security(verify_api_key)])
app.include_router(analytics.router, dependencies=[Security(verify_api_key)])
app.include_router(ingest.router, dependencies=[Security(verify_api_key)])
app.include_router(search.router, dependencies=[Security(verify_api_key)])
