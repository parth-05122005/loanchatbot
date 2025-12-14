from openai import OpenAI


class LLMService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def chat(self, system_prompt: str, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content
