# Product-drop demand spike + marketplace flywheel (Jordan/iPhone-style launch)

**Brand:** Fifi's Soul Food Plate / Momma Fifi Soul  
**Date:** Sep 22, 2026 (PT)  
**CSV:** `ops-simulation-flywheel-demand.csv` · **Generator:** `generate_flywheel_sim.py`  
**Not financial advice.** Illustrative mid-path week-for-week simulator.

---

## How to use (the simulator)

**Open the CSV and scroll week 1 → week 52. That IS the simulator.**

- `mode=mobile` rows = weeks 1–52 (never leases)  
- Then `location_path` weeks 1–52 (leases when gate hits)  
- Trailing `SUMMARY_*` = Month 1/3/6/12, week-1 drop, ads 1–4, lease, crossover, BOM  

Each week: demand bands, capacity, fulfilled, lost, weekday/weekend plates, **peak_night_orders**, DD + GH counts, channels, **itemized COGS**, revenues, fees, ads, opex, nets.

---

## Phenomenon (not the old timid S-curve)

Jordan shoe / iPhone-style **day-one drop**: front-loaded ads, marketplace volume from night one.

1. Weeks 1–4 spike into **200–600+ plates/week** mid band  
2. **Peak nights:** DD + GH (+ LIVE) — hundreds of orders/night when ads hit  
3. Marketplace **~45–65%** day one (`ch_doordash`, `ch_grubhub`; DD 25%, GH ~27%)  
4. Post-drop: hype decays; habit/loyalty logistic holds a high floor  
5. Kitchen throughput binds — hire hard for the drop; lost sales when demand > capacity  
6. Flyer **50 plates** = marketing scarcity, not this sim's ceiling  

### Week-1 mid

| | |
|--|--|
| Latent mid (low–high) | **480.0** (220.0–720.0) |
| Fulfilled | **480** |
| Peak night | **192** (cap ~210.0) |
| DD / GH | **179** / **94** (DD+GH=273) |
| Ads W1 / W1–4 | **$1200.0** / **$3100** → 1488 plates |

First capacity bind: none early.

---

## Itemized COGS (chicken, greens, supplies)

| Line | $/plate | Source |
|------|---------|--------|
| Chicken 2pc | **$0.59** | RD drums 0.60lb × $0.99 |
| Oil/breading/seasoning | **$0.62** | $0.22+$0.30+$0.10 |
| Collard greens | **$0.85** | greens mid |
| Candied sweet potatoes | **$0.7** | sides mid |
| Dinner roll | **$0.25** | sides mid |
| Yield/waste bridge | **$0.69** | ASSUMPTION → brand food **$3.70** |
| **Food total** | **$3.7** | metrics/ops mid |
| Pack supplies | **$0.44** | packaging mid |
| DD/GH bonus sweet | **$0.75** | cake/cinnamon |

Weekly columns scale these by `plates_fulfilled`.

---

## 7-day ops · weekend-weighted

`weekday_plates` ≈45% · `weekend_plates` ≈55% · `peak_night_orders` ≈28% of week on biggest night.

## Modes

- **mobile** — drop hire ~50 help hrs; hundreds/night capacity during launch  
- **location_path** — lease when demand ≥160/wk × 8 weeks AND cash ≥ $11,700  

Lease week: **8**. Crossover: **None**.

## Rollups (illustrative · NOT financial advice)

| Period | Mobile plates | Mobile net | Loc plates | Loc net |
|--------|---------------|------------|------------|---------|
| M1 | 1570.8 | $12572.59 | 1570.8 | $12572.59 |
| M6 | 1421.9 | $15717.88 | 1421.9 | $7145.1 |
| M12 | 1509 | $16667.43 | 1509 | $8735.52 |

Also: pickup $20, LIVE $20, overnight $20+$65 (~$4.53 net), local $20+$12 + Drive $9.95, Happy Hour, Plate Club, rewards, drinks later, Mom @$20/hr.

**Illustrative only. Not financial, legal, or tax advice.**
