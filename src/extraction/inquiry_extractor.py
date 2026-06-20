from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_event_info(inquiry_text):
    prompt = f"""
Extract the event information from this inquiry.

Return ONLY valid JSON with these fields:
event_type
guest_count
wants_prints
location
event_date
start_time
duration
venue
outdoor_event
night_event
needs_power

Inquiry:
{inquiry_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    raw_text = response.choices[0].message.content

    print("RAW AI RESPONSE:")
    print(repr(raw_text))

    cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()

    return json.loads(cleaned_text)