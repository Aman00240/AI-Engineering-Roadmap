import json
import random
from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def get_weather(city: str):
    return f"The Weather in {city} Is 1°C, ITS COLD DONT GO OUTSIDE"


def calculate_tax(income: float):
    return f"Tax owed: {income * 0.3}"


def roll_dice():
    return f"Dice Rolled : {random.randint(1, 6)}"


available_tools = {
    "get_weather": get_weather,
    "calculate_tax": calculate_tax,
    "roll_dice": roll_dice,
}

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get Weather for a city ",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_tax",
            "description": "calculate tax for an income ",
            "parameters": {
                "type": "object",
                "properties": {"income": {"type": "number"}},
                "required": ["income"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "roll_dice",
            "description": "roll a dice for a random number ",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def run_agent(user_prompt: str):
    messages = [{"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        messages=messages,  # type:ignore
        model=settings.MODEL_NAME,
        tools=tools_schema,  # type:ignore
        tool_choice="auto",
        temperature=0,
    )

    response_msg = response.choices[0].message
    tool_calls = response_msg.tool_calls

    if tool_calls:
        for tool_call in tool_calls:
            fname = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if args is None:
                args = {}

            print(f"\n AI wants to run: {fname} with {args}\n")

            if fname in available_tools:
                func_to_call = available_tools[fname]

                result = func_to_call(**args)

                print(f" Result: {result}")

            else:
                print(f"Error: Tool {fname} not found in registory")


print("--- Test 1 ---")
run_agent("I made $100000 this year, how much tax do I owe?")

print("\n--- Test 2 ---")
run_agent("Roll a dice for me.")

print("\n--- Test 3 ---")
run_agent("whats the weather in pilani today?")
