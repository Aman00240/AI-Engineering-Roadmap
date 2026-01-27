import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_KEY"))


retrived_chunk = """
● Languages: Python (Advanced), SQL 
● Backend: FastAPI, Docker, PostgreSQL, SQLAlchemy , REST APIs 
● Data & ML: Pandas, Numpy, Matplotlib, Pytorch, Keras, Scikit-Learn 
"""

user_query = "what tech knowledge does he have about backend?"

prompt = f"""
You are a helpful assistant .
Answer the question delimited by triple backticks (```) 
ONLY using the context below ,delimited by triple backticks (```)
if answer is not in the context say "I dont know"

Context:
```{retrived_chunk}```

User Question: ```{user_query}```
"""

print("Sending Prompt to AI...")
print("-" * 20)
print(prompt)
print("-" * 20)

completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,
)

answer = completion.choices[0].message.content
print(f"\nAI Answer: {answer}")
