from __future__ import annotations

from datetime import datetime
import plotly.graph_objects as go


def _parse_ts(ts: str) -> datetime:
    # Ex: "2026-01-14T00:00:00Z"
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def build_history_chart(history: list[dict], title: str = "Price history") -> go.Figure:
    """
    Construit un graphe style poe.ninja :
    - ligne = rate
    - barres = volume
    """
    fig = go.Figure()

    if not history:
        fig.update_layout(
            title=title,
            template="plotly_dark",
            height=520,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        return fig

    xs = [_parse_ts(h["timestamp"]) for h in history if h.get("timestamp")]
    ys = [h.get("rate") for h in history]
    vols = [h.get("volumePrimaryValue", 0) for h in history]

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines+markers",
            name="Rate",
            line=dict(width=2),
            marker=dict(size=5),
        )
    )

    fig.add_trace(
        go.Bar(
            x=xs,
            y=vols,
            name="Volume",
            opacity=0.30,
            yaxis="y2",
        )
    )

    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=560,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="", showgrid=True),
        yaxis2=dict(
            title="",
            overlaying="y",
            side="right",
            showgrid=False,
            rangemode="tozero",
        ),
    )

    return fig
