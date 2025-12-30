from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


asset_db = []


class AssetCreate(BaseModel):
    name: str


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


@app.delete("/del_assets/{name_to_delete}")
def remove_asset(name_to_delete: str):
    if name_to_delete not in asset_db:
        raise HTTPException(status_code=404, detail="Item not found")

    asset_db.remove(name_to_delete)

    return {"message": "Item deleted", "name": {name_to_delete}}
