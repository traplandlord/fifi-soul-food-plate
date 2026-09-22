#!/usr/bin/env python3
"""
Fifi's Soul Food Plate — Logistic / S-curve demand + social/loyalty flywheel sim.
Deterministic mid-path model. NOT financial advice. Illustrative only.
Re-run: python3 generate_flywheel_sim.py
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

OUT_DIR = Path("/workspace/fifi-soul-food")
SITE_BIZ = Path("/workspace/fifi-soul-food-site/business")

# ── Mid knobs (reuse existing CSVs; do not invent contradicting COGS) ──
COGS_FOOD = 3.70
PACK_BAG = 0.25
PACK_STALL = 0.30
DD_MENU = 26.0
DD_COMMISSION = 0.25
DD_BONUS_COGS = 0.75  # cake/cinnamon mid
PICKUP_PRICE = 20.0
LIVE_PRICE = 20.0
OVERNIGHT_DINNER = 20.0
OVERNIGHT_SHIP = 65.0
OVERNIGHT_TOTAL = 85.0
OVERNIGHT_NET = 4.53  # mid — sizes Uline BOM
ULINE_BOM_BEYOND_COGS = OVERNIGHT_TOTAL - COGS_FOOD - OVERNIGHT_NET  # ~76.77
LOCAL_DINNER = 20.0
LOCAL_FEE = 12.0
DRIVE_COST = 9.95
PAYMENT_PCT = 0.025
MOM_WAGE = 20.0
RENT_MO = 3500.0
UTILS_MO = 400.0
RENT_UTILS_WK = (RENT_MO + UTILS_MO) / 4.33
INS_MOBILE_WK = 20.0
INS_LOC_WK = 250.0 / 4.33
PERMITS_MOBILE_WK = 15.0
PERMITS_LOC_WK = 80.0 / 4.33
PHONE_MOBILE_WK = 15.0
PHONE_LOC_WK = 60.0 / 4.33
GAS_MOBILE_WK = 45.0
GAS_LOC_WK = 25.0
HIRE_LOC_WK = 1600.0 / 4.33  # ~20 hr/wk @ $20
DRINK_SELL = 3.50
DRINK_COGS = 0.80
CLUB_PRICE = 10.0  # half-off dinner
REWARD_PRICE = 5.0  # 75% off
HH_SPIN_EV = 0.56
WEEKS_PER_MONTH = 4.33
LEASE_BUFFER_TARGET = 3 * (RENT_MO + UTILS_MO)  # 3 months rent+utils
LEASE_DEMAND_GATE = 160
LEASE_STREAK_NEEDED = 8

# Logistic mid: demand_t = K / (1 + e^(-r*(t-t0)))
K_MID = 450.0  # saturation latent plates/wk
R_MID = 0.155
T0_MID = 18.0
K_LOW, R_LOW, T0_LOW = 280.0, 0.12, 20.0
K_HIGH, R_HIGH, T0_HIGH = 650.0, 0.18, 15.0

CSV_COLS = [
    "week",
    "mode",
    "demand_latent",
    "demand_low_band",
    "demand_high_band",
    "waitlist_in",
    "capacity_plates",
    "plates_fulfilled",
    "lost_demand",
    "waitlist_out",
    "followers_or_reach_proxy",
    "mom_cook_hours",
    "help_hours",
    "throughput_pph",
    "ch_pickup",
    "ch_live",
    "ch_doordash",
    "ch_overnight",
    "ch_local_delivery",
    "ch_plate_club",
    "ch_happy_hour_half",
    "ch_rewards",
    "rev_pickup",
    "rev_live",
    "rev_doordash",
    "rev_overnight",
    "rev_local_delivery",
    "rev_plate_club",
    "rev_happy_hour",
    "rev_rewards",
    "rev_drinks",
    "rev_platform_monetize",
    "revenue_total",
    "cogs_food_pack",
    "cogs_dd_bonus",
    "cogs_drinks",
    "fees_dd_commission",
    "fees_payment",
    "fulfill_drive",
    "fulfill_uline_bom",
    "opex_ads",
    "opex_gas_permits_ins_phone",
    "opex_hire_cash",
    "opex_rent_utils",
    "hh_spin_cost",
    "club_members",
    "SUMMARY_net_cash",
    "SUMMARY_net_after_mom",
    "cum_cash",
    "lease_gate_met",
    "notes",
]


def logistic(t: float, K: float, r: float, t0: float) -> float:
    return K / (1.0 + math.exp(-r * (t - t0)))


def channel_mix(plates: int, mode: str, week: int, club_share_target: float) -> dict:
    """Allocate fulfilled plates across channels. Counts are ints summing to plates."""
    if plates <= 0:
        return {k: 0 for k in (
            "pickup", "live", "doordash", "overnight", "local_delivery",
            "plate_club", "happy_hour_half", "rewards"
        )}

    # Base mix evolves with scale / mode
    maturity = min(1.0, (week - 1) / 40.0)
    if mode == "mobile":
        # early: pickup+live heavy; later more DD/delivery/overnight
        w_pickup = 0.48 - 0.10 * maturity
        w_live = 0.14 - 0.05 * maturity
        w_dd = 0.12 + 0.10 * maturity
        w_on = 0.10 + 0.02 * maturity
        w_del = 0.14 + 0.04 * maturity
    else:
        w_pickup = 0.42 - 0.05 * maturity
        w_live = 0.06 - 0.02 * maturity
        w_dd = 0.22 + 0.08 * maturity
        w_on = 0.08 - 0.02 * maturity
        w_del = 0.14 + 0.02 * maturity

    # Plate Club takes a growing slice (half-off dinners) from pickup/live pool
    club_w = min(club_share_target, 0.18)
    # Happy Hour: ~12% of weeks intense; average ~6% of plates half-off across year
    hh_w = 0.04 + 0.03 * maturity
    # Rewards: ~1/6 of remaining full-price path → model ~8% of all plates at reward price
    rew_w = 0.08

    # Normalize base five to (1 - club - hh - rew)
    base_sum = w_pickup + w_live + w_dd + w_on + w_del
    remain = max(0.01, 1.0 - club_w - hh_w - rew_w)
    scale = remain / base_sum
    weights = {
        "pickup": w_pickup * scale,
        "live": w_live * scale,
        "doordash": w_dd * scale,
        "overnight": w_on * scale,
        "local_delivery": w_del * scale,
        "plate_club": club_w,
        "happy_hour_half": hh_w,
        "rewards": rew_w,
    }

    # Largest-remainder allocation
    raw = {k: plates * v for k, v in weights.items()}
    counts = {k: int(math.floor(v)) for k, v in raw.items()}
    rem = plates - sum(counts.values())
    frac = sorted(((raw[k] - counts[k], k) for k in raw), reverse=True)
    for i in range(rem):
        counts[frac[i % len(frac)][1]] += 1
    return counts


def mobile_capacity(week: int, help_hours: float) -> tuple[float, float, float, float]:
    """Return capacity, mom_hours, help_hours, pph."""
    maturity = min(1.0, (week - 1) / 36.0)
    # Start ~15–25 hr cookable; grows with stage (home/MEHKO / pop constraints)
    mom_hours = 15.0 + 8.0 * maturity  # 15 → 23
    # Effective plates/hour cooking+packing: ~11–14.5 mid
    pph = 11.0 + 3.0 * maturity  # 11 → 14
    solo_cap = mom_hours * pph
    help_cap = help_hours * (pph * 0.9)
    logistics = 0.86 + 0.06 * maturity  # travel/setup haircut
    cap = (solo_cap + help_cap) * logistics
    # Hard mobile ceiling: no commercial kitchen / single fryer line
    hard_ceiling = 200.0 + (60.0 if help_hours >= 8 else 0.0)  # ~200 solo / ~260 with help
    cap = min(cap, hard_ceiling)
    return cap, mom_hours, help_hours, pph


def location_capacity(week: int, lease_week: int) -> tuple[float, float, float, float]:
    """Capacity after lease; starts near mobile-with-help and ramps toward ~480."""
    weeks_open = max(0, week - lease_week)
    ramp = min(1.0, weeks_open / 14.0)
    mom_hours = 28.0 + 7.0 * ramp  # 28 → 35
    help_hours = 16.0 + 12.0 * ramp  # 16 → 28
    pph = 13.0 + 2.0 * ramp  # 13 → 15
    cap = (mom_hours + help_hours) * pph * 0.93
    # Open at ~260 (match mobile+help), ramp to 480 commercial throughput
    cap = min(cap, 260.0 + 220.0 * ramp)  # 260 → 480
    return cap, mom_hours, help_hours, pph




def ads_spend(week: int, mode: str, demand: float) -> float:
    """Ads / LIVE boost — lifts awareness (already baked into logistic; cost still counted)."""
    base = 25.0 if mode == "mobile" else 46.0
    # Scale ads gently with demand (reinvest)
    return base + min(80.0, demand * 0.12)


def simulate_mode(mode_label: str, allow_lease: bool) -> list[dict]:
    rows = []
    waitlist = 0.0
    cum_cash = 0.0
    club_members = 0.0
    help_hours_mobile = 0.0
    lease_week = None
    streak_ge_160 = 0
    followers = 800.0

    for week in range(1, 53):
        d_mid = logistic(week, K_MID, R_MID, T0_MID)
        d_low = logistic(week, K_LOW, R_LOW, T0_LOW)
        d_high = logistic(week, K_HIGH, R_HIGH, T0_HIGH)

        # Awareness proxy grows with logistic + ads feedback (directional)
        followers = 800.0 + 24000.0 * (d_mid / K_MID) + week * 40.0

        # Lease gate check (before capacity for this week)
        if allow_lease and lease_week is None:
            if d_mid >= LEASE_DEMAND_GATE:
                streak_ge_160 += 1
            else:
                streak_ge_160 = 0
            if streak_ge_160 >= LEASE_STREAK_NEEDED and cum_cash >= LEASE_BUFFER_TARGET:
                lease_week = week

        leased = allow_lease and lease_week is not None and week >= lease_week
        op_mode = "location" if leased else "mobile"

        # Hire help on mobile if demand presses capacity / cash allows
        if op_mode == "mobile":
            trial_cap, _, _, _ = mobile_capacity(week, help_hours_mobile)
            if help_hours_mobile < 12 and cum_cash >= 3500 and (d_mid > trial_cap * 0.80 or week >= 16):
                help_hours_mobile = 12.0
            cap, mom_h, help_h, pph = mobile_capacity(week, help_hours_mobile)
        else:
            cap, mom_h, help_h, pph = location_capacity(week, lease_week)

        demand_eff = d_mid + waitlist
        fulfilled = min(demand_eff, cap)
        lost = max(0.0, demand_eff - fulfilled)
        # Partial spill: 40% of lost joins next-week waitlist (capped)
        waitlist_out = min(lost * 0.40, cap * 0.25)
        waitlist_in = waitlist

        plates = int(round(fulfilled))
        # Club share target grows with members / potential
        club_share = min(0.16, club_members / max(plates, 1)) if plates else 0.0
        # Grow members: list capture 25% of payers × 8% club convert, weekly fraction
        new_members = plates * 0.25 * 0.08 * 0.35  # ~0.7% of plates → members/wk
        club_members = club_members * (1 - 0.02) + new_members  # ~8%/mo churn ≈ 2%/wk
        club_share = min(0.16, (club_members * 0.85) / max(plates, 1)) if plates else 0.0

        ch = channel_mix(plates, op_mode, week, club_share)

        # Revenues
        rev_pickup = ch["pickup"] * PICKUP_PRICE
        rev_live = ch["live"] * LIVE_PRICE
        rev_dd = ch["doordash"] * DD_MENU
        rev_on = ch["overnight"] * OVERNIGHT_TOTAL
        rev_del = ch["local_delivery"] * (LOCAL_DINNER + LOCAL_FEE)
        rev_club = ch["plate_club"] * CLUB_PRICE
        rev_hh = ch["happy_hour_half"] * 10.0  # half-off $20
        rev_rew = ch["rewards"] * REWARD_PRICE

        # Drinks attach later (week 28+ or location)
        drink_units = 0
        if week >= 28 or op_mode == "location":
            attach = 0.15 if op_mode == "mobile" else 0.22
            drink_units = int(round(plates * attach))
        rev_drinks = drink_units * DRINK_SELL

        # Platform monetization directional (~$5 / 100 viewers mid from funnel)
        live_viewers = followers * 0.08  # 8% of followership joins a LIVE some weeks
        rev_plat = (live_viewers / 100.0) * 5.0 * (0.4 + 0.6 * min(1.0, week / 40.0))
        rev_plat = round(rev_plat, 2)

        revenue = (
            rev_pickup + rev_live + rev_dd + rev_on + rev_del
            + rev_club + rev_hh + rev_rew + rev_drinks + rev_plat
        )

        # Costs
        cogs_food = plates * (COGS_FOOD + (PACK_STALL if op_mode == "location" else PACK_BAG))
        cogs_bonus = ch["doordash"] * DD_BONUS_COGS
        cogs_drinks = drink_units * DRINK_COGS
        fees_dd = ch["doordash"] * DD_MENU * DD_COMMISSION
        # Payment on non-DD, non-cash-live portion (~ live is cash; DD platform)
        card_base = revenue - rev_live - rev_dd - rev_plat
        fees_pay = max(0.0, card_base) * PAYMENT_PCT
        fulfill_drive = ch["local_delivery"] * DRIVE_COST
        fulfill_uline = ch["overnight"] * ULINE_BOM_BEYOND_COGS
        hh_spin = ch["happy_hour_half"] * HH_SPIN_EV

        ads = ads_spend(week, op_mode, d_mid)
        if op_mode == "mobile":
            opex_fixed = GAS_MOBILE_WK + PERMITS_MOBILE_WK + INS_MOBILE_WK + PHONE_MOBILE_WK
            hire_cash = help_h * MOM_WAGE  # help paid cash when hired
            rent = 0.0
        else:
            opex_fixed = GAS_LOC_WK + PERMITS_LOC_WK + INS_LOC_WK + PHONE_LOC_WK
            hire_cash = HIRE_LOC_WK
            rent = RENT_UTILS_WK

        net_cash = (
            revenue
            - cogs_food - cogs_bonus - cogs_drinks
            - fees_dd - fees_pay
            - fulfill_drive - fulfill_uline
            - ads - opex_fixed - hire_cash - rent
            - hh_spin
        )
        mom_opp = mom_h * MOM_WAGE
        net_after_mom = net_cash - mom_opp
        cum_cash += net_cash

        notes_parts = []
        if week == 1:
            notes_parts.append("Start; logistic ramp; NO 50-plate hard cap")
        if int(round(d_mid)) > 50 and int(round(logistic(week - 1, K_MID, R_MID, T0_MID))) <= 50:
            notes_parts.append("FIRST week latent demand exceeds old 50-plate marketing cap")
        if lost > 1:
            notes_parts.append(f"Capacity bind: lost≈{lost:.0f} plates (waitlist spill {waitlist_out:.0f})")
        if lease_week == week:
            notes_parts.append(
                f"LEASE GATE MET: demand≥{LEASE_DEMAND_GATE} for {LEASE_STREAK_NEEDED}wks "
                f"+ cash buffer≥${LEASE_BUFFER_TARGET:.0f}"
            )
        if op_mode == "location" and week == lease_week:
            notes_parts.append("Switched to fixed location opex/capacity")
        if drink_units and week == 28 and op_mode == "mobile":
            notes_parts.append("Bottled drinks attach begins")
        if not notes_parts:
            notes_parts.append("mid-path deterministic")

        gate_flag = 1 if (lease_week is not None and week >= lease_week) else 0
        if not allow_lease:
            gate_flag = 0

        rows.append({
            "week": week,
            "mode": op_mode if allow_lease else "mobile",
            "demand_latent": round(d_mid, 2),
            "demand_low_band": round(d_low, 2),
            "demand_high_band": round(d_high, 2),
            "waitlist_in": round(waitlist_in, 2),
            "capacity_plates": round(cap, 2),
            "plates_fulfilled": plates,
            "lost_demand": round(lost, 2),
            "waitlist_out": round(waitlist_out, 2),
            "followers_or_reach_proxy": int(round(followers)),
            "mom_cook_hours": round(mom_h, 2),
            "help_hours": round(help_h, 2),
            "throughput_pph": round(pph, 2),
            "ch_pickup": ch["pickup"],
            "ch_live": ch["live"],
            "ch_doordash": ch["doordash"],
            "ch_overnight": ch["overnight"],
            "ch_local_delivery": ch["local_delivery"],
            "ch_plate_club": ch["plate_club"],
            "ch_happy_hour_half": ch["happy_hour_half"],
            "ch_rewards": ch["rewards"],
            "rev_pickup": round(rev_pickup, 2),
            "rev_live": round(rev_live, 2),
            "rev_doordash": round(rev_dd, 2),
            "rev_overnight": round(rev_on, 2),
            "rev_local_delivery": round(rev_del, 2),
            "rev_plate_club": round(rev_club, 2),
            "rev_happy_hour": round(rev_hh, 2),
            "rev_rewards": round(rev_rew, 2),
            "rev_drinks": round(rev_drinks, 2),
            "rev_platform_monetize": rev_plat,
            "revenue_total": round(revenue, 2),
            "cogs_food_pack": round(cogs_food, 2),
            "cogs_dd_bonus": round(cogs_bonus, 2),
            "cogs_drinks": round(cogs_drinks, 2),
            "fees_dd_commission": round(fees_dd, 2),
            "fees_payment": round(fees_pay, 2),
            "fulfill_drive": round(fulfill_drive, 2),
            "fulfill_uline_bom": round(fulfill_uline, 2),
            "opex_ads": round(ads, 2),
            "opex_gas_permits_ins_phone": round(opex_fixed, 2),
            "opex_hire_cash": round(hire_cash, 2),
            "opex_rent_utils": round(rent, 2),
            "hh_spin_cost": round(hh_spin, 2),
            "club_members": round(club_members, 2),
            "SUMMARY_net_cash": round(net_cash, 2),
            "SUMMARY_net_after_mom": round(net_after_mom, 2),
            "cum_cash": round(cum_cash, 2),
            "lease_gate_met": gate_flag,
            "notes": "; ".join(notes_parts),
        })
        waitlist = waitlist_out

    return rows, lease_week


def month_aggregate(rows: list[dict], start_week: int, n_weeks: int = None) -> dict:
    """Aggregate ~4.33 weeks starting at start_week (1-indexed). Uses 4 full weeks + 0.33 of 5th."""
    # Use weeks start_week .. start_week+3 fully, plus 0.33 of week start_week+4 if exists
    idxs = list(range(start_week - 1, min(start_week - 1 + 5, len(rows))))
    if not idxs:
        return {}
    full = rows[idxs[0]:idxs[0] + 4] if len(idxs) >= 4 else rows[idxs[0]:]
    partial = rows[idxs[0] + 4] if len(idxs) >= 5 else None
    wfrac = 0.33

    def sum_key(k):
        s = sum(r[k] for r in full)
        if partial is not None and isinstance(partial.get(k), (int, float)):
            s += partial[k] * wfrac
        return s

    plates = sum_key("plates_fulfilled")
    net = sum_key("SUMMARY_net_cash")
    net_m = sum_key("SUMMARY_net_after_mom")
    demand = sum_key("demand_latent") / (4 + (wfrac if partial else 0))
    cap = sum_key("capacity_plates") / (4 + (wfrac if partial else 0))
    lost = sum_key("lost_demand")
    return {
        "plates": round(plates, 1),
        "net_cash": round(net, 2),
        "net_after_mom": round(net_m, 2),
        "avg_demand_wk": round(demand, 1),
        "avg_cap_wk": round(cap, 1),
        "lost": round(lost, 1),
        "weeks_span": f"{start_week}-{start_week + 3}",
    }


def summary_rows(mobile_rows, loc_rows, lease_week) -> list[dict]:
    """Build SUMMARY_* rows (same columns, week/mode special)."""
    out = []
    blank = {c: "" for c in CSV_COLS}

    def add_summary(label, mode, data, notes):
        r = dict(blank)
        r["week"] = label
        r["mode"] = mode
        r["plates_fulfilled"] = data.get("plates", "")
        r["demand_latent"] = data.get("avg_demand_wk", "")
        r["capacity_plates"] = data.get("avg_cap_wk", "")
        r["lost_demand"] = data.get("lost", "")
        r["SUMMARY_net_cash"] = data.get("net_cash", "")
        r["SUMMARY_net_after_mom"] = data.get("net_after_mom", "")
        r["notes"] = notes
        out.append(r)

    for label, start in [("SUMMARY_month_1", 1), ("SUMMARY_month_3", 9),
                         ("SUMMARY_month_6", 23), ("SUMMARY_month_12", 49)]:
        # month 12 = weeks 49-52 (+ partial none) — use last 4.33 from week 49
        if label == "SUMMARY_month_12":
            start = 49
        add_summary(label, "mobile", month_aggregate(mobile_rows, start),
                    f"Mobile-only path · {label} ≈4.33 wks from week {start}. Illustrative. NOT financial advice.")
        add_summary(label, "location_path", month_aggregate(loc_rows, start),
                    f"Lease-when-gated path · {label}. Illustrative. NOT financial advice.")

    # Week demand > 50
    cross50 = next((r["week"] for r in mobile_rows if r["demand_latent"] > 50), None)
    # Crossover: first week location path net_cash > mobile path net_cash (after lease)
    crossover = None
    if lease_week:
        for m, loc in zip(mobile_rows, loc_rows):
            if loc["week"] >= lease_week and loc["SUMMARY_net_cash"] > m["SUMMARY_net_cash"]:
                crossover = loc["week"]
                break

    r = dict(blank)
    r["week"] = "SUMMARY_cross_demand_gt_50"
    r["mode"] = "both"
    r["demand_latent"] = round(logistic(cross50, K_MID, R_MID, T0_MID), 2) if cross50 else ""
    r["plates_fulfilled"] = cross50 or ""
    r["notes"] = (
        f"First week latent demand > old marketing 50-cap: week {cross50}. "
        "50 was flyer scarcity, not physical limit."
    )
    out.append(r)

    r = dict(blank)
    r["week"] = "SUMMARY_lease_gate_week"
    r["mode"] = "location_path"
    r["lease_gate_met"] = 1 if lease_week else 0
    r["plates_fulfilled"] = lease_week or ""
    r["cum_cash"] = loc_rows[lease_week - 1]["cum_cash"] if lease_week else ""
    r["notes"] = (
        f"Lease week={lease_week} when demand≥{LEASE_DEMAND_GATE} for {LEASE_STREAK_NEEDED} wks "
        f"AND cum cash≥${LEASE_BUFFER_TARGET:.0f} (3 mo rent+utils). "
        + ("Gate not met in 52 weeks on mid path." if not lease_week else "")
    )
    out.append(r)

    r = dict(blank)
    r["week"] = "SUMMARY_crossover_location_beats_mobile"
    r["mode"] = "compare"
    r["plates_fulfilled"] = crossover or ""
    if crossover:
        r["SUMMARY_net_cash"] = loc_rows[crossover - 1]["SUMMARY_net_cash"]
        r["notes"] = (
            f"Week {crossover}: location-path weekly cash net first exceeds mobile-only. "
            "NOT financial advice."
        )
    else:
        r["notes"] = "No crossover within 52 weeks (lease never beats mobile weekly, or never leased)."
    out.append(r)

    r = dict(blank)
    r["week"] = "SUMMARY_saturation_K"
    r["mode"] = "mid"
    r["demand_latent"] = K_MID
    r["capacity_plates"] = round(mobile_rows[-1]["capacity_plates"], 2)
    r["plates_fulfilled"] = mobile_rows[-1]["plates_fulfilled"]
    r["notes"] = (
        f"Logistic K_mid={K_MID} plates/wk latent saturation; r={R_MID}, t0={T0_MID}. "
        f"Week-52 mobile capacity={mobile_rows[-1]['capacity_plates']}, "
        f"fulfilled={mobile_rows[-1]['plates_fulfilled']}, "
        f"lost={mobile_rows[-1]['lost_demand']}. "
        f"Low K={K_LOW} / High K={K_HIGH} bands in weekly columns."
    )
    out.append(r)

    # Peak lost-demand week
    peak_lost = max(mobile_rows, key=lambda x: x["lost_demand"])
    r = dict(blank)
    r["week"] = "SUMMARY_peak_capacity_bind_mobile"
    r["mode"] = "mobile"
    r["plates_fulfilled"] = peak_lost["week"]
    r["lost_demand"] = peak_lost["lost_demand"]
    r["capacity_plates"] = peak_lost["capacity_plates"]
    r["demand_latent"] = peak_lost["demand_latent"]
    r["notes"] = (
        f"Peak mobile capacity bind week {peak_lost['week']}: "
        f"latent={peak_lost['demand_latent']}, cap={peak_lost['capacity_plates']}, "
        f"lost={peak_lost['lost_demand']}."
    )
    out.append(r)

    return out, cross50, crossover, lease_week


def write_csv(path: Path, mobile_rows, loc_rows, summaries):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS)
        w.writeheader()
        for row in mobile_rows:
            # force mode label for clarity in long format
            row = dict(row)
            row["mode"] = "mobile"
            w.writerow(row)
        for row in loc_rows:
            row = dict(row)
            # keep actual op mode (mobile until lease, then location)
            w.writerow(row)
        for row in summaries:
            w.writerow(row)


def write_readme(path: Path, cross50, crossover, lease_week, mobile_rows, loc_rows):
    m1 = month_aggregate(mobile_rows, 1)
    m6 = month_aggregate(mobile_rows, 23)
    m12 = month_aggregate(mobile_rows, 49)
    l1 = month_aggregate(loc_rows, 1)
    l6 = month_aggregate(loc_rows, 23)
    l12 = month_aggregate(loc_rows, 49)
    w52m = mobile_rows[-1]
    w52l = loc_rows[-1]

    text = f"""# Ops simulation — Logistic flywheel demand (uncapped)

