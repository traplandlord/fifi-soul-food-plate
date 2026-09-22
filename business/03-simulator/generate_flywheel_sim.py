#!/usr/bin/env python3
"""Fifi Soul Food — Product-drop + marketplace flywheel (Jordan/iPhone launch).
Week-for-week simulator weeks 1-52. Itemized COGS. NOT financial advice.
Re-run: python3 generate_flywheel_sim.py
"""
from __future__ import annotations
import csv, math
from pathlib import Path

OUT = Path("/workspace/fifi-soul-food")
SITE = Path("/workspace/fifi-soul-food-site/business")
BIZ = Path("/workspace/fifi-soul-food-business")

# --- Itemized mid COGS from cogs-and-pricing.csv (brand food mid $3.70) ---
COGS_CHICKEN_2PC = 0.59          # RD drums 0.60lb * $0.99
COGS_OIL_BREAD_SEASON = 0.62     # 0.22+0.30+0.10
COGS_GREENS = 0.85
COGS_SWEETS = 0.70
COGS_ROLL = 0.25
COGS_YIELD_WASTE = round(3.70 - (0.59+0.62+0.85+0.70+0.25), 2)  # bridge to $3.70
COGS_FOOD = 3.70
COGS_PACK = 0.44
COGS_PACK_STALL = 0.50
DD_BONUS = 0.75

PICKUP, LIVE = 20.0, 20.0
DD_MENU, DD_FEE = 26.0, 0.25
GH_MENU, GH_FEE = 26.0, 0.27
ON_TOTAL, ON_NET = 85.0, 4.53
ULINE = ON_TOTAL - COGS_FOOD - ON_NET
LOCAL_BUNDLE, DRIVE = 32.0, 9.95
CLUB, REWARD, HH = 10.0, 5.0, 10.0
HH_SPIN, PAY = 0.56, 0.025
MOM_W = 20.0
RENT_WK = 3900.0 / 4.33
LEASE_GATE, LEASE_STREAK, LEASE_BUF = 160, 8, 11700.0

DROP_W1 = (220.0, 480.0, 720.0)  # low, mid, high
PULSE = {1:1.0, 2:0.88, 3:0.70, 4:0.52}
AD = {1:1200.0, 2:900.0, 3:600.0, 4:400.0}
HABIT_K, HABIT_R, HABIT_T0 = 380.0, 0.12, 10.0

COLS = [
 "week","mode","demand_latent","demand_low_band","demand_high_band","waitlist_in",
 "capacity_plates","plates_fulfilled","lost_demand","waitlist_out",
 "weekday_plates","weekend_plates","peak_night_orders","service_nights",
 "followers_or_reach_proxy","mom_cook_hours","help_hours","throughput_pph","peak_night_capacity",
 "ch_pickup","ch_live","ch_doordash","ch_grubhub","ch_overnight","ch_local_delivery",
 "ch_plate_club","ch_happy_hour_half","ch_rewards",
 "rev_pickup","rev_live","rev_doordash","rev_grubhub","rev_overnight","rev_local_delivery",
 "rev_plate_club","rev_happy_hour","rev_rewards","rev_drinks","rev_platform_monetize","revenue_total",
 "cogs_chicken","cogs_greens","cogs_sweet_potatoes","cogs_roll","cogs_oil_breading_seasoning",
 "cogs_yield_waste","cogs_food_total","cogs_pack_supplies","cogs_pack_total",
 "cogs_dd_gh_bonus","cogs_drinks",
 "fees_dd_commission","fees_gh_commission","fees_payment","fulfill_drive","fulfill_uline_bom",
 "opex_ads","opex_gas_permits_ins_phone","opex_hire_cash","opex_rent_utils","hh_spin_cost",
 "club_members","SUMMARY_net_cash","SUMMARY_net_after_mom","cum_cash","lease_gate_met","notes"
]

def demand(week):
    lo, mid, hi = DROP_W1
    if week in PULSE:
        p = PULSE[week]
        return mid*p, lo*p, hi*p
    w4m, w4l, w4h = mid*PULSE[4], lo*PULSE[4], hi*PULSE[4]
    dec = math.exp(-(week-4)/6.0)
    hype_m, hype_l, hype_h = w4m*dec*0.55, w4l*dec*0.55, w4h*dec*0.55
    habit_m = HABIT_K/(1+math.exp(-HABIT_R*(week-HABIT_T0)))
    habit_l = 240/(1+math.exp(-0.10*(week-12)))
    habit_h = 520/(1+math.exp(-0.14*(week-8)))
    return hype_m+habit_m, hype_l+habit_l, hype_h+habit_h

