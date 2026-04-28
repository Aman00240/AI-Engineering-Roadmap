from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class LabState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    steps_taken: int


def input_logger(state: LabState):
    print("Executing: input_logger")
    return {"messages": ["Logged: User is starting the process"], "steps_taken": 1}


def process_update(state: LabState):
    print("Executing: process_update")

    history_length = len(state["messages"])
    print(f"{history_length} messages in history.")

    new_step_count = state["steps_taken"] + 1

    return {
        "messages": ["Update: Step 2 is now complete."],
        "steps_taken": new_step_count,
    }


workflow = StateGraph(LabState)

workflow.add_node("input_logger", input_logger)
workflow.add_node("process_update", process_update)


workflow.add_edge(START, "input_logger")
workflow.add_edge("input_logger", "process_update")
workflow.add_edge("process_update", END)

app = workflow.compile()


initial_input = {"messages": [], "user_id": "abc23", "steps_taken": 0}

print("Program Starting...\n")

final_output = app.invoke(initial_input)  # type: ignore

print("\nFinal State Summary..")
print(f"User ID: {final_output['user_id']}")
print(f"Total Steps: {final_output['steps_taken']}")
print("Full Message Log:")
for msg in final_output["messages"]:
    print(f" - {msg}")
