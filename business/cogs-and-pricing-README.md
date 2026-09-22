# Fifi's Soul Food — COGS & Pricing CSV Guide

Companion to `cogs-and-pricing.csv` (research date: Sep 22, 2026).  
Open the CSV in Excel or Google Sheets to filter by **category** and plan buys, plate cost, and sell prices. This file is separate from the website and `business-plan.md`.

## What each column means

| Column | Plain English |
|--------|----------------|
| **category** | Bucket: `chicken`, `greens`, `cornbread`, `seasoning`, `packaging`, `capital`, `summary`, `pricing`, `scenario`, `addon`. |
| **item** | What you buy or sell (e.g. chicken drums, wet wipe, farmers market price). |
| **variant_or_source** | Brand, store, or path (USDA FOB, Restaurant Depot, Walmart, Jiffy, Uline, etc.). |
| **unit** | How the item is measured (lb, each, plate, bunch, can). |
| **pack_size** | Case/bag size when you buy in bulk (e.g. 40 lb case, 150 ct). |
| **pack_price_usd** | Dollars for that whole pack/case. |
| **unit_cost_usd** | Dollars per unit (per lb or per piece) after dividing the pack. |
| **qty_per_plate** | How much of that unit goes on one plate. |
| **cost_per_plate_low_usd** | Optimistic (cheapest realistic) cost on one plate. |
| **cost_per_plate_mid_usd** | Planning / default cost on one plate. |
| **cost_per_plate_high_usd** | Conservative (expensive path) cost on one plate. |
| **suggested_sell_price_usd** | Recommended sell price when this row is a price or scenario. |
| **sell_price_low_usd** / **sell_price_high_usd** | Low–high sell band for that channel. |
| **margin_at_mid_cogs_pct** | Gross margin % if you sell at suggested price and COGS is mid: `(sell − mid_cogs) / sell × 100`. |
| **channel_or_scenario** | Where it applies: depot path, Walmart path, soft launch, market, events, breakeven, etc. |
| **notes** | Extra context, yields, warnings (e.g. 3× food cost floors are too low for market). |
| **confidence** | `sourced` = from a price list/USDA; `estimate` = judgment band; `calculated` = math from other rows. |
| **source_or_date** | Where the number came from and when (Sep 2026 research). |

## How to use it day-to-day

1. Filter **category = summary** for the plate planning band: **$2.10 / $2.90 / $4.40** variable COGS.  
2. Prefer **depot_path** chicken (~$0.99/lb drums) over retail wings/Perdue.  
3. Start selling at **$15** (farmers market / recommended); soft launch car **$12–14**; events **$15–18**.  
4. At $15 and mid $2.90 COGS, contribution is **$12.10**/plate → roughly **5 / 9 / 13 / 17** plates/day to cover **$50 / $100 / $150 / $200** fixed.  
5. Treat brick comps ($18–25) and 3× floors ($6.75 / $8.10) as reference only — not launch targets.

**confidence legend:** sourced | estimate | calculated