**Brand:** Fifi's Soul Food Plate / Momma Fifi Soul  
**Date:** Sep 22, 2026 (PT)  
**Companion CSV:** `ops-simulation-flywheel-demand.csv`  
**Generator:** `generate_flywheel_sim.py` (re-run anytime)  
**Not financial advice.** Illustrative mid-path model only.

---

## The phenomenon (plain English)

Demand for Soul Food Plates does **not** stop at 50. The old flyer line ("only 50 plates") is **marketing scarcity** for a single pop — useful urgency, not a physics law.

This simulation models a **logistic / S-curve** of *latent weekly demand* driven by a **social + loyalty flywheel**:

1. **Awareness** grows (TikTok followers / LIVE reach proxy).
2. **Conversion** turns viewers into paid plates (LIVE funnel mid rates).
3. **Repeat** + **referral** spillover pull the curve up the S.
4. Growth slows as it approaches a **saturation ceiling K** (addressable weekly demand for this brand/geo) — classic logistic:

```
demand_t = K / (1 + e^(-r * (t - t0)))
```

- **K (mid)** = **{K_MID:.0f}** plates/week latent saturation  
- **r (mid)** = **{R_MID}**  
- **t0 (mid)** = **{T0_MID:.0f}** (inflection week)  
- Low / high bands use K={K_LOW:.0f}/{K_HIGH:.0f} (columns `demand_low_band` / `demand_high_band`).

