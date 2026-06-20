def generate_followup_questions(missing_info):

    if not missing_info:
        return "No follow-up questions needed."

    message = """
Before we finalize recommendations, could you please provide:

"""

    for item in missing_info:
        message += f"• {item}\n"

    message += """
This will help us recommend the best package and enhancements for your event.

Thank you,
Christina
VVC Photobooths
"""

    return message