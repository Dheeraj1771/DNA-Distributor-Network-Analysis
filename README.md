<div align="center">

# 🧬 DNA: Distributor Network Analysis
**Enterprise-Grade Geospatial Intelligence & Prescriptive Analytics**

[![Python Version](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Spatial Engine](https://img.shields.io/badge/GeoPandas-WGS84-139C5A?style=for-the-badge&logo=geopandas&logoColor=white)](https://geopandas.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

*Optimizing commercial supply chain infrastructure, territory boundaries, and asset distribution networks across **12,847 geographic mesh cells** in Maharashtra, India.*

**[🌐 View Live Dashboard Deployment Here](https://dna-distributor-network-analysis.streamlit.app/)**


</div>

---

> **The Mission:** > *To replace intuition with mathematical certainty. DNA transforms complex internal asset logs, customer touchpoints, and regional vehicle populations into a prescriptive, actionable expansion strategy—preventing blind capital deployment in high-risk distribution infrastructure.*

---

## 🧠 Core Intelligence Modules

The platform is split into two powerful machine learning pipelines, seamlessly unified by a responsive frontend:

### 🎯 1. Unsupervised Strategic White-Space Mapping
**Goal:** Discover high-density, untapped service clusters located entirely outside of our existing active business boundaries.

| Technology | Implementation & Parameters | Outcome |
| :--- | :--- | :--- |
| **Spatial Masking** | `gpd.sjoin` exact inner spatial joins against operational territory borders. | Isolates purely untapped demand. |
| **Density Engine** | **DBSCAN** core tracking radian-mapped coordinates. | Filters out scattered market noise. |
| **Hyperparameters**| $Eps = 25\text{km}$ (spherical Haversine), $MinSamples = 15$. | **9 Validated Target Zones.** |

### 💰 2. Supervised Econometric Scaling Engine
**Goal:** Extract the exact revenue capability of underlying regional assets and calculate localized investment yield profiles.

| ML Metric Parameter | Learned Weight (₹) | Commercial Operational Meaning |
| :--- | :--- | :--- |
| **Base Intercept** | `₹11,448,494.60` | Fixed baseline revenue threshold per operating cell. |
| **Vehicle Parc** ($\beta_1$) | `₹4,740.27` | Realized yearly value added per registered active vehicle. |
| **Workshop Density** ($\beta_2$) | `₹312,154.76` | Strategic revenue value generated per mechanic touchpoint. |

💡 **Prescriptive Optimization:** *Includes an interactive "What-If" simulation console. Operational leads can use a slider interface to simulate strategic partner placements and instantly view the projected Net ROI before deploying capital.*

---

## 🖥️ System Architecture

```text
                          ┌──────────────────────────┐
                          │   RAW DATA INGESTION     │
                          │ (CSVs, GeoJSON Borders)  │
                          └────────────┬─────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  【 MODULE 1: UNSUPERVISED 】                  【 MODULE 2: SUPERVISED 】
  Strategic White-Space Analysis               Econometric Scaling Engine
  ┌──────────────────────────┐                 ┌──────────────────────────┐
  │ Vector Polygon Masking   │                 │ Constrained Regression   │
  └────────────┬─────────────┘                 └────────────┬─────────────┘
               |                                            |
               ▼                                            ▼
  ┌──────────────────────────┐                 ┌──────────────────────────┐
  │ DBSCAN Density Engine    │                 │ Predictive Mesh Scoring  │
  └────────────┬─────────────┘                 └────────────┬─────────────┘
               |                                            |
               ▼                                            ▼
  ┌──────────────────────────┐                 ┌──────────────────────────┐
  │  Validated Expansion     │                 │ Prescriptive Simulator   │
  │     Footprint Zones      │                 │  (Interactive ROI Handle)│
  └──────────────────────────┘                 └──────────────────────────┘
```

---

## 📂 Repository File Structure

```text
📁 DNA-Distributor-Network-Analysis/
│
├── 📁 data/                           # Spatial layers, regression data, & telemetry
│   ├── 📄 customer_touchpoints.csv
│   ├── 📄 historical_performance.csv
│   ├── 📄 internal_touchpoints.csv
│   ├── 📄 maharashtra_border.geojson
│   ├── 📄 maharashtra_revenue_grid_data.csv
│   ├── 📄 market_potential_predictions.csv
│   ├── 📄 proposed_ro_locations.csv
│   ├── 📄 territory_boundaries.geojson
│   └── 📄 vehicle_parc.csv
│
├── 📁 notebooks/                      # ML Research & Model Training Pipelines
│   ├── 📄 01_DBSCAN_Whitespace_Analysis.ipynb
│   └── 📄 02_Market_Potential_Analysis.ipynb
│
├── 📁 pages/                          # Streamlit Dashboard Modules
│   ├── 📄 01_Whitespace_Analysis.py
│   └── 📄 02_Market_Potential_Analysis.py
│
├── 📁 src/                            # Backend Data Synthesis Scripts
│   ├── 📄 generate_all_data.py
│   └── 📄 generate_revenue_data.py
│
├── 📄 .gitignore                      # Git exclusion configurations
├── 📄 DNA.py                          # Streamlit Entry Point & Exec Home Page
├── 📄 LICENSE                         # Open Source License
├── 📄 README.md                       # Project Documentation
└── 📄 requirements.txt                # Production Container Dependencies
```

---

## 🚀 Quick Start Local Deployment

**1. Clone the Repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
```

**2. Configure Virtual Environment:**
```bash
conda create -n dna-env python=3.10 -y
conda activate dna-env
```

**3. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**4. Launch the Platform:**
```bash
streamlit run DNA.py
```

---

## 🛠️ Technical Stack

- **Core & Mathematical:** `Python 3.10+`, `NumPy`, `Pandas`
- **Dashboard Architecture:** `Streamlit Framework`, `CSS3/HTML5 Flexbox`
- **Geospatial Processing:** `GeoPandas`, `Folium`, `Streamlit-Folium`, `Shapely`
- **Machine Learning:** `Scikit-Learn` (DBSCAN, Linear Regression), `Jupyter`
- **Visualization:** `Matplotlib`, `Branca JavaScript Utilities`