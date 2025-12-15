def _calc_avg_confidence(payload: dict | None) -> float | None:
    if not payload:
        return None

    data = payload.get("data")
    if not isinstance(data, list) or not data:
        return None

    confidences = [
        d.get("confidence")
        for d in data
        if isinstance(d, dict) and d.get("confidence") is not None
    ]

    if not confidences:
        return None

    return round(sum(confidences) / len(confidences), 4)
