from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph


class SecurityState(TypedDict):
    command: str
    status: str


def planner_node(state: SecurityState):
    print(f"\n[Planner] Requesting permission to run: '{state['command']}'")
    return {"status": "pending_approval"}


def execute_node(state: SecurityState):
    print(f"\n Executing: '{state['command']}'")
    return {"status": "executed"}


workflow = StateGraph(SecurityState)

workflow.add_node("planner", planner_node)
workflow.add_node("execute", execute_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "execute")
workflow.add_edge("execute", END)

memory = MemorySaver()

app = workflow.compile(checkpointer=memory, interrupt_before=["execute"])

config: RunnableConfig = {"configurable": {"thread_id": "thread_1"}}

print("Initial Run:")
initial_state: SecurityState | None = {"command": "DROP TABLE users;", "status": "init"}
app.invoke(initial_state, config)

current_state = app.get_state(config)
print(f"\n{current_state}")
print(f"\nGraph is currently paused. Next node to run: {current_state.next}")

user_input = input("\nDo you approve this action? (y/n): ")

if user_input.lower() == "y":
    print("Resuming Graph")
    app.invoke(None, config)
else:
    print("\nAction Aborted by User.")


image_bytes = app.get_graph().draw_mermaid_png()

file_name = "human.png"
with open(file_name, "wb") as f:
    f.write(image_bytes)

print(f"Generated Image {file_name}")
