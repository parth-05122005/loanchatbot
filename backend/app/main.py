from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from app.api.loan_routes import router as loan_router
from app.api.chat_routes import router as chat_router


app = FastAPI(title="Loan Processing System")

app.include_router(loan_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
