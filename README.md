# London Transit Network & Real Estate Analysis

**Data Science Research Project | 2000-2024 | Python, Network Analysis, Econometrics**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)]()

## Project Overview

This project analyzes how London's public transport network evolution influenced borough-level housing prices over 25 years (2000-2024). Using advanced graph mining techniques and econometric modeling, I quantified the relationship between transit accessibility and real estate values, providing data-driven insights for urban planning and policy.

**Key Achievement**: Built a comprehensive analytical framework that processes 25 years of transit data to reveal significant correlations between network centrality and housing price changes.

## Technical Highlights

### **Data Engineering & Processing**
- **Harmonized** 25 years of TfL RODS and NUMBAT datasets (2000-2024)
- **Processed** 1,800+ transit network graphs and 189 origin-destination matrices
- **Built** automated ETL pipelines for multi-source data integration
- **Handled** missing data, standardization, and temporal alignment challenges

### **Network Analysis & Graph Mining**
- **Constructed** dynamic temporal graphs of London's transit system
- **Calculated** 5 centrality metrics (betweenness, closeness, eigenvector, in/out-degree)
- **Implemented** community detection algorithms for network structure analysis
- **Analyzed** network evolution and infrastructure impact over time

### **Statistical Modeling & Econometrics**
- **Developed** fixed-effects panel regression models with clustered standard errors
- **Implemented** lagged variable analysis for causal inference
- **Conducted** comprehensive model diagnostics and robustness testing
- **Created** interaction analysis for COVID-19 period effects

### **Data Visualization & Reporting**
- **Generated** publication-quality visualizations and dashboards
- **Built** comprehensive results interpretation framework
- **Created** interactive plots for network evolution analysis
- **Produced** professional reports with statistical significance testing

## Technical Stack

| Category | Technologies |
|----------|-------------|
| **Languages** | Python 3.8+ |
| **Data Processing** | pandas, numpy, scipy |
| **Network Analysis** | NetworkX, graph-tool |
| **Statistical Modeling** | statsmodels, scikit-learn |
| **Visualization** | matplotlib, seaborn, plotly |
| **Data Storage** | CSV, Excel, GraphML |
| **Development** | Jupyter Notebooks, Git |

## Key Results

- **Identified** significant correlations between transit centrality and housing prices
- **Quantified** effect sizes for different centrality measures
- **Revealed** differential impacts across London boroughs
- **Demonstrated** network structure changes during COVID-19 period
- **Provided** actionable insights for urban planning and policy

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
pip install pandas numpy networkx statsmodels matplotlib seaborn scipy
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

## Sample Results

The analysis reveals:
- **Betweenness Centrality**: Strongest predictor of housing price changes
- **Network Effects**: Boroughs with high transit connectivity show 3-8% price premiums
- **Temporal Dynamics**: COVID-19 period showed unique network restructuring patterns
- **Policy Implications**: Infrastructure investments have measurable economic impacts

## Academic Context

**Research Question**: How do changes in London's transit network structure influence borough-level housing prices over time?

**Methodology**: 
- Dynamic temporal graph construction
- Multi-metric centrality analysis
- Fixed-effects panel regression with lagged variables
- Comprehensive robustness testing

**Contribution**: Novel application of graph mining to urban economics, providing quantitative evidence for transport infrastructure's impact on real estate markets.

## Documentation

- **[Complete Research Report](MRP%20Report%20Andrey%20Zhuravlev.pdf)** - Full academic analysis
- **[Modeling Framework](modeling/README.md)** - Technical implementation details
- **[Centrality Analysis](Plots/Centrality_Analysis/README.md)** - Network metrics documentation

## About the Author

**Andrey Zhuravlev**  
Master of Science in Data Science and Analytics  
Toronto Metropolitan University, 2025

**Skills Demonstrated**: Data Engineering, Network Analysis, Statistical Modeling, Econometrics, Data Visualization, Research Methodology

---

*This project showcases advanced data science techniques applied to real-world urban planning challenges, demonstrating the intersection of network science, econometrics, and policy analysis.*