def mix(plates, mode, week, club_share):
    keys = ["pickup","live","doordash","grubhub","overnight","local_delivery","plate_club","happy_hour_half","rewards"]
    if plates<=0: return {k:0 for k in keys}
    mat = min(1.0,(week-1)/26)
    if mode=="mobile":
        base = dict(pickup=0.12+0.04*mat, live=0.08, doordash=0.38-0.04*mat, grubhub=0.20-0.02*mat,
                    overnight=0.05, local_delivery=0.07+0.02*mat)
    else:
        base = dict(pickup=0.14+0.04*mat, live=0.05, doordash=0.40-0.02*mat, grubhub=0.18,
                    overnight=0.04, local_delivery=0.08+0.02*mat)
    club_w=min(club_share,0.14); hh_w=0.04+0.02*mat; rew_w=0.07
    rem=max(0.01,1-club_w-hh_w-rew_w); s=sum(base.values())
    w={k:base[k]/s*rem for k in base}
    w.update(plate_club=club_w, happy_hour_half=hh_w, rewards=rew_w)
    raw={k:plates*w[k] for k in keys}
    c={k:int(math.floor(raw[k])) for k in keys}
    r=plates-sum(c.values())
    order=sorted(keys, key=lambda k: raw[k]-c[k], reverse=True)
    for i in range(r): c[order[i%len(order)]] += 1
    return c

def mob_cap(week, help_h):
    if week<=4: mom,pph=35.0,14.0
    else:
        mat=min(1,(week-5)/20); mom,pph=28+4*mat,13+1.5*mat
    weekly=(mom+help_h)*pph*(1.15 if week<=4 else 1.0)
    night_hrs=5 if week<=4 else 4
    peak=night_hrs*pph*(2 if week<=4 else 1.5)*(1+min(help_h,40)/80)
    if week<=4: weekly,peak=min(weekly,650),min(peak,320)
    else: weekly,peak=min(weekly,420+help_h*2),min(peak,200)
    return weekly,mom,help_h,pph,peak

def loc_cap(week, lease_w):
    ramp=min(1,max(0,week-lease_w)/10)
    mom,help_h,pph=35.0,40+30*ramp,14+1.5*ramp
    weekly=min((mom+help_h)*pph*0.95, 500+400*ramp)
    peak=220+180*ramp
    return weekly,mom,help_h,pph,peak

