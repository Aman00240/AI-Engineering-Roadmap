from groq import Groq
from groq.types.chat import ChatCompletionMessageParam
from config import settings


client = Groq(api_key=settings.GROQ_API_KEY)
conversation_history: list[ChatCompletionMessageParam] = [
    {
        "role": "system",
        "content": "you are a helpful companion.",
    }
]

print("Type 'quit' to exit")
while True:
    user_input = input("You :")

    if user_input.lower() in ["quit"]:
        break

    conversation_history.append({"role": "user", "content": user_input})

    completion = client.chat.completions.create(
        messages=conversation_history, model=settings.MODEL_NAME, temperature=0.5
    )

    ai_response = completion.choices[0].message.content
    print(f"AI: {ai_response}")

    conversation_history.append({"role": "assistant", "content": ai_response})
    print(f" [Context Size: {len(conversation_history)} messages]\n")
