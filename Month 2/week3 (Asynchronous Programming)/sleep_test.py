import time
import asyncio


def sync_task():
    print("Starting Sync task")
    time.sleep(1)
    print("Ending Sync task")


def run_sync():
    start = time.time()
    sync_task()
    sync_task()
    sync_task()

    print(f"Sync total time:{time.time() - start:.2f} seconds\n")


async def async_task():
    print("Starting Async task")
    await asyncio.sleep(1)
    print("Ending Async task")


async def run_async():
    start = time.time()

    await asyncio.gather(async_task(), async_task(), async_task())
    print(f"Async total time:{time.time() - start:.2f} seconds\n")


run_sync()

asyncio.run(run_async())
