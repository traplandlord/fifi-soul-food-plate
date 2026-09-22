# Ops simulation — Logistic flywheel demand (uncapped)

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

- **K (mid)** = **450** plates/week latent saturation  
- **r (mid)** = **0.155**  
- **t0 (mid)** = **18** (inflection week)  
- Low / high bands use K=280/650 (columns `demand_low_band` / `demand_high_band`).

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

First week latent demand exceeds the old 50 marketing line: **week 5**.

---

## Two operating modes (same demand curve)

| Mode | What happens |
|------|----------------|
| **mobile** | Never leases. Capacity = Mom (+ optional part-time help) + fryer/pack limits. Soft ceiling ~220–320/wk. |
| **location_path** | Identical demand. **Leases** when gate hits: sustained latent demand **≥ 160 plates/wk for 8 weeks** AND cumulative cash **≥ $11,700** (≈3 months rent+utils @ $3,900/mo). Then rent/utils, higher hire, higher capacity ramp. |

Lease gate week (mid path): **22**.  
Crossover week (location weekly cash net > mobile-only): **27**.

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
| Month 1 | 168.5 | $1644.15 | 168.5 | $1644.15 |
| Month 6 | 1125.8 | $12095.09 | 1308.9 | $10885.31 |
| Month 12 | 1040 | $10745.99 | 1788 | $16459.09 |

Week 52 snapshot — mobile: demand **447.7**, capacity **260.0**, fulfilled **260**, lost **252.7**.  
Week 52 snapshot — location path: mode **location**, fulfilled **448**, net cash **$4113.41**.

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
