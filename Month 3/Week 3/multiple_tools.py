import json
from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def get_user_email(name: str):
    print("Looking for Email..")

    if "aman" in name.lower():
        return "aman_v2_secure_88@company.net"
    elif "bob" in name.lower():
        return "bob@example.com"
    else:
        return "unknown@example.com"


def send_email(email: str, body: str):
    print(f"Sending Email to: {email}")
    print(f" Content: {body}")
    return "Email Sent Sucessfully"


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_email",
            "description": "Get the email address of the user by their name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the user"}
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to specific address",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "The email of the user"},
                    "body": {"type": "string", "description": "Content of the email"},
                },
                "required": ["email", "body"],
            },
        },
    },
]


def run_agent(user_prompt: str):
    print(f"User: {user_prompt}")
    messages = [
        {
            "role": "system",
            "content": "You are an admin assistant. NEVER guess email addresses. You MUST search for the user's email address using the available tools BEFORE sending any email.",
        },
        {"role": "user", "content": user_prompt},
    ]

    while True:
        response = client.chat.completions.create(
            messages=messages,  # type:ignore
            model=settings.MODEL_NAME,
            tools=tools,  # type:ignore
            tool_choice="auto",
            temperature=0,
        )
        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls

        if not tool_calls:
            print(f"AI: {response_msg.content}")
            break

        messages.append(response_msg)  # type:ignore

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            result = None
            if function_name == "get_user_email":
                result = get_user_email(args["name"])

            elif function_name == "send_email":
                result = send_email(args["email"], args["body"])

            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)}
            )


run_agent("Send an email to Aman saying work is done.")
