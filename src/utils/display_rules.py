from __future__ import annotations

from typing import Optional


def prefer_chaos_if_small_divine(pairs: list[dict], value_pair: dict | None) -> dict | None:
    """
    Si l'affichage actuel est en divine et < 1, bascule sur chaos si possible.
    """
    if not value_pair:
        return value_pair

    ref_id = value_pair.get("id")
    rate = value_pair.get("rate")

    if ref_id == "divine" and rate is not None and rate < 1:
        chaos_pair = next((p for p in pairs if p.get("id") == "chaos" and p.get("rate") is not None), None)
        if chaos_pair:
            return chaos_pair

    return value_pair
