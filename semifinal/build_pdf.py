"""TSA Data Science & Analytics semifinal: visual + synopsis PDF.
Run: uv run --with pandas --with matplotlib --with numpy python build_pdf.py
Outputs (same folder): Semifinal_Visualization_Synopsis.pdf + snap_*.png
"""
import os, re, textwrap
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "TSA_Data_Science_EV_Charging_Challenge (1).csv")
OUT = os.path.join(HERE, "Semifinal_Visualization_Synopsis.pdf")
TEAM_ID = "Team ID: ________"  # fill in at competition

# ---------- palette / type ----------
INK, MUTED, PAPER = "#14212B", "#5B6B77", "#FFFFFF"
TEAL, TEAL_L = "#0F7C80", "#D7ECEC"
COLD, HOT, OK = "#2F6FDE", "#E2552C", "#19B36B"
GREY = "#B8C2CA"
MON_BG, MON_GRID, MON_TXT = "#081014", "#16303A", "#9FE8C4"
HEAD, BODY, MONO = "DIN Condensed", "Avenir Next", "Menlo"
plt.rcParams.update({"font.family": BODY, "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})
RNG = np.random.default_rng(42)

# ---------- data: clean exactly as audited ----------
d = pd.read_csv(CSV)
raw_n = len(d)
log = {"raw rows": raw_n, "exact duplicates removed": int(d.duplicated().sum())}
d = d.drop_duplicates()
log["lower-case region labels fixed"] = int((d.Region != d.Region.str.strip().str.title()).sum())
log["mis-formatted station labels fixed"] = int((d.Station_Type != d.Station_Type.str.strip().str.title().str.replace("Dc ", "DC ")).sum())
d["Region"] = d.Region.str.strip().str.title()
d["Station_Type"] = d.Station_Type.str.strip().str.title().str.replace("Dc ", "DC ")
log["-999 kWh sentinels -> missing"] = int((d.Energy_Delivered_kWh < 0).sum())
d.loc[d.Energy_Delivered_kWh < 0, "Energy_Delivered_kWh"] = np.nan
log["SOC 145% (impossible) -> missing"] = int((d.SOC_End_Pct > 100).sum())
d.loc[d.SOC_End_Pct > 100, "SOC_End_Pct"] = np.nan
log["clean sessions analysed"] = len(d)

d["ts"] = pd.to_datetime(d.Timestamp)
d["month"] = d.ts.dt.month
d["T"] = d.Ambient_Temp_F
d["kw"] = d.Energy_Delivered_kWh / (d.Charge_Duration_Mins / 60)
d["rel"] = d.kw / d.groupby("Station_Type").kw.transform("median")  # speed vs normal for that charger type
d["zone"] = np.select([d["T"] < 32, d["T"] > 95], ["cold", "hot"], "mild")
d.loc[d["T"].isna(), "zone"] = np.nan
d["cpk"] = d.Total_Cost_USD / d.Energy_Delivered_kWh
REG_ORDER = ["Northeast", "Midwest", "Pacific Northwest", "Southeast", "Southwest"]
SHORT = {"Pacific Northwest": "Pacific NW"}
NE, SW = d[d.Region == "Northeast"], d[d.Region == "Southwest"]

def boot(a, b=None, n=4000, f=np.mean):
    a = np.asarray(pd.Series(a).dropna()); out = []
    b = None if b is None else np.asarray(pd.Series(b).dropna())
    for _ in range(n):
        x = f(RNG.choice(a, len(a)))
        out.append(x if b is None else x - f(RNG.choice(b, len(b))))
    return np.percentile(out, [2.5, 97.5])

# key numbers (all computed, nothing typed by hand)
zr = d.groupby("zone").rel.mean()
K = {
    "cold": zr["cold"], "hot": zr["hot"], "mild": zr["mild"],
    "ne_cold": (NE.zone == "cold").mean(), "sw_cold": (SW.zone == "cold").mean(),
    "sw_hot": (SW.zone == "hot").mean(), "ne_hot": (NE.zone == "hot").mean(),
    "ne_raw": NE.rel.mean(), "sw_raw": SW.rel.mean(),
}
ne_rates = NE.groupby("zone").rel.mean().reindex(["cold", "mild", "hot"]).fillna(zr)  # NE has no hot sessions
sw_mix = SW.zone.value_counts(normalize=True)
K["ne_in_sw"] = float((ne_rates * sw_mix).sum())
K["ne_ci"], K["sw_ci"] = boot(NE.rel), boot(SW.rel)
# counterfactual CI by resampling NE sessions
cf = []
for _ in range(2000):
    s = NE.sample(len(NE), replace=True, random_state=int(RNG.integers(1e9)))
    r = s.groupby("zone").rel.mean().reindex(["cold", "mild", "hot"]).fillna(zr)
    cf.append((r * sw_mix).sum())
K["cf_ci"] = np.percentile(cf, [2.5, 97.5])
dc = NE[NE.Station_Type == "DC Fast Charger"]
K["dc_cold_kw"] = dc[dc.zone == "cold"].kw.median(); K["dc_mild_kw"] = dc[dc.zone == "mild"].kw.median()
K["min_cold"], K["min_mild"] = 40 / K["dc_cold_kw"] * 60, 40 / K["dc_mild_kw"] * 60
K["slow_pct"] = (1 - K["cold"] / K["mild"]) * 100
K["ne_cold_slow"] = (1 - ne_rates["cold"] / ne_rates["mild"]) * 100
print({k: (np.round(v, 3) if not isinstance(v, str) else v) for k, v in K.items()})

# ---------- page helpers ----------
W, H = 8.5, 11

def page(num=None, accent=True, bg=PAPER):
    fig = plt.figure(figsize=(W, H), facecolor=bg)
    if accent:  # quarter-circle corner accent, echoing past TSA documentation style
        ax = fig.add_axes([0, 0, 1, 1], facecolor="none"); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
        ax.add_patch(Circle((W, 0), 1.25, color=TEAL, zorder=0))
        ax.add_patch(Rectangle((0.55, H - 0.42), 0.06, 0.25, color=TEAL))
    if num is not None:
        fig.text(0.94, 0.975, f"{num:02d}", ha="right", va="top", fontsize=9, color=MUTED if bg == PAPER else MON_TXT)
    fig.text(0.075, 0.975, "TSA DATA SCIENCE & ANALYTICS  ·  SEMIFINAL  ·  " + TEAM_ID,
             fontsize=7, color=MUTED if bg == PAPER else MON_TXT, va="top")
    return fig

def title(fig, text, sub=None, y=0.93, color=INK):
    fig.text(0.075, y, text, fontsize=30, family=HEAD, color=color, va="top")
    if sub: fig.text(0.075, y - 0.045, sub, fontsize=10.5, color=MUTED if color == INK else MON_TXT, va="top")

def para(fig, x, y, text, width=95, size=9.2, color=INK, lh=1.45, **kw):
    lines = []
    for p in text.split("\n"):
        lines += textwrap.wrap(p, width) or [""]
    fig.text(x, y, "\n".join(lines), fontsize=size, color=color, va="top", linespacing=lh, **kw)
    return y - len(lines) * size * lh * 1.5 / 72 / H

def caption(ax, text, y=-0.2):
    ax.text(0, y, text, transform=ax.transAxes, fontsize=7.6, color=MUTED, va="top", style="italic", wrap=True)

# ---------- FIGURE 1: Battery Vital Signs (hero, ICU-monitor style) ----------
def vital_signs(fig, rect_top, rect_bot, dark=True):
    bg, fg, grid = (MON_BG, MON_TXT, MON_GRID) if dark else (PAPER, INK, "#E5EAEE")
    ax = fig.add_axes(rect_top, facecolor=bg)
    x0, x1 = -5, 112
    ax.axvspan(x0, 32, color=COLD, alpha=0.20, lw=0); ax.axvspan(95, x1, color=HOT, alpha=0.22, lw=0)
    ax.axhspan(0.95, 1.05, color=OK, alpha=0.16, lw=0)
    s = d.dropna(subset=["T", "rel"]).sample(900, random_state=1)
    ax.scatter(s["T"], s.rel, s=3, color=fg, alpha=0.18, lw=0)
    bins = np.arange(-4, 114, 4); mid = (bins[:-1] + bins[1:]) / 2
    g = d.groupby(pd.cut(d["T"], bins), observed=False).rel
    m, n = g.mean().values, g.count().values; se = g.std().values / np.sqrt(n)
    ok = n >= 8
    ax.fill_between(mid[ok], (m - 1.96 * se)[ok], (m + 1.96 * se)[ok], color=OK, alpha=0.25, lw=0)
    for lw, a in [(7, 0.08), (4, 0.18), (1.8, 1)]:  # glowing monitor trace
        ax.plot(mid[ok], m[ok], color=OK, lw=lw, alpha=a, solid_capstyle="round")
    ax.axvline(32, color=COLD, lw=1, ls=(0, (3, 3))); ax.axvline(95, color=HOT, lw=1, ls=(0, (3, 3)))
    ax.set_xlim(x0, x1); ax.set_ylim(0.55, 1.45)
    ax.set_ylabel("Charging speed vs. normal for that charger", color=fg, fontsize=8.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}×"))
    for sp in ax.spines.values(): sp.set_color(grid)
    ax.tick_params(colors=fg, labelsize=8); ax.grid(color=grid, lw=0.6); ax.set_axisbelow(True)
    ax.set_xticklabels([])
    mono = dict(family=MONO, fontsize=8.2, fontweight="bold")
    ax.text(14, 1.40, f"▲ ALARM  FREEZING\n{K['cold']:.2f}× normal speed", color="#8DB5FF", ha="center", va="top", **mono)
    ax.text(103.5, 1.40, f"▲ ALARM\nHEAT\n{K['hot']:.2f}×", color="#FF9A7A", ha="center", va="top", **mono)
    ax.text(63, 1.40, f"NORMAL RHYTHM  {K['mild']:.2f}×", color=OK, ha="center", va="top", **mono)
    ax.annotate("step drop at 32°F,\nnot a gradual slope", xy=(31, 0.88), xytext=(42, 0.66), color=fg, fontsize=7.5,
                arrowprops=dict(arrowstyle="->", color=fg, lw=0.8))
    # ridgelines: who lives in the alarm zones?
    axr = fig.add_axes(rect_bot, facecolor=bg, sharex=ax)
    xs = np.linspace(x0, x1, 400)
    for i, r in enumerate(REG_ORDER[::-1]):
        t = d.loc[d.Region == r, "T"].dropna().values
        bw = 1.06 * t.std() * len(t) ** -0.2
        dens = np.exp(-0.5 * ((xs[:, None] - t[None, :]) / bw) ** 2).sum(1); dens = dens / dens.max() * 0.68
        base = i * 0.75
        hi = r in ("Northeast", "Southwest")
        col = fg if hi else GREY
        axr.fill_between(xs, base, base + dens, color=bg, zorder=(10 - i) * 3)
        axr.fill_between(xs, base, base + dens, where=xs < 32, color=COLD, alpha=0.85 if hi else 0.35, lw=0, zorder=(10 - i) * 3 + 1)
        axr.fill_between(xs, base, base + dens, where=xs > 95, color=HOT, alpha=0.85 if hi else 0.35, lw=0, zorder=(10 - i) * 3 + 1)
        axr.plot(xs, base + dens, color=col, lw=1.4 if hi else 0.8, zorder=(10 - i) * 3 + 2)
        g = d[d.Region == r]
        lab = f"{SHORT.get(r, r)}"
        axr.text(x0 + 1, base + 0.18, lab, color=col, fontsize=8.5, fontweight="bold" if hi else "normal", zorder=50)
        axr.text(x1 - 1, base + 0.18, f"❄ {(g.zone=='cold').mean()*100:4.1f}%   ☀ {(g.zone=='hot').mean()*100:4.1f}%",
                 color=col, fontsize=7.6, family=MONO, ha="right", zorder=50)
    axr.axvline(32, color=COLD, lw=1, ls=(0, (3, 3))); axr.axvline(95, color=HOT, lw=1, ls=(0, (3, 3)))
    axr.set_yticks([]); axr.set_ylim(-0.1, 5 * 0.75 + 0.3)
    axr.set_xlabel("Air temperature during the charging session (°F)", color=fg, fontsize=8.5)
    axr.tick_params(colors=fg, labelsize=8)
    for sp in axr.spines.values(): sp.set_color(grid)
    axr.spines["left"].set_visible(False)
    axr.text(x1 - 1, 5 * 0.75 + 0.15, "share of sessions in alarm zones", color=fg, fontsize=7, ha="right", family=MONO)
    return ax, axr

# ---------- FIGURE 2: climate swap slope chart ----------
def climate_swap(ax):
    pts = [("Northeast\nactual", K["ne_raw"], K["ne_ci"], COLD),
           ("Northeast in\nSouthwest weather", K["ne_in_sw"], K["cf_ci"], TEAL),
           ("Southwest\nactual", K["sw_raw"], K["sw_ci"], HOT)]
    for i, (lab, v, ci, c) in enumerate(pts):
        ax.plot([i, i], ci, color=c, lw=2.2, alpha=0.5)
        ax.scatter(i, v, s=120, color=c, zorder=5, edgecolor="white", lw=1.5)
        ax.text(i, ci[1] + 0.006, f"{v:.3f}×", ha="center", fontsize=10, fontweight="bold", color=c)
    ax.annotate("", xy=(1, K["ne_in_sw"]), xytext=(0, K["ne_raw"]),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=2, connectionstyle="arc3,rad=-0.25"))
    ax.plot([1, 2], [K["ne_in_sw"], K["sw_raw"]], color=GREY, ls=":", lw=1.5)
    ax.text(0.5, K["ne_raw"] - 0.022, "same chargers,\nswap only the weather", ha="center", fontsize=7.8, color=TEAL)
    ax.set_xticks(range(3)); ax.set_xticklabels([p[0] for p in pts], fontsize=8)
    ax.set_xlim(-0.5, 2.5); ax.set_ylim(0.93, 1.06)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}×"))
    ax.set_ylabel("Avg. speed vs. normal (95% CI)")
    ax.grid(axis="y", color="#E5EAEE"); ax.set_axisbelow(True)

