from fastapi import APIRouter
from pydantic import BaseModel
from app.services.session_store import SessionStore
from app.services.llm_service import LLMService
from app.agents.chat_agent import ChatAgent
from app.agents.master_agent import MasterAgent
from app.agents.sales_agent import SalesAgent
from app.agents.kyc_agent import KycAgent
from app.agents.credit_agent import CreditAgent
from app.agents.sanction_agent import SanctionAgent
from app.services.crm_service import CRMService
from app.services.credit_score_service import CreditScoreService
import os

router = APIRouter()
sessions = SessionStore()

llm_service = LLMService(api_key=os.getenv("OPENAI_API_KEY"))

master_agent = MasterAgent(
    SalesAgent(),
    KycAgent(CRMService()),
    CreditAgent(CreditScoreService()),
    SanctionAgent(),
)

chat_agent = ChatAgent(master_agent, llm_service)


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat(req: ChatRequest):
    state = sessions.get(req.session_id)
    result = await chat_agent.handle_message(req.message, state)
    sessions.save(req.session_id, result["state"])
    return result
