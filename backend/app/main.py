from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.loan_routes import router as loan_router
from app.api.chat_routes import router as chat_router

# Create FastAPI app FIRST
app = FastAPI(title="Loan Processing System")

# Add middleware AFTER app exists
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers LAST
app.include_router(loan_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
