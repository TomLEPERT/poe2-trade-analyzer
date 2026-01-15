from __future__ import annotations

from typing import Optional


def format_compact(value: Optional[float], decimals: int = 1) -> str:
    """
    4900 -> 4.9k
    399810 -> 399.8k
    1234567 -> 1.2m
    """
    if value is None:
        return "—"

    sign = "-" if value < 0 else ""
    v = abs(float(value))

    if v >= 1_000_000_000:
        return f"{sign}{v/1_000_000_000:.{decimals}f}b"
    if v >= 1_000_000:
        return f"{sign}{v/1_000_000:.{decimals}f}m"
    if v >= 1_000:
        return f"{sign}{v/1_000:.{decimals}f}k"

    # pour les petits nombres
    if v.is_integer():
        return f"{sign}{int(v)}"
    return f"{sign}{v:.{decimals}f}"
