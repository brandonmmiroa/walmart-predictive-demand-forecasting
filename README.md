# walmart-predictive-demand-forecasting
An end-to-end predictive retail pipeline syncing masked local features to a Supabase cloud data warehouse and visualizing forecasts in Tableau.



## 📊 Business Problem & Operational Impact
Retail operators constantly struggle to balance inventory overhead against consumer stockouts. Relying on reactive, historical sales tracking leads to empty shelves during unexpected customer surges or wasted labor and capital budgets during sudden retail slumps.

This project solves that operational bottleneck by deploying a proactive, end-to-end predictive architecture. Utilizing nearly **5,000 unique days of operational transaction data**, the pipeline normalizes metrics, streams anonymized features directly to a live cloud warehouse, runs a machine learning engine to forecast demand shifts, and surfaces visual timelines to executive stakeholders. This enables retail managers to optimize supply chains and employee shift hours days in advance.

---

## 🛠️ System Architecture & Tech Stack
* **Language:** Python 3.x (Pandas, NumPy, Scikit-Learn, Psycopg2)
* **Cloud Warehouse:** PostgreSQL (Hosted on Supabase Cloud Infrastructure)
* **BI Presentation Layer:** Tableau Public Web Authoring
* **Deployment Model:** Consolidated Master Pipeline with Global Environment Toggles

---

## 🚀 Key Engineering Phases

### 1. Data Anonymization & Security Standards
* Implemented secure data masking routines to convert sensitive operational revenue metrics into generic feature vectors prior to public cloud ingestion.
* Leveraged enterprise-standard cryptographic masking (`getpass`) within the Python runtime to prevent hardcoded database credentials from being exposed in public code repositories.

### 2. Cloud Data Warehousing & SQL Architecture
* Provisioned a remote PostgreSQL instance on Supabase.
* Designed a relational table schema optimized with chronological indexing for rapid daily analytical processing.
* Resolved time-grain conflicts by engineering date-normalization logic within the ingestion script, eliminating duplicate key unique violations on cloud tables.

### 3. Feature Engineering & Non-Linear Machine Learning
* Structured a multi-variable matrix to track historical purchase velocity alongside categorical day-of-week variants.
* Upgraded a baseline linear framework to an advanced **Random Forest Regressor** to successfully capture non-linear retail spikes and drops, achieving a high-performance **$R^2$ score of 0.7257** during live cloud feature evaluations.

### 4. Production Refactoring (Global Toggles)
* Refactored separate analytical modules into a single, production-ready master pipeline.
* Engineered a global configuration toggle (`DEVELOPMENT_CLOUD` vs. `PRODUCTION_LOCAL`) enabling instant switching between remote database engineering modes and unmasked high-volume enterprise execution branches.

---

## 📊 Live Interactive Dashboard
The final model outputs automatically synchronize to a production storage directory, fueling an executive-facing BI dashboard. 

* **Live Portfolio Link:** https://public.tableau.com/views/Walmart-Demand-Forecast-ML-Production/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link
* **Production Model Performance:** $R^2 = 72.57\%$ managing over 4,970+ unique operational days.

The visual timeline demonstrates the Random Forest model's strong predictive accuracy when mirroring real-world consumer behavior peaks, giving business leaders a distinct proactive edge.