def simulate(allow_lease):
    rows=[]; waitlist=0.0; cum=0.0; club=0.0; lease=None; streak=0; followers=2500.0
    for week in range(1,53):
        d_mid,d_lo,d_hi=demand(week)
        followers=2500+35000*min(1,d_mid/480)+week*120
        if allow_lease and lease is None:
            streak = streak+1 if d_mid>=LEASE_GATE else 0
            if streak>=LEASE_STREAK and cum>=LEASE_BUF: lease=week
        leased=allow_lease and lease and week>=lease
        mode="location" if leased else "mobile"
        if mode=="mobile":
            help_h=50 if week<=4 else (28 if week<=12 else (18 if d_mid>280 else 12))
            cap,mom,help_h,pph,peak=mob_cap(week,help_h)
            hire=help_h*MOM_W; rent=0; fixed=55+15+20+15; pack_u=COGS_PACK
        else:
            cap,mom,help_h,pph,peak=loc_cap(week,lease)
            hire=help_h*MOM_W; rent=RENT_WK; fixed=30+80/4.33+250/4.33+60/4.33; pack_u=COGS_PACK_STALL
        dem=d_mid+waitlist
        ful=min(dem,cap); lost=max(0,dem-ful); wout=min(lost*0.35,cap*0.20)
        plates=int(round(ful))
        club=club*0.98+plates*0.25*0.08*0.40
        cshare=min(0.14,(club*0.8)/max(plates,1)) if plates else 0
        ch=mix(plates,mode,week,cshare)
        weekend=int(round(plates*0.55)); weekday=plates-weekend
        peak_ord=int(round(min(plates*0.40, peak*1.15)))  # biggest Fri/Sat ~40% of week
        nights=7 if week<=8 else (6 if plates>200 else 5)
        ads=AD.get(week, (80 if mode=="mobile" else 120)+min(100,d_mid*0.05))
        if week in AD and mode=="location": ads+=200

        rev_p=ch["pickup"]*PICKUP; rev_l=ch["live"]*LIVE
        rev_dd=ch["doordash"]*DD_MENU; rev_gh=ch["grubhub"]*GH_MENU
        rev_on=ch["overnight"]*ON_TOTAL; rev_del=ch["local_delivery"]*LOCAL_BUNDLE
        rev_cl=ch["plate_club"]*CLUB; rev_hh=ch["happy_hour_half"]*HH; rev_rw=ch["rewards"]*REWARD
        drink=int(round(plates*(0.18 if week>=20 or mode=="location" else 0)))
        rev_dr=drink*3.5; rev_plat=round((followers*0.10/100)*5*min(1,0.5+week/40),2)
        revenue=rev_p+rev_l+rev_dd+rev_gh+rev_on+rev_del+rev_cl+rev_hh+rev_rw+rev_dr+rev_plat

        cc=round(plates*COGS_CHICKEN_2PC,2); cg=round(plates*COGS_GREENS,2)
        cs=round(plates*COGS_SWEETS,2); cr=round(plates*COGS_ROLL,2)
        co=round(plates*COGS_OIL_BREAD_SEASON,2); cy=round(plates*COGS_YIELD_WASTE,2)
        cfood=round(cc+cg+cs+cr+co+cy,2); cpack=round(plates*pack_u,2)
        cbon=round((ch["doordash"]+ch["grubhub"])*DD_BONUS,2); cdr=round(drink*0.80,2)
        fdd=round(ch["doordash"]*DD_MENU*DD_FEE,2); fgh=round(ch["grubhub"]*GH_MENU*GH_FEE,2)
        card=revenue-rev_l-rev_dd-rev_gh-rev_plat
        fpay=round(max(0,card)*PAY,2)
        fdrive=round(ch["local_delivery"]*DRIVE,2); fuline=round(ch["overnight"]*ULINE,2)
        hhs=round(ch["happy_hour_half"]*HH_SPIN,2)
        net=revenue-cfood-cpack-cbon-cdr-fdd-fgh-fpay-fdrive-fuline-ads-fixed-hire-rent-hhs
        netm=net-mom*MOM_W; cum+=net

        notes=[]
        if week==1: notes.append("DROP LAUNCH — Jordan/iPhone front-load; marketplace-heavy")
        if week<=4: notes.append(f"Drop pulse; ads ${ads:.0f}")
        if week==5: notes.append("Post-drop hype tail; habit floor building")
        if lost>1: notes.append(f"Capacity bind lost≈{lost:.0f}")
        if peak_ord>peak: notes.append(f"Peak night pressure {peak_ord}>{peak:.0f}")
        if lease==week: notes.append(f"LEASE GATE demand≥{LEASE_GATE}×{LEASE_STREAK}+cash≥${LEASE_BUF:.0f}")
        if not notes: notes.append("habit+LIVE+marketplace retention")
        mkt=(ch["doordash"]+ch["grubhub"])/plates if plates else 0

        rows.append(dict(
            week=week, mode=("location" if leased else "mobile") if allow_lease else "mobile",
            demand_latent=round(d_mid,2), demand_low_band=round(d_lo,2), demand_high_band=round(d_hi,2),
            waitlist_in=round(waitlist,2), capacity_plates=round(cap,2), plates_fulfilled=plates,
            lost_demand=round(lost,2), waitlist_out=round(wout,2),
            weekday_plates=weekday, weekend_plates=weekend, peak_night_orders=peak_ord,
            service_nights=nights, followers_or_reach_proxy=int(round(followers)),
            mom_cook_hours=round(mom,2), help_hours=round(help_h,2), throughput_pph=round(pph,2),
            peak_night_capacity=round(peak,2),
            ch_pickup=ch["pickup"], ch_live=ch["live"], ch_doordash=ch["doordash"], ch_grubhub=ch["grubhub"],
            ch_overnight=ch["overnight"], ch_local_delivery=ch["local_delivery"],
            ch_plate_club=ch["plate_club"], ch_happy_hour_half=ch["happy_hour_half"], ch_rewards=ch["rewards"],
            rev_pickup=round(rev_p,2), rev_live=round(rev_l,2), rev_doordash=round(rev_dd,2),
            rev_grubhub=round(rev_gh,2), rev_overnight=round(rev_on,2), rev_local_delivery=round(rev_del,2),
            rev_plate_club=round(rev_cl,2), rev_happy_hour=round(rev_hh,2), rev_rewards=round(rev_rw,2),
            rev_drinks=round(rev_dr,2), rev_platform_monetize=rev_plat, revenue_total=round(revenue,2),
            cogs_chicken=cc, cogs_greens=cg, cogs_sweet_potatoes=cs, cogs_roll=cr,
            cogs_oil_breading_seasoning=co, cogs_yield_waste=cy, cogs_food_total=cfood,
            cogs_pack_supplies=cpack, cogs_pack_total=cpack, cogs_dd_gh_bonus=cbon, cogs_drinks=cdr,
            fees_dd_commission=fdd, fees_gh_commission=fgh, fees_payment=fpay,
            fulfill_drive=fdrive, fulfill_uline_bom=fuline,
            opex_ads=round(ads,2), opex_gas_permits_ins_phone=round(fixed,2),
            opex_hire_cash=round(hire,2), opex_rent_utils=round(rent,2), hh_spin_cost=hhs,
            club_members=round(club,2), SUMMARY_net_cash=round(net,2),
            SUMMARY_net_after_mom=round(netm,2), cum_cash=round(cum,2),
            lease_gate_met=1 if leased else 0,
            notes="; ".join(notes)+f"; mkt_share≈{mkt:.0%}",
        ))
        waitlist=wout
    return rows, lease

