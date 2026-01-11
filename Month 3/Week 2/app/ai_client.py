from groq import AsyncGroq
from app.config import settings


class GroqClient:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.MODEL_NAME

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.5,
    ):
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                temperature=temperature,
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"Error communicating with groq {e}")
            return None


groq_client = GroqClient()
