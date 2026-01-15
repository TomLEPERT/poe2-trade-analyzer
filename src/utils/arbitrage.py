from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


BASE_QUOTES = {"divine", "chaos", "exalted"}


def convert_amount(amount: float, from_id: str, to_id: str, core: dict) -> Optional[float]:
    """
    Convertit un montant d'une currency quote vers une autre via core.primary + core.rates.
    core.primary est souvent 'divine'
    core.rates = {'chaos': X, 'exalted': Y} signifie 1 divine = X chaos, 1 divine = Y exalted.
    """
    if from_id == to_id:
        return float(amount)

    primary = core.get("primary")
    rates = core.get("rates", {}) or {}
    if not primary:
        return None

    # from -> primary
    if from_id == primary:
        amount_primary = float(amount)
    else:
        f = rates.get(from_id)
        if not f:
            return None
        amount_primary = float(amount) / float(f)

    # primary -> to
    if to_id == primary:
        return amount_primary

    t = rates.get(to_id)
    if not t:
        return None
    return amount_primary * float(t)


def volume_in_quote(volume_primary: float, core: dict, quote_id: str) -> Optional[float]:
    """
    volumePrimaryValue est en core.primary.
    On le convertit dans la quote demandée (chaos/exalted/divine) pour affichage.
    """
    primary = core.get("primary")
    if not primary:
        return None
    if quote_id == primary:
        return float(volume_primary)

    rates = core.get("rates", {}) or {}
    f = rates.get(quote_id)
    if not f:
        return None
    return float(volume_primary) * float(f)


@dataclass
class Opportunity:
    type_name: str
    details_id: str
    name: str

    buy_quote: str
    buy_rate: float

    sell_quote: str
    sell_rate: float

    target_quote: str

    cost_in_target: float
    revenue_in_target: float
    profit_per_unit: float
    profit_pct: float

    buy_volume_primary: float
    sell_volume_primary: float

    buy_volume_target: Optional[float]
    sell_volume_target: Optional[float]


def find_best_opportunity_for_item(
    type_name: str,
    details_id: str,
    item: dict,
    pairs: list[dict],
    core: dict,
    target_quote: str = "divine",
    min_buy_volume_primary: float = 0.0,
    min_sell_volume_primary: float = 0.0,
    buy_slippage_pct: float = 0.0,   # +% sur le coût
    sell_slippage_pct: float = 0.0,  # -% sur le revenu
) -> Optional[Opportunity]:
    """
    Cherche la meilleure opportunité buy_quote -> sell_quote pour 1 item.
    Profit calculé en target_quote.
    Slippage:
      - achat: cost *= (1 + buy_slippage_pct/100)
      - vente: revenue *= (1 - sell_slippage_pct/100)
    Liquidité:
      - buy_volume_primary >= min_buy_volume_primary
      - sell_volume_primary >= min_sell_volume_primary
    """
    name = item.get("name") or details_id

    # pairs utilisables
    usable = []
    for p in pairs:
        q = p.get("id")
        r = p.get("rate")
        if q in BASE_QUOTES and r is not None and r > 0:
            usable.append(p)

    if len(usable) < 2:
        return None

    best: Optional[Opportunity] = None

    for buy in usable:
        buy_q = buy["id"]
        buy_rate = float(buy["rate"])
        buy_vol_primary = float(buy.get("volumePrimaryValue", 0) or 0)

        if buy_vol_primary < min_buy_volume_primary:
            continue

        for sell in usable:
            if sell is buy:
                continue

            sell_q = sell["id"]
            sell_rate = float(sell["rate"])
            sell_vol_primary = float(sell.get("volumePrimaryValue", 0) or 0)

            if sell_vol_primary < min_sell_volume_primary:
                continue

            # Convertit buy/sell vers target_quote
            cost = convert_amount(buy_rate, buy_q, target_quote, core)
            revenue = convert_amount(sell_rate, sell_q, target_quote, core)

            if cost is None or revenue is None or cost <= 0:
                continue

            # slippage / spread
            cost *= (1.0 + buy_slippage_pct / 100.0)
            revenue *= (1.0 - sell_slippage_pct / 100.0)

            profit_per_unit = revenue - cost
            profit_pct = (revenue / cost - 1.0) * 100.0

            # on garde seulement les profits positifs
            if profit_per_unit <= 0:
                continue

            buy_vol_target = volume_in_quote(buy_vol_primary, core, target_quote)
            sell_vol_target = volume_in_quote(sell_vol_primary, core, target_quote)

            opp = Opportunity(
                type_name=type_name,
                details_id=details_id,
                name=name,
                buy_quote=buy_q,
                buy_rate=buy_rate,
                sell_quote=sell_q,
                sell_rate=sell_rate,
                target_quote=target_quote,
                cost_in_target=cost,
                revenue_in_target=revenue,
                profit_per_unit=profit_per_unit,
                profit_pct=profit_pct,
                buy_volume_primary=buy_vol_primary,
                sell_volume_primary=sell_vol_primary,
                buy_volume_target=buy_vol_target,
                sell_volume_target=sell_vol_target,
            )

            if best is None:
                best = opp
            else:
                # priorité: meilleur % puis meilleur profit valeur
                if (opp.profit_pct > best.profit_pct) or (
                    opp.profit_pct == best.profit_pct and opp.profit_per_unit > best.profit_per_unit
                ):
                    best = opp

    return best
