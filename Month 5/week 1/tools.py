import json
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.json_schema import models_json_schema


class CalculatorInput(BaseModel):
    a: int = Field(description="The First number")
    b: int = Field(description="The Second number")
    operation: str = Field(
        description="The operation to perform: 'add', 'subtract', 'multiply', 'divide'"
    )


class WeatherInput(BaseModel):
    city: str = Field(description="The name of the city, e.g., San Francisco")
    unit: str = Field(
        default="celsius",
        description="The temperature unit, either 'celsius' or 'fahrenheit'",
    )


class TimeInput(BaseModel):
    timezone: str = Field(description="Time Zone")


class ServerLogsInput(BaseModel):
    date: str = Field(
        description="The date of the logs to read. It must be strictly in YYYY-MM-DD format."
    )


def calculator(a: int, b: int, operation: str):
    if operation == "add":
        raise ValueError("CRITICAL CORE FAULT: CPU math module overheated.")
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero"
        return a / b
    else:
        return "Error: Unknown operation"


def get_weather(city, unit="celsius"):
    return f"The weather in {city} is 25{unit}"


def get_current_time(timezone):
    return f"The current time in {timezone} is 3:00 AM"


def read_server_logs(date: str):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return f"Logs for {date}: System nomianl"
    except ValueError:
        return "Error: Invalid date format. You must use strictly YYYY-MM-DD."


calculator_tool_definition = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "perform basic arithmetic operations (add, subtract, multiply, divide)",
        "parameters": CalculatorInput.model_json_schema(),
    },
}

weather_tool_defination = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Tell weather of a city",
        "parameters": WeatherInput.model_json_schema(),
    },
}

time_tool_defination = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "tell time according to timezone",
        "parameters": TimeInput.model_json_schema(),
    },
}

server_logs_tool_definition = {
    "type": "function",
    "function": {
        "name": "read_server_logs",
        "description": "Read the system server logs for a specific date.",
        "parameters": ServerLogsInput.model_json_schema(),
    },
}

print(json.dumps(calculator_tool_definition, indent=2))
print(json.dumps(weather_tool_defination, indent=2))
print(json.dumps(time_tool_defination, indent=2))
print(json.dumps(server_logs_tool_definition, indent=2))
