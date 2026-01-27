from os import environ
import chromadb
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=environ.get("GROQ_KEY"))

ch_client = chromadb.EphemeralClient()
collection = ch_client.create_collection(name="resume_data")


resume_chunks = [
    "Summary: AI Engineer with 3 years of experience in Python and FastAPI. Focused on building Agentic workflows.",
    "Skills: Backend tech includes FastAPI, Docker, PostgreSQL, and Redis. Frontend skills include Streamlit and React.",
    "Experience: Worked at TechCorp (2022-2024). Optimized database queries reducing latency by 40%. Built a RAG chatbot for internal docs.",
    "Education: B.Tech in Computer Science from Rajasthan (2018-2022). Major project was on Computer Vision.",
]

collection.add(documents=resume_chunks, ids=["chunk1", "chunk2", "chunk3", "chunk4"])


def query_rag(question):
    print(f"Asking question: {question}")

    results = collection.query(query_texts=[question], n_results=1)

    if not results["documents"]:
        return "I don't have enough information to answer that."

    best_chunk = results["documents"][0][0]
    print(f"Retrived Context: '{best_chunk}' ")

    prompt = f"""
    You are a helpful assistant. Answer the user question based ONLY on the context below.
    If the answer is not in the context, say "I don't know."
    
    Context:
    {best_chunk}
    
    Question: {question}
    """

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    return completion.choices[0].message.content


answer1 = query_rag("Does this candidate know Docker?")
print(f"AI Answer: {answer1}")


answer2 = query_rag("What did he do at TechCorp?")
print(f"AI Answer: {answer2}")


answer3 = query_rag("Does he know how to fly a plane?")
print(f"AI Answer: {answer3}")
