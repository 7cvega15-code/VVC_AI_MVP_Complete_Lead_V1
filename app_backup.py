import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Example customer inquiry
customer_message = """
Hi! I'm looking for a photobooth for my wedding on September 14 in Malibu.
We are expecting around 150 guests and are interested in fun modern experiences.
Can you send pricing and package recommendations?
"""

# SYSTEM PROMPT
system_prompt = """
You are an AI lead assistant for VVC Photobooths.

Your responsibilities:
- analyze customer inquiries
- extract event information
- recommend appropriate packages
- identify upsell opportunities
- identify missing information

Rules:
- never finalize pricing
- never confirm bookings
- always require human review

Return ONLY valid JSON.

JSON format:
{
  "event_type": "",
  "event_date": "",
  "location": "",
  "guest_count": "",
  "recommended_package": "",
  "upsell_opportunities": [],
  "missing_information": [],
  "lead_value": "",
  "draft_response": ""
}
"""

# AI CALL
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": customer_message
        }
    ],
    temperature=0.3
)
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Example customer inquiry
customer_message = """
Hi! I'm looking for a photobooth for my wedding on September 14 in Malibu.
We are expecting around 150 guests and are interested in fun modern experiences.
Can you send pricing and package recommendations?
"""

# SYSTEM PROMPT
system_prompt = """
You are an AI lead assistant for VVC Photobooths.

Your responsibilities:
- analyze customer inquiries
- extract event information
- recommend appropriate packages
- identify upsell opportunities
- identify missing information

Rules:
- never finalize pricing
- never confirm bookings
- always require human review

Return ONLY valid JSON.

JSON format:
{
  "event_type": "",
  "event_date": "",
  "location": "",
  "guest_count": "",
  "recommended_package": "",
  "upsell_opportunities": [],
  "missing_information": [],
  "lead_value": "",
  "draft_response": ""
}
"""

# AI CALL
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": customer_message
        }
    ],
    temperature=0.3
)

# Extract response
result = response.choices[0].message.content

# Convert JSON string to Python dictionary
parsed = json.loads(result)

# Pretty print results
print("\n--- AI LEAD ANALYSIS ---\n")

print("EVENT TYPE:", parsed["event_type"])
print("EVENT DATE:", parsed["event_date"])
print("LOCATION:", parsed["location"])
print("GUEST COUNT:", parsed["guest_count"])
print("PACKAGE:", parsed["recommended_package"])

print("\nUPSELL OPPORTUNITIES:")
for item in parsed["upsell_opportunities"]:
    print("-", item)

print("\nMISSING INFORMATION:")
for item in parsed["missing_information"]:
    print("-", item)

print("\nLEAD VALUE:", parsed["lead_value"])

print("\n--- DRAFT RESPONSE ---\n")
print(parsed["draft_response"])# Extract response
result = response.choices[0].message.content

# Convert JSON string to Python dictionary
parsed = json.loads(result)

# Pretty print results
print("\n--- AI LEAD ANALYSIS ---\n")

print("EVENT TYPE:", parsed["event_type"])
print("EVENT DATE:", parsed["event_date"])
print("LOCATION:", parsed["location"])
print("GUEST COUNT:", parsed["guest_count"])
print("PACKAGE:", parsed["recommended_package"])

print("\nUPSELL OPPORTUNITIES:")
for item in parsed["upsell_opportunities"]:
    print("-", item)

print("\nMISSING INFORMATION:")
for item in parsed["missing_information"]:
    print("-", item)

print("\nLEAD VALUE:", parsed["lead_value"])

print("\n--- DRAFT RESPONSE ---\n")
print(parsed["draft_response"])