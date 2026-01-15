from __future__ import annotations

from typing import List, Optional


def make_relative(values: List[float]) -> List[float]:
    """
    Transforme une série en index relatif (%) par rapport au premier point.
    Exemple: [4712, 4356, 4045] -> [100.0, 92.4, 85.9]
    Ça rend la sparkline lisible même si les valeurs sont énormes.
    """
    if not values:
        return values
    base = values[0]
    if base == 0 or base is None:
        return values
    return [(v / base) * 100.0 for v in values]


def sparkline_svg(values: List[float], width: int = 110, height: int = 28, stroke: str = "#93c5fd") -> str:
    """
    SVG mini-graph sans axes, normalisé.
    """
    if not values or len(values) < 2:
        return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"></svg>'

    vmin = min(values)
    vmax = max(values)
    rng = vmax - vmin

    # Si quasi-plat, on force une échelle minimale pour qu’on voie quelque chose
    if rng < 0.001:
        rng = 1.0
        vmin = vmin - 0.5
        vmax = vmax + 0.5

    pad = 2
    inner_h = height - pad * 2

    def x(i: int) -> float:
        return (i / (len(values) - 1)) * (width - 2) + 1

    def y(val: float) -> float:
        return pad + (1 - ((val - vmin) / rng)) * inner_h

    points = " ".join([f"{x(i):.2f},{y(v):.2f}" for i, v in enumerate(values)])

    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
      <polyline fill="none" stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                points="{points}" />
    </svg>
    """


def trend_color(pct: Optional[float]) -> str:
    if pct is None:
        return "#93c5fd"
    return "#22c55e" if pct > 0 else ("#ef4444" if pct < 0 else "#93c5fd")
