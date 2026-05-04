import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import SecretStr

load_dotenv()

llm = ChatGroq(
    api_key=SecretStr(os.environ.get("groq_key") or ""),
    model="llama-3.3-70b-versatile",
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert technical writer. Explain the concept of {concept} in exactly three sentences,
                making it easy for a beginner to understand.""",
        ),
        ("user", "please explain it now"),
    ]
)

print(prompt)

parser = StrOutputParser()

chain = prompt | llm | parser

print("Runnig the LCEL Chian..")
result = chain.invoke({"concept": "Neural Networks"})

print("\nFinal Output:")
print(result)
