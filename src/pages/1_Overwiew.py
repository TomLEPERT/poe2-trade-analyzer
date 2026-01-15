import streamlit as st

from components.loaders import load_all_details
from components.local_icons import icon_data_uri

from utils.calculations import get_7d_trend, safe_percent
from utils.render import render_trade_pair, render_value_pair
from utils.sparkline import sparkline_svg, trend_color, make_relative
from utils.numbers import format_compact
from utils.pairs import best_value_pair, most_popular_pair
from utils.detail_chart import build_history_chart


# ------------------------
# Helpers
# ------------------------
def to_full_image_url(path: str | None) -> str | None:
    if not path:
        return None
    if path.startswith("http"):
        return path
    return "https://poe.ninja" + path


def find_item_in_all(data: dict, details_id: str):
    for t, items in data.items():
        if details_id in items:
            return t, items[details_id]
    return None, None


def go_detail(details_id: str):
    st.query_params["page"] = "detail"
    st.query_params["currency"] = details_id
    st.rerun()


def go_overview():
    st.query_params["page"] = "overview"
    if "currency" in st.query_params:
        del st.query_params["currency"]
    st.rerun()


def get_ref_icon(core: dict, ref_id: str | None) -> str | None:
    """Icône de la currency de référence d'une pair: 'divine'/'chaos'/'exalted'/..."""
    if not ref_id:
        return None

    core_items = core.get("items", []) or []
    ref_item = next((x for x in core_items if x.get("id") == ref_id), None)

    ref_details_id = ref_item.get("detailsId") if ref_item else None
    local = icon_data_uri(ref_details_id) if ref_details_id else None
    remote = to_full_image_url(ref_item.get("image")) if ref_item and ref_item.get("image") else None

    return local or remote


def prefer_chaos_if_small_divine(pairs: list[dict], value_pair: dict | None) -> dict | None:
    """Si on affiche en divine et rate < 1, basculer sur chaos si dispo."""
    if not value_pair:
        return value_pair

    if value_pair.get("id") == "divine":
        rate = value_pair.get("rate")
        if rate is not None and rate < 1:
            chaos_pair = next((p for p in pairs if p.get("id") == "chaos" and p.get("rate") is not None), None)
            if chaos_pair:
                return chaos_pair

    return value_pair


def convert_volume(volume_primary: float | int, core: dict, to_id: str | None) -> float:
    """
    volumePrimaryValue est toujours en core.primary (souvent divine).
    Convertit vers to_id via core.rates si possible.
    """
    if volume_primary is None:
        return 0.0

    primary = core.get("primary")
    if not to_id or not primary or to_id == primary:
        return float(volume_primary)

    rates = core.get("rates", {}) or {}
    factor = rates.get(to_id)
    if factor is None:
        return float(volume_primary)

    return float(volume_primary) * float(factor)


def value_to_divine(rate: float | int | None, ref_id: str | None, core: dict) -> float:
    """
    Convertit une value affichée (rate + ref_id) en "divine" pour comparer et trier.
    core.rates[ref_id] = combien de ref_id pour 1 divine (primary).
    divine = ref / rates[ref_id]
    """
    if rate is None:
        return 0.0

    primary = core.get("primary")  # généralement "divine"
    if not ref_id or not primary:
        return float(rate)

    if ref_id == primary:
        return float(rate)

    rates = core.get("rates", {}) or {}
    factor = rates.get(ref_id)
    if not factor:
        return 0.0

    return float(rate) / float(factor)


# ------------------------
# Data + routing
# ------------------------
data = load_all_details()
page = st.query_params.get("page", "overview")
currency = st.query_params.get("currency", None)


# =========================
# DETAIL VIEW
# =========================
if page == "detail" and currency:
    type_name, found = find_item_in_all(data, currency)

    if not found:
        st.error(f"Currency introuvable: {currency}")
        if st.button("⬅ Retour"):
            go_overview()
        st.stop()

    item = found.get("item", {})
    pairs = found.get("pairs", [])
    core = found.get("core", {})

    name = item.get("name", currency)
    item_icon = icon_data_uri(currency) or to_full_image_url(item.get("image"))

    primary_id = core.get("primary")

    value_pair = best_value_pair(pairs, prefer_id=primary_id) or (pairs[0] if pairs else None)
    value_pair = prefer_chaos_if_small_divine(pairs, value_pair)

    if not value_pair:
        st.error("Pas de données de marché pour cet item.")
        if st.button("⬅ Retour"):
            go_overview()
        st.stop()

    ref_id = value_pair.get("id")
    ref_icon = get_ref_icon(core, ref_id)

    rate = value_pair.get("rate")
    history = value_pair.get("history", [])
    volume_primary = value_pair.get("volumePrimaryValue", 0)
    volume_h = convert_volume(volume_primary, core, ref_id)

    # top
    colA, colB = st.columns([1, 6])
    with colA:
        if st.button("⬅ Retour"):
            go_overview()
    with colB:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:12px;">
              {f"<img src='{item_icon}' style='width:34px;height:34px;' />" if item_icon else ""}
              <h1 style="margin:0;">{name}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

    exchange_html = render_trade_pair(rate if rate is not None else 0, ref_icon, item_icon)

    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns: 420px 1fr;gap:18px;align-items:start;margin-bottom:18px;">
          <div style="background:var(--bg-panel);border:1px solid rgba(34,197,94,0.45);border-radius:8px;padding:14px 16px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <div style="color:var(--text-muted);font-weight:700;">Exchange</div>
              <div>{exchange_html}</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <div style="color:var(--text-muted);font-weight:700;">Volume / Hour</div>
              <div style="display:flex;align-items:center;gap:8px;white-space:nowrap;">
                <div style="font-weight:700;color:var(--text-main);">{format_compact(volume_h)}</div>
                {f"<img src='{ref_icon}' style='width:18px;height:18px;' />" if ref_icon else ""}
                <span style="opacity:0.8;">/h</span>
              </div>
            </div>
          </div>
          <div></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Price history")
    ref_name = ref_id.capitalize() if ref_id else "Currency"
    fig = build_history_chart(history, title=f"{ref_name} ↔ {name}")
    st.plotly_chart(fig, width="stretch")

    st.stop()


