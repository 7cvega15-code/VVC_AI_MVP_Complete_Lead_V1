def generate_response(event_data, recommendation, addons):

    response = f"""
Hi,

Thank you for your inquiry regarding your {event_data['event_type']} in {event_data['location']}!

Based on the details provided, we recommend our {recommendation['product_family']} {recommendation['tier_name']} package.

Package Investment:
${recommendation['base_price']}

Recommended Enhancements:
"""

    for addon in addons:
        response += f"\n• {addon}"

    response += """

We would love to learn more about your event and discuss customization options.

Thank you,
Christina
VVC Photobooths
"""

    return response