from fastapi import FastAPI, HTTPException, Header, Depends
from typing import Annotated
from time import time
import asyncio

app = FastAPI()


def verify_api_key(x_api_key: Annotated[str, Header()]):
    if x_api_key != "super-secret":
        raise HTTPException(status_code=400, detail="Invalid API key")

    return x_api_key


async def get_profile(user_id: int):
    await asyncio.sleep(1)

    return {"name": "Tom", "age": 33}


async def get_posts(user_id: int):
    await asyncio.sleep(2)

    return {"posts": {1: "something", 2: "nothing"}}


async def get_friends(user_id: int):
    await asyncio.sleep(1)

    return {"friends": ["Tomy", "Timmy", "Tony"]}


@app.get("/user/{user_id}/dashbord")
async def get_user_dashbord(
    user_id: int, api_key: Annotated[str, Depends(verify_api_key)]
):
    start = time()
    task1 = get_profile(user_id)
    task2 = get_posts(user_id)
    task3 = get_friends(user_id)

    result = await asyncio.gather(task1, task2, task3)
    total = time() - start

    return {"result": result, "time taken": total}
