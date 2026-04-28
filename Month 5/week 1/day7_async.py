import asyncio
import json
import os

from dotenv import load_dotenv
from groq import AsyncGroq
from pydantic import BaseModel, Field

load_dotenv()

client = AsyncGroq(api_key=os.environ.get("groq_key"))


class ListDirInput(BaseModel):
    path: str = Field(
        description="The directory path to list. use '.' for current directory"
    )


class ReadFileInput(BaseModel):
    filename: str = Field(description="The exact path to the file to read")


class WriteFileInput(BaseModel):
    filename: str = Field(description="The exact path to the file to write")
    content: str = Field(description="The text content to write in this file")


async def list_directory(path: str) -> str:
    try:
        files = os.listdir(path)
        return f"Contents of the '{path}': {', '.join(files)}"

    except Exception as e:
        return f"Error listing directory: {str(e)}"


async def read_file(filename: str) -> str:
    try:
        with open(filename, "r") as f:
            content = f.read()
        return f"Content of '{filename}':\n{content}"

    except Exception as e:
        return f"Error reading file: {str(e)}"


async def write_file(filename: str, content: str) -> str:
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"

    except Exception as e:
        return f"Error writing file: {str(e)}"


available_tools = {
    "list_directory": list_directory,
    "read_file": read_file,
    "write_file": write_file,
}


tools_list = [
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List all the files and folders in a directory",
            "parameters": ListDirInput.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "read content of a file",
            "parameters": ReadFileInput.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file. This overwrites existing content.",
            "parameters": WriteFileInput.model_json_schema(),
        },
    },
]


system_prompt = """
You are the OS Commander, an advanced file system agent.
You have access to tools to list directories, read files, and write files.
1. If the user asks you to perform a file operation, CALL THE RELEVANT TOOL.
2. If the user asks for a multi-step operation (e.g., "read file A and write it to file B"), execute the tools sequentially.
3. NEVER hallucinate file contents. Always read the file first in case a read operation is performed.
4. If a tool returns an error, inform the user of the error and stop.
5. ANTI-LOOP RULE: You are strictly forbidden from calling the exact same tool with the exact same arguments more than once.
Once you receive a successful tool output, immediately give the final answer.
6. FORMATTING RULE: When quoting code or file contents in your final response,
ALWAYS use standard formatting and NEVER output raw JSON escape characters (like backslashes) to the user.
"""

messages = [{"role": "system", "content": system_prompt}]


async def start_interactive_shell():
    global messages
    print("OS Commander Initialized. Type 'exit' to quit.")
    print("-" * 50)

    while True:
        user_input = input("\nUser > ")

        if user_input.lower() in ["exit", "quit"]:
            print("Shutting down Commander...")
            break

        print(f"  [Memory Check] -> Currently holding {len(messages)} messages.")

        if len(messages) > 15:
            slice_idx = -10

            while True:
                item = messages[slice_idx]
                role = item["role"] if isinstance(item, dict) else item.role

                if role == "tool":
                    slice_idx += 1
                else:
                    break

            messages = [messages[0]] + messages[slice_idx:]

        messages.append({"role": "user", "content": user_input})

        while True:
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,  # type: ignore
                tools=tools_list,  # type: ignore
                tool_choice="auto",
                max_tokens=2048,
                temperature=0,
            )

            response_message = response.choices[0].message  # type: ignore
            messages.append(response_message)  # type: ignore

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f" [Action]-> {function_name} {function_args}")

                    function_to_call = available_tools[function_name]

                    try:
                        function_response = await function_to_call(**function_args)
                    except Exception as e:
                        function_response = f"Error: {str(e)}"

                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(function_response),
                        }
                    )
            else:
                print(f"\nAI : {response_message.content}")
                break


asyncio.run(start_interactive_shell())
