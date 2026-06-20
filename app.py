from src.extraction.inquiry_extractor import extract_event_info
from src.scoring.scoring_engine import score_event
from src.recommendations.package_recommender import recommend_package
from src.recommendations.addon_recommender import recommend_addons
from src.workflows.proposal_builder import build_proposal
from src.workflows.missing_info_checker import check_missing_info
from src.workflows.followup_generator import generate_followup_questions
from src.workflows.lead_status import determine_lead_status
from src.workflows.workflow_router import route_workflow
from src.workflows.workflow_executor import execute_workflow
from src.workflows.response_generator_v2 import generate_client_response
from src.workflows.confidence_engine import calculate_confidence
from src.recommendations.experience_recommender import recommend_experience
from src.recommendations.operational_recommender import recommend_operations


sample_inquiry = """
We are planning an outdoor school dance in Torrance for about 180 students. 
The event will be in the evening and we would like printed photos."""

event_data = extract_event_info(sample_inquiry)
missing_info = check_missing_info(event_data)
confidence = calculate_confidence(
    event_data,
    missing_info
)
followup = generate_followup_questions(missing_info)
lead_status = determine_lead_status(missing_info)
workflow = route_workflow(lead_status)
action = execute_workflow(workflow)
score = score_event(event_data)

recommendation = recommend_package(event_data, score)
experience = recommend_experience(event_data)
operations = recommend_operations(event_data)
addons = recommend_addons(event_data)

matrix_addons = experience["recommended_addons"]

final_addons = []

for addon in matrix_addons + addons:
    if addon not in final_addons:
        final_addons.append(addon)


proposal = build_proposal(
    event_data,
    experience,
    recommendation,
    final_addons
)

client_response = generate_client_response(
    event_data,
    recommendation,
    final_addons,
    missing_info,
    lead_status,
    action
)

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

print("\nRECOMMENDED ADD-ONS:")

for addon in addons:
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