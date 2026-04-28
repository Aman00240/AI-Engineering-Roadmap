from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class RouterState(TypedDict):
    messages: Annotated[list, add_messages]
    route_to: str


def gatekeeper_node(state: RouterState):
    print("Executing: gatekeeper...")
    last_message = state["messages"][-1]

    content = (
        last_message.content if hasattr(last_message, "content") else str(last_message)
    )

    if "apple" in content.lower():
        print("Decision: Routing to Fruit Node")
        return {"route_to": "fruit_node"}
    else:
        print("Decision: Routing to END")
        return {"route_to": "end"}


def should_continue(state: RouterState) -> Literal["fruit_node", "end"]:
    if state["route_to"] == "fruit_node":
        return "fruit_node"
    return "end"


def fruit_processing_node(state: RouterState):
    print("Executing: fruit_processing_node")
    return {"messages": ["Fruit node has processed your request."]}


workflow = StateGraph(RouterState)

workflow.add_node("gatekeeper", gatekeeper_node)
workflow.add_node("fruit_node", fruit_processing_node)

workflow.add_edge(START, "gatekeeper")

workflow.add_conditional_edges(
    "gatekeeper", should_continue, {"fruit_node": "fruit_node", "end": END}
)

workflow.add_edge("fruit_node", END)
app = workflow.compile()


print(">>> RUN 1: Input 'I like apple'")
state_1 = {"messages": ["I like apple"], "route_to": ""}
app.invoke(state_1)  # type: ignore

print(">>> RUN 2: Input 'I like pizza'")
state_2 = {"messages": ["I like pizza"], "route_to": ""}
app.invoke(state_2)  # type: ignore
