import asyncio
from fastapi import FastAPI
from time import time

app = FastAPI()


async def fake_api_call(source: str, delay: int):
    print(f"Start fetching {source}...")
    await asyncio.sleep(delay)
    print(f"Finished {source}!")
    return {"source": source, "status": "ok"}


@app.get("/dashbord")
async def get_dashbord():
    start = time()

    task1 = fake_api_call("Profile", 2)
    task2 = fake_api_call("Orders", 2)
    task3 = fake_api_call("Notifications", 2)

    results = await asyncio.gather(task1, task2, task3)

    total_time = time() - start

    return {"total time": total_time, "data": results}
