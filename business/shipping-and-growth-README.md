# Fifi's Soul Food — Shipping & Growth Economics Guide

**Brand:** Fifi's Soul Food Plate / Soul Food Pop  
**Companion files:** `shipping-and-growth-economics.csv`, `deals-economics.csv`, `cogs-and-pricing.csv`  
**Research date:** Sep 22, 2026 (America/Los_Angeles)  
**Website:** kept separate — these files are ops/finance planning only.

---

## Framing (read first)

**Overnight shipping is a primary, viable channel** when packed in proper Uline-style insulated shippers with heat packs (hot path) or gel/cold packs (cold path). Food does not spoil overnight when:

1. Plate is packed at correct temp (hot ≥135°F into preheated vessel, or fully chilled/frozen for cold meal-prep).
2. Media (heat packs or frozen gels) are activated/conditioned and placed correctly (gels on top).
3. Shipper is sealed and handed to the carrier **before cutoff** for next-day / Priority Express commitment.
4. Customer is told reheat / fridge instructions on arrival.

Operational discipline is **process**, not a reason to kill the channel. Permit/interstate steps are a **checklist** before taking paid national orders — not a model-killer.

---

## Headlines (Traplord Vee)

| Metric | Number |
|--------|--------|
| **Recommended customer ship charge (1 plate, overnight, mid-zone)** | **$65** (band $59–$75; foam/hot often $69–$75) |
| Dinner menu price (unchanged) | **$20** |
| Local pickup contribution (mid COGS ~$3.70) | **$16.30** (81.5% margin) |
| Fully loaded mid-zone liner cold + $65 ship | **~$4.53** total profit on $85 paid |
| Safe $1 spin EV (house edge) | **+$0.44** per spin (EV cost ~$0.56) |
| Plate Club (50% off) margin | **$6.30**/plate (63%) |
| Rewards 5+1 @ 75% off | **12.5%** loyalty cost vs full revenue; avg sell **$17.50** |
| Insulated inventory payback | **~$120** starter → **~8** local plates or **~10** ship orders |

**Default policy:** customer always pays overnight as a separate line. Do not bury overnight cost inside the $20 dinner.

---

## CSV columns (`shipping-and-growth-economics.csv`)

Exact headers:

`category,item,variant,unit,pack_price_usd,unit_cost_usd,weight_lb,dims_in,ship_zone_example,carrier_service,ship_rate_low_usd,ship_rate_mid_usd,ship_rate_high_usd,packaging_cost_usd,cold_or_hot_media_usd,total_fulfill_cost_usd,menu_price_usd,customer_ship_charge_usd,gross_profit_usd,gross_margin_pct,notes,confidence,source_or_date`

### Category filter cheat-sheet

| category | What you’ll find |
|----------|------------------|
| `bom` | Uline foam kits, thermal liners, gels, heat packs, labor, food COGS |
| `carrier_rate` | USPS PME / UPS NDA / FedEx Priority sample LA-origin rates + DIM note |
| `fulfill_1plate_cold` | 1-plate cold liner & foam × near/mid/far |
| `fulfill_1plate_hot` | 1-plate hot foam + heat packs / gel heat-sink |
| `fulfill_2plate` | 2-dinner ship economics |
| `fulfill_4meal` | 4-meal prep box (best ship unit economics) |
| `pricing_rule` | Free-ship thresholds, break-even charge, **headline $65** |
| `happy_hour` / `subscription` / `rewards` / `tiktok_live` | Growth mechanics |
| `summary` | Stats rollup |
| `checklist` | Permit, dry ice, spin counsel flags |

`deals-economics.csv` mirrors growth math with headers:  
`category,mechanic,customer_pays_usd,discount_or_prize,probability_or_frequency,expected_cost_usd,expected_revenue_usd,expected_margin_usd,notes,confidence`

---

## Full BOM — 1 plate overnight (viable)

### Cold path (national meal-prep standard)

| Line | Mid $ | Source |
|------|-------|--------|
| Food + inner tray (dinner COGS) | 3.70 | cogs rollup |
| Thermal liner + small box **or** Uline foam kit | 4.25 liner / ~12.30 foam | Uline S-16497 / S-11356 |
| 2× 32 oz gel packs | 3.34 | Uline S-14293 ($15/9) |
| Labor 10 min @ $20/hr | 3.33 | ops estimate |
| Overnight label mid-zone | ~65.85 | USPS PME 5 lb Z4 retail Jul 2026 |
| **Total fulfill (liner)** | **~$80.47** | |
| Customer ship charge | **$65** | covers pack+label with thin buffer |
| Menu | **$20** | food margin intact |