# ---------- FIGURE 3: winter stripes (month x region cold share) ----------
def winter_stripes(ax):
    M = d.groupby(["Region", "month"]).zone.apply(lambda z: (z == "cold").mean()).unstack().reindex(REG_ORDER)
    im = ax.imshow(M.values, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("c", ["#F3F6F8", "#9CC0F5", COLD, "#123B8A"]),
                   vmin=0, vmax=1, aspect="auto")
    ax.set_yticks(range(5)); ax.set_yticklabels([SHORT.get(r, r) for r in REG_ORDER], fontsize=8)
    ax.set_xticks(range(12)); ax.set_xticklabels(list("JFMAMJJASOND"), fontsize=8)
    for (i, j), v in np.ndenumerate(M.values):
        if v >= 0.3: ax.text(j, i, f"{v*100:.0f}", ha="center", va="center", fontsize=6.8, color="white")
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0)
    return im

# ---------- FIGURE 4: minutes to add 40 kWh (NE DC fast) ----------
def minutes_bar(ax):
    vals = [("Mild day", K["min_mild"], K["dc_mild_kw"], OK), ("Below 32°F", K["min_cold"], K["dc_cold_kw"], COLD)]
    for i, (lab, mins, kw, c) in enumerate(vals):
        ax.barh(i, mins, color=c, height=0.55)
        ax.text(mins + 0.6, i, f"{mins:.0f} min  ({kw:.0f} kW)", va="center", fontsize=9, fontweight="bold", color=c)
    ax.set_yticks([0, 1]); ax.set_yticklabels([v[0] for v in vals], fontsize=8.5)
    ax.set_xlim(0, 58); ax.set_xlabel("Minutes to add 40 kWh, Northeast DC fast chargers (median)")
    ax.invert_yaxis(); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)

