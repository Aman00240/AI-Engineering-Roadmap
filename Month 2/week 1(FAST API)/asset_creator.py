from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class AssetCreate(BaseModel):
    name: str


asset_db = []


@app.post("/create-asset")
def create_asset(asset: AssetCreate):
    asset_db.append(asset.name)
    return {"message": "Asset Created", "data": asset}


@app.get("/search")
def search(q: str, limit: int = 10):
    if limit >= 100:
        raise HTTPException(status_code=400, detail="Limit too high")

    filter_search = [item for item in asset_db if q.lower() in item.lower()]

    result = filter_search[:limit]

    return {"query": q, "limit_applied": limit, "results": result}