def month_agg(rows, start):
    idxs=list(range(start-1, min(start-1+5,len(rows))))
    full=rows[idxs[0]:idxs[0]+4] if len(idxs)>=4 else [rows[i] for i in idxs]
    part=rows[idxs[0]+4] if len(idxs)>=5 else None
    wf=0.33
    def sk(k):
        s=sum(r[k] for r in full if isinstance(r.get(k),(int,float)))
        if part and isinstance(part.get(k),(int,float)): s+=part[k]*wf
        return s
    n=4+(wf if part else 0)
    return dict(plates=round(sk("plates_fulfilled"),1), net_cash=round(sk("SUMMARY_net_cash"),2),
                net_after_mom=round(sk("SUMMARY_net_after_mom"),2),
                avg_demand=round(sk("demand_latent")/n,1), avg_cap=round(sk("capacity_plates")/n,1),
                lost=round(sk("lost_demand"),1), ads=round(sk("opex_ads"),2),
                peak=round(sk("peak_night_orders")/n,1), dd=round(sk("ch_doordash"),1),
                gh=round(sk("ch_grubhub"),1), cogs_food=round(sk("cogs_food_total"),2),
                cogs_chicken=round(sk("cogs_chicken"),2))

def blank(): return {c:"" for c in COLS}

def summaries(mobile, loc, lease):
    out=[]; cross=None
    for label,start in [("SUMMARY_month_1",1),("SUMMARY_month_3",9),("SUMMARY_month_6",23),("SUMMARY_month_12",49)]:
        for mode,rows in [("mobile",mobile),("location_path",loc)]:
            a=month_agg(rows,start); r=blank()
            r.update(week=label, mode=mode, plates_fulfilled=a["plates"], demand_latent=a["avg_demand"],
                     capacity_plates=a["avg_cap"], lost_demand=a["lost"], peak_night_orders=a["peak"],
                     ch_doordash=a["dd"], ch_grubhub=a["gh"], cogs_food_total=a["cogs_food"],
                     cogs_chicken=a["cogs_chicken"], opex_ads=a["ads"],
                     SUMMARY_net_cash=a["net_cash"], SUMMARY_net_after_mom=a["net_after_mom"],
                     notes=f"{label} ≈4.33wks from w{start} · {mode}. Illustrative. NOT financial advice.")
            out.append(r)
    w1=mobile[0]; r=blank()
    r.update(week="SUMMARY_week1_drop_launch", mode="mobile",
             plates_fulfilled=w1["plates_fulfilled"], demand_latent=w1["demand_latent"],
             demand_low_band=w1["demand_low_band"], demand_high_band=w1["demand_high_band"],
             peak_night_orders=w1["peak_night_orders"], ch_doordash=w1["ch_doordash"],
             ch_grubhub=w1["ch_grubhub"], opex_ads=w1["opex_ads"], cogs_food_total=w1["cogs_food_total"],
             cogs_chicken=w1["cogs_chicken"], SUMMARY_net_cash=w1["SUMMARY_net_cash"],
             notes=f"W1 drop fulfilled={w1['plates_fulfilled']} peak={w1['peak_night_orders']} DD+GH={w1['ch_doordash']+w1['ch_grubhub']} ads=${w1['opex_ads']}")
    out.append(r)
    ads14=sum(mobile[i]["opex_ads"] for i in range(4))
    p14=sum(mobile[i]["plates_fulfilled"] for i in range(4))
    r=blank(); r.update(week="SUMMARY_ads_weeks_1_4", mode="mobile", opex_ads=round(ads14,2),
                        plates_fulfilled=p14,
                        notes=f"Ads w1-4 ${ads14:.0f} → {p14} plates. CPA-ish ${ads14/max(p14,1):.2f}/plate. Illustrative.")
    out.append(r)
    r=blank(); r.update(week="SUMMARY_lease_gate_week", mode="location_path",
                        plates_fulfilled=lease or "", lease_gate_met=1 if lease else 0,
                        cum_cash=loc[lease-1]["cum_cash"] if lease else "",
                        notes=f"Lease week={lease}. Gate demand≥{LEASE_GATE}×{LEASE_STREAK} + cash≥${LEASE_BUF:.0f}.")
    out.append(r)
    if lease:
        for m,L in zip(mobile,loc):
            if L["week"]>=lease and L["SUMMARY_net_cash"]>m["SUMMARY_net_cash"]:
                cross=L["week"]; break
    r=blank(); r.update(week="SUMMARY_crossover_location_beats_mobile", mode="compare",
                        plates_fulfilled=cross or "",
                        SUMMARY_net_cash=loc[cross-1]["SUMMARY_net_cash"] if cross else "",
                        notes=f"Week {cross}: location cash > mobile." if cross else "No crossover in 52 weeks.")
    out.append(r)
    pl=max(mobile, key=lambda x:x["lost_demand"])
    r=blank(); r.update(week="SUMMARY_peak_capacity_bind_mobile", mode="mobile",
                        plates_fulfilled=pl["week"], lost_demand=pl["lost_demand"],
                        capacity_plates=pl["capacity_plates"], demand_latent=pl["demand_latent"],
                        peak_night_orders=pl["peak_night_orders"],
                        notes=f"Peak bind w{pl['week']}: latent={pl['demand_latent']} cap={pl['capacity_plates']} lost={pl['lost_demand']}")
    out.append(r)
    r=blank(); r.update(week="SUMMARY_per_plate_BOM", mode="mid",
                        cogs_chicken=COGS_CHICKEN_2PC, cogs_greens=COGS_GREENS,
                        cogs_sweet_potatoes=COGS_SWEETS, cogs_roll=COGS_ROLL,
                        cogs_oil_breading_seasoning=COGS_OIL_BREAD_SEASON, cogs_yield_waste=COGS_YIELD_WASTE,
                        cogs_food_total=COGS_FOOD, cogs_pack_supplies=COGS_PACK,
                        notes=f"BOM: chicken ${COGS_CHICKEN_2PC}+greens ${COGS_GREENS}+sweets ${COGS_SWEETS}+roll ${COGS_ROLL}+oil/bread ${COGS_OIL_BREAD_SEASON}+yield ${COGS_YIELD_WASTE}=food ${COGS_FOOD}; pack ${COGS_PACK}. From cogs-and-pricing.csv.")
    out.append(r)
    return out, cross