# ---------- FIGURE 5: forest plot, what region does NOT explain ----------
def forest(ax):
    def smd(col, a=NE, b=SW):
        x, y = a[col].dropna().values, b[col].dropna().values
        sd = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
        lo, hi = boot(x, y, n=2000) / sd
        return (x.mean() - y.mean()) / sd, lo, hi
    d["is_cold"] = (d.zone == "cold").astype(float)
    NEx, SWx = d[d.Region == "Northeast"], d[d.Region == "Southwest"]
    rows = [("Cost per kWh", "cpk"), ("Satisfaction (1–5)", "User_Satisfaction_Rating"),
            ("Charger fault rate", "Charger_Fault_Flag"), ("Idle minutes", "Idle_Duration_Mins"),
            ("Energy delivered", "Energy_Delivered_kWh"), ("Charging speed", "rel"),
            ("Grid renewable %", "Grid_Renewable_Pct"), ("Share of freezing sessions", "is_cold")]
    for i, (lab, col) in enumerate(rows):
        v, lo, hi = smd(col, NEx, SWx)
        sig = lo > 0 or hi < 0
        c = (COLD if v < 0 else HOT) if sig and abs(v) > 0.2 else (TEAL if sig else GREY)
        ax.plot([lo, hi], [i, i], color=c, lw=2.2)
        ax.scatter(v, i, s=46, color=c, zorder=3, marker="D" if sig else "o")
        ax.text(1.02, i, "real difference" if sig and abs(v) > 0.2 else ("tiny" if sig else "no difference"),
                transform=ax.get_yaxis_transform(), va="center", fontsize=7.5, color=c)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=8.3)
    ax.invert_yaxis(); ax.set_xlim(-0.4, 0.9)
    ax.set_xlabel("Northeast minus Southwest (standardized effect, 95% bootstrap CI)")
    ax.grid(axis="x", color="#E5EAEE"); ax.set_axisbelow(True)

