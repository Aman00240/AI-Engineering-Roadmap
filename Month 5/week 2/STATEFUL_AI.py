import os
import sqlite3
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from groq import Groq
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()

client = Groq(api_key=os.environ.get("groq_key"))


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: AgentState):
    groq_messages = []
    for msg in state["messages"]:
        if msg.type == "human":
            groq_messages.append({"role": "user", "content": msg.content})
        elif msg.type == "ai":
            groq_messages.append({"role": "assistant", "content": msg.content})
        elif msg.type == "system":
            groq_messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, dict):
            groq_messages.append(msg)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        temperature=0,
        max_tokens=1024,
    )
    bot_response = response.choices[0].message.content
    return {"messages": [AIMessage(content=bot_response)]}


workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)


def start_persistent_chat():
    conn = sqlite3.connect("manager.db", check_same_thread=False)
    memory = SqliteSaver(conn)

    app = workflow.compile(checkpointer=memory)

    config: RunnableConfig = {"configurable": {"thread_id": "my_persistent_session"}}

    print("Stateful Manager Initialized. Type 'exit' to quit.")
    print("-" * 50)

    while True:
        user_input = input("\nUser > ")
        if user_input.lower() in ["exit", "quit"]:
            print("Shutting Down")
            break

        state_update: AgentState = {
            "messages": [{"role": "user", "content": user_input}]
        }

        for event in app.stream(state_update, config):
            for node_name, values in event.items():
                if node_name == "agent":
                    print(f"\AI: {values['messages'][-1].content}")


start_persistent_chat()