# =========================
# OVERVIEW VIEW
# =========================
st.title("📊 Economy Overview")

header_html = (
    '<div class="poe-header sticky-header">'
    '<div style="display:grid;grid-template-columns:56px 3fr 2.2fr 2.2fr 2.1fr 2.2fr;gap:14px;align-items:center;">'
    '<div></div><div>Name</div><div>Value</div><div>Last 7 days</div><div>Volume / Hour</div><div>Most Popular</div>'
    '</div></div>'
)

tabs = st.tabs(list(data.keys()))

for tab, type_name in zip(tabs, data.keys()):
    with tab:
        st.markdown(header_html, unsafe_allow_html=True)

        items = data[type_name]

        # -------- Build sortable rows (desc by value in divine) --------
        rows = []
        for details_id, d in items.items():
            pairs = d.get("pairs", [])
            core = d.get("core", {})
            if not pairs:
                continue

            primary_id = core.get("primary")
            vp = best_value_pair(pairs, prefer_id=primary_id) or pairs[0]
            vp = prefer_chaos_if_small_divine(pairs, vp)
            if not vp:
                continue

            rate = vp.get("rate")
            ref_id = vp.get("id")
            sort_key = value_to_divine(rate, ref_id, core)

            rows.append((sort_key, details_id, d))

        rows.sort(key=lambda x: x[0], reverse=True)

        # -------- Render sorted rows --------
        for _, details_id, d in rows:
            item = d.get("item", {})
            pairs = d.get("pairs", [])
            core = d.get("core", {})

            name = item.get("name") or details_id
            item_icon = icon_data_uri(details_id) or to_full_image_url(item.get("image")) or None

            primary_id = core.get("primary")

            # displayed value pair
            value_pair = best_value_pair(pairs, prefer_id=primary_id) or pairs[0]
            value_pair = prefer_chaos_if_small_divine(pairs, value_pair)
            if not value_pair:
                continue

            value_rate = value_pair.get("rate")
            ref_id = value_pair.get("id")
            ref_icon = get_ref_icon(core, ref_id)

            # trend
            history = value_pair.get("history", [])
            pct, trend = get_7d_trend(history)
            delta = safe_percent(pct)

            rel_trend = make_relative(trend)
            color = trend_color(delta)
            svg = sparkline_svg(rel_trend, stroke=color)

            if delta is None:
                delta_html = ""
            else:
                cls = "positive" if delta > 0 else ("negative" if delta < 0 else "")
                sign = "+" if delta > 0 else ""
                delta_html = f'<span class="{cls}" style="margin-left:10px;white-space:nowrap;">{sign}{delta:.0f}%</span>'

            # volume converted to displayed unit
            volume_primary = value_pair.get("volumePrimaryValue", 0)
            volume_h = convert_volume(volume_primary, core, ref_id)

            volume_html = (
                '<div style="display:flex;align-items:center;gap:6px;white-space:nowrap;">'
                f'<span style="color:#e5e7eb;font-weight:600;">{format_compact(volume_h)}</span>'
                + (f'<img src="{ref_icon}" style="width:18px;height:18px;vertical-align:middle;" />' if ref_icon else "")
                + '<span style="opacity:0.8;">/h</span></div>'
            )

            # most popular (own ref icon)
            pop_pair = most_popular_pair(pairs)
            if pop_pair and pop_pair.get("rate") is not None:
                pop_ref_id = pop_pair.get("id")
                pop_ref_icon = get_ref_icon(core, pop_ref_id)
                popular_html = render_trade_pair(pop_pair["rate"], pop_ref_icon, item_icon)
            else:
                popular_html = '<span style="opacity:0.7;">—</span>'

            value_html = render_value_pair(value_rate, ref_icon, item_icon)

            cols = st.columns([0.6, 3.0, 2.2, 2.2, 2.1, 2.2])

            with cols[0]:
                st.write("")

            with cols[1]:
                c1, c2 = st.columns([0.35, 3.65])
                with c1:
                    if item_icon:
                        st.image(item_icon, width=28)
                with c2:
                    if st.button(name, key=f"open_{type_name}_{details_id}"):
                        go_detail(details_id)

            with cols[2]:
                st.markdown(value_html, unsafe_allow_html=True)

            with cols[3]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;white-space:nowrap;"><div>{svg}</div>{delta_html}</div>',
                    unsafe_allow_html=True
                )

            with cols[4]:
                st.markdown(volume_html, unsafe_allow_html=True)

            with cols[5]:
                st.markdown(popular_html, unsafe_allow_html=True)
