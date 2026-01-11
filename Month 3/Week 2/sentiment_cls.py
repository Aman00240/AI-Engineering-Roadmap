from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def analyze_sentiment(text):
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a sentiment classifier. Only give output exactly from this list [POSITIVE,NEGATIVE,NEUTRAL]",
            },
            {"role": "user", "content": "The battery lasts 10 hours!"},
            {"role": "assistant", "content": "POSITIVE"},
            {"role": "user", "content": "It arrived broken."},
            {"role": "assistant", "content": "NEGATIVE"},
            {"role": "user", "content": "The case is blue."},
            {"role": "assistant", "content": "NEUTRAL"},
            {"role": "user", "content": text},
        ],
        model=settings.MODEL_NAME,
        temperature=0,
    )
    return completion.choices[0].message.content


input_text = "ill die from laughing"

print(f"Input: {input_text}")
print(f"Result: {analyze_sentiment(input_text)}")
