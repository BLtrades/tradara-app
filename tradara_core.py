"""Pure Tradara scoring logic shared by web and future mobile clients."""

import pandas as pd


TRADE_INTEL = {
    "Earthworks": (["land division", "subdivision", "earthworks"], 0, 3, "Site preparation"),
    "Concreter": (["dwelling", "townhouse", "units", "apartment", "building"], 1, 5, "Foundations / structure"),
    "Bricklayer": (["dwelling", "townhouse", "units", "apartment", "building"], 3, 8, "Structure / envelope"),
    "Carpenter": (["dwelling", "townhouse", "units", "apartment", "building"], 2, 8, "Framing / fit-out"),
    "Roofer": (["dwelling", "townhouse", "units", "apartment", "building"], 4, 9, "Building envelope"),
    "Plumber": (["dwelling", "townhouse", "units", "apartment", "building", "commercial"], 3, 10, "Rough-in / fit-off"),
    "Electrician": (["dwelling", "townhouse", "units", "apartment", "building", "commercial"], 3, 11, "Rough-in / fit-off"),
    "HVAC": (["apartment", "commercial", "shop", "office", "building", "units"], 4, 11, "Services / fit-off"),
    "Plasterer": (["dwelling", "townhouse", "units", "apartment", "building"], 6, 11, "Internal fit-out"),
    "Tiler": (["dwelling", "townhouse", "units", "apartment", "building"], 7, 12, "Internal finishes"),
    "Painter": (["dwelling", "townhouse", "units", "apartment", "building"], 8, 13, "Finishes"),
    "Landscaper": (["dwelling", "townhouse", "units", "apartment", "land division", "subdivision"], 9, 15, "External completion"),
    "Fencer": (["dwelling", "townhouse", "units", "land division", "subdivision"], 8, 15, "External completion"),
}

OPPORTUNITY_COLUMNS = [
    "Score", "Action", "Trade", "Phase", "Development", "Description",
    "Decision date", "PlanSA",
]


def to_datetime(milliseconds):
    """Convert an ArcGIS epoch-millisecond value without raising on bad data."""
    try:
        return pd.to_datetime(milliseconds, unit="ms") if milliseconds else pd.NaT
    except (TypeError, ValueError, OverflowError):
        return pd.NaT


def opportunity_rows(data, trades, now=None):
    """Return ranked candidate rows from a Location SA feature collection."""
    current_time = pd.Timestamp(now) if now is not None else pd.Timestamp.now()
    output = []
    features = data.get("features", []) if isinstance(data, dict) else []

    for feature in features:
        if not isinstance(feature, dict):
            continue
        properties = feature.get("attributes") or feature.get("properties") or {}
        if not isinstance(properties, dict):
            continue
        description = str(properties.get("description") or "")
        description_lower = description.lower()
        decision_date = to_datetime(properties.get("decisiondate"))
        age_months = None if pd.isna(decision_date) else max(
            0, (current_time - decision_date).days / 30.44
        )

        for trade in trades:
            if trade not in TRADE_INTEL:
                continue
            keywords, start_month, end_month, phase = TRADE_INTEL[trade]
            hits = sum(keyword in description_lower for keyword in keywords)
            if not hits:
                continue

            score = min(40, 20 + hits * 7)
            decision = str(properties.get("decision") or "").lower()
            if any(word in decision for word in ("approved", "granted", "consent")):
                score += 20

            if age_months is None:
                action = "VERIFY TIMING"
            elif age_months < start_month:
                action = "CONTACT NOW — pre-position"
                score += 20
            elif age_months <= end_month:
                action = "CONTACT NOW — trade window"
                score += 30
            elif age_months <= end_month + 3:
                action = "LATE WINDOW — verify"
                score += 8
            else:
                action = "LIKELY PASSED — verify"
                score -= 15

            output.append({
                "Score": max(0, min(100, score)),
                "Action": action,
                "Trade": trade,
                "Phase": phase,
                "Development": properties.get("developmentnumber") or "Unknown",
                "Description": description or "No description",
                "Decision date": decision_date,
                "PlanSA": properties.get("applicationurl") or properties.get("urlonly") or "",
            })

    return pd.DataFrame(output, columns=OPPORTUNITY_COLUMNS)


def preference_list(profile, key):
    value = (profile or {}).get(key) or []
    if isinstance(value, list):
        return value
    return [item.strip() for item in str(value).split(",") if item.strip()]


def fit_boost(row, profile):
    if not profile:
        return 0, "Complete your company profile to personalise this score"
    boost = 0
    reasons = []
    description = str(row["Description"]).lower()
    if any(item.lower() in description for item in preference_list(profile, "preferred_project_types")):
        boost += 8
        reasons.append("preferred project type")
    if row["Trade"] in preference_list(profile, "preferred_trades"):
        boost += 8
        reasons.append("core company trade")
    if str(row["Action"]).startswith("CONTACT NOW"):
        boost += 5
        reasons.append("good timing")
    return boost, ", ".join(reasons) or "general company fit"
