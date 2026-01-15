def get_7d_trend(history):
    if len(history) < 2:
        return 0, []

    last_7 = history[-7:]
    start = last_7[0]["rate"]
    end = last_7[-1]["rate"]

    pct = ((end - start) / start) * 100 if start else 0
    values = [h["rate"] for h in last_7]

    return pct, values

def safe_percent(pct):
    if pct is None:
        return None
    return round(pct, 2)