**Physical kitchen throughput** — not a marketing cap — limits fulfilled plates:

```
capacity ≈ (Mom cook hours + help hours) × plates_per_hour × logistics_factor
```

- Mid throughput **~11–15 plates/hour** effective when cooking + packing.  
- Mom hours start ~**15 hr/wk** and rise toward ~**25** (mobile) or ~**35** (location).  
- Hire help adds capacity when cash allows / demand presses.  
- Demand above capacity → **lost sales** + **partial waitlist** (~40% spills to next week).

---

## Why no 50-plate hard cap

| Idea | Role |
|------|------|
| Flyer "only 50 plates" | Scarcity **marketing** for one Soul Food Pop |
| This sim | **Physical capacity** + logistic demand; shows when demand > 50 and when demand > kitchen |

First week latent demand exceeds the old 50 marketing line: **week {cross50}**.

---

## Two operating modes (same demand curve)

| Mode | What happens |
|------|----------------|
| **mobile** | Never leases. Capacity = Mom (+ optional part-time help) + fryer/pack limits. Soft ceiling ~220–320/wk. |
| **location_path** | Identical demand. **Leases** when gate hits: sustained latent demand **≥ {LEASE_DEMAND_GATE} plates/wk for {LEASE_STREAK_NEEDED} weeks** AND cumulative cash **≥ ${LEASE_BUFFER_TARGET:,.0f}** (≈3 months rent+utils @ $3,900/mo). Then rent/utils, higher hire, higher capacity ramp. |

