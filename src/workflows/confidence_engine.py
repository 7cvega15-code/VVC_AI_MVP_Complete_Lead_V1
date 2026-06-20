def calculate_confidence(event_data, missing_info):

    confidence = 100

    confidence -= len(missing_info) * 10

    if not event_data.get("guest_count"):
        confidence -= 10

    if not event_data.get("location"):
        confidence -= 10

    if confidence >= 80:
        level = "HIGH"

    elif confidence >= 50:
        level = "MEDIUM"

    else:
        level = "LOW"

    return {
        "score": confidence,
        "level": level
    }