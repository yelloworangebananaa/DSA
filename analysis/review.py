"""Independent scientific review of EV charging findings. Run: uv run --with pandas --with scipy --with statsmodels --with scikit-learn python review.py"""
import sys, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy import stats
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
np.random.seed(42)
d = pd.read_csv(sys.argv[1]).drop_duplicates()
d['Region'] = d.Region.str.strip().str.title().str.replace('Pacific Northwest', 'PNW')
d['ST'] = d.Station_Type.str.strip().str.title()
d.loc[d.Energy_Delivered_kWh < 0, 'Energy_Delivered_kWh'] = np.nan
d.loc[d.SOC_End_Pct > 100, 'SOC_End_Pct'] = np.nan
d['ts'] = pd.to_datetime(d.Timestamp); d['hour'] = d.ts.dt.hour; d['month'] = d.ts.dt.month
d['kw'] = d.Energy_Delivered_kWh / (d.Charge_Duration_Mins / 60)
d['rel'] = d.kw / d.groupby('ST').kw.transform('median')
d['cpk'] = d.Total_Cost_USD / d.Energy_Delivered_kWh
d['T'] = d.Ambient_Temp_F; d['cold'] = (d['T'] < 32).astype(int); d['hot'] = (d['T'] > 95).astype(int)
d['dSOC'] = d.SOC_End_Pct - d.SOC_Start_Pct
print("rows", len(d)); print(d.groupby('ST').kw.describe().round(1))

def boot_ci(a, b, n=2000):
    a, b = a.dropna().values, b.dropna().values
    diffs = [np.random.choice(a, len(a)).mean() - np.random.choice(b, len(b)).mean() for _ in range(n)]
    return np.round(np.percentile(diffs, [2.5, 97.5]), 3)

def cohend(a, b):
    a, b = a.dropna(), b.dropna(); s = np.sqrt(((len(a)-1)*a.var() + (len(b)-1)*b.var()) / (len(a)+len(b)-2))
    return round((a.mean() - b.mean()) / s, 2)

print("\n== H1 cold penalty, per station type (rel speed) ==")
for st, g in d.groupby('ST'):
    c, w = g[g.cold == 1].rel, g[(g.cold == 0) & (g.hot == 0)].rel
    print(f"{st:16s} cold {c.mean():.3f} (n={c.count()}) mild {w.mean():.3f} d={cohend(c,w)} CI={boot_ci(c,w)} p={stats.mannwhitneyu(c.dropna(),w.dropna()).pvalue:.1e}")

print("\n== H1b step or slope? rel by 4F bins around 32 ==")
b = pd.cut(d['T'], [-5, 16, 24, 28, 32, 36, 40, 48, 60, 80, 95, 100, 115])
print(d.groupby(b, observed=True).rel.agg(['mean', 'count']).round(3).T)

print("\n== H2 OLS: does region matter AFTER temperature? (rel speed) ==")
m0 = smf.ols('rel ~ C(ST) + C(Region)', d).fit()
m1 = smf.ols('rel ~ C(ST) + cold + hot + SOC_Start_Pct + dSOC + C(Region)', d).fit(cov_type='HC3')
m2 = smf.ols('rel ~ C(ST) + cold + hot + SOC_Start_Pct + dSOC', d.loc[m1.model.data.row_labels]).fit(cov_type='HC3')
print("region-only R2", round(m0.rsquared, 3), "| full R2", round(m1.rsquared, 3), "| w/o region R2", round(m2.rsquared, 3))
print(m1.summary().tables[1])
print("LR test region adds?", m1.compare_lr_test(m2) if hasattr(m1, 'compare_lr_test') else '')
print(m1.wald_test_terms(scalar=True).table.round(4))