Lease gate week (mid path): **{lease_week if lease_week else "not reached in 52 weeks"}**.  
Crossover week (location weekly cash net > mobile-only): **{crossover if crossover else "none in 52 weeks"}**.

---

## Channels & levers included

All mid knobs reused from existing brand CSVs:

| Lever | Mid treatment |
|-------|----------------|
| Local pickup | $20 |
| TikTok LIVE / Cash App | $20 |
| DoorDash | $26 menu + 25% commission + ~$0.75 bonus sweet COGS |
| Overnight | $20 + $65 ship; Uline BOM sized so net ≈ **$4.53** |
| Local delivery | $20 + $12 fee; Drive ≈ **$9.95** |
| Happy Hour | ~4–7% of plates half-off ($10) + spin EV **$0.56**/HH plate |
| Plate Club | Growing members; half-off dinners @ $10 (margin dilutes carefully) |
| Rewards | ~8% of plates @ $5 (75% off loyalty tax) |
| Ads / LIVE boost | Scales lightly with demand; lifts awareness story |
| Platform monetize | Small directional $ from LIVE-viewer backend |
| Bottled drinks | Attach from week 28+ (or sooner if leased) @ $3.50 / $0.80 COGS |
| Mom labor | Hours × **$20/hr** opportunity → `SUMMARY_net_after_mom` |
| Payment | ~2.5% on card/app portion |
| Gas / permits / insurance / phone | Mobile vs location rates from ops-sim |