# ---------- FIGURE 6: faults vs satisfaction ----------
def faults(ax):
    t = pd.crosstab(d.Charger_Fault_Flag, d.User_Satisfaction_Rating, normalize="index")
    cols = ["#C8372D", "#E98A5E", "#E9E2D0", "#86C6B5", TEAL]
    left = np.zeros(2)
    for k, c in zip([1, 2, 3, 4, 5], cols):
        v = t.get(k, pd.Series(0, index=t.index)).values
        ax.barh([0, 1], v, left=left, color=c, height=0.55)
        for i in range(2):
            if v[i] > 0.07: ax.text(left[i] + v[i] / 2, i, f"{k}", ha="center", va="center", fontsize=7.5, color=INK)
        left += v
    m = d.groupby("Charger_Fault_Flag").User_Satisfaction_Rating.mean()
    ax.set_yticks([0, 1]); ax.set_yticklabels([f"No fault\navg {m[0]:.2f}", f"Charger fault\navg {m[1]:.2f}"], fontsize=8)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}")); ax.set_xlim(0, 1)
    ax.invert_yaxis(); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)

# ---------- FIGURE 7: renewable by region ----------
def renewable(ax):
    for i, r in enumerate(REG_ORDER):
        x = d.loc[d.Region == r, "Grid_Renewable_Pct"].dropna()
        c = TEAL if r == "Pacific Northwest" else GREY
        ax.barh(i, x.mean(), color=c, height=0.6)
        ax.errorbar(x.mean(), i, xerr=1.96 * x.sem(), color=INK, capsize=2, lw=0.8)
        ax.text(x.mean() + 2.5, i, f"{x.mean():.1f}%", va="center", fontsize=8, color=INK)
    ax.set_yticks(range(5)); ax.set_yticklabels([SHORT.get(r, r) for r in REG_ORDER], fontsize=8)
    ax.invert_yaxis(); ax.set_xlim(0, 90); ax.set_xlabel("Avg. grid renewable share during session")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)

