from __future__ import annotations

from typing import Optional


def best_value_pair(pairs: list[dict], prefer_id: Optional[str] = None) -> Optional[dict]:
    """
    Choisit la meilleure paire pour afficher Value/Trend/Volume:
    - priorité à prefer_id si rate est dispo et volume > 0
    - sinon, parmi les paires avec rate != None, prendre celle avec le + gros volumePrimaryValue
    - fallback: 1ère paire avec rate != None
    """
    if not pairs:
        return None

    valid = [p for p in pairs if p.get("rate") is not None]
    if not valid:
        return None

    if prefer_id:
        pref = next((p for p in valid if p.get("id") == prefer_id), None)
        if pref and (pref.get("volumePrimaryValue", 0) > 0):
            return pref

    # take highest volume
    valid.sort(key=lambda p: (p.get("volumePrimaryValue", 0) or 0), reverse=True)
    return valid[0]


def most_popular_pair(pairs: list[dict]) -> Optional[dict]:
    """
    La paire la plus populaire = volumePrimaryValue max (rate peut être None, on filtre un minimum).
    """
    if not pairs:
        return None

    candidates = [p for p in pairs if (p.get("volumePrimaryValue", 0) or 0) > 0]
    if not candidates:
        # fallback: au moins une avec rate
        candidates = [p for p in pairs if p.get("rate") is not None]
        if not candidates:
            return None

    candidates.sort(key=lambda p: (p.get("volumePrimaryValue", 0) or 0), reverse=True)
    return candidates[0]
