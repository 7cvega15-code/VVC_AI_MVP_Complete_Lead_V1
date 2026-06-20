from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _parse_ai_json(raw_text: str):
    """Parse JSON produced by the LLM, stripping Markdown fences and returning
    a Python object. Raises ValueError with a helpful message if parsing fails.
    """
    cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        # Include a short preview of the raw response to aid debugging
        preview = repr(cleaned_text)[:500]
        raise ValueError(f"Failed to parse JSON from LLM response: {e}. Response preview: {preview}") from e


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

    # Parse AI output safely; raise ValueError if malformed
    return _parse_ai_json(raw_text)