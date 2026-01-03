from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Annotated


app = FastAPI()


def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "secret-password":
        raise HTTPException(status_code=400, detail="invalid Token Header")

    return x_token


@app.get("/secure-data")
def get_secure_data(token: Annotated[str, Depends(verify_token)]):
    return {"message": "you are authorized", "Token_used": token}
