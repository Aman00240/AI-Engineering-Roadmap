import json
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


system_msg = """"You an API that converts messy data into a JSON (key:value) pair,keys will be:
                Keys: street, city, state, zip_code.
                return null if a key value is missing in the text
                """


def parse_address(raw_address: str):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": raw_address},
            ],
            model=settings.MODEL_NAME,
            temperature=0,
            response_format={"type": "json_object"},
        )
        json_string = completion.choices[0].message.content

        if not json_string:
            print("Error: Received empty response from Groq")
            return None
        return json.loads(json_string)

    except Exception as e:
        print(f"Error communicating with groq {e}")
        return None


input1 = "123 main st, apt 4b, nyc, 10001 call me when u arrive"
print(f"Input: {input1}")

print(f"output {parse_address(input1)}")

data = parse_address(input1)

if data:
    print(f"city: {data.get('city', 'Unknown')}")
else:
    print("Failed to extract address data.")

input2 = "paris france, near the eiffel tower"
print(f"Input: {input2}")
print(f"output {parse_address(input2)}")

data = parse_address(input2)
if data:
    print(f"Zip code: {data.get('zip_code')}")
else:
    print("Failed to extract address data.")
