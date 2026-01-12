import json
from groq import Groq
from pydantic import BaseModel, Field
from app.config import settings
from typing import Literal

client = Groq(api_key=settings.GROQ_API_KEY)


class FraudAnalysis(BaseModel):
    step_1_location_check: str
    step_2_amount_check: str
    step_3_velocity_check: str
    risk_score: int = Field(gt=0, le=100)
    verdict: Literal["SAFE", "BLOCK"]


def analyze_transaction(tx_data: str):
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You are a fraud analyst. analyze the transaction and return JSON 
                based on these Exact keys:
                - step_1_location_check: Analyze Location consistency
                - step_2_amount_check: Analyze if amount fits the user history
                - step_3_velocity_check: Analyze time between transactions
                - risk_score: integer 1-100
                - verdict: "SAFE" or "BLOCK"
                
                only give a verdict after going through these steps 
                """,
            },
            {"role": "user", "content": tx_data},
        ],
        model=settings.MODEL_NAME,
        temperature=0,
        response_format={"type": "json_object"},
    )

    data = json.loads(completion.choices[0].message.content)  # type:ignore
    print(data)
    analysis = FraudAnalysis(**data)
    return analysis


transaction = """
User: Rahul (Home: Delhi). 
Transaction: $50 at 'Lagos Coffee Shop', Nigeria. 
Time: 10 mins after previous tx in Delhi.
"""

result = analyze_transaction(transaction)
print(f"Reasoning:{result.step_1_location_check}")
print(f"Verdict:{result.verdict}")
