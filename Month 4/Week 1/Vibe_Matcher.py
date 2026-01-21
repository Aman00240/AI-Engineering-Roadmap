from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

quotes = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "Life is what happens when you're busy making other plans. - John Lennon",
    "In the middle of every difficulty lies opportunity. - Albert Einstein",
    "Happiness depends upon ourselves. - Aristotle",
    "It does not matter how slowly you go as long as you do not stop. - Confucius",
]


quotes_embeddings = model.encode(quotes)


while True:
    print("\n-------------------------")
    user_mood = input("How are you feeling? ('q' to quit)")

    if user_mood.lower() == "q":
        break

    mood_embedding = model.encode([user_mood])

    score = cosine_similarity(mood_embedding, quotes_embeddings)[0]

    best_match_index = np.argmax(score)
    best_quote = quotes[best_match_index]
    confidence = score[best_match_index]

    print("\nRecommended Quote:")
    print(f'"{best_quote}"')
    print(f"(Confidence: {confidence:.4f})")
