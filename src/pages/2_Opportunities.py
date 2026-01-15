import streamlit as st

from components.loaders import load_all_details
from components.local_icons import icon_data_uri

from utils.arbitrage import find_best_opportunity_for_item
from utils.numbers import format_compact


# -----------------------------
# Navigation (même logique que ton overview/detail)
# -----------------------------
def go_detail(details_id: str):
    st.query_params["page"] = "detail"
    st.query_params["currency"] = details_id
    st.rerun()


# -----------------------------
# Helpers UI
# -----------------------------
def profit_color(pct: float) -> str:
    if pct >= 0:
        return "#22c55e"
    return "#ef4444"


def liq_color(v: float) -> str:
    # simple palette (tu peux ajuster)
    if v >= 5000:
        return "#22c55e"
    if v >= 1000:
        return "#eab308"
    return "#ef4444"


def spread_factor(buy_slip_pct: float, sell_slip_pct: float) -> float:
    """
    Plus le spread est fort, plus on pénalise le score.
    On transforme en facteur [0..1] environ.
    """
    total = (buy_slip_pct + sell_slip_pct) / 100.0
    # Ex: 2% -> facteur 0.98
    return max(0.0, 1.0 - total)


def opportunity_score(
    profit_pct: float,
    profit_value: float,
    buy_liq: float,
    sell_liq: float,
    buy_slip_pct: float,
    sell_slip_pct: float,
) -> float:
    """
    Score = profit% * sqrt(liquidité) * spread_factor
    + petit bonus selon profit en valeur.
    L'idée : gros % + liquide + faible spread => score haut.
    """
    liq = max(0.0, min(buy_liq, sell_liq))
    liq_component = (liq ** 0.5)  # racine pour éviter d'écraser tout
    spread = spread_factor(buy_slip_pct, sell_slip_pct)

    base = max(0.0, profit_pct) * liq_component * spread
    bonus = max(0.0, profit_value) * 100.0  # boost léger
    return base + bonus


# -----------------------------
# Page
# -----------------------------
data = load_all_details()

st.title("🧠 Opportunities Scanner")

with st.sidebar:
    st.subheader("Settings")

    target = st.selectbox("Capital target", ["divine", "chaos", "exalted"], index=0)

    sort_mode = st.selectbox("Sort by", ["Score", "Profit %", "Profit value"], index=0)

    st.subheader("Profit filters")
    min_profit_pct = st.slider("Min profit (%)", 0.0, 50.0, 2.0, 0.5)

    min_profit_value = st.number_input(
        f"Min profit ({target}) / unit",
        min_value=0.0,
        value=0.01,
        step=0.01,
        format="%.2f",
    )

    st.subheader("Liquidity")
    min_buy_vol = st.number_input("Min buy volume (primary / hour)", min_value=0.0, value=500.0, step=100.0)
    min_sell_vol = st.number_input("Min sell volume (primary / hour)", min_value=0.0, value=500.0, step=100.0)

    st.subheader("Slippage / Spread")
    buy_slip = st.slider("Buy slippage (+%)", 0.0, 5.0, 1.0, 0.1)
    sell_slip = st.slider("Sell slippage (-%)", 0.0, 5.0, 1.0, 0.1)

st.caption(
    "On compare les cotations (Divine/Chaos/Exalted) et on cherche les écarts exploitables. "
    "Le profit est calculé dans la currency cible, avec slippage et filtres de liquidité."
)

# -----------------------------
# Collect opportunities
# -----------------------------
opps = []

for type_name, items in data.items():
    for details_id, d in items.items():
        item = d.get("item", {})
        pairs = d.get("pairs", [])
        core = d.get("core", {})

        if not pairs:
            continue

        best = find_best_opportunity_for_item(
            type_name=type_name,
            details_id=details_id,
            item=item,
            pairs=pairs,
            core=core,
            target_quote=target,
            min_buy_volume_primary=min_buy_vol,
            min_sell_volume_primary=min_sell_vol,
            buy_slippage_pct=buy_slip,
            sell_slippage_pct=sell_slip,
        )

        if not best:
            continue

        if best.profit_pct < min_profit_pct:
            continue

        if best.profit_per_unit < min_profit_value:
            continue

        # liquidité (on préfère target, sinon primary)
        buy_liq = best.buy_volume_target if best.buy_volume_target is not None else best.buy_volume_primary
        sell_liq = best.sell_volume_target if best.sell_volume_target is not None else best.sell_volume_primary

        score = opportunity_score(
            profit_pct=best.profit_pct,
            profit_value=best.profit_per_unit,
            buy_liq=buy_liq,
            sell_liq=sell_liq,
            buy_slip_pct=buy_slip,
            sell_slip_pct=sell_slip,
        )

        opps.append((score, best, buy_liq, sell_liq))

