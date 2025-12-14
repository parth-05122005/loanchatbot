import re
from typing import Dict, Any

SYSTEM_PROMPT = """
You are a virtual sales officer for a personal loan chatbot.

Rules:
- Be polite and concise
- Never approve or reject loans yourself
- Explain backend decisions clearly
- NEVER change numbers or facts
"""

class ChatAgent:
    def __init__(self, master_agent, llm_service):
        self.master_agent = master_agent
        self.llm_service = llm_service

    # -----------------------------
    # Entity extractors
    # -----------------------------
    def extract_pan(self, message: str):
        match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", message.upper())
        return match.group() if match else None

    def extract_number(self, message: str):
        match = re.search(r"\b(\d{4,7})\b", message)
        return int(match.group(1)) if match else None

    def extract_confirmation(self, message: str):
        return bool(re.search(r"\b(yes|confirm|okay|correct|proceed)\b", message.lower()))

    # -----------------------------
    # Main handler (STATE MACHINE)
    # -----------------------------
    async def handle_message(self, message: str, state: Dict[str, Any]) -> Dict[str, Any]:
        state = state or {}
        stage = state.get("stage", "COLLECT_PAN")

        # =====================================================
        # FINAL STATE (DO NOT USE LLM HERE)
        # =====================================================
        if stage == "DONE" and "decision" in state:
            decision = state["decision"]
            result = decision.get("result", {})

            # SANCTIONED
            if decision.get("stage") == "SANCTION" and result.get("status") == "SANCTIONED":
                sanction_id = result.get("sanction_id")

                reply = (
                    "🎉 **Congratulations! Your loan has been approved.**\n\n"
                    f"• **Loan Amount:** {state['loan_amount']}\n"
                    f"• **Tenure:** 24 months\n"
                    f"• **Interest Rate:** 14%\n"
                    f"• **EMI:** {result.get('approved_emi')}\n\n"
                    "📄 You can download your sanction letter below."
                )

                return {
                    "reply": reply,
                    "state": state,
                    "decision": decision,
                    "sanction_letter_url": f"/static/outputs/sanction_{sanction_id}.txt",
                }

            # REJECTED / OTHER FINAL STATES
            reply = (
                "❌ **Your loan could not be approved.**\n\n"
                f"Reason: {result.get('reason', 'Not eligible as per policy.')}"
            )

            return {
                "reply": reply,
                "state": state,
                "decision": decision,
            }

        # =====================================================
        # STAGE 1: COLLECT PAN
        # =====================================================
        if stage == "COLLECT_PAN":
            pan = self.extract_pan(message)
            if pan:
                state["pan"] = pan
                state["stage"] = "COLLECT_INCOME"
                reply = "Thanks! Please tell me your monthly income."
            else:
                reply = "Please provide your PAN (e.g. ABCDE1234F)."

            return {"reply": reply, "state": state}

        # =====================================================
        # STAGE 2: COLLECT INCOME
        # =====================================================
        if stage == "COLLECT_INCOME":
            income = self.extract_number(message)
            if income:
                state["monthly_income"] = income
                state["stage"] = "COLLECT_LOAN"
                reply = "Got it. How much loan amount are you looking for?"
            else:
                reply = "Please tell me your monthly income."

            return {"reply": reply, "state": state}

        # =====================================================
        # STAGE 3: COLLECT LOAN AMOUNT
        # =====================================================
        if stage == "COLLECT_LOAN":
            loan = self.extract_number(message)
            if loan:
                state["loan_amount"] = loan
                state["stage"] = "CONFIRM_LOAN"
                reply = f"Please confirm: do you want to apply for a loan of {loan}?"
            else:
                reply = "Please tell me the loan amount you need."

            return {"reply": reply, "state": state}

        # =====================================================
        # STAGE 4: CONFIRM LOAN
        # =====================================================
        if stage == "CONFIRM_LOAN":
            if self.extract_confirmation(message):
                state["stage"] = "PROCESSING"
            else:
                reply = f"Please confirm whether you want a loan of {state['loan_amount']}."
                return {"reply": reply, "state": state}

        # =====================================================
        # STAGE 5: PROCESS BACKEND (ONE TIME)
        # =====================================================
        if stage == "PROCESSING":
            result = await self.master_agent.process_loan_application(
                pan=state["pan"],
                loan_amount=state["loan_amount"],
                tenure_months=24,
                monthly_income=state["monthly_income"],
                is_preapproved=False,
            )

            # Save final decision
            state["stage"] = "DONE"
            state["decision"] = result

            # Let DONE handler render it immediately
            return await self.handle_message("", state)

        # =====================================================
        # FALLBACK
        # =====================================================
        return {
            "reply": "Let me know if you need any further help.",
            "state": state,
        }