COGS food mid **$3.70** + pack bags (~$0.25 mobile / ~$0.30 stall).

---

## How to read the CSV

- **Long format:** weeks **1–52** for `mode=mobile`, then weeks **1–52** for `mode=mobile→location` (location_path rows keep `mobile` until lease, then `location`).  
- Primary path columns: `demand_latent`, `capacity_plates`, `plates_fulfilled`, `lost_demand`.  
- Channel counts `ch_*` and revenues `rev_*`.  
- **`SUMMARY_net_cash`** = revenue − COGS − fees − fulfillment − opex (**before** Mom opportunity).  
- **`SUMMARY_net_after_mom`** = cash net − Mom hours × $20.  
- Trailing **SUMMARY_*** rows: Month 1 / 3 / 6 / 12 rollups (≈4.33 weeks), cross-50 week, lease gate, crossover, saturation K, peak capacity bind.

### Headline mid-path rollups (illustrative)

| Period | Mobile plates (≈mo) | Mobile net cash | Location-path plates | Location-path net cash |
|--------|---------------------|-----------------|----------------------|------------------------|
| Month 1 | {m1.get('plates')} | ${m1.get('net_cash')} | {l1.get('plates')} | ${l1.get('net_cash')} |
| Month 6 | {m6.get('plates')} | ${m6.get('net_cash')} | {l6.get('plates')} | ${l6.get('net_cash')} |
| Month 12 | {m12.get('plates')} | ${m12.get('net_cash')} | {l12.get('plates')} | ${l12.get('net_cash')} |

