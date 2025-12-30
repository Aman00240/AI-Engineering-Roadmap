from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def greet():
    return "Hello World"


@app.get("/products")
def get_all_products():
    return "all products"
