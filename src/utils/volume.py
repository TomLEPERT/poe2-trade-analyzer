from __future__ import annotations


def convert_volume(volume_primary: float | int, core: dict, to_id: str | None) -> float:
    """
    volume_primary est en currency 'core.primary' (souvent divine).
    On convertit vers to_id (chaos/exalted/divine...) si possible via core.rates.
    """
    if volume_primary is None:
        return 0.0

    primary = core.get("primary")
    if not to_id or not primary or to_id == primary:
        return float(volume_primary)

    rates = core.get("rates", {}) or {}

    # core.rates donne les conversions depuis primary vers {chaos, exalted, ...}
    factor = rates.get(to_id)
    if factor is None:
        # pas de taux => pas de conversion
        return float(volume_primary)

    return float(volume_primary) * float(factor)
