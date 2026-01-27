import requests
import chromadb
from os import environ
from dotenv import load_dotenv
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from bs4 import BeautifulSoup

load_dotenv()

groq_client = Groq(api_key=environ.get("GROQ_KEY"))
ch_client = chromadb.EphemeralClient()

collection = ch_client.create_collection(name="wiki_data")

print("Loading Re-ranker model...")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def get_wikipedia_text(topic):
    formatted_topic = topic.strip().replace(" ", "_").title()

    url = f"https://en.wikipedia.org/wiki/{formatted_topic}"
    print(f"fetching: {url} ..")

    headers = {"User-Agent": "MyWikiScraper/1.0 (contact: yourname@example.com)"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: Couldnt fetch page, {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")
    text = "\n\n".join([p.get_text() for p in paragraphs])

    return text


topic = input("Search Wikipedia for: ")
raw_text = get_wikipedia_text(topic)


if raw_text:
    print(f"Found {len(raw_text)} characters of text")

    print("Chunking..")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(raw_text)

    print(f"Saving {len(chunks)} chunks to ChromDB")

    collection.add(documents=chunks, ids=[f"id_{i}" for i in range(len(chunks))])

    while True:
        print("\n" + "=" * 40)
        question = input("Ask a question ('q' to quit): ")
        if question.lower() == "q":
            break

        results = collection.query(query_texts=[question], n_results=15)

        retrieved_docs_list = results.get("documents", [])

        if not retrieved_docs_list or not retrieved_docs_list[0]:
            print("No relevant info found.")
            continue

        retrieved_docs = retrieved_docs_list[0]

        pairs = [[question, doc] for doc in retrieved_docs]

        scores = cross_encoder.predict(pairs)
        scored_docs = zip(retrieved_docs, scores)

        sorted_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)

        top_5_docs = [doc for doc, _ in sorted_docs[:5]]

        context_text = "\n\n--\n\n".join(top_5_docs)

        prompt = f"""
        Answer the user based ONLY on the context
        if you dont know the answer say 'I dont know'
        
        context:
        {context_text}
        
        Question: {question}
        """

        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.0,
        )

        print(f"\nAnswer: {completion.choices[0].message.content}")
