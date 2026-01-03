from fastapi import FastAPI


app = FastAPI()


def heavy_computation():
    sum = [i * i for i in range(50000000)]

    return sum


@app.get("/")
def hello():
    return {"message": "Hello"}


@app.get("/heavy")
async def heavy():
    result = heavy_computation()

    return {"result": result}
