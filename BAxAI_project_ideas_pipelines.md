# BA x AI — Project Ideas: Business Challenge + Technical Pipeline

This document turns a set of potential final-project topics into (1) a clear business challenge framed as a decision problem and (2) a fit-for-purpose technical pipeline you can execute with public datasets.

## Idea 1 — Direct Marketing Offer Prioritisation (Classification)

### Business challenge (decision problem)
- **Context:** A retail bank runs outbound campaigns (phone/email) for term deposits or similar products.
- **Decision:** Which customers should be contacted (and in what priority) to maximise conversions **given limited contact capacity**?
- **Objective:** Maximise expected profit or conversion rate subject to campaign constraints.
- **Key levers:** Contact list size, contact channel, offer type, decision threshold (probability cut-off), prioritisation rule.
- **Constraints:** Limited agent time/calls, customer-contact policies (do-not-call), compliance rules, budget per campaign.
- **Assumptions (acceptable if stated):** Profit per conversion is fixed; cost per contact is fixed; historical response is indicative.

### Potential technical pipeline
1. **Data acquisition & provenance**
   - Use UCI Bank Marketing dataset: `https://archive.ics.uci.edu/dataset/222/bank+marketing` (CC BY 4.0; DOI `doi.org/10.24432/C5K306`).
   - Record: access date, licence, dataset version/DOI, sample size, target variable definition.
2. **Problem formulation**
   - Predict `P(conversion | customer, campaign)`; optimise contact selection under a capacity constraint (top‑K or threshold).
3. **Data preparation**
   - Handle missing/unknown values; encode categorical variables; scale numeric where needed.
   - Split into train/test (and optionally validation); prevent leakage (e.g., keep time-based split if timestamps exist).
4. **Feature engineering**
   - Customer attributes (age, job, etc.), interaction history features, campaign context.
5. **Modeling**
   - Baselines: logistic regression; stronger: gradient boosted trees / random forest.
6. **Evaluation**
   - Metrics: AUC/ROC, PR-AUC, calibration; business metrics: precision@K, expected profit@K, lift chart.
7. **Interpretation → business recommendations**
   - Translate “top drivers” into actionable targeting rules; recommend contact threshold and expected incremental conversions.
8. **Reproducibility**
   - Document split strategy, random seed, model hyperparameters, library versions.

## Idea 2 — E‑commerce Customer Segmentation & Targeting (Clustering)

### Business challenge (decision problem)
- **Context:** An online retailer wants to improve retention and increase customer lifetime value.
- **Decision:** How to segment customers into actionable groups and assign **segment-specific actions** (retention, upsell, win-back)?
- **Objective:** Increase revenue and repeat purchase while keeping marketing spend efficient.
- **Key levers:** Segment definitions, coupon/incentive policy per segment, communication frequency, channel strategy.
- **Constraints:** Marketing budget, customer fatigue, operational capacity (fulfilment, support).
- **Assumptions:** Segment behaviours are stable enough to act on; incentives have measurable cost and effect.

### Potential technical pipeline
1. **Data acquisition & provenance**
   - Use UCI Online Retail dataset: `https://archive.ics.uci.edu/dataset/352/online+retail` (CC BY 4.0; DOI `doi.org/10.24432/C5BW33`).
2. **Data preparation**
   - Clean invoices (remove cancellations/returns as appropriate); parse timestamps; compute customer-level aggregates.
3. **Feature engineering**
   - RFM: recency, frequency, monetary value.
   - Optional: basket size, product-category diversity, return rate, seasonality.
4. **Clustering**
   - Baselines: k-means (with standardisation); alternatives: GMM, hierarchical clustering.
   - Choose K using silhouette score + business interpretability (not metrics alone).
5. **Cluster profiling**
   - Describe segments with summary tables/plots; label segments (“High value loyal”, “At-risk”, etc.).
6. **Action design**
   - Map each segment to interventions (e.g., “At-risk” → win-back offer; “High value” → VIP benefits).
7. **Evaluation**
   - Offline: separation metrics, stability across resamples/time.
   - Business framing: estimated uplift targets; A/B test plan (even if not executed).
8. **Reproducibility**
   - Document filtering rules, scaling, distance metric, cluster parameters, random seed.

## Idea 3 — Staffing Level & Service Performance (Forecasting + Simulation)

### Business challenge (decision problem)
- **Context:** A service operation (retail store, helpdesk, call centre) must meet a wait-time SLA with limited labour.
- **Decision:** How many staff to schedule per time interval to meet SLA at minimum cost?
- **Objective:** Minimise staffing cost subject to service-level constraints (e.g., % served within X minutes).
/- **Key levers:** Staffing levels per hour/day, shift design, cross-training, queue priority rules.
- **Constraints:** Labour availability, shift rules, budget, service-level agreement.
- **Assumptions:** Service times follow a distribution; arrivals can be forecasted from historical demand proxies.

### Potential technical pipeline
1. **Data acquisition (demand proxy)**
   - Use traffic/demand time series as arrivals proxy:
     - UCI Metro Interstate Traffic Volume: `https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume` (CC BY 4.0; DOI `doi.org/10.24432/C5X60B`).
     - Or NYC TLC trips as demand proxy: `https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page`.
