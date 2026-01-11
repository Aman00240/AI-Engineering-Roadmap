from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

print("Asking Shrek")

completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are Shrek, Speak in Shrek"},
        {"role": "user", "content": "Explain what pytohn is"},
    ],
    model=settings.MODEL_NAME,
)

print("\nShrek Says:")
print(completion.choices[0].message.content)
