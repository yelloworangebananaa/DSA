# EV Charging Real-World Context (for TSA Data Science)

Source tags: **[Gov]** = federal or national lab, **[Peer]** = peer-reviewed, **[Ind]** = industry or press. Retrieved Nov 2026.

## 1. Cold temperature and charging speed

- **[Peer/Gov] INL, *Energy Policy* 122 (2018):** The study covered about 500 DC fast charges (50 kW, Nissan Leaf taxis) at 15–103°F. At 25°C, a session reached about 80% in 30 min. At 0°C, the same session ended with about 36% less charge. In the coldest conditions, charging ran about **3x slower**, because the battery management system limits current to protect a cold pack. Abstract: https://www.osti.gov/pages/biblio/1477732 ; figures as reported: https://www.techbriefs.com/component/content/article/33002-ev-charging-in-cold-temperatures-could-pose-challenges-for-drivers
- **[Ind] Recurrent (224,066 Tesla Model 3 fast-charge visits):** At 0°F, a session took only about **9 min longer** on average. Without preconditioning, the first 30–45 min of a session may add almost no charge. Separately, Recurrent measured a 29.7% average winter range loss. https://www.recurrentauto.com/research/study-ev-charging-speeds-in-cold-temperatures
- **[Gov-affiliated] Univ. of Alaska ACEP:** A Chevy Bolt charged at about half of a 50 kW charger's rating near -16°C (3°F). Below freezing, cold-pack limits favor slow AC charging. https://www.uaf.edu/acep/files/projects/Cold-Weather-Issues-for-EVs-in-Alaska.pdf
- **Level 2:** Public data is thin. Level 2 runs at 7–19 kW, well below the pack's acceptance limit, so a cold battery throttles it much less than DC fast charging. The main loss is energy spent heating the pack and a slow start. FLO (an industry source) analyzed 2,230 Montreal stations and found that colder temperatures lengthened sessions on **both** Level 2 and DC fast chargers. https://www.recurrentauto.com/research/cold-weather-winter-ev-charging-lessons-tested
- **Takeaway for the dataset:** A plausible dataset shows DC fast sessions taking clearly longer below about 0°C, while Level 2 sessions change only modestly.

## 2. Charger reliability and satisfaction

- **[Ind] J.D. Power 2025 EVX Public Charging Study (n=7,428, Jan–Jun 2025):** **14%** of visits ended without a charge, down from about 19–20% the year before. Broken or out-of-service equipment caused **60%** of the failed visits. Satisfaction on a 1,000-point scale was **654 for DC fast** and **607 for Level 2**. Cost satisfaction fell 16 points and was the lowest-rated DC fast factor. https://www.jdpower.com/business/press-releases/2025-us-electric-vehicle-experience-evx-public-charging-study ; scores: https://insideevs.com/news/768900/ev-public-charging-reliability-2025/
- **[Ind] Regional failure rates (J.D. Power 2025):** The **Pacific region had the highest failed-visit rate at 21%**, and East South Central had the lowest at 7%. https://driveteslacanada.ca/?p=106842
- **[Peer] Rempel et al., UC Berkeley (Human Factors, 2023):** Testers checked 657 non-Tesla DC fast connectors in the SF Bay Area in 2022. **27.5% did not work.** Electrify America disputed the method. https://electrek.co/2022/06/16/study-finds-more-than-fourth-charging-stations-were-non-functional/
- **[Ind] Paren Reliability Index:** The Q2 2025 national index was 85.5. The top states scored about 93–94%. https://electrek.co/2025/04/22/us-dc-fast-charging-network-surges-past-55k-ports-more-reliable/

## 3. Regional electricity price and renewable share

**[Gov] EIA Electric Power Monthly.** Renewable share below = (hydro + wind + utility-scale solar) / total utility-scale generation, Jan–Aug 2026 YTD. It excludes biomass and geothermal, and it reflects in-state generation, not imports.

| Region (state) | Residential ¢/kWh (Aug 2026) | Commercial ¢/kWh | Hydro share | Hydro+wind+solar share |
|---|---|---|---|---|
| Pacific NW (WA) | 14.63 | 11.81 | 73% | **~81%** |
| Pacific NW (OR) | 15.92 | 10.72 | 49% | ≥64% (hydro + wind only) |
| Southeast (GA) | 15.90 | 13.81 | 1.7% | **~10%** |
| Southeast (FL) | 14.99 | 11.35 | 0.1% | ~11% |
| Northeast (MA) | **30.48** | 24.11 | 4% | ~24% |
| Northeast (NY) | 28.65 | 23.06 | 19% | ≥24% (hydro + wind only) |
| U.S. | 18.16 | 14.47 | 5.9% | ~25% |

Prices: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a · Total generation: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_1_3_b · Hydro: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_1_10_b · Wind: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_1_14_b · Solar: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_1_17_b

- **[Gov]** Washington produced **25% of all U.S. utility-scale hydropower** in 2024, more than any other state. https://www.eia.gov/state/print.php?sid=WA
- **Pattern:** Pacific NW combines cheap power with high renewable share from hydro. The Northeast has the highest prices and mid-range renewables. The Southeast has middling prices and the lowest renewable share, since natural gas is Georgia's primary source. https://www.eia.gov/electricity/state/georgia/

## 4. DC fast vs Level 2 cost and idle fees

- **[Ind] Paren, DC fast national average:** **$0.49/kWh** in Q3 2025, with most states at $0.48–0.54, Nebraska lowest at $0.42 and Hawaii highest at $0.85. https://evmagz.com/?p=127032 . By Q3 2026 the average had risen to **$0.54/kWh**. https://evwire.com/p/us-ev-fast-charging-network-q3-2026-paren-report
- **[Ind] Public Level 2:** typically **$0.20–0.35/kWh**, or $1–3/hour where billing is by time. https://www.energysage.com/ev-charging/ev-home-charging-vs-public-charging
- **[Gov] NREL baseline:** With a realistic mix of home, work and public charging, EV owners pay 8–27¢/kWh, about 15¢ on average. Using only DC fast chargers raises the average to about 18¢ (2020 data, mostly home charging). https://www.nrel.gov/news/press/2020/research-determines-financial-benefit-from-driving-electric-vehicles.html
- **[Ind] Idle fees:** Tesla charges $0.50/min, which can double to $1.00/min when a station is full. Idle fees apply only when a station is at least 50% occupied, after a 5-min grace period. https://www.tesla.com/support/supercharger-idle-fee . Electrify America says idle fees "may be imposed" after the session ends. https://www.electrifyamerica.com/pricing/ . Industry guides cite **$0.40–1.00+/min** for DC fast chargers.

## 5. Benchmarks to sanity-check the dataset

1. **About 14% failed visits nationally, and about 21% in the Pacific region** (J.D. Power 2025). Dataset fault rates far above or below this range need explanation.
2. **DC fast price about $0.49–0.54/kWh vs Level 2 about $0.20–0.35/kWh.** DC fast should cost roughly 1.5–2.5x Level 2.
3. **DC fast satisfaction is higher than Level 2 (654 vs 607 out of 1,000)**, and cost is the lowest-rated factor.
4. **Grid renewable share: Pacific NW about 65–80%, Northeast about 24%, Southeast about 10%, U.S. about 25%** (EIA).
5. **Cold effect: near 0°C, DC fast delivers about one-third less energy per 30 min, and up to 3x slower when very cold (INL). Level 2 changes far less.**

**Caveat:** The team's data is synthetic. Use these numbers to judge plausibility, not as ground truth. When writing the synopsis, label industry surveys as industry sources.
