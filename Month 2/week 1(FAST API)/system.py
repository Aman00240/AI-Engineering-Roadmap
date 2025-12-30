from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def home():
    return {"message": "System Online", "status": "active"}


@app.get("/data")
def get_data():
    return {"user_id": 101, "role": "AI Engineer"}