### Hot path (Uline insulated + heat)

| Line | Mid $ | Notes |
|------|-------|--------|
| Food + inner tray | 3.70 | pack hot |
| Uline foam kit + tray | ~12.30 | preheated vessel |
| 2× instant heat packs (UniHeat-style) | ~4.50 | estimate; or Uline gels as heat sinks |
| Labor | 3.33 | seal before cutoff |
| Overnight label mid | ~66 | same carriers |
| **Customer ship** | **$65–$75** | use **$69–$75** if foam+heat |

**Process (not skepticism):** probe → pack → activate media → seal → label → carrier pickup same day.

---

## Carrier rate snapshot (origin ZIP 90012 / 90210)

| Service | ~2–5 lb near | mid | far | Dated |
|---------|--------------|-----|-----|-------|
| USPS Priority Mail Express retail | $36–38 | ~$49–66 | ~$72–102 | EasyPost / Notice 123; Jul 12 2026 slice |
| UPS Next Day Air list | ~$50+ | ~$99 | ~$166+ | 2026 UPS rate preview; +res ~$7 + fuel |
| FedEx Priority Overnight | ~$49 (5 lb Z2) | higher | higher | 2026 guides; +fuel/residential |

**DIM weight:** USPS divisor **139** (Jul 12 2026). Oversized foam can bill like a heavy package — **right-size** or prefer liner+small box for single plates. Commercial/account rates beat retail.

**Dry ice:** optional for deep freeze; prefer gels. If used: UN1845, vented pack, declare to UPS/FedEx; USPS often unsuitable. Not legal advice.

---

## Happy Hour — safe prize table (house edge)

**$1 spin** expected prize cost ≈ **$0.56** → expected margin **+$0.44** (44% house edge).

| Prize | Prob | Cost basis |
|-------|------|------------|
| Nothing | 50% | $0 |
| Free bite / roll | 25% | COGS $0.30 |
| Free drink | 15% | COGS $0.45 |
| $5 off next plate | 8% | ×70% redeem |
| 50% off dinner | 1.5% | ×80% redeem |
| Free dinner | 0.5% | COGS $3.50 |

**FLAG:** paid $1 spin may touch sweepstakes/gambling rules. Safer launch: **free spin with plate purchase**, or **trivia → promo code**. Get counsel. Not legal advice. Wheel is “optimal” during the happy-hour window for engagement; trivia is lower risk.

---

## Subscription & Rewards

- **Plate Club:** half-off → customer pays **$10**; contribution **$6.30** at mid COGS — still healthy. Churn placeholder **8%/mo**.
- **Rewards:** buy 5 full-price → 6th at **75% off ($5)**. Over 6 plates: **$105** revenue vs **$120** full = **12.5%** loyalty cost; margin still ~**79%**.

---

## TikTok Live

Limited drops + optional tip jar. Conversion assumption **2–5%** of viewers (placeholder). Call ship cutoffs on stream. 50-plate Soul Food Pop on live ≈ **$1,000** revenue / **~$185** COGS if sold out local.

---

## Checklist flags (clear path — don’t kill the channel)

1. **CA MEHKO / cottage:** often **no mail-order** for MEHKO; cottage ≠ fried chicken. For interstate PHF, plan **licensed commercial kitchen / PFR** path. Verify with county EH.
2. **Happy hour spin:** counsel if pay-to-win; prefer free-with-purchase or trivia.
3. **Dry ice:** labeling / carrier bans — gels preferred.

---

## Sources (cite / date)

- Uline S-11356, S-13392 foam kits; S-14293 / S-18253 cold packs; Cool Shield liners — fetched **2026-09-22**
- EasyPost “USPS Overnight Shipping Cost and 2026 Priority Mail Express Rates” — **Aug 3, 2026** (rates as of Jul 12, 2026)
- UPS 2026 retail rate preview PDF; FedEx overnight 2026 guides (Shippo / Clickpost)
- UPS / FedEx dry ice / coolants pages; ShippingLabel perishable guide 2026
- CA MEHKO summaries (county FAQs / Vibekitchen) — **2026** — checklist only

Rows marked `estimate` or `ESTIMATE` in notes are modeled, not carrier quotes for a specific ZIP pair. Always price live labels before launch.
