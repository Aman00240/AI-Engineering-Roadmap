import asyncio
import json
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from groq import AsyncGroq
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from tavily import AsyncTavilyClient

load_dotenv()

tavily = AsyncTavilyClient(api_key=os.environ.get("tavily_key"))
client = AsyncGroq(api_key=os.environ.get("groq_key"))


class SearchToolInput(BaseModel):
    query: str = Field(description="The query to search on web")


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


async def search_tool(query: str):
    print(f"Searching the web for {query}...")

    response = await tavily.search(query=query, search_depth="basic")

    content = "\n".join(
        [f"- {res['content']} (Source: {res['url']})" for res in response["results"]]
    )
    return content


tools_list = [
    {
        "type": "function",
        "function": {
            "name": "search_tool",
            "description": "Searches a query on the web for answer",
            "parameters": SearchToolInput.model_json_schema(),
        },
    }
]

available_tools = {"search_tool": search_tool}


async def call_model(state: AgentState):
    groq_messages = [
        {
            "role": "system",
            "content": """You are a helpful research assistant.
                            You have access to a web search tool. Only give the necessary information and give the answer in proper format (e.g., using bullet points).
                            If the user asks for current events, stock prices, weather, or any data about a present condition/event in the world, you must use the search_tool.
                            Do not output information from the tool if it does not have an attached source URL.
                            """,
        }
    ]

    for msg in state["messages"]:
        if msg.type == "human":
            groq_messages.append({"role": "user", "content": msg.content})
        elif msg.type == "ai":
            groq_messages.append({"role": "assistant", "content": msg.content})
        elif msg.type == "system":
            groq_messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, dict):
            groq_messages.append(msg)

    response = await client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=groq_messages,  # type: ignore
        tools=tools_list,  # type: ignore
        tool_choice="auto",
        temperature=0,
        max_tokens=1024,
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        groq_messages.append(response_message.model_dump(exclude_unset=True))

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            function_to_call = available_tools[function_name]

            try:
                function_response = await function_to_call(**function_args)
            except Exception as e:
                function_response = f"Error: {str(e)}"

            groq_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_response,
                }
            )

        final_response = await client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=groq_messages,  # type: ignore
            temperature=0,
            max_tokens=1024,
        )
        bot_response = final_response.choices[0].message.content
        return {"messages": [AIMessage(content=bot_response)]}

    else:
        bot_response = response_message.content
        return {"messages": [AIMessage(content=bot_response)]}


workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)


async def start_chat():
    memory = MemorySaver()

    app = workflow.compile(checkpointer=memory)

    config: RunnableConfig = {"configurable": {"thread_id": "my_thread"}}

    print("AI Booting up. Type 'exit' to quit.")
    print("-" * 50)

    while True:
        user_input = input("User >")

        if user_input in ["quit", "exit"]:
            print("Shutting Down")
            break

        state_update: AgentState = {
            "messages": [{"role": "user", "content": user_input}]
        }

        async for event in app.astream(state_update, config):
            for node_name, value in event.items():
                if node_name == "agent":
                    print(f"\nAI: {value['messages'][-1].content}\n")


asyncio.run(start_chat())
