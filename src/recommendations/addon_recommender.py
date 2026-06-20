import json


def load_addons():
    with open("configs/addons.json", "r") as file:
        return json.load(file)


def recommend_addons(event_data):
    addons = load_addons()

    event_type = event_data.get("event_type", "").lower()

    return addons["addons"].get(event_type, [])