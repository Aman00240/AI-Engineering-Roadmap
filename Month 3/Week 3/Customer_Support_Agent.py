import json
from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def get_order_details(order_id: int):
    if order_id == 101:
        return {
            "id": "101",
            "product": "Phone",
            "status": "Delivered",
            "return_eligible": True,
        }
    elif order_id == 202:
        return {
            "id": "202",
            "product": "Laptop",
            "status": "Shipped",
            "return_eligible": False,
        }
    else:
        return "Item Not present"


def process_refund(order_id: int, reason: str):
    order_info = get_order_details(order_id)

    if isinstance(order_info, dict):
        if order_info["return_eligible"] is True:
            return "Refund ticket #9999 created."
        else:
            return "Error: Item not eligible."
    else:
        return "Item Not present"


def track_order(order_id: int):
    order_info = get_order_details(order_id)

    if isinstance(order_info, dict):
        if order_info["status"] == "Delivered":
            return "Already Delivered"
        elif order_info["status"] == "Shipped":
            return "Arriving tomorrow by 5 PM."

    else:
        return "Item Not present"


available_tools = {
    "get_order_details": get_order_details,
    "process_refund": process_refund,
    "track_order": track_order,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_details",
            "description": "get order details of an item",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "integer"}},
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": "Process refund for an order only if its return eligibility is True ",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["order_id", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Track order status ",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "integer"}},
                "required": ["order_id"],
            },
        },
    },
]

system_prompt = """You are a Customer Support Agent You must follow this protocol for all the requests:
                PROTOCOL:
                1. You MUST run `get_order_details` FIRST to check eligibility.
                2.ONLY IF `return_eligible` is True, you may call `process_refund`.
                3.If False, you must decline the refund.
                4.You can track orders anytime"""


def run_agent(user_prompt: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    while True:
        response = client.chat.completions.create(
            messages=messages,  # type:ignore
            model=settings.MODEL_NAME,
            tools=tools,  # type: ignore
            tool_choice="auto",
            temperature=0,
        )

        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls
        messages.append(response_msg)  # type:ignore

        if not tool_calls:
            print(f"AI: {response_msg.content}")
            break

        if tool_calls:
            for tool_call in tool_calls:
                fname = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"AI wants to run {fname} with {args}")

                if fname in available_tools:
                    func_to_call = available_tools[fname]

                    result = func_to_call(**args)
                    print(f"Result: {result}")

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result),
                        }
                    )
                else:
                    print(f"Error tool with {fname} not found")


run_agent("I want to return order 101 because it's broken. Also where is order 202?")
print("\n")
run_agent("I want to return my laptop (Order 202) because I hate it.")
