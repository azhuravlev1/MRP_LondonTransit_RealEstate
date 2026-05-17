# London Transit Network & Real Estate Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)]()

## Overview

This repository contains the code, data pipelines, and findings from my Master's Research Project (MRP) in Data Science and Analytics at Toronto Metropolitan University.

The project investigates how the structural evolution of London's public transport network influenced borough-level housing prices over a 24-year period (2000-2023). By constructing dynamic temporal graphs from historical passenger flow data and applying econometric panel modeling, this research quantifies the direct relationship between transit accessibility and real estate valuation.

## Key Findings

Unlike traditional proximity-based transit studies, this graph-based approach revealed nuanced dynamics about *how* a borough functions within the broader network:

* **Destination Value:** Total passenger arrivals (Weighted In-Degree) proved to be a highly significant positive predictor of property value. A one standard deviation increase in passenger arrivals correlated with a 1.28% increase in a borough's average housing price.

* **The "Corridor Penalty":** Serving primarily as a transit corridor (Betweenness Centrality) showed a marginally significant *negative* effect (-0.69%), suggesting that the disamenities of high-traffic transit corridors (noise, congestion) can slightly offset pure connectivity benefits.

* **Pandemic Shifts:** Interaction analysis revealed a distinct structural shift post-2020, with central business hubs (Westminster, City of London) losing relative traffic share to outer residential boroughs (Sutton, Havering).

* **Infrastructure Impact:** Long-term centrality heatmaps clearly tracked the economic impact of targeted infrastructure, such as the DLR expansion preceding the 2012 Olympics.

## Technical Methodology

This project required extensive data engineering to harmonize decades of disjointed transportation data into a unified, model-ready format.

### 1. Data Engineering & Harmonization

* **Transit Data Integration:** Processed and harmonized 24 years of passenger flow data from two fundamentally different TfL systems: manual survey data (RODS, 2000-2017) and smartcard/ticketing data (NUMBAT, 2017-2023).

* **Geospatial Mapping:** Built custom Python web scrapers to extract historical station data from Wikipedia, mapping hundreds of uniquely coded stations (including the Underground, Overground, DLR, and Elizabeth Line) to their respective London boroughs.

* **Entity Resolution:** Handled complex entity matching, resolving discrepancies between Master National Location Codes (NLCs), station names, and changing borough administrative boundaries over two decades.

### 2. Network Analysis (Graph Mining)

* **Dynamic Graphs:** Constructed directed, weighted graphs for each year using `igraph`, where nodes represent London boroughs and edges represent passenger journey volumes.

* **Metric Extraction:** Calculated key topological features for each borough annually, including Weighted In/Out-Degree, Betweenness Centrality, Closeness Centrality, and Eigenvector Centrality.

* **Community Detection:** Temporarily converted directed edges to undirected to run the Leiden algorithm, identifying distinct travel clusters and community structures across the network.

### 3. Econometric Modeling

* **Panel Regression:** Developed a fixed-effects panel regression model using OLS with clustered standard errors at the borough level to ensure reliable statistical inference.

* **Causal Inference:** Utilized lagged accessibility metrics to isolate the causal, anticipatory impact of network changes on housing prices, controlling for macroeconomic trends and unobserved local heterogeneity.

## Technical Stack

| Category | Technologies |
|----------|-------------|
| **Languages** | Python 3.8+ |
| **Data Processing** | pandas, numpy, scipy |
| **Network Analysis** | igraph, graph-tool |
| **Statistical Modeling** | statsmodels, scikit-learn |
| **Visualization** | matplotlib, seaborn, plotly |
| **Data Storage** | CSV, Excel, GraphML |
| **Development** | Jupyter Notebooks, Git |

## Project Structure

```
├── Data/                          # Raw datasets and processed files
│   ├── NUMBAT/                       # Transit flow matrices (2000-2024)
│   ├── RODS_OD/                      # Origin-destination data
│   └── Graphs/                       # Network graph files
├── Scripts/                       # Analysis pipeline
│   ├── EDA/                          # Exploratory data analysis
│   ├── Graphs Construction/          # Network building
│   ├── Accessibility Analysis/       # Centrality calculations
│   └── Modeling/                     # Statistical modeling
├── Plots/                         # Visualizations and results
│   ├── Centrality Analysis/          # Network metrics plots
│   └── network_visualizations/       # Graph visualizations
├── modeling/                      # Final analysis framework
│   ├── data/                         # Processed datasets
│   └── outputs/                      # Results and diagnostics
└── 📋 MRP Report Andrey Zhuravlev.pdf # Complete research report
```

## Quick Start

### Prerequisites
```bash
pip install pandas numpy igraph statsmodels matplotlib seaborn scipy
```

### Run Complete Analysis
```bash
# Navigate to modeling directory
cd modeling/

# Execute full analysis pipeline
python Scripts/Modeling/run_complete_analysis.py
```

### Key Scripts
- **`Scripts/Modeling/run_complete_analysis.py`** - Master pipeline execution
- **`Scripts/Accessibility_Analysis/`** - Network centrality calculations
- **`Scripts/EDA/`** - Exploratory data analysis


## Documentation

- **[Complete Research Report](MRP%20Report%20Andrey%20Zhuravlev.pdf)** - Full academic analysis
- **[Modeling Framework](modeling/README.md)** - Technical implementation details
- **[Centrality Analysis](Plots/Centrality_Analysis/README.md)** - Network metrics documentation

## About the Author

**Andrey Zhuravlev**  
Master of Science in Data Science and Analytics  
Toronto Metropolitan University, 2025
