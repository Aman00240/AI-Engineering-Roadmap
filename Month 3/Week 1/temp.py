from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def ask_bot(temp_value: float):
    print(f"\nTesting with Temperature {temp_value}")

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a concise encyclopedia"},
            {
                "role": "user",
                "content": "Define the word 'Creativity' in 5 words or less",
            },
        ],
        model=settings.MODEL_NAME,
        temperature=temp_value,
    )

    print(f"Answer: {completion.choices[0].message.content}")


print("--- Temp 0 ---")
ask_bot(0.0)
ask_bot(0.0)
ask_bot(0.0)


print("\n--- Temp 1.5 ---")
ask_bot(1.5)
ask_bot(1.5)
ask_bot(1.5)