Week 52 snapshot — mobile: demand **{w52m['demand_latent']}**, capacity **{w52m['capacity_plates']}**, fulfilled **{w52m['plates_fulfilled']}**, lost **{w52m['lost_demand']}**.  
Week 52 snapshot — location path: mode **{w52l['mode']}**, fulfilled **{w52l['plates_fulfilled']}**, net cash **${w52l['SUMMARY_net_cash']}**.

---

## Knobs you can turn (in `generate_flywheel_sim.py`)

- `K_MID`, `R_MID`, `T0_MID` — logistic shape  
- Mom hours / `pph` / help hire thresholds — capacity  
- `LEASE_DEMAND_GATE`, `LEASE_STREAK_NEEDED`, `LEASE_BUFFER_TARGET` — when to lease  
- Channel weight functions — mix by scale  
- Club convert / rewards / HH fractions — loyalty tax  

---

## Related files

- `ops-simulation-location-vs-mobile.csv` — earlier period P&L (kept; still valid for fixed period snapshots)  
- `ops-simulation-README.md` — points here for uncapped demand  
- `deals-economics.csv` · `live-sales-funnel.csv` · `cogs-and-pricing.csv` · `shipping-and-growth-economics.csv`  
- `fifi-comprehensive-metrics.csv` — highlight rows H32+  

