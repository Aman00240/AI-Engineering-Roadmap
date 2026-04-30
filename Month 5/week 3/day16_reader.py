import asyncio
import json
import os
from typing import Annotated, Any, TypedDict

import aiohttp
from dotenv.main import load_dotenv
from groq import AsyncClient
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from tavily import AsyncTavilyClient

load_dotenv()


class ReadUrlInput(BaseModel):
    url: str = Field(description="url for the tool")


class SearchToolInput(BaseModel):
    query: str = Field(description="The query to search on web")


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


client = AsyncClient(api_key=os.environ.get("groq_key"))
tavily = AsyncTavilyClient(api_key=os.environ.get("tavily_key"))


async def search_tool(query: str):
    print(f"Searching the web for {query}...")

    response = await tavily.search(query=query, search_depth="basic")

    content = "\n".join(
        [f"- {res['content']} (Source: {res['url']})" for res in response["results"]]
    )
    return content


async def read_url_tool(url: str) -> str:
    print(f"Reading Webpage: {url}...")

    jina_url = f"https://r.jina.ai/{url}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(jina_url) as response:
                if response.status == 200:
                    content = await response.text()
                    return content[:8000]
                else:
                    return (
                        f"Error: Could not read webpage. Status code {response.status}"
                    )

    except Exception as e:
        return f"Error reading url: {str(e)}"


system_prompt = """You are an autonomous research assistant. Your goal is to provide highly accurate, up-to-date, and well-structured answers.

You have access to two specific tools. You must use them strategically to gather information before answering.

TOOL USAGE RULES:
1. search_tool: Use this for current events, real-time data (weather, prices), or to find authoritative URLs on a specific topic.
2. read_url_tool: Use this to scrape the full text of a webpage.
3. TOOL CHAINING (IMPORTANT): If you need to summarize an article or extract deep context, first use the `search_tool` to find the direct URL, and then use the `read_url_tool`
    to read that exact URL. Do not guess or hallucinate the contents of a webpage based solely on search snippets.

OUTPUT GUIDELINES:
- Strict Constraints: Follow user instructions exactly.If asked for a specific number of items (e.g., "3 bullets"),
            you must provide exactly that number.
- Conciseness: Be highly direct and professional.Avoid repeating yourself and
            don't write redundant introductory sentences.
- Citations: You must append a "Sources:" section at the end of your response containing the exact
            URLs you used to gather the information.
- Accuracy: If the tools fail to return relevant information, state clearly that you cannot find the answer.
            Do not invent data. Be concise and direct.
"""


async def call_model(state: AgentState):
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

    response = await client.chat.completions.create(
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


async def execute_tools(state: AgentState):
    last_message = state["messages"][-1]

    tool_results = []

    for tool_call in last_message.tool_calls:
        function_name = tool_call["name"]
        function_args = tool_call["args"]

        function_to_call = available_tools[function_name]

        try:
            function_response = await function_to_call(**function_args)
        except Exception as e:
            function_response = f"Error:{str(e)}"

        tool_results.append(
            ToolMessage(
                content=function_response,
                name=function_name,
                tool_call_id=tool_call["id"],
            )
        )

    return {"messages": tool_results}


def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"

    return END


workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", execute_tools)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")


tool_list = [
    {
        "type": "function",
        "function": {
            "name": "read_url_tool",
            "description": "Reads the full content of a specific webpage, Use this when you have a specific URL to summarize ",
            "parameters": ReadUrlInput.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_tool",
            "description": "Searches a query on the web for answer",
            "parameters": SearchToolInput.model_json_schema(),
        },
    },
]


available_tools = {"read_url_tool": read_url_tool, "search_tool": search_tool}


async def start_chat():
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    config: RunnableConfig = {"configurable": {"thread_id": "my_thread"}}

    print("AI Booting up. Type 'exit' to quit.")
    print("-" * 50)

    while True:
        user_input = input("User> ")

        if user_input in ["quit", "exit"]:
            print("Shutting Down")
            break

        state_update: AgentState = {
            "messages": [{"role": "user", "content": user_input}]
        }

        async for event in app.astream(state_update, config):
            for node_name, value in event.items():
                if node_name == "agent":
                    last_msg = value["messages"][-1]
                    if last_msg.content:
                        print(f"\nAI: {last_msg.content}\n")
                    else:
                        print("\nAI: (Thinking/Calling Tools...)\n")


asyncio.run(start_chat())
