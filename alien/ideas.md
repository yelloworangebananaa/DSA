# Visual/Synopsis Concepts — EV Charging (alien-ideas, quick mode)

Data facts used (verified on cleaned data, n = 2,500):
- Speed vs station-type norm: <32°F = 0.87×, otherwise 1.02×. Second dip >95°F (0.87×, n=58).
- Share of sessions below freezing: Northeast 24.7%, Midwest 22.8%, PNW 11.3%, Southeast 11.3%, Southwest 0.6%.
- Southwest: 11.7% of sessions >95°F.
- NE DC fast: 59 kW cold vs 75 kW mild.
- PNW renewable 71.5% vs ~47% everywhere else.
- Fault -> satisfaction 2.22 vs 4.51. Cost, idle, fault rate, satisfaction do NOT differ by region (p > 0.15).

## 1. "Battery Vital Signs" (A10 vital monitor + A14 dose-response + A19 ridgeline)
ICU-monitor styling. Speed-vs-temperature curve drawn as a monitor trace, a green "normal band" (0.95–1.05×), red alarm zones below 32°F and above 95°F. Under it, ridgelines of each region's temperature distribution: Northeast's mass sits in the cold alarm zone, Southwest's in the heat zone.
Bottleneck: temperature exposure, not region. Opportunity: explanation gap. Method: empirical mapping.

## 2. "Give the Northeast Arizona's Weather" (A4 slope + A6 standardization + A14 dose-response) — also β=0.4 safe pick
Fit the speed-vs-temperature curve, then re-weight Northeast sessions to Southwest's temperature mix. A slope chart shows the Northeast's raw speed moving to its climate-adjusted speed, and the gap closes. This proves the climate, not the chargers, causes the slowdown.
Opportunity: puzzle (looks identical on average). Method: formal derivation.

## 3. "Averages Lie" (A6 standardization + A7 reversal reveal + A8 24h clock)
Panel 1: the year-round averages, where all regions look the same. Panel 2: split by freezing, and the Northeast gap appears. Panel 3: a radial clock of when cold sessions happen (early-morning commuters).
Note: there is no true Simpson flip here, only masking. Call it "masking", not "Simpson's paradox".
Opportunity: evidence gap. Method: relax scope.

## 4. "Charging Nutrition Label" (A7 reveal + A11 label panel + A15 forest plot)
Each region gets an FDA-style label: kWh, $/kWh, minutes, idle, fault risk "1 in 14", renewable %. A forest plot beside the labels shows every regional difference crossing zero except renewable % and freezing exposure.
Opportunity: failure/risk gap. Method: artifact.

## 5. "The Charging Journey" (A4 slope + A17 journey map + A19 ridgeline)
Stages run plug-in → charge → idle → pay, with ridgelines per stage for Northeast vs Southwest. This is weaker: only the charge stage differs.

Not done (quick mode): neighbor search, literature check, blind tournament vs baseline.
