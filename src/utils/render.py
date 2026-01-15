from __future__ import annotations
from typing import Optional
from utils.numbers import format_compact


def safe_img(url: Optional[str], size: int = 18) -> str:
    if not url or url == "None":
        return ""
    return f'<img src="{url}" style="width:{size}px;height:{size}px;vertical-align:middle;" />'


def render_trade_pair(rate: float, left_icon: Optional[str], right_icon: Optional[str]) -> str:
    return (
        '<div style="display:flex;align-items:center;gap:6px;white-space:nowrap;">'
        f'<span style="color:#e5e7eb;font-weight:600;">{format_compact(rate)}</span>'
        f'{safe_img(left_icon)}'
        '<span style="opacity:0.65;">⇄</span>'
        '<span style="color:#e5e7eb;">1.0</span>'
        f'{safe_img(right_icon)}'
        '</div>'
    )


def render_value_pair(rate: Optional[float], left_icon: Optional[str], right_icon: Optional[str]) -> str:
    if rate is None:
        return '<span style="opacity:0.7;">—</span>'

    return (
        '<div style="display:flex;align-items:center;gap:6px;white-space:nowrap;">'
        f'<span style="color:#e5e7eb;font-weight:700;">{format_compact(rate)}</span>'
        f'{safe_img(left_icon)}'
        '<span style="opacity:0.65;">⇄</span>'
        '<span style="color:#e5e7eb;">1.0</span>'
        f'{safe_img(right_icon)}'
        '</div>'
    )
