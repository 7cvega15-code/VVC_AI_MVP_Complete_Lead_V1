def check_missing_info(event_data):

    missing = []

    if not event_data.get("event_type"):
        missing.append("Event Type")

    if not event_data.get("guest_count"):
        missing.append("Guest Count")

    if not event_data.get("location"):
        missing.append("Location")

    if not event_data.get("event_date"):
        missing.append("Event Date")

    if not event_data.get("start_time"):
        missing.append("Start Time")

    if not event_data.get("duration"):
        missing.append("Duration")

    if not event_data.get("venue"):
        missing.append("Venue")

    return missing