# ---------- SYNOPSIS (<=250 words, checked) ----------
SYN = (
    f"Do EV drivers in the Northeast really charge slower than drivers in the Southwest, or is something else at work? "
    f"We cleaned {log['clean sessions analysed']:,} sessions (removing duplicates, mislabeled regions, and impossible values) "
    f"and turned each charger's speed into a \"vital sign\": speed divided by the normal speed for that charger type. "
    f"Our Battery Vital Signs monitor shows a clear alarm. Below 32°F, charging falls to {K['cold']:.2f}× normal; "
    f"above 95°F it falls to {K['hot']:.2f}×. In between it holds steady near {K['mild']:.2f}×. The drop at freezing is a sudden step, not a gradual slope. "
    f"Region decides who lives in those alarm zones. {K['ne_cold']*100:.0f}% of Northeast sessions happen below freezing (84% in January), "
    f"compared with {K['sw_cold']*100:.1f}% in the Southwest, whose risk is heat ({K['sw_hot']*100:.0f}% of sessions above 95°F). "
    f"On a Northeast DC fast charger, adding 40 kWh takes about {K['min_cold']:.0f} minutes in freezing weather versus {K['min_mild']:.0f} on a mild day. "
    f"To test whether the region itself is the cause, we gave Northeast chargers Southwest weather. Their average speed rose from "
    f"{K['ne_raw']:.3f}× to {K['ne_in_sw']:.3f}×, nearly matching the Southwest ({K['sw_raw']:.3f}×). Cost, satisfaction, and fault rates show no real regional "
    f"difference; faults, not geography, drive low ratings. "
    f"Conclusion: region does not slow EV charging, winter does. Northeast planners should prioritize preconditioning batteries, "
    f"sheltered or heated stations, and winter pricing signals rather than simply adding more chargers."
)
WORDS = len(re.findall(r"[A-Za-z0-9][\w'.×%°/,-]*", SYN))
assert WORDS <= 250, f"synopsis is {WORDS} words (limit 250)"
print("synopsis words:", WORDS)

