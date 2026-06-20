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
    # Allow explicit product_family override in event_data for testing or special cases
    product_family = event_data.get("product_family")

    if not product_family:
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

    # Determine recommended tier name from business rules (glamour > signature > classic)
    if score >= tier_rules.get("glamour_min_score", 9999):
        recommended_tier = "Glamour"
    elif score >= tier_rules.get("signature_min_score", 0):
        recommended_tier = "Signature"
    else:
        recommended_tier = "Classic"

    # Helper to find package dict for a family
    def _find_product(packages_list, family):
        for p in packages_list:
            if p.get("product_family") == family:
                return p
        return None

    # Try to find the recommended/alternative/entry tiers, with sensible fallbacks
    recommended = find_package_tier(packages, product_family, recommended_tier)
    alternative = find_package_tier(packages, product_family, "Signature")
    entry = find_package_tier(packages, product_family, "Classic")

    if not recommended or not alternative or not entry:
        product = _find_product(packages, product_family)
        if product and product.get("tiers"):
            tiers = product["tiers"]
            # Assume tiers are ordered from lowest to highest; fallback safely
            entry_t = tiers[0]
            alt_t = tiers[1] if len(tiers) > 1 else tiers[0]
            rec_t = tiers[-1]

            # Build dicts if any were missing
            if not entry:
                entry = {
                    "product_family": product_family,
                    "tier_name": entry_t["tier_name"],
                    "base_price": entry_t.get("base_price"),
                    "included_hours": entry_t.get("included_hours"),
                    "additional_hour_rate": entry_t.get("additional_hour_rate")
                }
            if not alternative:
                alternative = {
                    "product_family": product_family,
                    "tier_name": alt_t["tier_name"],
                    "base_price": alt_t.get("base_price"),
                    "included_hours": alt_t.get("included_hours"),
                    "additional_hour_rate": alt_t.get("additional_hour_rate")
                }
            if not recommended:
                recommended = {
                    "product_family": product_family,
                    "tier_name": rec_t["tier_name"],
                    "base_price": rec_t.get("base_price"),
                    "included_hours": rec_t.get("included_hours"),
                    "additional_hour_rate": rec_t.get("additional_hour_rate")
                }

    return {
        "recommended": recommended,
        "alternative": alternative,
        "entry": entry
    }