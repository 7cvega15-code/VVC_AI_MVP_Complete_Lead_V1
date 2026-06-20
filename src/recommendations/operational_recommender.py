import json


def load_operational_rules():
    with open("configs/operational_rules.json", "r") as file:
        return json.load(file)


def recommend_operations(event_data):

    rules = load_operational_rules()

    recommendations = []

    event_type = event_data.get("event_type", "").lower()

    guest_count = event_data.get("guest_count") or 0

    if event_data.get("outdoor_event"):
        recommendations.extend(
            rules["outdoor"]
    )

    if event_data.get("night_event"):
        recommendations.extend(
            rules["night_event"]
    )
   
    if guest_count >= 200:
        recommendations.extend(
            rules["guest_count_200_plus"]
    )
    elif guest_count >= 150:
        recommendations.extend(
            rules["guest_count_150_plus"]
    )

    if "wedding" in event_type:
        recommendations.extend(
            rules["wedding"]
        )

    if "corporate" in event_type:
        recommendations.extend(
            rules["corporate"]
        )

    if "school" in event_type:
        recommendations.extend(
            rules["school event"]
        )

    return list(dict.fromkeys(recommendations))