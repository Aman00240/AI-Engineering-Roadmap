import chromadb

client=chromadb.PersistentClient(path="./chroma_db")

try:
    client.delete_collection(name="movies")
except:
    pass

collection=client.create_collection(name="movies")

movies = [
    {
        "id": "m1",
        "title": "The Matrix",
        "plot": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "genre": "Sci-Fi"
    },
    {
        "id": "m2",
        "title": "Titanic",
        "plot": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
        "genre": "Romance"
    },
    {
        "id": "m3",
        "title": "The Lion King",
        "plot": "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.",
        "genre": "Animation"
    },
    {
        "id": "m4",
        "title": "Inception",
        "plot": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "genre": "Sci-Fi"
    },
    {
        "id": "m5",
        "title": "Toy Story",
        "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
        "genre": "Animation"
    }
]


print("Loding Movies..")
collection.add(
    documents=[m["plot"] for m in movies],
    metadatas=[{"title": m["title"],"genre":m["genre"]} for m in movies],
    ids=[m["id"] for m in movies]
)


while True:
    print("------------")
    query=input("Describe a movie('q' for quitting)")
    
    if query.lower()=='q':
        break
    
    results=collection.query(
        query_texts=[query],
        n_results=1
    )
    
    print(results)
    if results is None:
        print("NO result found")
        break
    
    title=results['metadatas'][0][0]['title']
    genre=results['metadatas'][0][0]['genre']
    plot=results["documents"][0][0]
    distance=results["distances"][0][0]
    
    print(f"\nI think you mean: '{title}' ({genre})")
    print(f"Plot Match: \"{plot}\"")
    print(f"Confidence Score: {distance:.4f}")
    