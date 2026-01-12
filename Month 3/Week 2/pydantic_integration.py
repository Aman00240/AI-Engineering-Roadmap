from groq import Groq
from pydantic import BaseModel, Field, ValidationError
from app.config import settings
import json


class UserProfile(BaseModel):
    full_name: str = Field(min_length=2)
    age: int
    email: str | None
    job_title: str
    confidence_score: float = Field(gt=0, le=1)


client = Groq(api_key=settings.GROQ_API_KEY)


def extract_user_profile(bio: str):
    print("Extracting Info\n")

    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """Extract User Profile as JSON.
                                Keys:full_name,age(number),email,job_title,confidence_score(0.0-1.0)
                                if a value is missing , use null""",
                },
                {"role": "user", "content": bio},
            ],
            model=settings.MODEL_NAME,
            temperature=0,
            response_format={"type": "json_object"},
        )
        data_dict = json.loads(completion.choices[0].message.content)  # type: ignore
        print(data_dict)
        user = UserProfile(**data_dict)

        print("\nValidation Success")
        print(f"Name: {user.full_name}")
        print(f"Age: {user.age} (Type: {type(user.age)})")
        return user

    except ValidationError as e:
        print("Validation Error AI returned bad data")
        return e.json()
    except Exception as e:
        print(f"System Error {e}")


bio1 = "Hi, I'm Sarah Connor, 29 years old. I work as a Chef. No email."
extract_user_profile(bio1)


bio2 = "I am Mike, forty years old. email is mike@test.com"
extract_user_profile(bio2)
