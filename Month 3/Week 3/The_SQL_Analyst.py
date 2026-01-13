import sqlite3
import json
from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

DB = "my_business.db"


def setup_db():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT,monthly_spend REAL)"
        )

        cursor.execute("DELETE FROM users")

        cursor.execute(
            "INSERT INTO users (name, email, monthly_spend) VALUES ('Alice', 'alice@company.com', 50.0)"
        )
        cursor.execute(
            "INSERT INTO users (name, email, monthly_spend) VALUES ('Bob', 'bob@company.com', 120.5)"
        )
        cursor.execute(
            "INSERT INTO users (name, email, monthly_spend) VALUES ('Charlie', 'charlie@company.com', 5.0)"
        )

        print("DataBase connection completed")


def run_sql_query(query: str):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        try:
            print(f" Executing: {query}")

            cursor.execute(query)
            result = cursor.fetchall()
            return str(result)

        except Exception as e:
            print(f"Error: {e}")


tools = [
    {
        "type": "function",
        "function": {
            "name": "run_sql_query",
            "description": "Run a SQLite query on the users table. Schema: id (int), name (text), email (text), monthly_spend (real).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The SQL query to run"}
                },
                "required": ["query"],
            },
        },
    }
]


def chat_with_data(user_query: str):
    setup_db()
    messages = [{"role": "user", "content": user_query}]

    response = client.chat.completions.create(
        messages=messages,  # type:ignore
        model=settings.MODEL_NAME,
        tools=tools,  # type:ignore
        tool_choice="auto",
        temperature=0,
    )

    response_msg = response.choices[0].message
    print(f"\nResponse_MSG:{response_msg} \n")
    tool_calls = response_msg.tool_calls
    print(f"\nTool CAlls:{tool_calls}\n")

    if tool_calls:
        for tool_call in tool_calls:
            sql_query = json.loads(tool_call.function.arguments)["query"]

            db_result = run_sql_query(sql_query)
            print(f"DB Result: {db_result}")

            messages.append(response_msg)  # type:ignore
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": db_result,  # type:ignore
                }
            )
            print(f"\n MESSAGE: {messages}\n")
            final_resp = client.chat.completions.create(
                messages=messages,  # type:ignore
                model=settings.MODEL_NAME,
                temperature=0,
            )
            print(f"Answer: {final_resp.choices[0].message.content}")

    else:
        print("AI:I didnt need the database for that")


print("--- Test 1 ---")
chat_with_data("How many users do we have?")


print("\n--- Test 2 ---")
chat_with_data("Who spends the most money and what is their email?")
