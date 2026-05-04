import json
import os
import subprocess
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import Annotated, TypedDict, add_messages
from pydantic import BaseModel, Field

load_dotenv()

client = Groq(api_key=os.environ.get("groq_key"))


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


class ExecuteFileInput(BaseModel):
    filename: str = Field(
        description="The name of python file to execute (eg.,script.py)"
    )


class SaveFileInput(BaseModel):
    filename: str = Field(description="The name of python file to save (eg.,script.py)")
    content: str = Field(description="The full text content to write into file")


def execute_python_file(filename: str) -> str:
    print(f"Executing Script: {filename}...")

    try:
        if not os.path.exists(filename):
            return f"Error File {filename} not found "

        result = subprocess.run(
            ["python3", filename], capture_output=True, text=True, timeout=40
        )

        if result.returncode == 0:
            return f"Execution Successful.\nOutput:\n{result.stdout}"
        else:
            return f"Execution Failed.\nOutput:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: Script Execution Timed Out"
    except Exception as e:
        return f"Error: {str(e)}"


def save_python_file(filename: str, content: str) -> str:
    print(f"Saving File {filename}...")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: Content saved to file: {filename}"
    except Exception as e:
        return f"Error: Failed to save file - {str(e)}"


tool_list = [
    {
        "type": "function",
        "function": {
            "name": "save_file",
            "description": "Saves code or text to a local file.",
            "parameters": SaveFileInput.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python_file",
            "description": "Executes a Python script and returns the terminal output.",
            "parameters": ExecuteFileInput.model_json_schema(),
        },
    },
]

available_tools = {
    "save_file": save_python_file,
    "execute_python_file": execute_python_file,
}

system_prompt = """You are an Autonomous Software Engineer. Your goal is to write, save, and test Python code.

You have access to tools to save files and execute Python scripts.

WORKFLOW & RULES:
1. ACTION FIRST: When asked to write a program, your very first action MUST be to call the `save_file` tool. Do not type any introductory text, explanations, or raw code in the chat.
2. PASSING CODE: Pass the complete, working Python code strictly into the `content` argument of the `save_file` tool.
3. EXECUTE: Use the `execute_python_file` tool to run the file you just saved.
4. SILENT DEBUGGING: If the execution returns an Error, you MUST NOT explain the error or chat. SILENTLY generate the corrected code and pass it directly into the `save_file` tool again.
5. FINAL OUTPUT: Once the code executes successfully, you MUST STOP calling tools. Tell the user the final output in standard plain text.
6. CRITICAL FORMATTING: NEVER use square brackets `[` or `]` in your final chat response. If the script output is a list, format it as comma-separated numbers.
"""


def call_model(state: AgentState):
    groq_messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    for msg in state["messages"]:
        if isinstance(msg, AIMessage):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                groq_messages.append(
                    {
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": [
                            {
                                "id": tc["id"],
                                "type": "function",
                                "function": {
                                    "name": tc["name"],
                                    "arguments": json.dumps(tc["args"]),
                                },
                            }
                            for tc in msg.tool_calls
                        ],
                    }
                )
            else:
                groq_messages.append({"role": "assistant", "content": msg.content})

        elif isinstance(msg, ToolMessage):
            groq_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "name": msg.name,
                    "content": msg.content,
                }
            )

        elif msg.type == "human":
            groq_messages.append({"role": "user", "content": msg.content})

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=groq_messages,  # type: ignore
        tools=tool_list,  # type: ignore
        tool_choice="auto",
        temperature=0,
        max_tokens=1024,
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        lc_tool_calls = [
            {
                "id": tc.id,
                "name": tc.function.name,
                "args": json.loads(tc.function.arguments),
            }
            for tc in response_message.tool_calls
        ]
        return {"messages": [AIMessage(content="", tool_calls=lc_tool_calls)]}
    else:
        return {"messages": [AIMessage(content=response_message.content)]}


def execute_tools(state: AgentState):
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message.tool_calls:
        function_name = tool_call["name"]
        function_args = tool_call["args"]
        function_to_call = available_tools[function_name]

        try:
            function_response = function_to_call(**function_args)
        except Exception as e:
            function_response = f"Error: {str(e)}"

        tool_results.append(
            ToolMessage(
                content=function_response,
                name=function_name,
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": tool_results}


def should_continus(state: AgentState):
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"
    return END


workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", execute_tools)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continus, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


def start_chat():
    config: RunnableConfig = {"configurable": {"thread_id": "coder_thread"}}

    print("Coder Agent Booting up. Type 'exit' to quit.")
    print("-" * 50)

    while True:
        user_input = input("User> ")

        if user_input.lower() in ["quit", "exit"]:
            print("Shutting Down")
            break

        status_update: AgentState = {
            "messages": [{"role": "user", "content": user_input}]
        }

        for event in app.stream(status_update, config):
            for node_name, value in event.items():
                if node_name == "agent":
                    last_msg = value["messages"][-1]
                    if last_msg.content:
                        print(f"\nAI: {last_msg.content}\n")
                    else:
                        print("\nAI: (Thinking/Calling Tools...)\n")


start_chat()
