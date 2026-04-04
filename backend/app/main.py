import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.loan_routes import router as loan_router
from app.api.chat_routes import router as chat_router

app = FastAPI(title="Loan Processing System")

# FIX 1: Read allowed origin from env — falls back to localhost for local dev
# Set ALLOWED_ORIGIN=https://your-app.vercel.app in production .env
allowed_origin = os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIX 2: Mount static files so sanction letter download URLs actually work
# SanctionAgent writes to app/static/outputs/ and returns /static/outputs/<file>
os.makedirs("app/static/outputs", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(loan_router, prefix="/api")
app.include_router(chat_router, prefix="/api")