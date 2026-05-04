import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from pydantic import SecretStr

load_dotenv()

llm = ChatGroq(
    api_key=SecretStr(os.environ.get("groq_key") or ""),
    model="llama-3.3-70b-versatile",
    temperature=0,
)


@tool
def calculate_string_length(text: str) -> int:
    """Calculates the length of a given text string.
    Use this when you need to know how many characters are in a word or sentence."""
    return len(text)


tools = [calculate_string_length]


llm_with_tools = llm.bind_tools(tools)

print("Asking the LLM to use the tool...")

response = llm_with_tools.invoke(
    [
        HumanMessage(
            content="How many characters are in the word 'Supercalifragilisticexpialidocious'?"
        )
    ]
)

print("\nRaw Response Object:")
print(response)

print("\nExtracted Tool Calls:")
print(response.tool_calls)

tool_call = response.tool_calls[0]
tool_args = tool_call["args"]
tool_id = tool_call["id"]

print(f"Executing tools with args: {tool_args} ")

tool_result = calculate_string_length.invoke(tool_args)
print(f"Tool Result: {tool_result}")


tool_message = ToolMessage(content=str(tool_result), tool_call_id=tool_id)

print("\nSending Result back to LLM...")

conversation_history = [
    HumanMessage(
        content="How many characters are in the word 'Supercalifragilisticexpialidocious'?"
    ),
    response,
    tool_message,
]

final_response = llm_with_tools.invoke(conversation_history)
print(final_response)
