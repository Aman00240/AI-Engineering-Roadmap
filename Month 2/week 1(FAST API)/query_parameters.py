from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
def home():
    return {"message": "System Online", "status": "active"}


fake_asset_db = [
    "Laptop Dell",
    "Macbook Air",
    "iPhone 13",
    "Monitor Samsung",
    "Keyboard Logitech",
    "Mouse Razer",
    "Projector Epson",
    "Printer HP",
    "Server Rack",
    "Switch Cisco",
    "Router Netgear",
    "Webcam Logitech",
]


@app.get("/search")
def search(q: str, limit: int = 10):
    if limit >= 100:
        raise HTTPException(status_code=400, detail="Limit too high")

    filter_search = [item for item in fake_asset_db if q.lower() in item.lower()]

    result = filter_search[:limit]

    return {"query": q, "limit_applied": limit, "results": result}
