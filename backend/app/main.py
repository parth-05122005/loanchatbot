from fastapi import FastAPI
from app.api.loan_routes import router as loan_router

app = FastAPI(title="Loan Processing System")

app.include_router(loan_router, prefix="/api")