def write_csv(path, mobile, loc, sums):
    with path.open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore"); w.writeheader()
        for row in mobile:
            rr=dict(row); rr["mode"]="mobile"; w.writerow(rr)
        for row in loc: w.writerow(row)
        for row in sums: w.writerow(row)

def write_readme(path, mobile, loc, lease, cross):
    w1=mobile[0]
    m1,m6,m12=month_agg(mobile,1),month_agg(mobile,23),month_agg(mobile,49)
    l1,l6,l12=month_agg(loc,1),month_agg(loc,23),month_agg(loc,49)
    ads14=sum(mobile[i]["opex_ads"] for i in range(4))
    p14=sum(mobile[i]["plates_fulfilled"] for i in range(4))
    mkt=w1["ch_doordash"]+w1["ch_grubhub"]
    bind=next((r for r in mobile if r["lost_demand"]>1), None)
    path.write_text(f"""# Product-drop demand spike + marketplace flywheel (Jordan/iPhone-style launch)

**Brand:** Fifi's Soul Food Plate / Momma Fifi Soul  
**Date:** Sep 22, 2026 (PT)  
**CSV:** `ops-simulation-flywheel-demand.csv` · **Generator:** `generate_flywheel_sim.py`  
**Not financial advice.** Illustrative mid-path week-for-week simulator.

---

## How to use (the simulator)

**Open the CSV and scroll week 1 → week 52. That IS the simulator.**

- `mode=mobile` rows = weeks 1–52 (never leases)  
- Then `location_path` weeks 1–52 (leases when gate hits)  
- Trailing `SUMMARY_*` = Month 1/3/6/12, week-1 drop, ads 1–4, lease, crossover, BOM  

Each week: demand bands, capacity, fulfilled, lost, weekday/weekend plates, **peak_night_orders**, DD + GH counts, channels, **itemized COGS**, revenues, fees, ads, opex, nets.

---

## Phenomenon (not the old timid S-curve)

Jordan shoe / iPhone-style **day-one drop**: front-loaded ads, marketplace volume from night one.

1. Weeks 1–4 spike into **200–600+ plates/week** mid band  
2. **Peak nights:** DD + GH (+ LIVE) — hundreds of orders/night when ads hit  
3. Marketplace **~45–65%** day one (`ch_doordash`, `ch_grubhub`; DD 25%, GH ~27%)  
4. Post-drop: hype decays; habit/loyalty logistic holds a high floor  
5. Kitchen throughput binds — hire hard for the drop; lost sales when demand > capacity  
6. Flyer **50 plates** = marketing scarcity, not this sim's ceiling  

### Week-1 mid

| | |
|--|--|
| Latent mid (low–high) | **{w1['demand_latent']}** ({w1['demand_low_band']}–{w1['demand_high_band']}) |
| Fulfilled | **{w1['plates_fulfilled']}** |
| Peak night | **{w1['peak_night_orders']}** (cap ~{w1['peak_night_capacity']}) |
| DD / GH | **{w1['ch_doordash']}** / **{w1['ch_grubhub']}** (DD+GH={mkt}) |
| Ads W1 / W1–4 | **${w1['opex_ads']}** / **${ads14:.0f}** → {p14} plates |

First capacity bind: {"week "+str(bind['week']) if bind else "none early"}.

---

## Itemized COGS (chicken, greens, supplies)

| Line | $/plate | Source |
|------|---------|--------|
| Chicken 2pc | **${COGS_CHICKEN_2PC}** | RD drums 0.60lb × $0.99 |
| Oil/breading/seasoning | **${COGS_OIL_BREAD_SEASON}** | $0.22+$0.30+$0.10 |
| Collard greens | **${COGS_GREENS}** | greens mid |
| Candied sweet potatoes | **${COGS_SWEETS}** | sides mid |
| Dinner roll | **${COGS_ROLL}** | sides mid |
| Yield/waste bridge | **${COGS_YIELD_WASTE}** | ASSUMPTION → brand food **$3.70** |
| **Food total** | **${COGS_FOOD}** | metrics/ops mid |
| Pack supplies | **${COGS_PACK}** | packaging mid |
| DD/GH bonus sweet | **${DD_BONUS}** | cake/cinnamon |

Weekly columns scale these by `plates_fulfilled`.

---

## 7-day ops · weekend-weighted

`weekday_plates` ≈45% · `weekend_plates` ≈55% · `peak_night_orders` ≈28% of week on biggest night.

## Modes

- **mobile** — drop hire ~50 help hrs; hundreds/night capacity during launch  
- **location_path** — lease when demand ≥{LEASE_GATE}/wk × {LEASE_STREAK} weeks AND cash ≥ ${LEASE_BUF:,.0f}  

Lease week: **{lease}**. Crossover: **{cross}**.

## Rollups (illustrative · NOT financial advice)

| Period | Mobile plates | Mobile net | Loc plates | Loc net |
|--------|---------------|------------|------------|---------|
| M1 | {m1['plates']} | ${m1['net_cash']} | {l1['plates']} | ${l1['net_cash']} |
| M6 | {m6['plates']} | ${m6['net_cash']} | {l6['plates']} | ${l6['net_cash']} |
| M12 | {m12['plates']} | ${m12['net_cash']} | {l12['plates']} | ${l12['net_cash']} |

Also: pickup $20, LIVE $20, overnight $20+$65 (~$4.53 net), local $20+$12 + Drive $9.95, Happy Hour, Plate Club, rewards, drinks later, Mom @$20/hr.

**Illustrative only. Not financial, legal, or tax advice.**
""")

