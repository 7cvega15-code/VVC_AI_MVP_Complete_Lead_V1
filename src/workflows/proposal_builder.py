def build_proposal(event_data, experience, recommendation, addons):

    recommended = recommendation["recommended"]
    alternative = recommendation["alternative"]
    entry = recommendation["entry"]

    package_options = []

    for package in [entry, alternative, recommended]:
        if package not in package_options:
            package_options.append(package)

    proposal = f"""
CLIENT PROPOSAL

Event Type: {event_data['event_type']}
Location: {event_data['location']}

Experience Options:
• Entry Experience: {experience['entry_experience']}
• Recommended Experience: {experience['recommended_experience']}
"""

    proposal += "\n• Premium Experience(s):"

    for premium in experience["premium_experiences"]:
        proposal += f"\n  - {premium}"

    proposal += f"""

Recommended Collection:
{recommended['product_family']}

Available Package Options:
"""

    for package in package_options:
        proposal += f"• {package['tier_name']} - ${package['base_price']}\n"

    proposal += "\nRecommended Enhancements:\n"

    for addon in addons:
        proposal += f"\n• {addon}"

    return proposal