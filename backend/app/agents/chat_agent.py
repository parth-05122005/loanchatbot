import re
from typing import Dict, Any


SYSTEM_PROMPT = """
You are a virtual sales officer for a personal loan chatbot.

Your role:
- Converse naturally with users
- Collect required details politely
- Explain backend loan decisions
- NEVER approve or reject loans

Rules:
- Do NOT calculate EMI
- Do NOT invent policies
- Always rely on backend decisions
"""


class ChatAgent:
    def __init__(self, master_agent, llm_service):
        self.master_agent = master_agent
        self.llm_service = llm_service

    def _extract_entities(self, message: str, state: Dict[str, Any]):
        # PAN
        pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", message)
        if pan_match:
            state["pan"] = pan_match.group()

        # Income
        income_match = re.search(r"(\d{4,6})", message)
        if "income" in message.lower() and income_match:
            state["monthly_income"] = int(income_match.group())

        # Loan amount
        if "loan" in message.lower() and income_match:
            state["loan_amount"] = int(income_match.group())

        return state

    async def handle_message(self, user_message: str, state: Dict[str, Any]) -> Dict[str, Any]:
        state = self._extract_entities(user_message, state)

        required = ["pan", "monthly_income", "loan_amount"]
        missing = [r for r in required if r not in state]

        # Ask for missing info
        if missing:
            reply = self.llm_service.chat(
                SYSTEM_PROMPT,
                f"User said: {user_message}. Ask politely for {missing}."
            )
            return {"reply": reply, "state": state}

        # Backend call
        result = await self.master_agent.process_loan_application(
            pan=state["pan"],
            loan_amount=state["loan_amount"],
            tenure_months=24,
            monthly_income=state["monthly_income"],
            is_preapproved=False,
        )

        # Explain result
        reply = self.llm_service.chat(
            SYSTEM_PROMPT,
            f"Explain this backend decision politely: {result}"
        )

        return {"reply": reply, "state": state, "decision": result}