2. **Forecasting arrivals**
   - Build a forecast of arrivals per interval (hour/day) using baselines (seasonal naive) and a stronger model (SARIMA/Prophet/GBM).
3. **Queue model selection**
   - Choose a simple queue (e.g., M/M/c or empirical simulation) depending on assumptions and course expectations.
4. **Simulation**
   - Simulate arrivals + service times; vary staff count `c` and compute SLA metrics and cost.
   - Run multiple replications; report confidence intervals.
5. **Optimisation / decision rule**
   - Choose staffing that meets SLA with lowest cost (or Pareto curve cost vs. SLA).
6. **Interpretation → recommendations**
   - Provide recommended staffing by time-of-day and expected SLA; highlight peak periods and contingency buffer.
7. **Reproducibility**
   - Document random seeds, number of replications, distribution assumptions, forecast method + versions.

## Idea 4 — Property Price Valuation & Investment Screening (Regression)

### Business challenge (decision problem)
- **Context:** A property investor/agency needs a data-driven way to estimate prices and identify opportunities.
- **Decision:** What is the expected sale price for a given property, and which listings/areas look undervalued relative to model expectations?
- **Objective:** Reduce pricing errors and improve ROI via better acquisition and negotiation decisions.
- **Key levers:** Offer price / reserve price, renovation budget, area focus, property-type focus.
- **Constraints:** Capital budget, risk tolerance, time-to-sell, regulatory constraints.
- **Assumptions:** Historical transaction prices are comparable; available features proxy property quality sufficiently.

### Potential technical pipeline
1. **Data acquisition & provenance**
   - UK Price Paid Data: `https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads` (Open Government Licence v3.0).
   - (Optional enrichment, if you keep scope manageable): basic geographic joins (postcode area), simple time features.
2. **Data preparation**
   - Filter by geography/time window; handle duplicates; engineer time (month/quarter); encode property type.
3. **Modeling**
   - Baselines: linear regression with regularisation; stronger: gradient boosted trees.
4. **Evaluation**
   - Metrics: MAE/MAPE; residual analysis by region/property type to check systematic bias.
5. **Decision logic**
   - Define “undervalued” = actual listing price < predicted price − margin; rank opportunities.
6. **Interpretation → recommendations**
   - Recommend pricing bands/target areas; identify key drivers (location/time/property type).
7. **Reproducibility**
   - Document filtering criteria, train/test split (time-based recommended), features used, model parameters.

## Idea 5 — Taxi Demand Hotspots & Driver Repositioning (Spatio‑temporal Analytics)

### Business challenge (decision problem)
- **Context:** A fleet/ride-hailing operator wants to reduce passenger wait times and driver idle time.
- **Decision:** Where should drivers reposition (and when) to better match demand?
- **Objective:** Maximise completed trips or minimise wait time/idle time with minimal incentive spend.
- **Key levers:** Repositioning rules, incentive amounts, dispatch policies, supply allocation by zone/time.
- **Constraints:** Driver autonomy, traffic, fairness, safety, limited incentive budget.
- **Assumptions:** Past demand patterns generalise; zones approximate true locations; travel time between zones is manageable.

### Potential technical pipeline
1. **Data acquisition & provenance**
   - NYC TLC Trip Record Data: `https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page` (also cite NYC terms-of-use where appropriate).
2. **Data preparation**
   - Aggregate trips by zone and time bucket (e.g., 15/60 minutes); clean anomalies; join zone shapefiles if needed.
3. **Demand modeling**
   - Forecast demand per zone/time (baseline seasonal; stronger: gradient boosting with weather/time features if available).
4. **Hotspot identification**
   - Cluster zones by demand patterns; detect peak hotspots; compute heatmaps.
5. **Policy simulation**
   - Simulate a repositioning policy (simple rules: “move to top-N nearby zones with highest predicted demand”).
6. **Evaluation**
   - Metrics: predicted vs. observed demand error; operational KPIs (idle time proxy, coverage rate).
7. **Interpretation → recommendations**
   - Produce an “operating playbook”: hotspot schedules, suggested staging areas, when incentives are most efficient.
8. **Reproducibility**
   - Document aggregation choices, forecast horizon, model parameters, evaluation window.

## How to choose (fast rubric)
- Prefer topics where you can clearly state **objectives, levers, and constraints** in one slide.
- Prefer datasets with explicit **licence + provenance** and enough rows to be meaningful (but not unmanageable).
- Pick one technique and do it *deeply* (clean data → justified method → business translation), rather than many techniques shallowly.

## Recording checklist (mapped to brief)
- **Challenge clarity:** deliverables, levers, scope, assumptions.
- **Technique justification:** why this method is fit-for-purpose.
- **Data description:** provenance (link, date accessed, licence), sample size, key features.
- **Reproducibility:** split strategy, random seed, model/simulation parameters.
- **Results → business:** charts/metrics + practical recommendations.
- **Admin:** references + 1‑line GenAI disclosure + stay under 10 minutes.

