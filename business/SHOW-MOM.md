# Show Mom — quick start

1. **Open the flyer** — `/workspace/fifi-soul-food-site/flyer.html` (phone-width, full-screen friendly). Or from the site folder: `python3 -m http.server 8080` → http://localhost:8080/flyer.html
2. **Open the ordering site** — same folder, `index.html` (or http://localhost:8080/) — browse menu, add to cart, checkout, text/email/copy the order.
3. **What’s in the CSV** — `cogs-and-pricing.csv` has ingredient cost research; we appended candied sweet potatoes, dinner roll, and the **$20** flyer sell price for Soul Food Pop.
4. **The plate is $20** — Fried Chicken Dinner: 2 pieces chicken, collard greens, candied sweet potatoes, dinner roll. Only **50 plates**.
5. **Edit before go-live** — in `fifi-soul-food-site/config.js` set real `phone` / `phoneDigits`, `email`, `pickupLocation`, `eventDate`, and `eventTime` (they show as `[Location]` / `[Date]` / `[Time]` until you change them).
