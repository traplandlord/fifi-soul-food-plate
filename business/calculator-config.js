/* Fifi Soul Food — calculator mid defaults. Illustrative · Not financial advice. Sep 2026 */
window.FIFI_CALC = {
  disclaimer: "Illustrative model · Not financial advice · Sep 2026",
  cogs: {
    chicken: 0.59,      // RD drums 2pc
    greens: 0.85,
    sweets: 0.70,
    roll: 0.25,
    oilBreadSeason: 0.62, // 0.22+0.30+0.10
    yieldWaste: 0.69,     // bridge to brand food mid $3.70
    pack: 0.44,
    ddBonus: 0.75
  },
  get foodTotal() {
    const c = this.cogs;
    return +(c.chicken + c.greens + c.sweets + c.roll + c.oilBreadSeason + c.yieldWaste).toFixed(2);
  },
  prices: {
    pickup: 20,
    live: 20,
    doordash: 26,
    grubhub: 26,
    overnightDinner: 20,
    overnightShip: 65,
    localDinner: 20,
    localFee: 12
  },
  fees: {
    ddCommission: 0.25,
    ghCommission: 0.27,
    paymentPct: 0.025,
    drive: 9.95,
    overnightNetTarget: 4.53
  },
  labor: { momWage: 20 },
  location: { rentUtilsMo: 3900 },
  ops: {
    fullThrottle24h: true,
    weekendShare: 0.55,
    weekdayShare: 0.45,
    peakNightShareOfWeek: 0.40,
    defaultPlatesWeek: 480,
    defaultPeakNight: 192,
    defaultAdWeek: 1200,
    defaultMomHours: 35,
    defaultHelpHoursPop: 50,
    defaultHelpHoursLoc: 40
  },
  platforms: [
    { id: "pickup", name: "Pickup / Pop", priceKey: "pickup", feeType: "payment", note: "Best net after COGS" },
    { id: "live", name: "LIVE / Cash App", priceKey: "live", feeType: "none", note: "Cash — no card fee mid" },
    { id: "doordash", name: "DoorDash", priceKey: "doordash", feeType: "dd", note: "25% + bonus sweet" },
    { id: "grubhub", name: "Grubhub", priceKey: "grubhub", feeType: "gh", note: "~27% commission mid" },
    { id: "overnight", name: "Overnight ship", priceKey: "overnight", feeType: "overnight", note: "$20+$65 · ~$4.53 net mid" },
    { id: "local_delivery", name: "Local delivery", priceKey: "local", feeType: "drive", note: "$20+$12 fee · Drive ~$9.95" }
  ]
};
