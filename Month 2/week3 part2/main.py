from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

asset_db = []


class AssetCreate(BaseModel):
    name: str
    price: float
    category: str

    @field_validator("name")
    def check_name_empty(cls, v: str) -> str:
        v = v.strip().title()

        if not v:
            raise ValueError("Asset name cannot be empty")

        if len(v) < 2:
            raise ValueError("Asset name must be at least 2 characters")

        if v.isdigit():
            raise ValueError("Asset name cannot be just numbers")

        return v

    @field_validator("price")
    def check_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Asset Price cant be negative")

        return v

    @field_validator("category")
    def check_category(cls, v: str) -> str:
        cat = ["Laptop", "Phone", "Monitor"]

        if v.strip().title() not in cat:
            raise ValueError("Asset category can only be:(Laptop,Phone,Monitor)")

        return v.strip().title()


@app.post("/create-asset")
def create_asset(asset: AssetCreate):
    asset_db.append(
        {"name": asset.name, "price": asset.price, "category": asset.category}
    )

    return {"message": "Asset valid!", "data": asset}


@app.get("/search")
def search(q: str, limit: int = 10):
    if limit >= 100:
        raise HTTPException(status_code=400, detail="Limit too high")

    filter_search = [item for item in asset_db if q.lower() in item["name"].lower()]

    result = filter_search[:limit]

    return {"query": q, "limit_applied": limit, "results": result}


@app.put("/update_asset/{old_name}/{new_name}")
def update(old_name: str, new_name: str):
    for asset in asset_db:
        if asset["name"].lower() == old_name.lower():
            asset["name"] = new_name

            return {"message": "Asset name updated", "new_data": asset}

    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/del_assets/{name_to_delete}")
def remove_asset(name_to_delete: str):
    for asset in asset_db:
        if asset["name"] == name_to_delete:
            asset_db.remove(asset)

            return {"message": "Item deleted", "name": asset}

    raise HTTPException(status_code=404, detail="Item not found")
