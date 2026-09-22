# Fifi's Soul Food Plate — Ordering Website

Static ordering site for **Fifi's Soul Food Plate**. No backend: cart, checkout, and confirmation run in the browser. Customers send orders via prefilled **SMS**, **email**, or **copy to clipboard**.

**Happy Hour · Plate Club · Rewards** — fun / loyalty / live-commerce on a static site (payments simulated; connect Square/Stripe later).

## The Journey

**Pop-up → Ship nationwide → Plate Club → Our kitchen** — on-site roadmap (`#journey`) and footer teaser. Every order fuels the path to a real location.

## Show Mom today

1. Open **`flyer.html`** (phone-width flyer) — badge: *Happy Hour · Plate Club · Rewards*.
2. Open **`index.html`** ($20 Fried Chicken Dinner, 50-plate limit).
3. Tap **Demo Happy Hour** (works offline) → **Pay $1 to spin** or play **Trivia**.
4. Toggle **I'm a Plate Club member (demo)** for half-off plates; check Rewards stamps.
5. Checkout: **Pickup** | **Overnight cold** | **Overnight hot** (insulated Uline shippers).
6. Edit **`config.js`** for phone, location, date/time, Happy Hour hours, ship prices.

Also see `/workspace/fifi-soul-food/SHOW-MOM.md` if present.

**GET THE BAG:** see [`business/get-the-bag-playbook.md`](business/get-the-bag-playbook.md) + [`business/live-sales-funnel.csv`](business/live-sales-funnel.csv). Overnight line on Live Drop / checkout comes from `overnightCutoffCopy` in `config.js`.

## Preview locally

```bash
cd fifi-soul-food-site
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080). Opening `index.html` as a file also works (clipboard may need a local server).

## Edit prices & knobs (`config.js`)

| Field | Controls |
|--------|----------|
| `businessName`, `tagline` | Branding |
| `phone`, `phoneDigits` | Display phone + `sms:` target |
| `email` | Contact + `mailto:` |
| `instagram`, `tiktok` | Social links |
| `pickupNote`, `taxNote`, `marketHours`, `locationLabel` | Order / Contact copy |
| `eventName`, `maxPlates`, `pickupLocation`, `eventDate`, `eventTime` | Soul Food Pop + 50-plate cap |
| `menu[]` | Items, prices, includes, options |
| **Happy Hour** | |
| `happyHourEnabled` | Master switch |
| `happyHourStart` / `happyHourEnd` | Local window (e.g. `"15:00"`–`"18:00"`) |
| `spinPrice` | Simulated $1 spin fee (cart line) |
| `wheelPrizes[]` | Weighted prizes + codes (`HALF_OFF`, `FREE_DRINK`, `FREE_DINNER`) |
| `trivia[]` | Questions for free spins |
| **Plate Club** | |
| `plateClubPriceMonthly` | Placeholder $/mo |
| `plateClubHalfOff` | Members: 50% off dinner plates |
| **Rewards** | |
| `rewardsEveryN` | Full-price plates per cycle (default 5) |
| `rewardsDiscountPct` | Next plate off % (75 → pay $5 on $20) |
| **Live / ship** | |
| `tiktokLiveLabel`, `tiktokLiveUrl`, `tiktokLiveCountdownMins` | Tonight's Live Drop |
| `shipCold`, `shipHot` | Overnight cold / hot add-ons ($) |
| `shipCopy` | Confident Uline packaging copy |
| `orderByLocalTime` | Customer order-by time for next-day overnight (default `"10:00"` PT) |
| `orderByDaysLabel` | Days window label (default `"Mon–Thu"`) |
| `carrierPickupTime` | Ops pack-before time (default `"14:30"`) |
| `trackingOptional` | `false` = tracking on paid overnight; local courier may be optional |
| `overnightCutoffCopy` | Customer-facing cutoff line on Live Drop + checkout |

### Demo Happy Hour

Uses the real local window **or** the **Demo Happy Hour** toggle (`localStorage`). Spin confirm is fake: *Demo — connect Square/Stripe later*.

### Discount codes

| Code | Effect |
|------|--------|
| `HALF_OFF` | 50% off one dinner |
| `FREE_DRINK` | One drink free |
| `FREE_DINNER` | One dinner free |

Plate priority: free dinner → rewards 75% off → Plate Club / `HALF_OFF`.

## Publish to GitHub Pages

1. Push this folder as the repo root (or `/docs`).
2. **Settings → Pages** → **Deploy from a branch**.
3. Branch **main**, folder **/ (root)**.
4. Site: `https://<user>.github.io/<repo>/`.

## What's included

- `index.html` — Home, Menu, How it works, Happy Hour, Plate Club / Rewards, Live Drop, Journey, Order, Contact
- `styles.css` — warm soul-food brand + neon/gold Happy Hour accents
- `config.js` — all business + feature knobs
- `app.js` — cart, discounts, wheel/trivia, SMS / mailto / copy
- `flyer.html` — phone flyer + feature badge
- `assets/` — SVG icons

### localStorage keys

| Key | Purpose |
|-----|---------|
| `fifi_cart_v1` | Cart |
| `fifi_last_order_v1` | Last order |
| `fifi_plates_reserved_v1` | Soft plate cap |
| `fifi_discounts_v1` | Prize codes |
| `fifi_plate_club_v1` | Demo member flag |
| `fifi_rewards_stamps_v1` | Stamp count |
| `fifi_rewards_ready_v1` | Next plate 75% off ready |
| `fifi_demo_hh_v1` | Demo Happy Hour toggle |

## Placeholder contact (change before live)

- Phone: `555-014-FIFI` · SMS: `5550143434`
- Email: `orders@fifissoulfood.example`
