from pydantic import BaseModel, Field


class User(BaseModel):
    user_name: str = Field(min_length=3, max_length=15)
    age: int = Field(gt=18, max_digits=15)
    referral_code: str | None = Field(default=None, lt=100)


user1 = User(user_name="jo", age=17)

print(user1.user_name)