def refresh_metrics(path, mobile, loc, lease, cross):
    if not path.exists(): return
    w1=mobile[0]; m1=month_agg(mobile,1); m6=month_agg(mobile,23); m12=month_agg(mobile,49)
    l6=month_agg(loc,23); l12=month_agg(loc,49)
    ads14=sum(mobile[i]["opex_ads"] for i in range(4))
    mkt=w1["ch_doordash"]+w1["ch_grubhub"]
    bind=next((r["week"] for r in mobile if r["lost_demand"]>5), "")
    lines=path.read_text().strip().splitlines()
    kept=[ln for ln in lines if not (
        "flywheel_" in ln and (ln.startswith("highlight,H3") or ln.startswith("highlight,H4"))
        or ln.startswith("FLYWHEEL_SIM,"))]
    new=[
        f'highlight,H32_flywheel_drop_w1_plates,drop launch week1,plates,{w1["demand_low_band"]},{w1["plates_fulfilled"]},{w1["demand_high_band"]},count,Jordan/iPhone week1 fulfilled mid. NOT financial advice.,calculated,flywheel-drop 2026-09-22',
        f'highlight,H33_flywheel_peak_night_w1,DD+GH+LIVE night,orders,100,{w1["peak_night_orders"]},300,count,Week1 peak_night_orders mid,calculated,flywheel-drop 2026-09-22',
        f'highlight,H34_flywheel_dd_gh_share_w1,marketplace day1,plates,,{mkt},,count,W1 DD={w1["ch_doordash"]} GH={w1["ch_grubhub"]},calculated,flywheel-drop 2026-09-22',
        f'highlight,H35_flywheel_ads_weeks_1_4,drop front-load,USD,,,{ads14},USD,Ads weeks1-4 total,calculated,flywheel-drop 2026-09-22',
        f'highlight,H36_flywheel_mobile_m1_net_cash,mobile Month-1,USD,,,{m1["net_cash"]},USD,Drop M1 cash net before Mom labor,calculated,flywheel-drop 2026-09-22',
        f'highlight,H37_flywheel_mobile_m6_net_cash,mobile Month-6,USD,,,{m6["net_cash"]},USD,Mobile M6 cash net before Mom labor,calculated,flywheel-drop 2026-09-22',
        f'highlight,H38_flywheel_mobile_m12_net_cash,mobile Month-12,USD,,,{m12["net_cash"]},USD,Mobile M12 cash net before Mom labor,calculated,flywheel-drop 2026-09-22',
        f'highlight,H39_flywheel_location_m6_net_cash,location_path M6,USD,,,{l6["net_cash"]},USD,Lease path M6,calculated,flywheel-drop 2026-09-22',
        f'highlight,H40_flywheel_location_m12_net_cash,location_path M12,USD,,,{l12["net_cash"]},USD,Lease path M12,calculated,flywheel-drop 2026-09-22',
        f'highlight,H41_flywheel_lease_gate_week,Phase4,week,,,{lease or ""},count,Demand≥160×8 + 3mo rent,calculated,flywheel-drop 2026-09-22',
        f'highlight,H42_flywheel_crossover_week,location>mobile,week,,,{cross or ""},count,First week location cash > mobile,calculated,flywheel-drop 2026-09-22',
        f'highlight,H43_flywheel_capacity_bind_week,mobile bind,week,,,{bind},count,First material capacity bind,calculated,flywheel-drop 2026-09-22',
        f'highlight,H44_flywheel_bom_food_mid,itemized COGS,USD_per_plate,,,{COGS_FOOD},USD,Chicken+greens+sweets+roll+oil/bread+yield=$3.70,calculated,cogs CSV',
        f'highlight,H45_flywheel_bom_chicken_mid,2pc chicken,USD_per_plate,,,{COGS_CHICKEN_2PC},USD,RD drums from cogs-and-pricing.csv,sourced,2026-09-22',
        'FLYWHEEL_SIM,phenomenon,product_drop_marketplace,flag,1,1,1,flag,Jordan/iPhone drop + DD/GH hundreds/night,policy,2026-09-22',
        f'FLYWHEEL_SIM,week1_latent_mid,drop,plates_per_week,{DROP_W1[0]},{DROP_W1[1]},{DROP_W1[2]},count,Front-loaded launch band,estimate,2026-09-22',
        f'FLYWHEEL_SIM,cogs_chicken_2pc_mid,BOM,USD,{COGS_CHICKEN_2PC},{COGS_CHICKEN_2PC},{COGS_CHICKEN_2PC},USD,cogs-and-pricing.csv,sourced,2026-09-22',
        f'FLYWHEEL_SIM,cogs_greens_mid,BOM,USD,{COGS_GREENS},{COGS_GREENS},{COGS_GREENS},USD,sourced,sourced,2026-09-22',
        f'FLYWHEEL_SIM,cogs_sweets_mid,BOM,USD,{COGS_SWEETS},{COGS_SWEETS},{COGS_SWEETS},USD,sourced,sourced,2026-09-22',
        f'FLYWHEEL_SIM,cogs_roll_mid,BOM,USD,{COGS_ROLL},{COGS_ROLL},{COGS_ROLL},USD,sourced,sourced,2026-09-22',
        f'FLYWHEEL_SIM,cogs_oil_bread_season_mid,BOM,USD,{COGS_OIL_BREAD_SEASON},{COGS_OIL_BREAD_SEASON},{COGS_OIL_BREAD_SEASON},USD,sourced,sourced,2026-09-22',
        'FLYWHEEL_SIM,no_hard_50_cap,policy,flag,1,1,1,flag,50-plate flyer=marketing scarcity only,policy,2026-09-22',
    ]
    path.write_text("\n".join(kept)+"\n"+"\n".join(new)+"\n")

