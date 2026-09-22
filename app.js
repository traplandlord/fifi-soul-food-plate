/**
 * Fifi's Soul Food Plate — cart, checkout, Happy Hour, Plate Club, Rewards, ship
 * Soft client-side 50-plate limit for Soul Food Pop (localStorage).
 * Payments are simulated — Demo note for Square/Stripe later.
 */
(function () {
  "use strict";

  const CFG = window.FIFI_CONFIG;
  if (!CFG) {
    console.error("config.js missing — load config.js before app.js");
    return;
  }

  const STORAGE_CART = "fifi_cart_v1";
  const STORAGE_ORDER = "fifi_last_order_v1";
  const STORAGE_PLATES = "fifi_plates_reserved_v1";
  const STORAGE_DISCOUNTS = "fifi_discounts_v1";
  const STORAGE_CLUB = "fifi_plate_club_v1";
  const STORAGE_STAMPS = "fifi_rewards_stamps_v1";
  const STORAGE_REWARD_READY = "fifi_rewards_ready_v1";
  const STORAGE_DEMO_HH = "fifi_demo_hh_v1";

  const SPIN_ITEM_ID = "addon-hh-spin";

  /** @type {Array<{uid:string,itemId:string,name:string,unitPrice:number,qty:number,countsTowardPlateLimit?:boolean,optionLabel?:string,addons?:Array<{id:string,name:string,price:number}>,isSpinFee?:boolean}>} */
  let cart = [];
  let lastOrder = null;
  let platesReserved = 0;
  /** @type {string[]} */
  let discountCodes = [];
  let plateClubMember = false;
  let rewardStamps = 0;
  let rewardReady = false;
  let demoHappyHour = false;
  let spinUnlocked = false;
  let spinning = false;
  let triviaIndex = 0;
  let triviaCorrect = false;
  let triviaDone = false;
  let wheelRotation = 0;

  const MAX_PLATES = CFG.maxPlates || 50;
  const REWARDS_N = CFG.rewardsEveryN || 5;
  const REWARDS_PCT = CFG.rewardsDiscountPct || 75;

  // ——— Utils ———
  function money(n) {
    return "$" + Number(n).toFixed(2);
  }

  function uid() {
    return "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  function orderNumber() {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    const stamp =
      String(d.getFullYear()).slice(2) +
      pad(d.getMonth() + 1) +
      pad(d.getDate()) +
      "-" +
      pad(d.getHours()) +
      pad(d.getMinutes());
    const rand = Math.floor(100 + Math.random() * 900);
    return "FIFI-" + stamp + "-" + rand;
  }

  function lineTotal(line) {
    const addonSum = (line.addons || []).reduce((s, a) => s + a.price, 0);
    return (line.unitPrice + addonSum) * line.qty;
  }

  function isPlateItem(itemOrId) {
    const item = typeof itemOrId === "string" ? findItem(itemOrId) : itemOrId;
    if (!item) return false;
    return item.category === "plates" || item.countsTowardPlateLimit === true;
  }

  function isDrinkItem(itemOrId) {
    const item = typeof itemOrId === "string" ? findItem(itemOrId) : itemOrId;
    return item && item.category === "drinks";
  }

  function platesInCart() {
    return cart.reduce((s, l) => {
      if (l.countsTowardPlateLimit || isPlateItem(l.itemId)) return s + l.qty;
      return s;
    }, 0);
  }

  function platesLeft() {
    return Math.max(0, MAX_PLATES - platesReserved - platesInCart());
  }

  function platesLeftAfterReserve() {
    return Math.max(0, MAX_PLATES - platesReserved);
  }

  function lsGet(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      if (raw == null) return fallback;
      return JSON.parse(raw);
    } catch (_) {
      return fallback;
    }
  }

  function lsSet(key, val) {
    try {
      localStorage.setItem(key, JSON.stringify(val));
    } catch (_) {}
  }

  function saveCart() {
    lsSet(STORAGE_CART, cart);
  }

  function loadCart() {
    const raw = lsGet(STORAGE_CART, []);
    cart = Array.isArray(raw) ? raw : [];
  }

  function savePlatesReserved() {
    try {
      localStorage.setItem(STORAGE_PLATES, String(platesReserved));
    } catch (_) {}
  }

  function loadPlatesReserved() {
    try {
      const raw = localStorage.getItem(STORAGE_PLATES);
      platesReserved = Math.max(0, parseInt(raw, 10) || 0);
      if (platesReserved > MAX_PLATES) platesReserved = MAX_PLATES;
    } catch (_) {
      platesReserved = 0;
    }
  }

  function saveLastOrder(order) {
    lastOrder = order;
    lsSet(STORAGE_ORDER, order);
  }

  function loadLastOrder() {
    lastOrder = lsGet(STORAGE_ORDER, null);
  }

  function loadLoyaltyState() {
    discountCodes = lsGet(STORAGE_DISCOUNTS, []) || [];
    if (!Array.isArray(discountCodes)) discountCodes = [];
    plateClubMember = !!lsGet(STORAGE_CLUB, false);
    rewardStamps = Math.max(0, parseInt(lsGet(STORAGE_STAMPS, 0), 10) || 0);
    rewardReady = !!lsGet(STORAGE_REWARD_READY, false);
    demoHappyHour = !!lsGet(STORAGE_DEMO_HH, false);
  }

  function saveDiscounts() {
    lsSet(STORAGE_DISCOUNTS, discountCodes);
  }

  function addDiscountCode(code) {
    if (!code) return;
    if (!discountCodes.includes(code)) {
      discountCodes.push(code);
      saveDiscounts();
    }
  }

  function removeDiscountCode(code) {
    discountCodes = discountCodes.filter((c) => c !== code);
    saveDiscounts();
  }

  function showToast(msg) {
    const el = document.getElementById("toast");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => el.classList.remove("show"), 2800);
  }

  function findItem(id) {
    return (CFG.menu || []).find((m) => m.id === id);
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  // ——— Pricing / discounts ———
  /**
   * Compute cart breakdown with loyalty + prize codes.
   * Priority on plates: FREE_DINNER > reward 75% off > Plate Club / HALF_OFF
   * FREE_DRINK zeros one drink line (cheapest first unused).
   */
  function computeTotals() {
    let plateDiscountTotal = 0;
    let drinkDiscountTotal = 0;
    let spinFees = 0;
    let rawSub = 0;
    let freeDinnerLeft = discountCodes.includes("FREE_DINNER") ? 1 : 0;
    let halfOffLeft = discountCodes.includes("HALF_OFF") ? 1 : 0;
    let freeDrinkLeft = discountCodes.includes("FREE_DRINK") ? 1 : 0;
    let reward75Left = rewardReady ? 1 : 0;
    const notes = [];
    const lines = [];

    // Sort drinks cheapest for free drink apply
    const drinkLines = cart
      .filter((l) => isDrinkItem(l.itemId) && !l.isSpinFee)
      .slice()
      .sort((a, b) => a.unitPrice - b.unitPrice);

    const freeDrinkUid = freeDrinkLeft && drinkLines.length ? drinkLines[0].uid : null;

    cart.forEach((line) => {
      const base = lineTotal(line);
      rawSub += base;
      let disc = 0;
      let tag = "";

      if (line.isSpinFee || line.itemId === SPIN_ITEM_ID) {
        spinFees += base;
        lines.push({ line, charge: base, disc: 0, tag: "spin" });
        return;
      }

      if (isPlateItem(line.itemId)) {
        // Apply per unit with priority
        let unit = line.unitPrice;
        const addonSum = (line.addons || []).reduce((s, a) => s + a.price, 0);
        let chargeUnits = 0;
        for (let i = 0; i < line.qty; i++) {
          let u = unit + addonSum;
          if (freeDinnerLeft > 0) {
            disc += u;
            freeDinnerLeft--;
            tag = "FREE_DINNER";
            u = 0;
          } else if (reward75Left > 0) {
            const off = u * (REWARDS_PCT / 100);
            disc += off;
            reward75Left--;
            tag = "REWARDS_75";
            u = u - off;
          } else if (plateClubMember && CFG.plateClubHalfOff !== false) {
            disc += u * 0.5;
            tag = tag || "PLATE_CLUB";
            u = u * 0.5;
          } else if (halfOffLeft > 0) {
            disc += u * 0.5;
            halfOffLeft--;
            tag = "HALF_OFF";
            u = u * 0.5;
          }
          chargeUnits += u;
        }
        plateDiscountTotal += disc;
        lines.push({ line, charge: chargeUnits, disc, tag });
        return;
      }

      if (isDrinkItem(line.itemId) && freeDrinkUid === line.uid && freeDrinkLeft > 0) {
        // free one unit of this drink
        const unit = line.unitPrice;
        const addonSum = (line.addons || []).reduce((s, a) => s + a.price, 0);
        const freeAmt = unit + addonSum;
        disc = freeAmt;
        drinkDiscountTotal += disc;
        freeDrinkLeft--;
        lines.push({
          line,
          charge: base - disc,
          disc,
          tag: "FREE_DRINK",
        });
        return;
      }

      lines.push({ line, charge: base, disc: 0, tag: "" });
    });

    const discountTotal = plateDiscountTotal + drinkDiscountTotal;
    const subtotal = Math.max(0, rawSub - discountTotal);

    // Fulfillment ship add-on
    const fulfill = getFulfillment();
    let shipAdd = 0;
    let shipLabel = "";
    if (fulfill === "overnight-cold") {
      shipAdd = Number(CFG.shipCold) || 0;
      shipLabel = "Overnight cold (Uline)";
    } else if (fulfill === "overnight-hot") {
      shipAdd = Number(CFG.shipHot) || 0;
      shipLabel = "Overnight hot (Uline)";
    }

    if (discountCodes.includes("FREE_DINNER")) notes.push("Free dinner code");
    if (discountCodes.includes("HALF_OFF")) notes.push("50% off dinner code");
    if (discountCodes.includes("FREE_DRINK")) notes.push("Free drink code");
    if (plateClubMember) notes.push("Plate Club half-off");
    if (rewardReady) notes.push("Rewards 75% off next plate");

    return {
      rawSub,
      discountTotal,
      subtotal,
      shipAdd,
      shipLabel,
      total: subtotal + shipAdd,
      lines,
      notes,
    };
  }

  function cartSubtotal() {
    return computeTotals().total;
  }

  function cartQty() {
    return cart.reduce((s, l) => s + l.qty, 0);
  }

  function getFulfillment() {
    const el = document.querySelector('input[name="fulfillment"]:checked');
    return el ? el.value : "pickup";
  }

  // ——— Happy Hour window ———
  function parseHHTime(str) {
    const [h, m] = String(str || "15:00").split(":").map((x) => parseInt(x, 10) || 0);
    return h * 60 + m;
  }

  function isHappyHourActive() {
    if (demoHappyHour) return true;
    if (CFG.happyHourEnabled === false) return false;
    const now = new Date();
    const mins = now.getHours() * 60 + now.getMinutes();
    const start = parseHHTime(CFG.happyHourStart);
    const end = parseHHTime(CFG.happyHourEnd);
    if (start <= end) return mins >= start && mins < end;
    // overnight window
    return mins >= start || mins < end;
  }

  function formatHHLabel() {
    const s = CFG.happyHourStart || "15:00";
    const e = CFG.happyHourEnd || "18:00";
    function pretty(t) {
      const [h, m] = t.split(":").map(Number);
      const am = h < 12;
      const h12 = ((h + 11) % 12) + 1;
      return h12 + (m ? ":" + String(m).padStart(2, "0") : "") + (am ? " AM" : " PM");
    }
    return pretty(s) + "–" + pretty(e);
  }

  function updateHappyHourUI() {
    const active = isHappyHourActive();
    const banner = document.getElementById("hh-banner");
    if (banner) banner.hidden = !active;

    const pill = document.getElementById("hh-status-pill");
    if (pill) {
      pill.textContent = active
        ? demoHappyHour
          ? "Demo ON"
          : "Happy Hour ON"
        : "Off hours";
      pill.classList.toggle("on", active);
    }

    document.body.classList.toggle("hh-active", active);

    ["hh-demo-toggle", "hh-demo-btn"].forEach((id) => {
      const btn = document.getElementById(id);
      if (btn) {
        btn.classList.toggle("active", demoHappyHour);
        btn.setAttribute("aria-pressed", String(demoHappyHour));
        btn.textContent = demoHappyHour ? "Demo ON ✓" : "Demo Happy Hour";
      }
    });

    const hoursLabel = document.getElementById("hh-hours-label");
    if (hoursLabel) hoursLabel.textContent = formatHHLabel();

    // Games available whenever demo OR real window — soft lock with message
    const payBtn = document.getElementById("btn-pay-spin");
    const spinBtn = document.getElementById("btn-spin");
    if (payBtn) {
      payBtn.disabled = !active || spinUnlocked;
      payBtn.textContent = spinUnlocked
        ? "Spin unlocked"
        : "Pay $" + Number(CFG.spinPrice || 1).toFixed(0) + " to spin";
    }
    if (spinBtn) spinBtn.disabled = !active || !spinUnlocked || spinning;

    renderActiveCodes();
  }

  function toggleDemoHH() {
    demoHappyHour = !demoHappyHour;
    lsSet(STORAGE_DEMO_HH, demoHappyHour);
    updateHappyHourUI();
    showToast(demoHappyHour ? "Demo Happy Hour ON" : "Demo Happy Hour off");
  }

  // ——— Wheel ———
  function getPrizes() {
    return CFG.wheelPrizes || [
      { id: "try_again", label: "Try again", weight: 40, code: null },
      { id: "free_drink", label: "Free drink", weight: 30, code: "FREE_DRINK" },
      { id: "half_off", label: "50% off dinner", weight: 25, code: "HALF_OFF" },
      { id: "free_dinner", label: "FREE DINNER!", weight: 5, code: "FREE_DINNER" },
    ];
  }

  function pickWeightedPrize() {
    const prizes = getPrizes();
    const total = prizes.reduce((s, p) => s + (p.weight || 1), 0);
    let r = Math.random() * total;
    for (const p of prizes) {
      r -= p.weight || 1;
      if (r <= 0) return p;
    }
    return prizes[prizes.length - 1];
  }

  function drawWheel() {
    const canvas = document.getElementById("prize-wheel");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const prizes = getPrizes();
    const n = prizes.length;
    const size = canvas.width;
    const cx = size / 2;
    const cy = size / 2;
    const r = size / 2 - 4;
    const colors = ["#3c2415", "#c4783a", "#d4a017", "#5c3a21", "#a05a28", "#e8c547"];

    ctx.clearRect(0, 0, size, size);
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate((wheelRotation * Math.PI) / 180);

    const slice = (2 * Math.PI) / n;
    for (let i = 0; i < n; i++) {
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, r, i * slice - Math.PI / 2, (i + 1) * slice - Math.PI / 2);
      ctx.closePath();
      ctx.fillStyle = colors[i % colors.length];
      ctx.fill();
      ctx.strokeStyle = "#faf6f0";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.save();
      ctx.rotate(i * slice + slice / 2 - Math.PI / 2);
      ctx.textAlign = "center";
      ctx.fillStyle = i % 2 === 0 ? "#f5e6d3" : "#3c2415";
      ctx.font = "bold 11px system-ui, sans-serif";
      const label = prizes[i].label;
      const words = label.split(" ");
      ctx.fillText(words[0], r * 0.62, words.length > 1 ? -4 : 4);
      if (words.length > 1) ctx.fillText(words.slice(1).join(" "), r * 0.62, 10);
      ctx.restore();
    }

    // hub
    ctx.beginPath();
    ctx.arc(0, 0, 22, 0, Math.PI * 2);
    ctx.fillStyle = "#faf6f0";
    ctx.fill();
    ctx.strokeStyle = "#d4a017";
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.fillStyle = "#3c2415";
    ctx.font = "bold 10px system-ui";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("SPIN", 0, 0);

    ctx.restore();

    // outer neon ring
    ctx.beginPath();
    ctx.arc(cx, cy, r + 2, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(232, 197, 71, 0.85)";
    ctx.lineWidth = 4;
    ctx.stroke();
  }

  function renderPrizeList() {
    const el = document.getElementById("wheel-prize-list");
    if (!el) return;
    el.innerHTML =
      "<strong>Prizes:</strong> " +
      getPrizes()
        .map((p) => escapeHtml(p.label))
        .join(" · ");
  }

  function unlockSpin(fromTrivia) {
    spinUnlocked = true;
    if (!fromTrivia) {
      // Add $1 spin fee line if not present
      const price = Number(CFG.spinPrice) || 1;
      const existing = cart.find((l) => l.isSpinFee || l.itemId === SPIN_ITEM_ID);
      if (!existing) {
        cart.push({
          uid: uid(),
          itemId: SPIN_ITEM_ID,
          name: "Happy Hour Spin",
          unitPrice: price,
          qty: 1,
          countsTowardPlateLimit: false,
          isSpinFee: true,
          addons: [],
        });
        saveCart();
        updateCartUI();
      }
      showToast("Demo pay confirmed — spin unlocked ($1 in cart)");
    } else {
      showToast("Trivia win — free spin unlocked!");
    }
    updateHappyHourUI();
  }

  function payToSpin() {
    if (!isHappyHourActive()) {
      showToast("Happy Hour is off — try Demo Happy Hour");
      return;
    }
    // Fake confirm
    const ok = window.confirm(
      "Demo payment: charge $" +
        Number(CFG.spinPrice || 1).toFixed(2) +
        " to spin?\n\n(Demo — connect Square/Stripe later)"
    );
    if (!ok) return;
    unlockSpin(false);
  }

  function spinWheel() {
    if (!spinUnlocked || spinning || !isHappyHourActive()) return;
    spinning = true;
    updateHappyHourUI();
    const resultEl = document.getElementById("wheel-result");
    if (resultEl) resultEl.textContent = "Spinning…";

    const prize = pickWeightedPrize();
    const prizes = getPrizes();
    const idx = prizes.findIndex((p) => p.id === prize.id);
    const n = prizes.length;
    const slice = 360 / n;
    // Pointer at top; wheel rotates clockwise in our draw. Landing: center of slice under pointer.
    const targetCenter = 360 - (idx * slice + slice / 2);
    const extra = 360 * (4 + Math.floor(Math.random() * 3));
    const start = wheelRotation % 360;
    const end = extra + targetCenter;
    const duration = 4200;
    const t0 = performance.now();

    function easeOut(t) {
      return 1 - Math.pow(1 - t, 3);
    }

    function frame(now) {
      const t = Math.min(1, (now - t0) / duration);
      wheelRotation = start + (end - start) * easeOut(t);
      drawWheel();
      if (t < 1) {
        requestAnimationFrame(frame);
      } else {
        spinning = false;
        spinUnlocked = false;
        applyPrize(prize);
        updateHappyHourUI();
      }
    }
    requestAnimationFrame(frame);
  }

  function applyPrize(prize) {
    const resultEl = document.getElementById("wheel-result");
    if (!prize.code) {
      if (resultEl) resultEl.textContent = "✨ " + prize.label + " — spin again next time!";
      showToast(prize.label);
      return;
    }
    addDiscountCode(prize.code);
    if (resultEl) {
      resultEl.innerHTML =
        "🎉 You won <strong>" +
        escapeHtml(prize.label) +
        "</strong> — code <code>" +
        escapeHtml(prize.code) +
        "</code> applied!";
    }
    showToast("Won: " + prize.label);
    updateCartUI();
    renderActiveCodes();
  }

  function renderActiveCodes() {
    const el = document.getElementById("active-codes");
    const perks = document.getElementById("cart-perks");
    const html =
      discountCodes.length || plateClubMember || rewardReady
        ? `<div class="codes-row">
            ${discountCodes
              .map(
                (c) =>
                  `<span class="code-chip">${escapeHtml(c)} <button type="button" data-rm-code="${escapeAttr(c)}" aria-label="Remove ${escapeAttr(c)}">×</button></span>`
              )
              .join("")}
            ${plateClubMember ? '<span class="code-chip club">PLATE CLUB</span>' : ""}
            ${rewardReady ? '<span class="code-chip reward">75% OFF READY</span>' : ""}
          </div>`
        : "";
    if (el) {
      el.innerHTML = html || '<p class="form-hint">No prize codes yet — spin or play trivia.</p>';
      el.querySelectorAll("[data-rm-code]").forEach((b) =>
        b.addEventListener("click", () => {
          removeDiscountCode(b.dataset.rmCode);
          renderActiveCodes();
          updateCartUI();
        })
      );
    }
    if (perks) {
      perks.innerHTML = html;
      perks.querySelectorAll("[data-rm-code]").forEach((b) =>
        b.addEventListener("click", () => {
          removeDiscountCode(b.dataset.rmCode);
          renderActiveCodes();
          updateCartUI();
        })
      );
    }
  }

  // ——— Trivia ———
  function triviaQuestions() {
    return (CFG.trivia || []).slice(0, 3);
  }

  function renderTrivia() {
    const qs = triviaQuestions();
    const progress = document.getElementById("trivia-progress");
    const qEl = document.getElementById("trivia-q");
    const choices = document.getElementById("trivia-choices");
    const feedback = document.getElementById("trivia-feedback");
    const nextBtn = document.getElementById("trivia-next");
    const freeBtn = document.getElementById("trivia-free-spin");

    if (!qEl || !choices) return;

    if (triviaDone || triviaIndex >= qs.length) {
      if (progress) progress.textContent = "Round complete";
      qEl.textContent = triviaCorrect
        ? "You got one right — claim a free prize spin!"
        : "Nice try — come back next Happy Hour!";
      choices.innerHTML = "";
      if (feedback) feedback.textContent = "";
      if (nextBtn) nextBtn.hidden = true;
      if (freeBtn) {
        freeBtn.hidden = !triviaCorrect || !isHappyHourActive();
      }
      return;
    }

    const q = qs[triviaIndex];
    if (progress) progress.textContent = "Question " + (triviaIndex + 1) + " of " + qs.length;
    qEl.textContent = q.q;
    if (feedback) feedback.textContent = "";
    if (nextBtn) nextBtn.hidden = true;
    if (freeBtn) freeBtn.hidden = true;

    choices.innerHTML = q.choices
      .map(
        (c, i) =>
          `<button type="button" class="trivia-choice" data-choice="${i}">${escapeHtml(c)}</button>`
      )
      .join("");

    choices.querySelectorAll("[data-choice]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const pick = parseInt(btn.dataset.choice, 10);
        const correct = pick === q.answer;
        choices.querySelectorAll(".trivia-choice").forEach((b) => {
          b.disabled = true;
          if (parseInt(b.dataset.choice, 10) === q.answer) b.classList.add("correct");
        });
        if (correct) {
          btn.classList.add("correct");
          triviaCorrect = true;
          if (feedback) feedback.textContent = "Correct! 🎉";
          triviaDone = true;
          renderTrivia();
        } else {
          btn.classList.add("wrong");
          if (feedback)
            feedback.textContent = "Not quite — keep that soul-food energy. Next question!";
          if (nextBtn) {
            nextBtn.hidden = false;
            nextBtn.onclick = () => {
              triviaIndex++;
              if (triviaIndex >= qs.length) triviaDone = true;
              renderTrivia();
            };
          }
        }
      });
    });
  }

  function setupTabs() {
    const tabWheel = document.getElementById("tab-wheel");
    const tabTrivia = document.getElementById("tab-trivia");
    const panelWheel = document.getElementById("panel-wheel");
    const panelTrivia = document.getElementById("panel-trivia");
    if (!tabWheel || !tabTrivia) return;

    function activate(which) {
      const wheel = which === "wheel";
      tabWheel.classList.toggle("active", wheel);
      tabTrivia.classList.toggle("active", !wheel);
      tabWheel.setAttribute("aria-selected", String(wheel));
      tabTrivia.setAttribute("aria-selected", String(!wheel));
      panelWheel.classList.toggle("active", wheel);
      panelTrivia.classList.toggle("active", !wheel);
      panelWheel.hidden = !wheel;
      panelTrivia.hidden = wheel;
      if (!wheel) renderTrivia();
    }

    tabWheel.addEventListener("click", () => activate("wheel"));
    tabTrivia.addEventListener("click", () => activate("trivia"));
  }

  // ——— Plate Club / Rewards UI ———
  function updateClubUI() {
    const toggle = document.getElementById("plate-club-toggle");
    const note = document.getElementById("club-active-note");
    const price = document.getElementById("club-price-label");
    if (price) price.textContent = money(CFG.plateClubPriceMonthly || 9.99);
    if (toggle) toggle.checked = plateClubMember;
    if (note) note.hidden = !plateClubMember;
  }

  function updateRewardsUI() {
    const row = document.getElementById("stamps-row");
    const progress = document.getElementById("stamp-progress");
    const unlock = document.getElementById("rewards-unlock");
    const n = REWARDS_N;
    const stamps = Math.min(rewardStamps, n);
    if (row) {
      row.innerHTML = Array.from({ length: n }, (_, i) => {
        const filled = i < stamps;
        return `<span class="stamp${filled ? " filled" : ""}" aria-hidden="true">${filled ? "🍗" : "○"}</span>`;
      }).join("");
    }
    if (progress) {
      progress.textContent = rewardReady
        ? "Reward ready — 75% off your next plate!"
        : stamps + " / " + n + " toward 75% off plate";
    }
    if (unlock) unlock.hidden = !rewardReady;
  }

  // ——— Live countdown ———
  function setupLiveDrop() {
    const label = document.getElementById("live-time-label");
    const cta = document.getElementById("live-cta");
    const countdown = document.getElementById("live-countdown");
    const shipTeaser = document.getElementById("ship-copy-teaser");
    const coldP = document.getElementById("ship-cold-price");
    const hotP = document.getElementById("ship-hot-price");
    const optCold = document.getElementById("opt-ship-cold");
    const optHot = document.getElementById("opt-ship-hot");
    const shipHint = document.getElementById("ship-hint");

    if (label) label.textContent = CFG.tiktokLiveLabel || "Tonight";
    if (cta) {
      cta.href = CFG.tiktokLiveUrl || CFG.tiktok || "#";
      cta.textContent = "Watch on TikTok · " + (CFG.tiktokLiveLabel || "Live");
    }
    if (shipTeaser) {
      shipTeaser.textContent =
        CFG.shipCopy ||
        "Packed hot or cold in insulated Uline shippers for next-day delivery.";
    }
    if (coldP) coldP.textContent = "Cold " + money(CFG.shipCold || 28);
    if (hotP) hotP.textContent = "Hot " + money(CFG.shipHot || 35);
    if (optCold)
      optCold.textContent = "+" + money(CFG.shipCold || 28) + " · Uline insulated";
    if (optHot) optHot.textContent = "+" + money(CFG.shipHot || 35) + " · Uline insulated";
    if (shipHint) {
      shipHint.textContent =
        CFG.shipCopy ||
        "Packed hot or cold in insulated Uline shippers for next-day delivery.";
    }

    const mins = Number(CFG.tiktokLiveCountdownMins) || 90;
    const end = Date.now() + mins * 60 * 1000;

    function tick() {
      if (!countdown) return;
      const left = Math.max(0, end - Date.now());
      const h = Math.floor(left / 3600000);
      const m = Math.floor((left % 3600000) / 60000);
      const s = Math.floor((left % 60000) / 1000);
      const pad = (n) => String(n).padStart(2, "0");
      countdown.textContent = pad(h) + ":" + pad(m) + ":" + pad(s);
      if (left <= 0) countdown.textContent = "Starting soon";
    }
    tick();
    setInterval(tick, 1000);

    document.querySelectorAll('input[name="fulfillment"]').forEach((r) => {
      r.addEventListener("change", () => {
        const v = getFulfillment();
        if (shipHint) shipHint.hidden = v === "pickup";
        updateCartUI();
      });
    });
  }

  // ——— Plate limit UI ———
  function updatePlatesUI() {
    const left = platesLeft();
    const remainingPool = platesLeftAfterReserve();
    const banner = document.getElementById("limited-banner");
    const bannerLeft = document.getElementById("banner-left");
    const bannerEvent = document.getElementById("banner-event");
    if (bannerEvent) bannerEvent.textContent = CFG.eventName || "Soul Food Pop";

    let label;
    if (remainingPool <= 0 && platesInCart() === 0) {
      label = "Sold out — 0 plates left";
    } else if (left <= 0) {
      label = "Cart holds the last plates";
    } else {
      label = "Only " + left + " plate" + (left === 1 ? "" : "s") + " left";
    }
    if (bannerLeft) bannerLeft.textContent = label;
    if (banner) banner.classList.toggle("sold-out", remainingPool <= 0);

    const orderLeft = document.getElementById("order-plates-left");
    if (orderLeft) {
      const chipClass =
        left <= 0 ? "plates-left-chip gone" : left <= 10 ? "plates-left-chip low" : "plates-left-chip";
      orderLeft.innerHTML =
        '<span class="' +
        chipClass +
        '">' +
        (remainingPool <= 0 && platesInCart() === 0
          ? "Sold out"
          : "Only " + left + " of " + MAX_PLATES + " left") +
        "</span>";
    }

    document.querySelectorAll("[data-add]").forEach((btn) => {
      const item = findItem(btn.dataset.add);
      if (!item || !isPlateItem(item)) return;
      const sold = platesLeft() <= 0;
      btn.disabled = sold;
      btn.textContent = sold ? (remainingPool <= 0 ? "Sold out" : "Limit in cart") : "Add to cart";
    });
  }

  // ——— Brand / contact fill ———
  function applyBrand() {
    const set = (id, text) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    };
    set("brand-name", CFG.businessName);
    set("brand-tag", CFG.tagline);
    set("hero-title", CFG.businessName);
    set("hero-tagline", CFG.tagline);
    set("footer-name", CFG.businessName);
    set("footer-tagline", CFG.tagline);
    set("footer-year", String(new Date().getFullYear()));
    set("pickup-hint", CFG.pickupNote);
    set("contact-pickup", CFG.pickupNote);
    set(
      "contact-location",
      (CFG.eventName ? CFG.eventName + " · " : "") + (CFG.pickupLocation || CFG.locationLabel || "")
    );
    set(
      "contact-hours",
      [CFG.eventDate, CFG.eventTime].filter(Boolean).join(" · ") || CFG.marketHours
    );
    set("contact-tax", CFG.taxNote);
    set("drawer-tax-note", CFG.taxNote);
    set("confirm-tax-note", CFG.taxNote);

    const kicker = document.getElementById("hero-kicker");
    if (kicker) {
      kicker.textContent =
        (CFG.eventName || "Soul Food Pop") + " · Black-owned · Home-cooked";
    }

    const badge = document.getElementById("hero-badge");
    if (badge) {
      const plate = CFG.menu.find((m) => m.category === "plates");
      badge.textContent = plate ? money(plate.price) : "$20";
    }

    const meta = document.getElementById("hero-event-meta");
    if (meta) {
      meta.innerHTML =
        "<span><strong>Pickup:</strong> " +
        escapeHtml(CFG.pickupLocation || "[Location]") +
        "</span>" +
        "<span><strong>Date:</strong> " +
        escapeHtml(CFG.eventDate || "[Date]") +
        "</span>" +
        "<span><strong>Time:</strong> " +
        escapeHtml(CFG.eventTime || "[Time]") +
        "</span>";
    }

    const phoneA = document.getElementById("contact-phone");
    if (phoneA) {
      phoneA.textContent = CFG.phone;
      phoneA.href = "tel:" + CFG.phoneDigits;
    }
    const emailA = document.getElementById("contact-email");
    if (emailA) {
      emailA.textContent = CFG.email;
      emailA.href = "mailto:" + CFG.email;
    }
    const ig = document.getElementById("link-instagram");
    if (ig) ig.href = CFG.instagram;
    const tt = document.getElementById("link-tiktok");
    if (tt) tt.href = CFG.tiktok;

    const marketNote = document.getElementById("market-note");
    if (marketNote && !marketNote.value) {
      marketNote.placeholder =
        (CFG.eventName || "Soul Food Pop") +
        " — " +
        (CFG.pickupLocation || "[Location]");
    }

    document.title = CFG.businessName + " — " + CFG.tagline;
    updatePlatesUI();
  }

  // ——— Menu render ———
  function iconFor(item) {
    if (item.category === "drinks") return "assets/drink.svg";
    return "assets/plate.svg";
  }

  function renderMenu() {
    const platesEl = document.getElementById("menu-plates");
    const drinksEl = document.getElementById("menu-drinks");
    if (!platesEl || !drinksEl) return;
    platesEl.innerHTML = "";
    drinksEl.innerHTML = "";

    CFG.menu.forEach((item) => {
      const isPlate = item.category === "plates";
      const card = document.createElement("article");
      card.className = "menu-card" + (isPlate ? " featured" : "");
      card.dataset.itemId = item.id;

      const visualClass = isPlate ? "plate-grad" : "drink-grad";
      const badge = item.badge
        ? `<span class="badge">${escapeHtml(item.badge)}</span>`
        : "";

      let includesHtml = "";
      if (item.includes && item.includes.length) {
        includesHtml =
          `<ul class="includes-list">` +
          item.includes.map((x) => `<li>${escapeHtml(x)}</li>`).join("") +
          `</ul>`;
      }

      let optionsHtml = "";
      if (item.options) {
        const choices = item.options.choices
          .map((c) => {
            const checked = c.default ? " checked" : "";
            return `<label><input type="radio" name="opt-${item.id}" value="${escapeAttr(c.id)}" data-label="${escapeAttr(c.label)}"${checked} /> ${escapeHtml(c.label)}</label>`;
          })
          .join("");
        optionsHtml = `
          <div class="option-group">
            <span class="opt-label">${escapeHtml(item.options.label)}</span>
            <div class="option-choices">${choices}</div>
          </div>`;
      }

      let addonsHtml = "";
      if (item.addons && item.addons.length) {
        addonsHtml =
          `<div class="addons">` +
          item.addons
            .map(
              (a) => `
            <label class="addon-row">
              <input type="checkbox" data-addon-id="${escapeAttr(a.id)}" data-addon-name="${escapeAttr(a.name)}" data-addon-price="${a.price}" />
              <span>${escapeHtml(a.name)}</span>
              <span class="addon-price">+${money(a.price)}</span>
            </label>`
            )
            .join("") +
          `</div>`;
      }

      const leftChip = isPlate
        ? `<p style="margin:0"><span class="plates-left-chip" data-plate-chip>Limited — ${MAX_PLATES} plates</span></p>`
        : "";

      card.innerHTML = `
        <div class="card-visual ${visualClass}">
          ${badge}
          <img src="${iconFor(item)}" alt="" width="90" height="90" />
          <span class="dish-label">${escapeHtml(item.name)}</span>
        </div>
        <div class="card-body">
          <div class="card-top">
            <h3>${escapeHtml(item.name)}</h3>
            <span class="price">${money(item.price)}</span>
          </div>
          <p class="card-desc">${escapeHtml(item.description)}</p>
          ${includesHtml}
          ${leftChip}
          ${optionsHtml}
          ${addonsHtml}
          <div class="qty-row">
            <div class="qty-control" data-role="qty">
              <button type="button" aria-label="Decrease quantity" data-qty-delta="-1">−</button>
              <span data-qty-display>1</span>
              <button type="button" aria-label="Increase quantity" data-qty-delta="1">+</button>
            </div>
            <button type="button" class="btn btn-primary btn-sm" data-add="${escapeAttr(item.id)}">Add to cart</button>
          </div>
        </div>`;

      (isPlate ? platesEl : drinksEl).appendChild(card);
    });

    document.querySelectorAll("[data-role=qty]").forEach((ctrl) => {
      ctrl.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-qty-delta]");
        if (!btn) return;
        const display = ctrl.querySelector("[data-qty-display]");
        let q = parseInt(display.textContent, 10) || 1;
        q = Math.max(1, Math.min(20, q + parseInt(btn.dataset.qtyDelta, 10)));
        display.textContent = String(q);
      });
    });

    document.querySelectorAll("[data-add]").forEach((btn) => {
      btn.addEventListener("click", () => addFromCard(btn));
    });

    updatePlatesUI();
  }

  function addFromCard(btn) {
    const itemId = btn.dataset.add;
    const item = findItem(itemId);
    if (!item) return;
    const card = btn.closest(".menu-card");
    let qty = parseInt(card.querySelector("[data-qty-display]").textContent, 10) || 1;

    if (isPlateItem(item)) {
      const left = platesLeft();
      if (left <= 0) {
        showToast("No plates left — only " + MAX_PLATES + " available");
        updatePlatesUI();
        return;
      }
      if (qty > left) {
        qty = left;
        showToast("Only " + left + " plate" + (left === 1 ? "" : "s") + " left — adjusted qty");
      }
    }

    let optionLabel = null;
    let optionId = null;
    if (item.options) {
      const checked = card.querySelector(`input[name="opt-${item.id}"]:checked`);
      if (checked) {
        optionId = checked.value;
        optionLabel = checked.dataset.label;
      }
    }

    const addons = [];
    card.querySelectorAll("[data-addon-id]:checked").forEach((cb) => {
      addons.push({
        id: cb.dataset.addonId,
        name: cb.dataset.addonName,
        price: parseFloat(cb.dataset.addonPrice),
      });
    });

    const match = cart.find(
      (l) =>
        l.itemId === itemId &&
        l.optionLabel === optionLabel &&
        JSON.stringify(l.addons || []) === JSON.stringify(addons)
    );
    if (match) {
      if (isPlateItem(item)) {
        const left = platesLeft();
        const canAdd = Math.min(qty, left);
        if (canAdd <= 0) {
          showToast("No plates left");
          return;
        }
        match.qty = Math.min(99, match.qty + canAdd);
      } else {
        match.qty = Math.min(99, match.qty + qty);
      }
    } else {
      cart.push({
        uid: uid(),
        itemId,
        name: item.name,
        unitPrice: item.price,
        qty,
        optionId,
        optionLabel,
        addons,
        countsTowardPlateLimit: isPlateItem(item),
      });
    }
    saveCart();
    updateCartUI();
    showToast("Added to cart");
    card.querySelector("[data-qty-display]").textContent = "1";
  }

  // ——— Cart UI ———
  function renderCartLines(container, { editable } = { editable: true }) {
    if (!container) return;
    if (!cart.length) {
      container.innerHTML = `<p class="cart-empty">Your cart is empty. <a href="#menu">Browse the menu</a>.</p>`;
      return;
    }
    const breakdown = computeTotals();
    const ul = document.createElement("ul");
    ul.className = "cart-lines";
    breakdown.lines.forEach(({ line, charge, disc, tag }) => {
      const li = document.createElement("li");
      li.className = "cart-line";
      const metaParts = [];
      if (line.optionLabel) metaParts.push(line.optionLabel);
      (line.addons || []).forEach((a) => metaParts.push("+ " + a.name));
      if (tag === "FREE_DINNER") metaParts.push("Free dinner");
      if (tag === "HALF_OFF") metaParts.push("50% off");
      if (tag === "PLATE_CLUB") metaParts.push("Plate Club 50% off");
      if (tag === "REWARDS_75") metaParts.push("Rewards 75% off");
      if (tag === "FREE_DRINK") metaParts.push("Free drink");
      if (tag === "spin") metaParts.push("Demo spin fee");
      li.innerHTML = `
        <span class="cart-line-name">${escapeHtml(line.name)} × ${line.qty}</span>
        <span class="price">${disc > 0 ? `<s class="was">${money(lineTotal(line))}</s> ` : ""}${money(charge)}</span>
        ${metaParts.length ? `<span class="cart-line-meta">${escapeHtml(metaParts.join(" · "))}</span>` : ""}
        ${
          editable && !line.isSpinFee
            ? `<div class="cart-line-actions">
                <button type="button" data-dec="${escapeAttr(line.uid)}" aria-label="Decrease">−</button>
                <span>${line.qty}</span>
                <button type="button" data-inc="${escapeAttr(line.uid)}" aria-label="Increase">+</button>
                <button type="button" class="remove-btn" data-rm="${escapeAttr(line.uid)}">Remove</button>
              </div>`
            : editable && line.isSpinFee
              ? `<div class="cart-line-actions"><button type="button" class="remove-btn" data-rm="${escapeAttr(line.uid)}">Remove</button></div>`
              : ""
        }`;
      ul.appendChild(li);
    });
    container.innerHTML = "";
    container.appendChild(ul);

    if (editable) {
      container.querySelectorAll("[data-inc]").forEach((b) =>
        b.addEventListener("click", () => changeQty(b.dataset.inc, 1))
      );
      container.querySelectorAll("[data-dec]").forEach((b) =>
        b.addEventListener("click", () => changeQty(b.dataset.dec, -1))
      );
      container.querySelectorAll("[data-rm]").forEach((b) =>
        b.addEventListener("click", () => removeLine(b.dataset.rm))
      );
    }
  }

  function renderTotals(el) {
    if (!el) return;
    const t = computeTotals();
    el.innerHTML = `
      <div class="row"><span>Subtotal</span><span>${money(t.rawSub)}</span></div>
      ${
        t.discountTotal > 0
          ? `<div class="row discount"><span>Discounts</span><span>−${money(t.discountTotal)}</span></div>`
          : ""
      }
      ${
        t.shipAdd > 0
          ? `<div class="row"><span>${escapeHtml(t.shipLabel)}</span><span>${money(t.shipAdd)}</span></div>`
          : ""
      }
      <div class="row total"><span>Total</span><span>${money(t.total)}</span></div>`;
  }

  function changeQty(lineUid, delta) {
    const line = cart.find((l) => l.uid === lineUid);
    if (!line) return;
    if (delta > 0 && (line.countsTowardPlateLimit || isPlateItem(line.itemId))) {
      if (platesLeft() <= 0) {
        showToast("Only " + MAX_PLATES + " plates available");
        return;
      }
    }
    line.qty += delta;
    if (line.qty <= 0) cart = cart.filter((l) => l.uid !== lineUid);
    saveCart();
    updateCartUI();
  }

  function removeLine(lineUid) {
    const line = cart.find((l) => l.uid === lineUid);
    if (line && (line.isSpinFee || line.itemId === SPIN_ITEM_ID)) {
      spinUnlocked = false;
    }
    cart = cart.filter((l) => l.uid !== lineUid);
    saveCart();
    updateCartUI();
    updateHappyHourUI();
    showToast("Removed from cart");
  }

  function updateCartUI() {
    const count = cartQty();
    const countEl = document.getElementById("cart-count");
    if (countEl) {
      countEl.textContent = String(count);
      countEl.setAttribute("aria-label", count + " items in cart");
    }

    renderCartLines(document.getElementById("drawer-cart-body"), { editable: true });
    renderCartLines(document.getElementById("order-cart-body"), { editable: true });
    renderTotals(document.getElementById("drawer-totals"));

    const orderBody = document.getElementById("order-cart-body");
    if (orderBody) {
      let totals = orderBody.querySelector(".cart-totals");
      if (!totals && cart.length) {
        totals = document.createElement("div");
        totals.className = "cart-totals";
        orderBody.appendChild(totals);
        const tax = document.createElement("p");
        tax.className = "tax-note";
        tax.textContent = CFG.taxNote;
        orderBody.appendChild(tax);
      }
      if (cart.length) {
        renderTotals(orderBody.querySelector(".cart-totals"));
        const taxEl = orderBody.querySelector(".tax-note");
        if (taxEl) taxEl.textContent = CFG.taxNote;
      }
    }
    renderActiveCodes();
    updatePlatesUI();
  }

  // ——— Drawer ———
  function openCart() {
    const drawer = document.getElementById("cart-drawer");
    const overlay = document.getElementById("cart-overlay");
    drawer.hidden = false;
    overlay.hidden = false;
    void drawer.offsetWidth;
    drawer.classList.add("open");
    overlay.classList.add("open");
    document.getElementById("cart-open-btn").setAttribute("aria-expanded", "true");
    document.getElementById("cart-close-btn").focus();
    document.addEventListener("keydown", onEscCart);
  }

  function closeCart() {
    const drawer = document.getElementById("cart-drawer");
    const overlay = document.getElementById("cart-overlay");
    drawer.classList.remove("open");
    overlay.classList.remove("open");
    document.getElementById("cart-open-btn").setAttribute("aria-expanded", "false");
    document.removeEventListener("keydown", onEscCart);
    setTimeout(() => {
      drawer.hidden = true;
      overlay.hidden = true;
    }, 280);
  }

  function onEscCart(e) {
    if (e.key === "Escape") closeCart();
  }

  // ——— Order text ———
  function buildOrderText(order) {
    const lines = [];
    lines.push((CFG.eventName || "Soul Food Pop").toUpperCase());
    lines.push(CFG.businessName.toUpperCase() + " ORDER");
    lines.push("Order #: " + order.number);
    lines.push(
      "Event: " +
        [CFG.eventDate, CFG.eventTime, CFG.pickupLocation].filter(Boolean).join(" · ")
    );
    lines.push("Fulfillment: " + (order.fulfillmentLabel || "Pickup"));
    lines.push("————————————");
    order.items.forEach((l) => {
      lines.push(`• ${l.name} x${l.qty} — ${money(lineTotal(l))}`);
      if (l.optionLabel) lines.push(`  (${l.optionLabel})`);
      (l.addons || []).forEach((a) => lines.push(`  + ${a.name} (${money(a.price)})`));
    });
    lines.push("————————————");
    if (order.discountTotal) lines.push("Discounts: −" + money(order.discountTotal));
    if (order.shipAdd) lines.push("Shipping: " + money(order.shipAdd));
    lines.push("Total: " + money(order.subtotal));
    if (order.codes && order.codes.length) lines.push("Codes: " + order.codes.join(", "));
    if (order.plateClub) lines.push("Plate Club member: yes");
    lines.push("(" + CFG.taxNote + ")");
    lines.push("");
    lines.push("Customer: " + order.customer.name);
    lines.push("Phone: " + order.customer.phone);
    lines.push("Email: " + order.customer.email);
    if (order.customer.pickupDate || order.customer.pickupTime) {
      lines.push(
        "Pickup: " +
          [order.customer.pickupDate, order.customer.pickupTime].filter(Boolean).join(" ")
      );
    }
    if (order.customer.marketNote) lines.push("Market note: " + order.customer.marketNote);
    if (order.customer.specialRequests)
      lines.push("Requests: " + order.customer.specialRequests);
    lines.push("");
    lines.push("Sent via " + CFG.businessName + " website");
    return lines.join("\n");
  }

  function showConfirmation(order) {
    document.getElementById("checkout-view").classList.add("hidden");
    const panel = document.getElementById("confirm-panel");
    panel.classList.add("visible");

    document.getElementById("confirm-order-number").textContent = "Order #" + order.number;

    const cust = document.getElementById("confirm-customer");
    cust.innerHTML = `
      <dl>
        <dt>Name</dt><dd>${escapeHtml(order.customer.name)}</dd>
        <dt>Phone</dt><dd>${escapeHtml(order.customer.phone)}</dd>
        <dt>Email</dt><dd>${escapeHtml(order.customer.email)}</dd>
        <dt>Fulfillment</dt><dd>${escapeHtml(order.fulfillmentLabel || "Pickup")}</dd>
        ${
          order.customer.pickupDate || order.customer.pickupTime
            ? `<dt>Preferred pickup</dt><dd>${escapeHtml(
                [order.customer.pickupDate, order.customer.pickupTime].filter(Boolean).join(" ")
              )}</dd>`
            : ""
        }
        ${
          order.customer.marketNote
            ? `<dt>Market note</dt><dd>${escapeHtml(order.customer.marketNote)}</dd>`
            : ""
        }
        ${
          order.customer.specialRequests
            ? `<dt>Special requests</dt><dd>${escapeHtml(order.customer.specialRequests)}</dd>`
            : ""
        }
      </dl>`;

    const linesEl = document.getElementById("confirm-lines");
    linesEl.innerHTML = order.items
      .map((l) => {
        const meta = [];
        if (l.optionLabel) meta.push(l.optionLabel);
        (l.addons || []).forEach((a) => meta.push("+ " + a.name));
        return `<li class="cart-line">
          <span class="cart-line-name">${escapeHtml(l.name)} × ${l.qty}</span>
          <span class="price">${money(lineTotal(l))}</span>
          ${meta.length ? `<span class="cart-line-meta">${escapeHtml(meta.join(" · "))}</span>` : ""}
        </li>`;
      })
      .join("");

    document.getElementById("confirm-totals").innerHTML = `
      ${
        order.discountTotal
          ? `<div class="row discount"><span>Discounts</span><span>−${money(order.discountTotal)}</span></div>`
          : ""
      }
      ${
        order.shipAdd
          ? `<div class="row"><span>${escapeHtml(order.fulfillmentLabel)}</span><span>${money(order.shipAdd)}</span></div>`
          : ""
      }
      <div class="row total"><span>Total</span><span>${money(order.subtotal)}</span></div>`;

    const body = buildOrderText(order);
    const sms = document.getElementById("btn-sms");
    sms.href = "sms:" + CFG.phoneDigits + "?&body=" + encodeURIComponent(body);

    const mail = document.getElementById("btn-email");
    mail.href =
      "mailto:" +
      encodeURIComponent(CFG.email) +
      "?subject=" +
      encodeURIComponent(
        (CFG.eventName || "Soul Food Pop") + " — Order " + order.number
      ) +
      "&body=" +
      encodeURIComponent(body);

    document.getElementById("btn-copy").onclick = async () => {
      try {
        await navigator.clipboard.writeText(body);
        showToast("Order copied to clipboard");
      } catch (_) {
        const ta = document.createElement("textarea");
        ta.value = body;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
        showToast("Order copied to clipboard");
      }
    };

    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function resetToCheckout() {
    document.getElementById("confirm-panel").classList.remove("visible");
    document.getElementById("checkout-view").classList.remove("hidden");
    document.getElementById("checkout-form").reset();
    const pickup = document.querySelector('input[name="fulfillment"][value="pickup"]');
    if (pickup) pickup.checked = true;
    updateCartUI();
  }

  function validateForm(form) {
    let ok = true;
    const name = form.name.value.trim();
    const phone = form.phone.value.trim();
    const email = form.email.value.trim();

    function flag(inputId, errId, show) {
      const input = document.getElementById(inputId);
      const err = document.getElementById(errId);
      if (show) {
        input.classList.add("input-error");
        err.classList.add("show");
        ok = false;
      } else {
        input.classList.remove("input-error");
        err.classList.remove("show");
      }
    }

    flag("cust-name", "err-name", !name);
    flag("cust-phone", "err-phone", !phone);
    flag("cust-email", "err-email", !email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email));
    return ok;
  }

  function placeOrder(e) {
    e.preventDefault();
    const form = e.target;
    if (!cart.length) {
      showToast("Add something to your cart first");
      document.getElementById("menu").scrollIntoView({ behavior: "smooth" });
      return;
    }
    if (!validateForm(form)) {
      showToast("Please fill in required fields");
      return;
    }

    const plateCount = platesInCart();
    if (plateCount > platesLeftAfterReserve()) {
      showToast("Not enough plates left — reduce your cart");
      return;
    }

    const totals = computeTotals();
    const fulfill = getFulfillment();
    const fulfillLabels = {
      pickup: "Pickup",
      "overnight-cold": "Overnight cold (Uline) +" + money(CFG.shipCold || 28),
      "overnight-hot": "Overnight hot (Uline) +" + money(CFG.shipHot || 35),
    };

    // Count full-price plate units for stamps (no club/code/reward discount on that unit)
    let fullPricePlates = 0;
    let usedReward = false;
    let usedFreeDinner = false;
    let usedHalfOff = false;
    totals.lines.forEach(({ line, tag }) => {
      if (!isPlateItem(line.itemId)) return;
      if (tag === "REWARDS_75") {
        usedReward = true;
        // remaining qty beyond first may be full price — approximate via per-unit tags not tracked; stamp non-discounted
      } else if (tag === "FREE_DINNER") {
        usedFreeDinner = true;
      } else if (tag === "HALF_OFF" || tag === "PLATE_CLUB") {
        usedHalfOff = true;
      } else {
        fullPricePlates += line.qty;
      }
    });
    // Better stamp logic: each plate unit that paid full menu price
    fullPricePlates = 0;
    let freeDinnerLeft = discountCodes.includes("FREE_DINNER") ? 1 : 0;
    let halfOffLeft = discountCodes.includes("HALF_OFF") ? 1 : 0;
    let reward75Left = rewardReady ? 1 : 0;
    cart.forEach((line) => {
      if (!isPlateItem(line.itemId)) return;
      for (let i = 0; i < line.qty; i++) {
        if (freeDinnerLeft > 0) {
          freeDinnerLeft--;
          usedFreeDinner = true;
        } else if (reward75Left > 0) {
          reward75Left--;
          usedReward = true;
        } else if (plateClubMember && CFG.plateClubHalfOff !== false) {
          usedHalfOff = true;
        } else if (halfOffLeft > 0) {
          halfOffLeft--;
          usedHalfOff = true;
        } else {
          fullPricePlates++;
        }
      }
    });

    const order = {
      number: orderNumber(),
      createdAt: new Date().toISOString(),
      items: cart.map((l) => ({ ...l, addons: (l.addons || []).map((a) => ({ ...a })) })),
      subtotal: totals.total,
      discountTotal: totals.discountTotal,
      shipAdd: totals.shipAdd,
      fulfillment: fulfill,
      fulfillmentLabel: fulfillLabels[fulfill] || "Pickup",
      codes: discountCodes.slice(),
      plateClub: plateClubMember,
      plateCount,
      customer: {
        name: form.name.value.trim(),
        phone: form.phone.value.trim(),
        email: form.email.value.trim(),
        pickupDate: form.pickupDate.value || "",
        pickupTime: form.pickupTime.value || "",
        marketNote: form.marketNote.value.trim(),
        specialRequests: form.specialRequests.value.trim(),
      },
    };

    platesReserved = Math.min(MAX_PLATES, platesReserved + plateCount);
    savePlatesReserved();

    // Update rewards
    if (usedReward) {
      rewardReady = false;
      lsSet(STORAGE_REWARD_READY, false);
    }
    if (fullPricePlates > 0) {
      rewardStamps += fullPricePlates;
      while (rewardStamps >= REWARDS_N) {
        rewardStamps -= REWARDS_N;
        rewardReady = true;
      }
      lsSet(STORAGE_STAMPS, rewardStamps);
      lsSet(STORAGE_REWARD_READY, rewardReady);
    }

    // Consume one-shot codes that were applied
    if (usedFreeDinner) removeDiscountCode("FREE_DINNER");
    if (usedHalfOff && discountCodes.includes("HALF_OFF")) removeDiscountCode("HALF_OFF");
    // Free drink: remove if was in codes (assume used if drinks in cart)
    if (
      discountCodes.includes("FREE_DRINK") &&
      cart.some((l) => isDrinkItem(l.itemId))
    ) {
      removeDiscountCode("FREE_DRINK");
    }

    saveLastOrder(order);
    cart = [];
    spinUnlocked = false;
    saveCart();
    updateCartUI();
    updateRewardsUI();
    updateHappyHourUI();
    showConfirmation(order);
    showToast("Order #" + order.number + " ready — send it below");
  }

  function setupNav() {
    const toggle = document.getElementById("menu-toggle");
    const nav = document.getElementById("nav-mobile");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      nav.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => {
        nav.classList.remove("open");
        nav.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
      })
    );
  }

  function init() {
    applyBrand();
    loadLoyaltyState();
    loadPlatesReserved();
    loadCart();
    let left = platesLeftAfterReserve();
    let plateSeen = 0;
    cart = cart.filter((l) => {
      if (!(l.countsTowardPlateLimit || isPlateItem(l.itemId))) return true;
      if (plateSeen >= left) return false;
      const room = left - plateSeen;
      if (l.qty > room) l.qty = room;
      plateSeen += l.qty;
      return l.qty > 0;
    });
    saveCart();
    loadLastOrder();
    renderMenu();
    updateCartUI();
    updateClubUI();
    updateRewardsUI();
    setupNav();
    setupTabs();
    setupLiveDrop();
    renderPrizeList();
    drawWheel();
    updateHappyHourUI();
    renderTrivia();

    document.getElementById("cart-open-btn").addEventListener("click", openCart);
    document.getElementById("cart-close-btn").addEventListener("click", closeCart);
    document.getElementById("cart-overlay").addEventListener("click", closeCart);
    document.getElementById("drawer-checkout-btn").addEventListener("click", closeCart);
    document.getElementById("checkout-form").addEventListener("submit", placeOrder);
    document.getElementById("btn-new-order").addEventListener("click", () => {
      resetToCheckout();
      document.getElementById("menu").scrollIntoView({ behavior: "smooth" });
    });

    const clubToggle = document.getElementById("plate-club-toggle");
    if (clubToggle) {
      clubToggle.addEventListener("change", () => {
        plateClubMember = clubToggle.checked;
        lsSet(STORAGE_CLUB, plateClubMember);
        updateClubUI();
        updateCartUI();
        showToast(plateClubMember ? "Plate Club half-off on" : "Plate Club off");
      });
    }

    ["hh-demo-toggle", "hh-demo-btn"].forEach((id) => {
      const b = document.getElementById(id);
      if (b) b.addEventListener("click", toggleDemoHH);
    });

    const paySpin = document.getElementById("btn-pay-spin");
    if (paySpin) paySpin.addEventListener("click", payToSpin);
    const spinBtn = document.getElementById("btn-spin");
    if (spinBtn) spinBtn.addEventListener("click", spinWheel);

    const freeSpin = document.getElementById("trivia-free-spin");
    if (freeSpin) {
      freeSpin.addEventListener("click", () => {
        if (!isHappyHourActive()) {
          showToast("Turn on Demo Happy Hour first");
          return;
        }
        unlockSpin(true);
        // switch to wheel tab
        document.getElementById("tab-wheel").click();
        freeSpin.hidden = true;
      });
    }

    // Refresh HH status every minute
    setInterval(updateHappyHourUI, 30000);

    if (lastOrder && !cart.length && location.hash === "#order-confirm") {
      showConfirmation(lastOrder);
    }

    const dateInput = document.getElementById("pickup-date");
    if (dateInput) {
      const t = new Date();
      const pad = (n) => String(n).padStart(2, "0");
      dateInput.min = `${t.getFullYear()}-${pad(t.getMonth() + 1)}-${pad(t.getDate())}`;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
