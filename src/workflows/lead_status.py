def determine_lead_status(missing_info):

    if not missing_info:
        return {
            "status": "COMPLETE",
            "message": "Lead has the key information needed."
        }

    if len(missing_info) <= 3:
        return {
            "status": "PARTIAL",
            "message": "Lead has enough information for a preliminary recommendation, but needs follow-up."
        }

    return {
        "status": "INCOMPLETE",
        "message": "Lead is missing several key details before a strong recommendation can be made."
    }