# -----------------------------
# Sort
# -----------------------------
if sort_mode == "Profit value":
    opps.sort(key=lambda x: x[1].profit_per_unit, reverse=True)
elif sort_mode == "Profit %":
    opps.sort(key=lambda x: x[1].profit_pct, reverse=True)
else:
    opps.sort(key=lambda x: x[0], reverse=True)

# -----------------------------
# Header (poe style)
# -----------------------------
st.markdown(
    """
    <div class="poe-header sticky-header opp-header">
      <div style="display:grid;grid-template-columns: 3.4fr 2.2fr 2.2fr 1.5fr 1.8fr 2.6fr 1.2fr; gap:14px; align-items:center;">
        <div>Currency</div>
        <div>Buy</div>
        <div>Sell</div>
        <div>Profit %</div>
        <div>Profit</div>
        <div>Liquidity</div>
        <div>Score</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

if not opps:
    st.info("Aucune opportunité avec ces filtres.")
    st.stop()

# -----------------------------
# Rows
# -----------------------------
for score, opp, buy_liq, sell_liq in opps:
    icon = icon_data_uri(opp.details_id)

    # BUY/SELL text
    buy_txt = f"{opp.buy_rate:.4g} {opp.buy_quote} ⇄ 1.0"
    sell_txt = f"{opp.sell_rate:.4g} {opp.sell_quote} ⇄ 1.0"

    # PROFIT %
    pct_col = profit_color(opp.profit_pct)
    profit_pct_html = (
        f'<span style="color:{pct_col};font-weight:800;white-space:nowrap;">{opp.profit_pct:+.2f}%</span>'
    )

    # PROFIT value
    profit_value_html = (
        '<div style="display:flex;align-items:center;gap:6px;white-space:nowrap;">'
        f'<span style="color:{pct_col};font-weight:800;">+{opp.profit_per_unit:.4g}</span>'
        f'<span style="opacity:0.85;">{opp.target_quote}</span>'
        '</div>'
    )

    # Liquidity (2 lignes)
    buy_col = liq_color(buy_liq)
    sell_col = liq_color(sell_liq)
    liquidity_html = (
        '<div class="opp-liq">'
        f'<div><span class="opp-liq-label">Buy</span> '
        f'<span style="color:{buy_col};font-weight:800;">{format_compact(buy_liq)}</span> '
        f'<span class="opp-liq-unit">{opp.target_quote}/h</span></div>'
        f'<div><span class="opp-liq-label">Sell</span> '
        f'<span style="color:{sell_col};font-weight:800;">{format_compact(sell_liq)}</span> '
        f'<span class="opp-liq-unit">{opp.target_quote}/h</span></div>'
        '</div>'
    )

    score_html = f'<span style="font-weight:800;white-space:nowrap;">{score:,.0f}</span>'

    cols = st.columns([3.4, 2.2, 2.2, 1.5, 1.8, 2.6, 1.2])

    # Currency (icon + button)
    with cols[0]:
        c1, c2 = st.columns([0.22, 3.78])
        with c1:
            if icon:
                st.image(icon, width=28)
        with c2:
            if st.button(opp.name, key=f"opp_{opp.type_name}_{opp.details_id}"):
                go_detail(opp.details_id)

    with cols[1]:
        st.write(buy_txt)

    with cols[2]:
        st.write(sell_txt)

    with cols[3]:
        st.markdown(profit_pct_html, unsafe_allow_html=True)

    with cols[4]:
        st.markdown(profit_value_html, unsafe_allow_html=True)

    with cols[5]:
        st.markdown(liquidity_html, unsafe_allow_html=True)

    with cols[6]:
        st.markdown(score_html, unsafe_allow_html=True)
