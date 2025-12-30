from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"status": "Orbiting", "altitude": "400km"}


@app.get("/diagnostics")
def diagnostics():
    return {"fuel": "98%", "temperature": "Nominal", "batteries": "Charging"}


@app.get("/id")
def get_id():
    return {"name": "Voyager-X", "year": 2025}
