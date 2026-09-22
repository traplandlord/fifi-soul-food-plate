/**
 * Fifi's Soul Food Plate — single place to edit business info, menu & prices.
 * Change anything here; the site + flyer.html read this on load.
 *
 * NEW knobs (Happy Hour · Plate Club · Rewards · Live Drop):
 *   happyHourEnabled, happyHourStart, happyHourEnd, spinPrice
 *   plateClubPriceMonthly, plateClubHalfOff
 *   rewardsEveryN, rewardsDiscountPct (75% off = pay 25%)
 *   tiktokLiveLabel, tiktokLiveUrl, tiktokLiveCountdownMins
 *   shipCold, shipHot, shipCopy
 *   orderByLocalTime, orderByDaysLabel, carrierPickupTime, trackingOptional, overnightCutoffCopy
 */
window.FIFI_CONFIG = {
  businessName: "Fifi's Soul Food Plate",
  tagline: "Soul Food Pop · Home-cooked dinners",
  eventName: "Soul Food Pop",
  maxPlates: 50,
  // Edit these before you go live / show Mom the real details:
  pickupLocation: "[Location]",
  eventDate: "[Date]",
  eventTime: "[Time]",
  phone: "555-014-FIFI",
  phoneDigits: "5550143434",
  email: "orders@fifissoulfood.example",
  instagram: "https://instagram.com/fifissoulfood",
  tiktok: "https://tiktok.com/@fifissoulfood",
  pickupNote:
    "Pre-orders recommended — only 50 plates. Pickup at the Soul Food Pop: see date, time & location. Text us after you send your order to confirm.",
  taxNote: "Sales tax may apply at pickup.",
  marketHours: "[Date] · [Time] — Soul Food Pop (edit in config.js)",
  locationLabel: "[Location] — Soul Food Pop pickup",

  // ——— Happy Hour (local clock; Demo toggle always works offline) ———
  happyHourEnabled: true,
  happyHourStart: "15:00", // 3:00 PM local
  happyHourEnd: "18:00", // 6:00 PM local
  spinPrice: 1.0, // simulated $1 to spin (demo — connect Square/Stripe later)

  // ——— Plate Club subscription (demo flag, no real billing) ———
  plateClubPriceMonthly: 9.99, // placeholder display price
  plateClubHalfOff: true, // members get 50% off dinner plates

  // ——— Rewards stamp card ———
  rewardsEveryN: 5, // every N full-price paid plates…
  rewardsDiscountPct: 75, // …unlock next plate at 75% off (pay $5 on $20)

  // ——— TikTok Live / overnight ship teaser ———
  tiktokLiveLabel: "Tonight · 7:00 PM PT",
  tiktokLiveUrl: "https://tiktok.com/@fifissoulfood/live",
  tiktokLiveCountdownMins: 90, // placeholder countdown from page load
  shipCold: 28, // overnight cold — insulated Uline shipper ($)
  shipHot: 35, // overnight hot — insulated Uline shipper ($)
  // ——— Overnight order window (PT / local) ———
  orderByLocalTime: "10:00", // customer order-by for next-day overnight (Mon–Thu)
  orderByDaysLabel: "Mon–Thu",
  carrierPickupTime: "14:30", // ops: pack before ~2:30 PM carrier pickup
  trackingOptional: false, // paid overnight includes tracking; local courier may skip
  overnightCutoffCopy:
    "Order by 10:00 AM PT Mon–Thu for next-day overnight (tracking included on paid ship). Local courier: tracking optional — text us.",
  shipCopy:
    "Packed hot or cold in insulated Uline shippers for next-day delivery. We pack before carrier pickup so your plate arrives ready. Order by 10:00 AM PT Mon–Thu for overnight — tracking available on paid ship.",

  // Wheel prize weights (higher = more common). Codes map to cart discounts.
  wheelPrizes: [
    { id: "try_again", label: "Try again", weight: 40, code: null },
    { id: "free_drink", label: "Free drink", weight: 30, code: "FREE_DRINK" },
    { id: "half_off", label: "50% off dinner", weight: 25, code: "HALF_OFF" },
    { id: "free_dinner", label: "FREE DINNER!", weight: 5, code: "FREE_DINNER" },
  ],

  // Trivia pool (3 shown at random / in order)
  trivia: [
    {
      q: "What's in Fifi's Fried Chicken Dinner?",
      choices: [
        "Chicken, greens, candied sweets, roll",
        "Only chicken and fries",
        "Waffle and syrup",
      ],
      answer: 0,
    },
    {
      q: "How many plates are available at Soul Food Pop?",
      choices: ["25", "50", "100"],
      answer: 1,
    },
    {
      q: "What time is Happy Hour (default)?",
      choices: ["11–2", "3–6 PM", "9–11 PM"],
      answer: 1,
    },
  ],

  menu: [
    {
      id: "plate-fried-chicken-dinner",
      name: "Fried Chicken Dinner",
      description:
        "2 pieces crispy fried chicken, collard greens, candied sweet potatoes, and a dinner roll. Home-cooked for Soul Food Pop.",
      price: 20.0,
      category: "plates",
      countsTowardPlateLimit: true,
      badge: "Soul Food Pop",
      includes: [
        "2 pieces crispy fried chicken",
        "Collard greens",
        "Candied sweet potatoes",
        "Dinner roll",
      ],
      options: {
        id: "chickenCut",
        label: "Chicken pieces",
        choices: [
          { id: "2pieces", label: "2 pieces (default)", default: true },
          { id: "drum-wings", label: "Drum + wings" },
        ],
      },
      addons: [],
    },
    {
      id: "drink-coffee",
      name: "Coffee",
      description: "Hot, bold, and ready to go.",
      price: 2.5,
      category: "drinks",
    },
    {
      id: "drink-hot-chocolate",
      name: "Hot chocolate",
      description: "Rich and comforting — a cold-day favorite.",
      price: 3.0,
      category: "drinks",
    },
    {
      id: "drink-agua-fresca",
      name: "Agua fresca",
      description: "Light, refreshing, house-made.",
      price: 3.5,
      category: "drinks",
    },
  ],
};