**Illustrative only. Not financial, legal, or tax advice.**
"""
    path.write_text(text)


def append_metrics(metrics_path: Path, cross50, crossover, lease_week, mobile_rows, loc_rows):
    m6 = month_aggregate(mobile_rows, 23)
    m12 = month_aggregate(mobile_rows, 49)
    l6 = month_aggregate(loc_rows, 23)
    l12 = month_aggregate(loc_rows, 49)
    w52 = mobile_rows[-1]
    # saturation plates ~ K fulfilled when capacity allows
    sat_plates = min(K_MID, w52["capacity_plates"])

    new_rows = [
        ["highlight", "H32_flywheel_uncapped_demand_gt_50_week", "logistic mid", "week",
         cross50 or "", cross50 or "", cross50 or "", "count",
         "First week latent demand > old 50-plate marketing scarcity line. Sim uses physical capacity.",
         "calculated", "flywheel-sim 2026-09-22"],
        ["highlight", "H33_flywheel_mobile_m6_net_cash", "mobile flywheel Month-6", "USD",
         "", m6.get("net_cash", ""), "", "USD",
         f"Uncapped flywheel mobile M6≈{m6.get('plates')} plates; cash net BEFORE Mom labor. NOT financial advice.",
         "calculated", "flywheel-sim 2026-09-22"],
        ["highlight", "H34_flywheel_mobile_m12_net_cash", "mobile flywheel Month-12", "USD",
         "", m12.get("net_cash", ""), "", "USD",
         f"Uncapped flywheel mobile M12≈{m12.get('plates')} plates; cash net BEFORE Mom labor.",
         "calculated", "flywheel-sim 2026-09-22"],
        ["highlight", "H35_flywheel_location_m6_net_cash", "location_path Month-6", "USD",
         "", l6.get("net_cash", ""), "", "USD",
         f"Lease-when-gated path M6≈{l6.get('plates')} plates; cash net BEFORE Mom labor.",
         "calculated", "flywheel-sim 2026-09-22"],
        ["highlight", "H36_flywheel_location_m12_net_cash", "location_path Month-12", "USD",
         "", l12.get("net_cash", ""), "", "USD",
         f"Lease-when-gated path M12≈{l12.get('plates')} plates; cash net BEFORE Mom labor.",
         "calculated", "flywheel-sim 2026-09-22"],
        ["highlight", "H37_flywheel_crossover_week", "location beats mobile weekly", "week",
         crossover or "", crossover or "", crossover or "", "count",
         "First week location-path SUMMARY_net_cash > mobile-only (after lease).",
         "calculated", "flywheel-sim 2026-09-22"],
        ["highlight", "H38_flywheel_saturation_K", "logistic mid", "plates_per_week",
         K_LOW, K_MID, K_HIGH, "count",
         f"Latent demand saturation K; week-52 mobile cap={w52['capacity_plates']} fulfilled={w52['plates_fulfilled']}.",
         "estimate", "flywheel-sim 2026-09-22"],
        ["highlight", "H39_flywheel_lease_gate_week", "Phase4 gate", "week",
         lease_week or "", lease_week or "", lease_week or "", "count",
         f"Demand≥{LEASE_DEMAND_GATE}/wk × {LEASE_STREAK_NEEDED} wks AND cash≥3mo rent (${LEASE_BUFFER_TARGET:.0f}).",
         "calculated", "flywheel-sim 2026-09-22"],
        ["highlight", "H40_flywheel_m12_plates_wk_mobile", "mobile week52-ish", "plates_per_week",
         "", w52["plates_fulfilled"], "", "count",
         f"Week-52 mobile fulfilled; latent={w52['demand_latent']} cap={w52['capacity_plates']} lost={w52['lost_demand']}.",
         "calculated", "flywheel-sim 2026-09-22"],
        ["FLYWHEEL_SIM", "logistic_K_mid", "demand", "plates_per_week", K_LOW, K_MID, K_HIGH, "count",
         f"demand_t=K/(1+e^(-r*(t-t0))); r_mid={R_MID} t0={T0_MID}", "estimate", "2026-09-22"],
        ["FLYWHEEL_SIM", "no_hard_50_cap", "policy", "flag", 1, 1, 1, "flag",
         "50-plate flyer line = marketing scarcity; sim limited by kitchen throughput only", "policy", "2026-09-22"],
        ["FLYWHEEL_SIM", "throughput_pph_mid", "kitchen", "plates_per_hour", 11, 13.5, 15, "count",
         "Effective cook+pack plates/hour", "estimate", "2026-09-22"],
        ["FLYWHEEL_SIM", "sat_plates_wk_approx", "mobile", "plates_per_week", "", round(sat_plates, 1), "", "count",
         "Approx plates/wk near saturation given mobile capacity", "calculated", "2026-09-22"],
    ]

    existing = metrics_path.read_text()
    # Avoid duplicate append on re-run
    if "H32_flywheel_uncapped_demand_gt_50_week" in existing:
        lines = existing.strip().splitlines()
        kept = [ln for ln in lines if "H32_flywheel_" not in ln and "H33_flywheel_" not in ln
                and "H34_flywheel_" not in ln and "H35_flywheel_" not in ln
                and "H36_flywheel_" not in ln and "H37_flywheel_" not in ln
                and "H38_flywheel_" not in ln and "H39_flywheel_" not in ln
                and "H40_flywheel_" not in ln and ",FLYWHEEL_SIM," not in ln
                and not ln.startswith("FLYWHEEL_SIM,")]
        # also filter highlight flywheel by section
        kept2 = []
        for ln in kept:
            if ln.startswith("highlight,H3") and "_flywheel_" in ln:
                continue
            if ln.startswith("FLYWHEEL_SIM,"):
                continue
            kept2.append(ln)
        metrics_path.write_text("\n".join(kept2) + "\n")

    with metrics_path.open("a", newline="") as f:
        w = csv.writer(f)
        for row in new_rows:
            w.writerow(row)


def main():
    mobile_rows, _ = simulate_mode("mobile", allow_lease=False)
    loc_rows, lease_week = simulate_mode("location_path", allow_lease=True)
    summaries, cross50, crossover, lease_week = summary_rows(mobile_rows, loc_rows, lease_week)

    csv_path = OUT_DIR / "ops-simulation-flywheel-demand.csv"
    readme_path = OUT_DIR / "ops-simulation-flywheel-README.md"
    write_csv(csv_path, mobile_rows, loc_rows, summaries)
    write_readme(readme_path, cross50, crossover, lease_week, mobile_rows, loc_rows)

    # Mirror to site business/
    SITE_BIZ.mkdir(parents=True, exist_ok=True)
    write_csv(SITE_BIZ / "ops-simulation-flywheel-demand.csv", mobile_rows, loc_rows, summaries)
    write_readme(SITE_BIZ / "ops-simulation-flywheel-README.md", cross50, crossover, lease_week, mobile_rows, loc_rows)

    # Metrics both copies
    for mp in [OUT_DIR / "fifi-comprehensive-metrics.csv", SITE_BIZ / "fifi-comprehensive-metrics.csv"]:
        if mp.exists():
            append_metrics(mp, cross50, crossover, lease_week, mobile_rows, loc_rows)

    # Print headlines for operator
    m6 = month_aggregate(mobile_rows, 23)
    m12 = month_aggregate(mobile_rows, 49)
    l6 = month_aggregate(loc_rows, 23)
    l12 = month_aggregate(loc_rows, 49)
    print("=== FLYWHEEL SIM HEADLINES (illustrative, NOT financial advice) ===")
    print(f"K_mid={K_MID} r={R_MID} t0={T0_MID}")
    print(f"Week demand>50: {cross50}")
    print(f"Lease gate week: {lease_week}")
    print(f"Crossover week: {crossover}")
    print(f"Mobile M6: plates={m6['plates']} net_cash=${m6['net_cash']}")
    print(f"Mobile M12: plates={m12['plates']} net_cash=${m12['net_cash']}")
    print(f"Location M6: plates={l6['plates']} net_cash=${l6['net_cash']}")
    print(f"Location M12: plates={l12['plates']} net_cash=${l12['net_cash']}")
    print(f"Week52 mobile: demand={mobile_rows[-1]['demand_latent']} cap={mobile_rows[-1]['capacity_plates']} "
          f"fulfilled={mobile_rows[-1]['plates_fulfilled']} lost={mobile_rows[-1]['lost_demand']}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {readme_path}")


if __name__ == "__main__":
    main()
