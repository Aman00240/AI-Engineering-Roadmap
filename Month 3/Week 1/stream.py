from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import AsyncGroq
from config import settings

app = FastAPI()

client = AsyncGroq(api_key=settings.GROQ_API_KEY)


class UserQuery(BaseModel):
    text: str


async def generate_response_stream(user_text: str):
    print(f"Streaming started for: {user_text}")

    stream = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_text},
        ],
        model=settings.MODEL_NAME,
        temperature=0.7,
        stream=True,
    )

    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content


@app.post("/chat")
async def chat_stram(query: UserQuery):
    return StreamingResponse(
        generate_response_stream(query.text), media_type="text/plain"
    )