def main():
    mobile,_=simulate(False)
    loc,lease=simulate(True)
    sums,cross=summaries(mobile,loc,lease)
    write_csv(OUT/"ops-simulation-flywheel-demand.csv", mobile, loc, sums)
    write_readme(OUT/"ops-simulation-flywheel-README.md", mobile, loc, lease, cross)
    SITE.mkdir(parents=True, exist_ok=True)
    write_csv(SITE/"ops-simulation-flywheel-demand.csv", mobile, loc, sums)
    write_readme(SITE/"ops-simulation-flywheel-README.md", mobile, loc, lease, cross)
    (SITE/"generate_flywheel_sim.py").write_text((OUT/"generate_flywheel_sim.py").read_text())
    for mp in [OUT/"fifi-comprehensive-metrics.csv", SITE/"fifi-comprehensive-metrics.csv"]:
        refresh_metrics(mp, mobile, loc, lease, cross)
    if BIZ.exists():
        write_csv(BIZ/"ops-simulation-flywheel-demand.csv", mobile, loc, sums)
        write_readme(BIZ/"ops-simulation-flywheel-README.md", mobile, loc, lease, cross)
        (BIZ/"generate_flywheel_sim.py").write_text((OUT/"generate_flywheel_sim.py").read_text())
        refresh_metrics(BIZ/"fifi-comprehensive-metrics.csv", mobile, loc, lease, cross)
    w1=mobile[0]
    print("W1", w1["plates_fulfilled"], w1["peak_night_orders"], w1["ch_doordash"], w1["ch_grubhub"], w1["opex_ads"])
    print("M6", month_agg(mobile,23)["net_cash"], month_agg(loc,23)["net_cash"])
    print("M12", month_agg(mobile,49)["net_cash"], month_agg(loc,49)["net_cash"])
    print("lease", lease, "cross", cross, "rows", len(mobile), len(loc), len(sums))
    return dict(mobile=mobile, loc=loc, lease=lease, cross=cross, w1=w1,
                m6=month_agg(mobile,23), m12=month_agg(mobile,49),
                l6=month_agg(loc,23), l12=month_agg(loc,49),
                ads14=sum(mobile[i]["opex_ads"] for i in range(4)))

if __name__ == "__main__":
    main()
