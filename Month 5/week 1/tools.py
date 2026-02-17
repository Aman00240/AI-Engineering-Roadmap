from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    a: int = Field(description="The First Number:")
    b: int = Field(description="The Second Number:")

    operation: str = Field(
        description="The operation to perform: 'add', 'subtract', 'multiply', 'divide'"
    )


def calculator(a: int, b: int, operation: str) -> int | str:
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        return "Unknown Operation"


calculator_tool_defination = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform basic arithematic operations (add, subtract, multiply, divide)",
        "parameters": CalculatorInput.model_json_schema(),
    },
}
