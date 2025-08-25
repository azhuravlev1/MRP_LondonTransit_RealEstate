# Centrality Analysis Visualizations

This folder contains comprehensive visualizations for the London Transit Network Analysis (2000-2023), focusing on centrality measures and community structure.

## Generated Files

### 📊 Summary Tables
- `centrality_summary_table.csv` - Raw data table with pre/post COVID comparisons
- `centrality_summary_display.csv` - Formatted table for display purposes

### 📈 Visualization Plots

#### 1. Borough Rankings (`01_borough_rankings.png`)
**What it shows:** Top 10 boroughs ranked by each centrality measure (2000-2023 average)
**Insight:** Identifies the most important hubs in London's transport system
**Measures:** Weighted In-Degree, Weighted Out-Degree, Betweenness, Closeness, Eigenvector Centrality

#### 2. COVID Winners and Losers (`02_covid_winners_losers.png`)
**What it shows:** Percentage change in passenger arrivals between 2019 and 2022
**Insight:** Visualizes the pandemic's impact on urban mobility patterns
**Story:** Separates boroughs that saw declines (central business districts) from those with relative increases (outer residential areas)

#### 3. Time Band Distributions (`03_time_band_distributions.png`)
**What it shows:** Distribution of centrality measures across different time bands (if available)
**Insight:** Reveals how borough roles change throughout the day
**Pattern:** Wider distributions during peak hours indicate more hierarchical networks

#### 4. Centrality Distributions (`04_centrality_distributions.png`)
**What it shows:** Overall distribution of each centrality measure across all years
**Insight:** Understanding the statistical properties of network centrality
**Use:** Identifies outliers and typical centrality ranges

#### 5. Correlation Heatmap (`05_correlation_heatmap.png`)
**What it shows:** Pearson correlation matrix between all centrality measures
**Insight:** Critical diagnostic for modeling - reveals multicollinearity and relationships
**Value:** Helps select appropriate variables for regression analysis

#### 6. Evolution Heatmap (`06_evolution_heatmap.png`)
**What it shows:** 24-year evolution of betweenness centrality (Year × Borough)
**Insight:** Most powerful single visualization - shows entire network history at a glance
**Features:** Identifies major shocks (2008 crisis, COVID-19), long-term trends, and borough evolution

#### 7. Scatter Analysis (`07_scatter_analysis.png`)
**What it shows:** Four key relationship plots:
- Betweenness vs Arrivals (Borough roles)
- Closeness vs Eigenvector (Network position)
- Arrivals vs Departures (Flow balance)
- Pre vs Post COVID (Pandemic impact)
**Insight:** Classifies boroughs into different functional roles

#### 8. Time Series Evolution (`08_time_series_evolution.png`)
**What it shows:** Centrality evolution over time for top 5 boroughs
**Insight:** Tracks how individual boroughs have changed over 24 years
**Story:** Reveals long-term trends and infrastructure impacts

#### 9. Infrastructure Impact (`09_infrastructure_impact.png`)
**What it shows:** Impact of three major infrastructure events:
- Elizabeth Line (2022)
- London Overground (2007)
- DLR Extension (2011)
**Insight:** Quantifies the effect of major transport investments
**Method:** Compares borough centrality before/after each event

#### 10. Community Evolution (`10_community_evolution.png`)
**What it shows:** Evolution of travel communities over time (if community data available)
**Insight:** How London's travel clusters have changed
**Value:** Identifies emerging and declining travel patterns

#### 11. Community Characteristics (`11_community_characteristics.png`)
**What it shows:** Community analysis including:
- Participation coefficient distribution by community
- Community size distribution
**Insight:** Gives communities qualitative identity and characteristics

#### 12. Ranking Stability (`12_ranking_stability.png`)
**What it shows:** How stable borough rankings are over time
**Insight:** Identifies consistently important vs. volatile boroughs
**Method:** Standard deviation of rankings across years

#### 13. Summary Dashboard (`13_summary_dashboard.png`)
**What it shows:** Comprehensive heatmap of average centrality measures by borough
**Insight:** Complete overview of London's transport hierarchy
**Use:** Final summary visualization for presentations

## Key Insights These Visualizations Reveal

### 🏙️ **Network Structure**
- Which boroughs are the most central hubs
- How centrality has evolved over 24 years
- The relationship between different centrality measures

### 🚇 **Infrastructure Impact**
- Quantified effects of major transport investments
- Before/after analysis of Elizabeth Line, Overground, and DLR
- Long-term trends in network development

### 🦠 **COVID-19 Effects**
- Winners and losers in the pandemic
- Changes in travel patterns
- Recovery patterns post-2020

### 📊 **Statistical Properties**
- Distribution of centrality measures
- Correlation between different metrics
- Stability of borough rankings

### 🏘️ **Borough Roles**
- Classification of boroughs by function
- Evolution of borough importance
- Spatial patterns in network centrality

## Usage Notes

- All plots are saved in high resolution (300 DPI) for publication quality
- Color schemes are optimized for accessibility and clarity
- File naming follows a logical sequence for easy reference
- CSV files provide raw data for further analysis

## Technical Details

- **Data Source:** `all_metrics_timeseries.csv` (57,319 records)
- **Time Period:** 2000-2023 (24 years)
- **Geographic Scope:** 33 London boroughs + "Out of London"
- **Centrality Measures:** 5 key metrics calculated for each borough-year combination
- **Community Analysis:** Leiden algorithm for community detection (if available)

## Generated By

`Scripts/Accessibility_Analysis/comprehensive_centrality_visualizations.py`

This script provides a complete analytical framework for understanding London's transit network evolution and its relationship to housing market dynamics.
