def assign_tier(is_fda_approved: bool, is_peer_reviewed: bool):
    """
    Assign Tier based on:
    Tier 1 → has FDA-approved drug/device
    Tier 2 → peer-reviewed but not FDA
    Tier 3 → neither FDA nor peer-reviewed
    """

    if is_fda_approved:
        return "Tier 1"

    if is_peer_reviewed:
        return "Tier 2"

    return "Tier 3"


def tier_details(is_fda_approved: bool, is_peer_reviewed: bool):
    """
    Returns detailed metadata for database storage.
    """

    tier = assign_tier(is_fda_approved, is_peer_reviewed)

    explanation = {
        "Tier 1": "Paper discusses at least one FDA-approved drug/device.",
        "Tier 2": "Paper is peer-reviewed but does not discuss an FDA-approved drug/device.",
        "Tier 3": "Paper is not peer-reviewed and has no FDA-approved drugs/devices.",
    }

    return {
        "tier": tier,
        "reason": explanation[tier]
    }
