def get_most_popular_pair(pairs):
    valid = [p for p in pairs if p.get("rate") and p.get("volumePrimaryValue")]
    if not valid:
        return None
    return max(valid, key=lambda p: p["volumePrimaryValue"])