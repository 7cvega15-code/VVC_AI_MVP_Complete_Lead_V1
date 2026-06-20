def generate_client_response(
    event_data,
    recommendation,
    addons,
    missing_info,
    lead_status,
    action
):
    recommended = recommendation["recommended"]
    alternative = recommendation["alternative"]
    entry = recommendation["entry"]

    if action == "SHOW_QUESTIONS_ONLY":
        event_type = event_data.get("event_type") or "event"

        message = f"""
Hi,

Thank you for your interest in VVC Photobooths!

To help us recommend the best package and provide an accurate quote, could you please share:

"""

        for item in missing_info:
            message += f"• {item}\n"

        message += """

We look forward to learning more about your event!

Thank you,
Christina
VVC Photobooths
"""

        return message

    message = f"""
Hi,

Thank you for reaching out regarding your {event_data['event_type']} in {event_data['location']}!

Based on the details shared so far, our {recommended['product_family'].replace("The ", "")} collection appears to be a great fit for your event.

Available package options:
• {entry['tier_name']} - ${entry['base_price']}
• {alternative['tier_name']} - ${alternative['base_price']}
• {recommended['tier_name']} - ${recommended['base_price']}

Recommended enhancements:
"""

    for addon in addons:
        message += f"\n• {addon}"

    if action == "SHOW_PROPOSAL_AND_QUESTIONS":
        message += """

To help us provide the most accurate recommendation and quote, could you also share:
"""

        for item in missing_info:
            message += f"\n• {item}"

    message += """

Thank you,
Christina
VVC Photobooths
"""

    return message