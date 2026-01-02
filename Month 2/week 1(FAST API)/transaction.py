from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

USER_WALLET = 1000.0

asset_db = []


class Assets(BaseModel):
    name: str
    price: float
    category: str


@app.post("/buy/{asset_name}")
def buy_asset(asset_name: str):
    global USER_WALLET
    target_asset = None

    for item in asset_db:
        if item["name"] == asset_name:
            target_asset = item

            break

    if not target_asset:
        raise HTTPException(status_code=404, detail="ASSET NOT FOUND")

    if USER_WALLET < target_asset["price"]:
        raise HTTPException(status_code=400, detail="INSUFFICIENT FUNDS")

    USER_WALLET -= target_asset["price"]
    asset_db.remove(target_asset)

    return {"message": "Sold", "remaining_wallet": USER_WALLET}
