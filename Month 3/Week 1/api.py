from fastapi import FastAPI
from pydantic import BaseModel
from groq import AsyncGroq
from config import settings


app = FastAPI()

client = AsyncGroq(api_key=settings.GROQ_API_KEY)


class UserText(BaseModel):
    text: str


@app.post("/chat")
async def chat_with_ai(query: UserText):
    print(f"Received: {query.text}")

    completion = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": query.text},
        ],
        model=settings.MODEL_NAME,
        temperature=0.7,
    )

    answer = completion.choices[0].message.content

    return {"ai_response": answer}