print("\n== H3 NE vs SW + standardization ==")
ne, sw = d[d.Region == 'Northeast'], d[d.Region == 'Southwest']
print("raw NE", round(ne.rel.mean(), 3), "SW", round(sw.rel.mean(), 3), "CI(NE-SW)", boot_ci(ne.rel, sw.rel), "d", cohend(ne.rel, sw.rel))
zone = lambda x: np.select([x < 32, x > 95], ['cold', 'hot'], 'mild')
d['zone'] = zone(d['T'])
rates = d[d.Region == 'Northeast'].groupby('zone').rel.mean()
rates = rates.reindex(['cold', 'mild', 'hot']).fillna(d.groupby('zone').rel.mean())  # NE has no hot sessions: borrow pooled hot rate
mix_sw = d[d.Region == 'Southwest'].zone.value_counts(normalize=True)
print("NE zone rates", rates.round(3).to_dict(), "| SW mix", mix_sw.round(3).to_dict())
print("NE standardized to SW climate:", round((rates * mix_sw).sum(), 3))
for r, g in d.groupby('Region'):
    print(f"  {r:10s} cold%={g.cold.mean()*100:4.1f} hot%={g.hot.mean()*100:4.1f} rel={g.rel.mean():.3f}")
tab = pd.crosstab(d.Region, d.zone); print("chi2 region x zone p=", stats.chi2_contingency(tab)[1])

print("\n== H4 real-world impact: NE DC fast minutes per 40 kWh ==")
dc = d[(d.Region == 'Northeast') & (d.ST == 'Dc Fast Charger')]
for z, g in dc.groupby('zone'): print(z, "kW", round(g.kw.median(), 1), "min/40kWh", round(40 / g.kw.median() * 60, 1), "n", len(g))

print("\n== H5 renewable by region, CI ==")
for r, g in d.groupby('Region'):
    x = g.Grid_Renewable_Pct.dropna(); print(f"  {r:10s} {x.mean():.1f} ±{1.96*x.sem():.1f} n={len(x)}")

print("\n== H6 satisfaction model: baseline vs linear vs RF (5-fold CV R2) ==")
s = d.dropna(subset=['User_Satisfaction_Rating', 'T', 'cpk', 'Idle_Duration_Mins', 'rel'])
X = pd.get_dummies(s[['Charger_Fault_Flag', 'T', 'cpk', 'Idle_Duration_Mins', 'rel', 'Charge_Duration_Mins', 'Region', 'ST', 'Membership_Tier']], drop_first=True).astype(float)
y = s.User_Satisfaction_Rating; kf = KFold(5, shuffle=True, random_state=42)
print("baseline(mean) R2 = 0 by definition")
print("linear", cross_val_score(LinearRegression(), X, y, cv=kf, scoring='r2').mean().round(3))
rf = RandomForestRegressor(300, min_samples_leaf=10, random_state=42)
print("RF    ", cross_val_score(rf, X, y, cv=kf, scoring='r2').mean().round(3))
rf.fit(X, y); print(pd.Series(rf.feature_importances_, X.columns).nlargest(6).round(3).to_dict())
f1, f0 = s[s.Charger_Fault_Flag == 1].User_Satisfaction_Rating, s[s.Charger_Fault_Flag == 0].User_Satisfaction_Rating
print("fault sat", round(f1.mean(), 2), "vs", round(f0.mean(), 2), "d", cohend(f1, f0), "CI", boot_ci(f1, f0))
print("fault rate by region", d.groupby('Region').Charger_Fault_Flag.mean().round(3).to_dict(), "chi2 p", round(stats.chi2_contingency(pd.crosstab(d.Region, d.Charger_Fault_Flag))[1], 3))
print("fault cold vs not", d.groupby('cold').Charger_Fault_Flag.mean().round(3).to_dict())

print("\n== H7 cold hours: when do NE cold sessions happen ==")
print(ne[ne.cold == 1].hour.value_counts().sort_index().to_dict())
print("cold by month NE", ne.groupby('month').cold.mean().round(2).to_dict())
