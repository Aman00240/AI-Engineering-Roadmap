from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    input_text: str
    processed_text: str


def format_input_node(state: AgentState):
    print("Executing Node: format_input_node")
    raw_text = state["input_text"]
    return {"processed_text": raw_text.strip().lower()}


def print_output_node(state: AgentState):
    print("Executing Node: print_output_node")
    print(f"Final Output: {state['processed_text']}")
    return {}


workflow = StateGraph(AgentState)

workflow.add_node("formatter", format_input_node)
workflow.add_node("printer", print_output_node)


workflow.add_edge(START, "formatter")
workflow.add_edge("formatter", "printer")
workflow.add_edge("printer", END)

app = workflow.compile()

initial_state = {"input_text": "   HELLO LANGGRAPH WORLD   ", "processed_text": ""}
print("Starting Graph Execution...\n")

final_state = app.invoke(initial_state)  # type: ignore
print("\nExecution Complete.")
