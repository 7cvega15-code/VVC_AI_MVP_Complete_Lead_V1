import json


def load_experience_matrix():
    with open("configs/event_experience_matrix.json", "r") as file:
        return json.load(file)


def recommend_experience(event_data):

    matrix = load_experience_matrix()

    event_type = event_data.get("event_type", "").lower()

    if "corporate" in event_type:
        return matrix["corporate"]

    if "wedding" in event_type:
        return matrix["wedding"]

    if "sweet 16" in event_type:
        return matrix["sweet 16"]

    if "quince" in event_type:
        return matrix["quinceañera"]

    if "graduation" in event_type:
        return matrix["graduation"]

    if "school" in event_type:
        return matrix["school event"]

    if "fundraiser" in event_type:
        return matrix["fundraiser"]

    if "birthday" in event_type:
        return matrix["birthday"]

    if "holiday" in event_type:
        return matrix["holiday party"]

    return matrix["special occasion"]