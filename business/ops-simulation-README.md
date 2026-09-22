# Ops simulation — Mobile / pop-up vs fixed location

**Brand:** Fifi's Soul Food Plate  
**Date:** Sep 22, 2026 (PT)  
**Companion CSV:** `ops-simulation-location-vs-mobile.csv`  
**Not financial advice.** Illustrative mid-path model only. Verify rent, permits, insurance, and labor before any lease.

---

## Why this exists

Compare **two operating modes** with the same plate math already used elsewhere:

| Knob | Mid value | Source |
|------|-----------|--------|
| Local pickup plate | **$20** | Flyer / config / metrics |
| DoorDash menu | **$26** (+ bonus/premium vs local) | Deals / marketplace policy |
| Overnight ship charge | **$65** mid-zone (dinner still $20) | Shipping CSV |
| Local delivery fee (customer) | **$12** | SoCal policy |
| Plate COGS | **$3.70** | COGS CSV mid |
| Overnight total profit mid | **~$4.53** / order | Shipping summary |
| DoorDash commission | **25%** of menu | Marketplace mid |
| DoorDash Drive courier | **~$9.95** / drop | Drive mid CA |

---

## Scenario A — Mobile / pop-up only (no storefront rent)

**Capacity:** ~**50–120 plates/week** (model mid path uses **55 → 80 → 95 → 115** plates/wk across Month 1 / steady / Month 6 / Month 12).

**Revenue mix (mid):**

- ~50% pickup @ $20  
- ~10% live / Cash App cash @ $20  
- ~15% DoorDash @ $26 menu  
- ~10% overnight ($20 + $65)  
- ~15% local delivery ($20 + $12 fee)

**Costs called out in the CSV:**

- Food COGS $3.70 + ~$0.25 pack bags  
- DD 25% commission; Drive ~$9.95 on local drops  
- Uline ship BOM (pack/label/media/postage) sized so overnight nets ~$4.53 mid  
- Gas, permits amortized, low insurance, phone, ads  
- Payment fees ~2.5% on card/app portion  
- **Mom labor:** hours noted + valued @ **$20/hr** as opportunity cost (separate SUMMARY row)

**Fixed costs:** low — no rent line.

**Month-6 net (cash, before Mom labor value):** ~**$5,414** (~95 plates/wk × 4.33 weeks).

---

## Scenario B — Fixed location (small kitchen / stall)

**Rent + utils (mid SoCal small footprint):** **$3,500 rent + $400 utils ≈ $3,900/mo**  
Research band for food-hall stall / small private kitchen often lands roughly **$2k–$5k+/mo** base (plus utils or CAM). Model uses mid of that band — not a quote.

**Capacity:** ~**150–400 plates/week** potential (model: **120 → 180 → 250 → 320** plates/wk across Month 1 / steady / Month 6 / Month 12).

**Mix shifts:**

- More walk-up / preorder pickup  
- Higher DoorDash share (~30%)  
- Smaller overnight share (still available)  
- Local delivery continues with $12 fee  
- **Bottled drinks** attach later @ **$3.50** sell / **$0.80** COGS

**Higher fixed / labor:**

- Commercial insurance (~$250/mo)  
- Part-time help (~$1,600/mo ≈ 20 hr/wk @ $20)  
- Higher ads / phone  
- Mom hours higher (~35/wk) and valued separately

**Month-6 net (cash, before Mom labor value):** ~**$10,859** (~250 plates/wk × 4.33 weeks) — **only if volume holds**.

---

## SUMMARY rows (how to read)

In the CSV, `category = summary` (and `scenario = summary_compare`) includes:

1. **`SUMMARY_net_profit_cash`** — revenue − COGS − fees − fulfillment − opex (**before** Mom opportunity cost).  
2. **`SUMMARY_net_profit_after_mom_labor`** — same, minus Mom hours × $20.  
3. **Breakeven / lease gates:**
   - Location **cash breakeven** ≈ **~95 plates/week** at mid rent.  
   - Location **beats mobile@80** cash net around **~160 plates/week**.  
   - Business-plan Phase 4 gate (from `business-plan.md`): sustained **≥80–100 plates/week** for **8+ weeks**, positive contribution after labor, and **≥3 months** rent+deposit cash buffer from operating profit.

### When to lease (plain English)

Stay **mobile** until the pop already sells ~**80–100+ plates/week** for **8+ weeks** with cash left over.  
Only sign a stall/kitchen when you can reasonably hit **~160+ plates/week** at the fixed site (so the lease actually beats staying mobile) **and** you have **~3 months rent** sitting in the bank.  
Until then, rent is a liability, not a flex.

---

## Period definitions

| `period` | Meaning |
|----------|---------|
| `week_steady` | One mid week (mobile 80 plates / location 180 plates) |
| `month_1` | 4.33 × early ramp week |
| `month_6` | 4.33 × mid growth week |
| `month_12` | 4.33 × later scale week |
| `breakeven` / `when_to_lease` | Cross-scenario decision rows |

---

## Explicit assumptions / caveats

- Mid numbers only — no low/high Monte Carlo here.  
- No sales tax modeled as net (pass-through).  
- No build-out / TI / equipment CapEx in weekly P&L (stall assumes warm box).  
- MEHKO / commissary / interstate ship rules may force kitchen path — legal not modeled.  
- DoorDash “bonus” = premium menu ($26), not a platform promo guarantee.  
- Mom labor is **valued**, not always a cash payroll line.  
- **Not financial, legal, or tax advice.**

---

## Related files

- `fifi-comprehensive-metrics.csv` — highlight rows for this sim  
- `get-the-bag-playbook.md` · `live-sales-funnel.csv` — sales flywheel  
- `business-plan.md` §10 Phase 4 — lease gates  
- `shipping-and-growth-economics.csv` · `cogs-and-pricing.csv`
