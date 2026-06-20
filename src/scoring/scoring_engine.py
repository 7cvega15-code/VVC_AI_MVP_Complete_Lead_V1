def score_event(event_data):
    """
    Simple first version of VVC event scoring.
    """

    score = 0

    guest_count = event_data.get("guest_count") or 0
    event_type = event_data.get("event_type", "").lower()

    if guest_count >= 100:
        score += 30

    if event_data.get("wants_prints"):
        score += 30

    if event_type in ["wedding", "corporate", "sweet 16"]:
        score += 25

    return score