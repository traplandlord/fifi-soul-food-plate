# Powerhouse Stats — Fifi's Soul Food Plate

**File:** `powerhouse-stats.csv`  
**Master (all highlights + detail):** `fifi-comprehensive-metrics.csv`  
**Brand / owner context:** Traplandlord / Traplord Vee · Fifi's Soul Food Plate  
**Draft:** Sep 22, 2026 (America/Los_Angeles)  
**Status:** Planning analytics — mix of sourced, estimate, and calculated. Not legal, tax, or financial advice.

Open **`fifi-comprehensive-metrics.csv` first** — highlight rows (`section=highlight`) sit at the top for Mom / Traplord one-glance numbers. `powerhouse-stats.csv` is the same detailed engine without the highlight block.

---

## Column schema (exact)

| Column | Meaning |
|--------|---------|
| `section` | Topic bucket (or `highlight` in master) |
| `metric` | What is measured |
| `channel_or_partner` | Pop, TikTok, DoorDash, Uline, etc. |
| `unit` | plates, USD, pct, flag… |
| `value_low` / `value_mid` / `value_high` | Range |
| `currency_or_pct` | USD, pct, count, flag… |
| `notes` | How to use the number |
| `confidence` | `sourced` \| `estimate` \| `calculated` |
| `source_or_date` | Citation or calc note |

---

## Sections

### 1) SALES
Local **$20** Soul Food Pop dinner, **50-plate sellout = $1,000**, contribution at mid COGS **~$3.70 → $16.30/plate**, weekly targets Phase 1–4, break-even plates at sample daily fixed costs.

### 2) SOCIAL_MEDIA
TikTok / IG / FB organic reach assumptions; paid **CPM/CPC** rough 2025–2026 bands; live conversion **2–5%**; **CPA vs $16.30** headroom; content frequency; hashtag/promo budget placeholders. Kill spend if CPA creeps above ~$12.

### 3) SHIPPING
Overnight mid customer charge **$65** (band $59–75); pack+label fulfill costs; profit after ship (**~$4.53** mid); starter kit & payback plates. Full BOM lives in `shipping-and-growth-economics.csv`.

### 4) COGS_PROFIT
Low/mid/high plate COGS; margin at **$20** and Plate Club **$10**; rewards 6-plate cycle profit. Detail lines: `cogs-and-pricing.csv`.

### 5) ULINE_SUPPLIES
Foam shippers, gel/heat packs, tape/labels — unit costs, starter kit (~**$175**), reorder points.

### 6) BUSINESS_CREDIT
Partners that often offer trade credit / Net-30 (Uline Invoice Me, Webstaurant/Credit Key, RD membership notes, later Sysco/US Foods, Office Depot, Square Capital / Amex Blue — marked research estimates). Prerequisites high-level: **EIN, business account, trade refs** — not legal advice. Net-30 float on a **50-plate week** (~$150–350).

### 7) MARKETPLACES
DoorDash Marketplace **15/25/30%**, Drive flat **~$6.99–10.99** (CA often ~$9.95), Storefront 0% + processing; Grubhub marketing + delivery bands; Uber Eats **20/25/30%**; Uber Direct from ~**$7.99**; Instacart note (meal kits rarely; grocery supply side); Toast / Square Online; farmers markets / ghost kitchens / commissaries LA. Each includes **fee impact on a $20 plate** at mid COGS.

### 8) LOCAL_DELIVERY (private courier / mandatory fees / Uber·Lyft)
- Private same-day (Roadie / bike-car courier) fee bands  
- **Mandatory customer delivery fee** — recommended flat **$12** SoCal (tiers by miles)  
- Outsourced labor / Drive / Direct cost per drop  
- UberX/Lyft passenger-as-courier cost vs Connect / Direct / Drive  
- Break-even: local delivery+fee ≫ overnight for in-radius; flat courier beats **25%** marketplace when ticket ≳ **~$40**  
- **ToS flag:** passenger rideshare often restricts commercial food — prefer **DoorDash Drive / Uber Direct / licensed courier** (not legal advice)

### 9) SUMMARY_DASHBOARD
Best net $ after fees: **local cash > local delivery with mandatory fee > overnight ship > marketplace @ ~25%**. Avoid absorbing courier fees without a customer fee or price bump.

### 10) DEALS / ROADMAP (also in master)
Happy Hour EV, trivia cost, Phase 1–4 win conditions. Offer math detail: `deals-economics.csv`. Roadmap narrative: `business-plan.md` §10.

---

## Headline numbers (memorize)

| Pillar | Mid number |
|--------|------------|
| 50-plate sellout revenue | **$1,000** |
| Local contrib @ $20 / COGS $3.70 | **$16.30** |
| DoorDash 25% on $20 → contrib | **$11.30** (−$5 vs local) |
| Net-30 float / 50-plate week | **~$220** mid |
| Social CPA target vs margin | **~$8 CPA** vs **$16.30** |
| Ship profit mid + $65 freight | **~$4.53** |
| Mandatory local delivery fee | **$12** |
| Drive CA flat | **~$9.95** |

---

## Related files (do not delete)

- `cogs-and-pricing.csv`
- `shipping-and-growth-economics.csv`
- `deals-economics.csv`
- `business-plan.md` (§11 points here)
- `fifi-comprehensive-metrics.csv` — **master for Mom / Traplord**

Site mirror: `/workspace/fifi-soul-food-site/business/`
