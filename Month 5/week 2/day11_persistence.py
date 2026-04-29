from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph


class CounterState(TypedDict):
    count: int


def increment_node(state: CounterState):
    incri = state["count"] + 1
    print(f"count:{incri}")
    return {"count": incri}


memory = MemorySaver()

workflow = StateGraph(CounterState)

workflow.add_node("task", increment_node)

workflow.add_edge(START, "task")
workflow.add_edge("task", END)

app = workflow.compile(checkpointer=memory)


print("Testing Thread 1:")
config_1 = {"configurable": {"thread_id": "thread_1"}}
app.invoke({"count": 0}, config_1)


print("Run 2:")
app.invoke({}, config_1)

print("Run 3:")
app.invoke({}, config_1)

print("Testing Thread 2:")
config_2 = {"configurable": {"thread_id": "thread_2"}}

print("Run 1 (New Thread):")
app.invoke({"count": 0}, config_2)
