from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
def home():
    return {"message": "System Online", "status": "active"}


@app.get("/code/{pin}")
def pin_check(pin: int):
    if pin == 1234:
        return {"access": "GRANTED", "message": "WELCOME BOZO"}
    else:
        return {"access": "DNIED", "message": "RED SPY IN THE BASE"}


@app.get("/user/{user_name}")
def get_username(user_name: str):
    if user_name.isdigit():
        raise HTTPException(
            status_code=400, detail="Usernames cannot be numbers: You are dumb"
        )

    if user_name.strip().lower() == "admin":
        return {"role": "BOSS", "permissions": "LIFE IN CREATIVE MODE"}
    else:
        return {"role": "Level 1 thug", "permissions": "BE MEAT SHIELD"}


@app.get("/add/{a}/{b}")
def add(a: int, b: int):
    return {"result": a + b}
