import json
import os

from dotenv import load_dotenv
from groq import Groq
from tools import (
    calculator,
    calculator_tool_definition,
    get_current_time,
    get_weather,
    read_server_logs,
    server_logs_tool_definition,
    time_tool_defination,
    weather_tool_defination,
)

load_dotenv()

client = Groq(api_key=os.environ.get("groq_key"))

available_tools = {
    "calculator": calculator,
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "read_server_logs": read_server_logs,
}

tools_list = [
    calculator_tool_definition,
    weather_tool_defination,
    time_tool_defination,
    server_logs_tool_definition,
]

system_prompt = """
You are a helpful AI Assistant with access to tools.
1. If the user asks a question that requires a tool, CALL THE TOOL.
2. Do not hallucinate answers. Use the tool output.
3. If you have the final answer, output it normally.
4. STRICT SCHEMA RULE: When passing numbers to the calculator tool, you MUST pass them as raw integers (e.g., 10), NEVER as strings (e.g., "10").
5. If a tool returns an error stating 'Invalid date format',
you are permitted to correct the format and call the tool ONE more time.
6. If the tool fails a second time, stop and report the error to the user.
7. ANTI-LOOP RULE: You are strictly forbidden from calling the exact same tool with the exact same arguments more than once.
Once you receive a successful tool output, immediately synthesize the final answer.
"""


def run_agent(user_query: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]

    print(f"\nUser: {user_query}")

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,  # type: ignore
            tools=tools_list,  # type: ignore
            tool_choice="auto",
            max_tokens=1024,
        )

        response_message = response.choices[0].message
        print(response_message, "\n")

        messages.append(response_message)  # type: ignore

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                print(tool_call, "\n")

                function_name = tool_call.function.name

                function_args = json.loads(tool_call.function.arguments)

                print(
                    f"Agent Thinking -> Calling Tool; {function_name} with {function_args}"
                )

                function_to_call = available_tools[function_name]

                try:
                    function_response = function_to_call(**function_args)
                except Exception as e:
                    function_response = f"Error:{str(e)}"

                print(f"Tool Output -> {function_response}")

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )
        else:
            print(f"Agent: {response_message.content}\n")
            break


if __name__ == "__main__":
    run_agent(
        "Check the server logs for 2026-04-15. CRITICAL: You must intentionally pass the literal text 'April 15th' into the tool on your first attempt."
    )
