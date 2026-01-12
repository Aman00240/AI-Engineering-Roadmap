import json
from groq import Groq
from config import settings
from groq.types.chat import ChatCompletionToolParam, ChatCompletionMessageParam

client = Groq(api_key=settings.GROQ_API_KEY)


def add_numbers(a: int, b: int):
    return a + b


tool: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "The first number"},
                    "b": {"type": "integer", "description": "The second number"},
                },
                "required": ["a", "b"],
            },
        },
    }
]


def chat_with_tools(user_text: str):
    print(f"User: {user_text}")
    message: list[ChatCompletionMessageParam] = [{"role": "user", "content": user_text}]

    completion = client.chat.completions.create(
        messages=message,
        model=settings.MODEL_NAME,
        tools=tool,
        tool_choice="auto",
    )

    response_msg = completion.choices[0].message
    print(response_msg, "\n")
    tool_calls = response_msg.tool_calls
    print(tool_calls, "\n")

    if tool_calls:
        function_name = tool_calls[0].function.name
        args = json.loads(tool_calls[0].function.arguments)

        print(f"AI Decision: CALL FUNCTION `{function_name}`")
        print(f"Arguments: {args}")
        message.append(response_msg)  # type:ignore
        print(f"\nMessage:{message}\n")

        if function_name == "add_numbers":
            result = add_numbers(args["a"], args["b"])
            print(f"Python Result: {result}")

            message.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_calls[0].id,
                    "content": str(result),
                }
            )
        print(f"\nMessage\n{message}")
        final_response = client.chat.completions.create(
            messages=message,
            model=settings.MODEL_NAME,
        )
        print(f" AI Final Answer: {final_response.choices[0].message.content}")
    else:
        print(f"AI: {response_msg.content}")


chat_with_tools("What is 50 plus 20")

print("-" * 20)

chat_with_tools("What is the capital of France?")
