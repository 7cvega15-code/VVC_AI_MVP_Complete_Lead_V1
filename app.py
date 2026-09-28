from src.workflows.inquiry_pipeline import process_inquiry


sample_inquiry = """
We are planning an outdoor school dance in Torrance for about 180 students. 
The event will be in the evening and we would like printed photos."""

result = process_inquiry(sample_inquiry)
event_data = result["event_data"]
missing_info = result["missing_info"]
confidence = result["confidence"]
followup = result["followup_questions"]
lead_status = result["lead_status"]
workflow = result["workflow"]
action = result["action"]
score = result["score"]
recommendation = result["package_recommendation"]
experience = result["experience_recommendation"]
operations = result["operational_recommendations"]
final_addons = result["addons"]
proposal = result["proposal"]
client_response = result["client_response"]

recommended = recommendation["recommended"]
alternative = recommendation["alternative"]
entry = recommendation["entry"]


print("\nMISSING INFORMATION:")

if missing_info:
    for item in missing_info:
        print(f"- {item}")
else:
    print("No required information missing.")

print("\nCONFIDENCE:")
print(confidence["level"])
print(f"{confidence['score']}%")

print("\nEXPERIENCE RECOMMENDATION:")

print(
    f"Entry Experience: {experience['entry_experience']}"
)

print(
    f"Recommended Experience: {experience['recommended_experience']}"
)

print(
    "Premium Experience(s):"
)

for premium in experience["premium_experiences"]:
    print(f"- {premium}")

print("\nMATRIX ADD-ONS:")

for addon in experience["recommended_addons"]:
    print(f"- {addon}")

print("\nRECOMMENDED PACKAGE:")
print(f"{recommended['product_family']} {recommended['tier_name']}")

print("\nPACKAGE DETAILS:")
print(f"Base Price: ${recommended['base_price']}")
print(f"Included Hours: {recommended['included_hours']}")
print(f"Additional Hour Rate: ${recommended['additional_hour_rate']}/hr")

print("\nOTHER OPTIONS:")

print(
    f"Signature: ${alternative['base_price']}"
)

print(
    f"Classic: ${entry['base_price']}"
)

print("\nOPERATIONAL RECOMMENDATIONS:")

for item in operations:
    print(f"- {item}")

print("\nFINAL ADD-ONS:")

for addon in final_addons:
    print(f"- {addon}")

print("\n")
print(proposal)

print("\nFOLLOW-UP QUESTIONS:")
print(followup)

print("\nLEAD STATUS:")
print(lead_status["status"])
print(lead_status["message"])

print("\nWORKFLOW:")
print(workflow)

print("\nACTION:")
print(action)

print("\nCLIENT RESPONSE:")
print(client_response)