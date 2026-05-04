import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from httpx import stream
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr

load_dotenv()

llm = ChatGroq(
    api_key=SecretStr(os.environ.get("groq_key") or ""),
    model="llama-3.3-70b-versatile",
    temperature=0,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def calculate_string_length(text: str) -> int:
    """Calculates the length of a given text string."""
    return len(text)


tools = [calculate_string_length]


def call_model(state: State):
    llm_with_tools = llm.bind_tools(tools)

    response = llm_with_tools.invoke(state["messages"])

    return {"messages": [response]}


tool_node = ToolNode(tools)

workflow = StateGraph(State)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges("agent", tools_condition)

workflow.add_edge("tools", "agent")

app = workflow.compile()

print("Running the LangGraph Agent...\n")

inputs = {
    "messages": [
        HumanMessage(
            content="How many characters are in the word 'Supercalifragilisticexpialidocious'?"
        )
    ]
}

for event in app.stream(inputs, stream_mode="values"):  # type:ignore
    messages = event["messages"][-1]
    messages.pretty_print()


final_state = app.invoke(inputs)  # type:ignore

final_message = final_state["messages"][-1]

print("\nFinal AI Answer:")
print(final_message.content)
