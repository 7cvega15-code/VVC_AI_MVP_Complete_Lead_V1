def route_workflow(lead_status):

    status = lead_status["status"]

    if status == "COMPLETE":
        return "FULL_PROPOSAL"

    elif status == "PARTIAL":
        return "PRELIMINARY_PROPOSAL"

    else:
        return "FOLLOWUP_ONLY"