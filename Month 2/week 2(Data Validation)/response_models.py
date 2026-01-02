from pydantic import BaseModel, Field
from fastapi import FastAPI


app = FastAPI()


class UserIn(BaseModel):
    name: str = Field(min_length=2, description="name must be longer then 2 characters")
    email: str
    password: str = Field(
        min_length=8, description="passworld must be longer than 8 digits"
    )


class UserOut(BaseModel):
    name: str = Field(min_length=2, description="name must be longer then 2 characters")
    email: str


@app.post("/register_user", response_model=UserOut)
def add_user(user: UserIn):
    return user