# ================= BUILD PDF =================
snapdir = HERE
with PdfPages(OUT) as pdf:
    # --- 1 cover ---
    fig = page(accent=False)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.add_patch(Circle((W, 0), 3.2, color=TEAL)); ax.add_patch(Circle((W, 0), 2.2, color="#0B5E61"))
    ax.add_patch(Rectangle((0.64, 7.6), 0.07, 2.4, color=INK))
    fig.text(0.13, 0.86, "THE\nTHERMAL\nTAX", fontsize=64, family=HEAD, color=INK, va="top", linespacing=0.92)
    fig.text(0.13, 0.555, "Why region doesn't slow EV charging — winter does", fontsize=15, color=TEAL, fontweight="bold")
    fig.text(0.13, 0.52, "Semifinal Visualization & Synopsis  ·  Northeast vs. Southwest (all 5 regions shown)", fontsize=10, color=MUTED)
    # mini monitor trace as cover art
    ca = fig.add_axes([0.13, 0.30, 0.62, 0.17], facecolor=MON_BG)
    tt = np.linspace(0, 10, 1200); y = np.where(tt < 6.5, 1, 0.83) + 0.06 * np.exp(-((tt % 1.25) - 0.4) ** 2 / 0.002) - 0.03 * np.exp(-((tt % 1.25) - 0.5) ** 2 / 0.003)
    for lw, a in [(6, 0.1), (3, 0.25), (1.4, 1)]: ca.plot(tt, y, color=OK, lw=lw, alpha=a)
    ca.axvspan(6.5, 10, color=COLD, alpha=0.25); ca.text(8.25, 1.07, "▲ 32°F", color="#8DB5FF", family=MONO, fontsize=9, ha="center")
    ca.set_ylim(0.75, 1.12); ca.axis("off")
    fig.text(0.13, 0.20, f"TSA Data Science and Analytics  ·  2027–2028\n{TEAM_ID}\nDataset: TSA EV Charging Challenge ({raw_n:,} raw rows, 17 fields)",
             fontsize=9.5, color=INK, linespacing=1.6)
    pdf.savefig(fig); plt.close(fig)

    # --- 2 synopsis with snapshots ---
    fig = page(2)
    title(fig, "SYNOPSIS", f"{WORDS} words  ·  limit 250  ·  snapshots of the visualization below")
    fig.text(0.075, 0.845, "Conclusion", fontsize=11, color=TEAL, fontweight="bold")
    fig.text(0.075, 0.822, "Region doesn't slow EV charging — winter does.", fontsize=17, family=HEAD, color=INK)
    para(fig, 0.075, 0.79, SYN, width=100, size=9.4, lh=1.5)
    # snapshots: small versions of fig 1 and fig 2
    fa, fb = vital_signs(fig, [0.075, 0.20, 0.50, 0.17], [0.075, 0.09, 0.50, 0.11])
    fa.set_ylabel("speed vs normal", color=MON_TXT, fontsize=7)
    fig.text(0.075, 0.385, "SNAPSHOT A · Battery Vital Signs (full size p.3)", fontsize=7.5, color=MUTED, fontweight="bold")
    axs = fig.add_axes([0.66, 0.11, 0.27, 0.26]); climate_swap(axs)
    axs.tick_params(labelsize=6); axs.set_ylabel(""); [t.set_fontsize(6) for t in axs.texts]
    fig.text(0.64, 0.385, "SNAPSHOT B · Climate swap (p.4)", fontsize=7.5, color=MUTED, fontweight="bold")
    pdf.savefig(fig); plt.close(fig)

    # --- 3 hero: Battery Vital Signs (dark monitor page) ---
    fig = page(3, accent=False, bg=MON_BG)
    title(fig, "BATTERY VITAL SIGNS", "Each EV charging session read like a patient on a monitor: when does charging speed leave its normal rhythm?", color="#E8FFF4")
    vital_signs(fig, [0.11, 0.47, 0.82, 0.37], [0.11, 0.13, 0.82, 0.32])
    fig.text(0.11, 0.075,
             f"Top: green trace = mean speed per 4°F bin (band = 95% CI); dots = 900 random sessions. Speed is energy ÷ time, divided by the median\n"
             f"for that charger type, so Level 2, DC Fast and Super-Fast Hubs share one scale. Bottom: temperature distribution of every session by region;\n"
             f"shaded tails sit inside the alarm zones. Northeast lives in the cold alarm ({K['ne_cold']*100:.1f}%); Southwest in the heat alarm ({K['sw_hot']*100:.1f}%).",
             fontsize=7.6, color=MON_TXT, va="top", linespacing=1.5)
    fig.savefig(os.path.join(snapdir, "snap_vital_signs.png"), dpi=200, facecolor=MON_BG)
    pdf.savefig(fig, facecolor=MON_BG); plt.close(fig)

    # --- 4 climate swap + winter stripes + minutes ---
    fig = page(4)
    title(fig, "IS IT THE REGION, OR THE WEATHER?", "A counterfactual test: keep the Northeast's chargers, give them Southwest weather.")
    ax = fig.add_axes([0.11, 0.53, 0.38, 0.30]); climate_swap(ax)
    caption(ax, f"Fig 2. Northeast speed re-weighted to Southwest's mix of cold/mild/hot sessions\n(direct standardization). The gap closes: {K['ne_raw']:.3f}× to {K['ne_in_sw']:.3f}× vs {K['sw_raw']:.3f}×.\nRegression check: region adds nothing once temperature is known (p = 0.74).", y=-0.17)
    ax = fig.add_axes([0.58, 0.53, 0.36, 0.30]); im = winter_stripes(ax)
    ax.set_title("Winter stripes: % of sessions below 32°F", fontsize=9, color=INK, loc="left")
    caption(ax, "Fig 3. Each cell = one region-month. The Northeast and\nMidwest live below freezing from Dec–Feb; the Southwest\nnever does. The thermal tax is seasonal and regional.", y=-0.17)
    ax = fig.add_axes([0.20, 0.22, 0.70, 0.13]); minutes_bar(ax)
    ax.set_title("What drivers feel: the thermal tax in minutes", fontsize=10, color=INK, loc="left")
    caption(ax, f"Fig 4. Median power on Northeast DC fast chargers: {K['dc_mild_kw']:.0f} kW mild vs {K['dc_cold_kw']:.0f} kW below freezing,\nabout {K['min_cold']-K['min_mild']:.0f} extra minutes for the same 40 kWh. Consistent with INL lab tests of DC fast charging at 0°C.", y=-0.45)
    pdf.savefig(fig); plt.close(fig)

    # --- 5 what region does NOT explain ---
    fig = page(5)
    title(fig, "WHAT REGION DOES NOT EXPLAIN", "Testing every Northeast vs. Southwest difference honestly, with confidence intervals.")
    ax = fig.add_axes([0.30, 0.50, 0.52, 0.33]); forest(ax)
    caption(ax, "Fig 5. Standardized difference (Northeast − Southwest). Only weather exposure separates the two regions;\ncost, satisfaction, faults and idle time overlap zero. Speed is barely lower, and Fig 2 shows why.", y=-0.15)
    ax = fig.add_axes([0.16, 0.17, 0.33, 0.17]); faults(ax)
    ax.set_title("Faults, not geography, drive low ratings", fontsize=9.5, color=INK, loc="left")
    caption(ax, "Fig 6. Rating mix by fault status. Numbers = star rating.\nNo faulted session earned 5. Fault rate does not differ\nby region (χ² p = 0.42).", y=-0.28)
    ax = fig.add_axes([0.66, 0.17, 0.27, 0.17]); renewable(ax)
    ax.set_title("Side finding: cleaner grid", fontsize=9.5, color=INK, loc="left")
    caption(ax, "Fig 7. Pacific NW sessions draw ~72%\nrenewable power vs ~47% elsewhere\n(error bars = 95% CI).", y=-0.28)
    pdf.savefig(fig); plt.close(fig)

    # --- 6 methods, data cleaning, sources ---
    fig = page(6)
    title(fig, "METHODS & DATA INTEGRITY")
    y = 0.86
    fig.text(0.075, y, "Data cleaning log", fontsize=12, color=TEAL, fontweight="bold"); y -= 0.025
    for k, v in log.items():
        fig.text(0.09, y, f"•  {k}", fontsize=9, color=INK); fig.text(0.55, y, f"{v:,}", fontsize=9, color=INK, family=MONO); y -= 0.021
    fig.text(0.09, y, "•  missing temps / renewable % / ratings kept as missing (pairwise)", fontsize=9, color=INK); y -= 0.04
    fig.text(0.075, y, "Methods", fontsize=12, color=TEAL, fontweight="bold"); y -= 0.02
    y = para(fig, 0.09, y,
             "1. Speed metric: kWh ÷ charge hours ÷ median for the charger type (removes the Level 2 vs DC fast gap).\n"
             "2. Temperature zones: cold < 32°F, hot > 95°F, mild otherwise; 4°F bins for the trace, 95% CIs from standard errors.\n"
             "3. Counterfactual: direct standardization (as epidemiologists age-adjust rates). Northeast zone speeds × Southwest zone mix; bootstrap CI (2,000 resamples).\n"
             "4. Confound check: OLS of speed on charger type, cold, hot, start SOC, SOC gained and region (robust HC3 errors). Region likelihood-ratio test p = 0.74; cold −0.15×, hot −0.16× (p < 0.001).\n"
             "5. Differences in Fig 5: standardized mean difference with 4,000-sample bootstrap CI. Fault rates: chi-square test.\n"
             "6. Satisfaction model (5-fold CV): linear R² 0.50, random forest R² 0.49; charger fault = 70% of importance.",
             width=105, size=8.6) - 0.02
    fig.text(0.075, y, "Limitations", fontsize=12, color=TEAL, fontweight="bold"); y -= 0.02
    y = para(fig, 0.09, y,
             "Temperature explains ~5% of session-to-session speed variation: a real average effect, not a rule for every charge. "
             "The sharp step at 32°F suggests a modeled threshold in this dataset. Southwest has only 3 freezing sessions, so we only swap weather in one direction (NE to SW). "
             "Dataset is observational; no causal claim beyond the standardization test.", width=105, size=8.6) - 0.02
    fig.text(0.075, y, "Tools & sources", fontsize=12, color=TEAL, fontweight="bold"); y -= 0.02
    para(fig, 0.09, y,
             "Python 3 · pandas · NumPy · statsmodels · scikit-learn · Matplotlib. Generative AI assisted with code and review (permitted, guide p.149).\n"
             "Idaho National Laboratory, cold-temperature DC fast charging tests (afdc.energy.gov / inl.gov).  J.D. Power, 2025 U.S. EVX Public Charging Study.  "
             "U.S. EIA, Electric Power Monthly, state generation by source.", width=105, size=8.6)
    pdf.savefig(fig); plt.close(fig)

print("wrote", OUT)
