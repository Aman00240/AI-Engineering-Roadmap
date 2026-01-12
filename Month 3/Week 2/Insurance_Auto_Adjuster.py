import json
from groq import Groq
from pydantic import BaseModel
from app.config import settings
from typing import Literal


client = Groq(api_key=settings.GROQ_API_KEY)


class ClaimVerdict(BaseModel):
    claimant_name: str | None
    policy_number: int | None

    incident_description: str

    logic_step_1_dates: str
    logic_step_2_details: str
    verdict: Literal["APPROVE", "FLAG_FRAUD", "MISSING_INFO"]


def analyze_claim(text: str):
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You are an insurence Fraud analyst,
                analyze the emails and return output in JSON format,
                Based on these exact keys:
                claimant_name: name of the client reutrn none if doenst exist
                policy_number:return None if policy number is not present
                policy_start_date:policy activation date
                incident_description:summary of incident in 5 words
                incident_date:date of the incident
                verdict: Literal["APPROVE", "FLAG_FRAUD", "MISSING_INFO"].
                before giving a verdict you must go through all these steps:
                FILL 'logic_step_1_dates': explicitly write "Comparing Incident Date [Date] vs Policy Start [Date]".
                FILL 'logic_step_2_details': Check for suspicious keywords or missing info.
                 DETERMINE 'verdict':
                    - If incident_date < policy_start_date -> FLAG_FRAUD
                    - If missing policy number -> MISSING_INFO
                    - Otherwise -> APPROVE
                """,
            },
            {"role": "user", "content": text},
        ],
        model=settings.MODEL_NAME,
        temperature=0,
        response_format={"type": "json_object"},
    )

    data = json.loads(completion.choices[0].message.content)  # type:ignore
    print(data)
    analysis = ClaimVerdict(**data)
    return analysis


text = "Policy Start: 2024-01-01, Subject: Crash. Date: Jan 2, 2024. Body: I crashed on Dec 31st. bad luck!"

result = analyze_claim(text)
print(f"Logic:{result.logic_step_1_dates}")
print(f"Verdict:{result.verdict}\n")


text = "Policy Start: 2023-05-01, Subject: Help. Date: Jan 2, 2024. Body: Hit a deer yesterday."
result = analyze_claim(text)
print(f"\nLogic:{result.logic_step_1_dates}")
print(f"Verdict:{result.verdict}\n")

text = """
Policy Start: 2024-01-01. 
Email from John Doe: "I crashed my car on Dec 31st 2023, bad luck!"
"""
result = analyze_claim(text)
print(f"\nLogic:{result.logic_step_1_dates}")
print(f"Verdict:{result.verdict}")

print(f"Logic: {result.logic_step_1_dates}")
print(f"Verdict: {result.verdict}\n")
