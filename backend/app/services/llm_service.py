from google import genai


class LLMService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def chat(self, system_prompt: str, user_message: str) -> str:
        try:
            prompt = f"System: {system_prompt}\nUser: {user_message}"

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return response.text.strip()

        except Exception as e:
            return f"LLM Error: {str(e)}"