# mobility-in-sousse-research
# 🚐 Kalaa Kebira → Beb Bhar — Urban Mobility Study
### Predicting shared taxi demand and diagnosing service failures on Sousse's most-used informal transit corridor


## The Problem

The city of Sousse has a formal bus network, but chronic unreliability — irregular schedules, long gaps, and unpredictable service — has pushed the majority of daily commuters toward **shared taxis (louages)** as their primary means of transport.

On the **Kalaa Kebira → Beb Bhar corridor**, louages are the de facto public transit system. Yet they operate with no schedule, no coordination, and no data. The result: passengers can wait 5 minutes or 40 minutes with no way to know which it will be. During peak hours, when a louage finally arrives after a long gap, the rush of passengers means many are left behind and the wait resets.

This project studies that system — rigorously and from the ground up — to understand *why* waits are long, *when* they are worst, and *what interventions* would have the highest impact.

---

## Research Questions

1. At which stations and time slots is demand consistently outpacing supply?
2. Which of the four service failure types dominates — and does it vary by location and hour?
3. Can we predict passenger demand 30–60 minutes ahead with sufficient accuracy to be operationally useful?
4. What is the measurable contribution of bus unreliability to louage overcrowding?
5. What low-cost interventions (scheduling coordination, physical infrastructure, signage) would close the gap?

---

## The Four Failure Cases

This project distinguishes four structurally different reasons a passenger waits:

| Case | Description | Root cause | Solution direction |
|------|-------------|------------|-------------------|
| **Case 1** | A louage passes but is already full | Demand exceeds total supply | More louages, or pre-positioning |
| **Case 2** | A louage passes but goes a different route (e.g. Sahloul) | Route confusion / mixed lines | Signage, route separation |
| **Case 3** | No louage passes at all for an extended period | Supply gap / irregular headway | Departure scheduling at origin |
| **Case 4** | A louage arrives but passenger is left behind due to rushing | No queue discipline, no boarding order | Physical queue markers, boarding protocol |

Each case has a different cause and a different fix. A model trained only on "wait time" cannot distinguish them. This project records each case separately, enabling multi-label failure classification.

---

## Corridor Overview

```
Kalaa Kebira (depart)
      │
      ├── Akouda: El Warda · Gamooun ★
      │
      ├── Hammam Sousse: Rp. Meublatex · Sidi Salem ★ · Menchia
      │
      ├── Khzema · Station Panorama · Station Hospital
      │
Beb Bhar (arrival)
```

**Louage types at origin (Kalaa Kebira):**
- 🟡 **Yellow, no sign** → our line (KK → Beb Bhar), capacity **8 passengers**
- 🔵 **White with blue stripe** → KK → Akouda → Sahloul (overlaps at Akouda stops)
- 🟡 **Yellow, "Sahloul" sign** → KK → Sahloul direct (no stop overlap)
- ⬜ **Internal KK** → within Kalaa Kebira only (no overlap, ignored)

---

## Methodology

### Phase 1 — Field Data Collection 
Structured 30-minute observation sessions at stations along the corridor. Three time slots per day: morning peak (07–09h), midday (12–14h), evening peak (17–20h). At minimum 3 days per week including Fridays.

Each session records:
- Supply: louages on line, full louages (Case 1), wrong-line louages (Case 2), longest dead period in minutes (Case 3)
- Demand: passengers at session start/end, boarded, left behind (Case 4), gave up
- Context: weather, school day, market day, Ramadan period, special events

### Phase 2 — Exploratory Data Analysis
Demand heatmaps by station × hour × day. Supply-demand gap analysis. Case frequency breakdown. Correlation with contextual variables.

### Phase 3 — Machine Learning Models
- **Target 1 (regression):** passenger count at a given station, time, and day
- **Target 2 (classification):** dominant failure case for the session
- **Models:** Linear Regression (baseline) → Decision Tree → Random Forest → XGBoost
- **Evaluation:** MAE, RMSE for regression; F1-score, confusion matrix for classification

### Phase 4 — Simulation & Scenario Testing
Use trained models to simulate interventions: what happens to unmet demand if departure intervals at KK are regularised to every 12 minutes during peak hours? Which stations benefit most from adding one additional louage?

### Phase 5 — Proposals & Deliverables
Data-backed recommendations for municipal authorities, an interactive demand dashboard, and a published academic-style report.

---

## Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Observation date |
| `day_of_week` | str | Auto-derived |
| `time_slot` | str | 30-min window (e.g. 07:00–08:00) |
| `station` | str | Station name on KK→BB line |
| `station_type` | str | Official / Informal / Junction / Market |
| `louages_on_line` | int | KK→BB louages passing (usable) |
| `louages_full` | int | Passed but full — Case 1 |
| `louages_wrongline` | int | Passed but wrong route — Case 2 |
| `longest_gap_min` | int | Longest dead period in minutes — Case 3 |
| `waiting_start` | int | Passengers waiting at session start |
| `waiting_end` | int | Passengers waiting at session end |
| `boarded` | int | Passengers who boarded during session |
| `left_behind` | int | Pushed out / failed to board — Case 4 |
| `gave_up` | int | Passengers who left the queue without boarding |
| `effective_supply` | int | `louages_on_line - louages_full` (auto) |
| `dominant_failure` | str | Auto-labelled failure case |
| `weather` | str | Sunny / Cloudy / Rain / Hot / Windy |
| `school_day` | bool | School in session? |
| `market_day` | bool | Weekly market active nearby? |
| `ramadan_period` | bool | Ramadan active? (shifts demand timing significantly) |
| `notes` | str | Free text observations |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data collection | Custom Excel observation sheet |
| Data processing | Python · pandas · numpy |
| Visualisation | matplotlib · seaborn · plotly |
| Machine learning | scikit-learn · XGBoost · SHAP |
| Dashboard | Streamlit |
| Report | LaTeX / Overleaf |
| Version control | Git / GitHub |

---

## Project Status

- [x] Problem definition and research design
- [x] Corridor mapping and louage type classification
- [x] Observation sheet designed and validated
- [ ] Phase 1: Data collection (in progress)
- [ ] Phase 2: Exploratory analysis
- [ ] Phase 3: ML modelling
- [ ] Phase 4: Simulation
- [ ] Phase 5: Report and dashboard

---

## Why This Matters

Informal transit systems like louages carry millions of daily passengers across North Africa and the Global South. They are fast, cheap, and demand-responsive — but opaque, uncoordinated, and unequal. This project is, to the author's knowledge, the first structured, ML-informed demand study on this specific corridor.

The outputs are designed to be immediately actionable: not a paper for a drawer, but evidence for a meeting with a city transport official.

---

## Author

**Mariem Belaid**  
Computer Science student, Sousse, Tunisia  
*Field observation, data collection, modelling, and analysis — all conducted independently as a self-directed research project.*

---

## License

Data collected in this project is original field observation data. Code is MIT licensed. Contact the author before reproducing findings.
