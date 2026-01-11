import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

print("Conecting To Groq")

completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "I am learning to be an AI Engineer. Give me a one-sentence motivation.",
        }
    ],
    model="llama-3.3-70b-versatile",
)
print("\nAI says:")
print(completion.choices[0].message.content)
