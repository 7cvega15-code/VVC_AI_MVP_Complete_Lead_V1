import json


def load_packages():
    with open("configs/packages.json", "r") as file:
        return json.load(file)


def load_business_rules():
    with open("configs/business_rules.json", "r") as file:
        return json.load(file)


def find_package_tier(packages, product_family, tier_name):
    for package in packages:
        if package["product_family"] == product_family:
            for package_tier in package["tiers"]:
                if package_tier["tier_name"] == tier_name:
                    return {
                        "product_family": product_family,
                        "tier_name": tier_name,
                        "base_price": package_tier["base_price"],
                        "included_hours": package_tier["included_hours"],
                        "additional_hour_rate": package_tier["additional_hour_rate"]
                    }
    return None


def recommend_package(event_data, score):
    package_config = load_packages()
    packages = package_config["packages"]

    business_rules = load_business_rules()
    tier_rules = business_rules["tier_rules"]

    event_type = event_data.get("event_type", "").lower()

    if "graduation" in event_type:
        product_family = "The Spark"
    elif "school" in event_type:
        product_family = "The Spark"
    elif "fundraiser" in event_type:
        product_family = "The Spark"
    elif event_data.get("wants_prints"):
        product_family = "The Luxe"
    else:
        product_family = "The Spark"

    if score >= tier_rules["grand_min_score"]:
        recommended_tier = "Grand"
    elif score >= tier_rules["signature_min_score"]:
        recommended_tier = "Signature"
    else:
        recommended_tier = "Classic"

    return {
        "recommended": find_package_tier(packages, product_family, recommended_tier),
        "alternative": find_package_tier(packages, product_family, "Signature"),
        "entry": find_package_tier(packages, product_family, "Classic")
    }