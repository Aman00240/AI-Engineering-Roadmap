from pydantic import BaseModel, field_validator, Field


class Employee(BaseModel):
    name: str = Field(min_length=2)
    email: str = Field(min_length=2)
    department: str = Field(min_length=2)

    @field_validator("name")
    def check_user(cls, n):
        name = n.strip().title()

        if name.isalnum():
            return name
        else:
            raise ValueError("Name cant contain special character")

    @field_validator("email")
    def check_email(cls, e):
        end = "@internal.com"

        if not e.endswith(end):
            raise ValueError("Wrong email")
        else:
            return e

    @field_validator("department")
    def check_department(cls, d):
        valid_dept = ["IT", "HR", "SALES"]

        dept = d.strip().upper()

        if dept in valid_dept:
            return dept

        else:
            raise ValueError("invalid department")
