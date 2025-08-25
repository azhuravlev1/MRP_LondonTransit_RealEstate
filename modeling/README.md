# London Transit Network and Housing Market Analysis: Modeling Framework

This folder contains the complete panel regression analysis framework for examining the relationship between London's transit network centrality and housing prices from 2000-2023.

## 📁 Folder Structure

```
Scripts/Modeling/           # Analysis scripts
├── 01_prepare_final_dataset.py
├── 02_run_panel_regression.py
├── 03_visualize_results.py
└── run_complete_analysis.py # Master script to run entire pipeline

modeling/                   # Data and outputs
├── data/                   # Final dataset and summaries
├── outputs/                # Regression results and visualizations
└── README.md              # This file
```

## 🚀 Quick Start

To run the complete analysis pipeline:

```bash
python Scripts/Modeling/run_complete_analysis.py
```

This will execute all three scripts in sequence and generate all outputs.

## 📊 Analysis Overview

### Research Question
How do changes in London's transit network centrality affect borough-level housing prices over time?

### Methodology
- **Panel Regression with Fixed Effects**: Controls for unobserved borough-specific and time-specific factors
- **Lagged Variables**: Uses centrality measures from year t-1 to predict housing prices in year t
- **Standardized Coefficients**: Allows comparison of effect sizes across different centrality measures
- **Clustered Standard Errors**: Accounts for potential correlation within boroughs

### Centrality Measures Analyzed
1. **Weighted In-Degree**: Total passenger arrivals to a borough
2. **Weighted Out-Degree**: Total passenger departures from a borough
3. **Betweenness Centrality**: Borough's role as a "pass-through" corridor
4. **Closeness Centrality**: How easily a borough can reach all others
5. **Eigenvector Centrality**: Borough's connection to other important hubs

## 🔧 Script Details

### 01_prepare_final_dataset.py
**Purpose**: Prepare the final dataset for regression analysis

**What it does**:
- Loads centrality metrics from `all_metrics_timeseries.csv`
- Loads housing price data from UK House Price Index
- Merges datasets by Year and Borough
- Creates lagged variables (t-1) for causality analysis
- Standardizes borough names for consistent matching
- Creates additional variables (fixed effects, interactions)
- Saves final dataset to `modeling/data/final_modeling_dataset.csv`

**Key Features**:
- Handles data cleaning and standardization
- Creates year and borough fixed effects
- Adds COVID period indicator and interactions
- Generates comprehensive dataset summary

### 02_run_panel_regression.py
**Purpose**: Run the panel regression analysis

**What it does**:
- Loads the final modeling dataset
- Runs multiple regression models:
  - Basic OLS (no fixed effects)
  - Panel regression with fixed effects
  - Models with interaction terms (COVID period)
- Calculates comprehensive diagnostics
- Saves detailed results and diagnostics

**Key Features**:
- Panel regression with year and borough fixed effects
- Clustered standard errors
- Multiple diagnostic tests (heteroscedasticity, multicollinearity, normality)
- Interaction analysis for COVID period effects
- Comprehensive model diagnostics

### 03_visualize_results.py
**Purpose**: Create publication-quality visualizations

**What it does**:
- Creates coefficient plots with significance indicators
- Generates effect size visualizations
- Produces interaction plots (COVID effects)
- Creates comprehensive results dashboard
- Generates interpretation report

**Key Features**:
- Publication-quality plots with proper styling
- Color-coded significance levels
- Effect size calculations and visualization
- Comprehensive dashboard with multiple views
- Detailed interpretation report

## 📈 Output Files

### Data Files (`modeling/data/`)
- `final_modeling_dataset.csv`: Complete dataset with lagged variables
- `dataset_summary.txt`: Summary statistics and data description

### Results Files (`modeling/outputs/`)
- `regression_summary.txt`: Complete regression results and diagnostics
- `coefficients.csv`: Coefficient estimates with standard errors and p-values
- `diagnostics.txt`: Model diagnostics and tests
- `residuals_plot.png`: Residual diagnostic plots

### Visualization Files (`modeling/outputs/`)
- `coefficient_plot.png`: Main coefficient plot with significance indicators
- `effect_size_plot.png`: Practical significance and precision analysis
- `interaction_plot.png`: COVID interaction effects
- `results_dashboard.png`: Comprehensive results summary
- `interpretation_report.txt`: Detailed results interpretation

## 🎯 Key Features

### Robust Methodology
- **Fixed Effects**: Controls for unobserved heterogeneity
- **Lagged Variables**: Establishes temporal precedence
- **Standardized Coefficients**: Comparable effect sizes
- **Clustered Errors**: Robust inference

### Comprehensive Diagnostics
- **Model Fit**: R-squared, F-statistics
- **Residual Analysis**: Normality, heteroscedasticity tests
- **Multicollinearity**: Variance Inflation Factors
- **Robustness**: Multiple model specifications

### Publication-Ready Outputs
- **High-Resolution Plots**: 300 DPI, publication quality
- **Professional Styling**: Consistent color schemes and formatting
- **Clear Interpretation**: Effect sizes and practical significance
- **Comprehensive Documentation**: Detailed reports and summaries

## 🔍 Interpreting Results

### Coefficient Interpretation
- **Positive Coefficient**: Higher centrality → Higher house prices
- **Negative Coefficient**: Higher centrality → Lower house prices
- **Effect Size**: Percentage change in house prices for 1 SD change in centrality

### Significance Levels
- **p < 0.01**: Highly significant (***)
- **p < 0.05**: Significant (**)
- **p < 0.10**: Marginally significant (*)
- **p ≥ 0.10**: Not significant

### Practical Significance
- **Effect Size > 5%**: Large practical effect
- **Effect Size 1-5%**: Moderate practical effect
- **Effect Size < 1%**: Small practical effect

## 🛠️ Customization

### Adding New Variables
1. Modify `centrality_measures` list in each script
2. Update borough name mappings if needed
3. Add new interaction terms as required

### Changing Model Specifications
1. Edit regression formulas in `02_run_panel_regression.py`
2. Modify fixed effects structure
3. Add new diagnostic tests

### Customizing Visualizations
1. Update color schemes in `03_visualize_results.py`
2. Modify plot layouts and styling
3. Add new visualization types

## 📚 Dependencies

Required Python packages:
- pandas
- numpy
- statsmodels
- matplotlib
- seaborn
- scipy
- pathlib

Install with:
```bash
pip install pandas numpy statsmodels matplotlib seaborn scipy
```

## 🚨 Troubleshooting

### Common Issues
1. **Missing Data Files**: Ensure `all_metrics_timeseries.csv` and housing price data are in the correct locations
2. **Memory Issues**: For large datasets, consider processing in chunks
3. **Convergence Issues**: Check for multicollinearity or insufficient variation

### Error Messages
- **"Script not found"**: Check file paths and ensure all scripts are in the `scripts/` folder
- **"Missing columns"**: Verify data structure matches expected format
- **"Convergence failed"**: Check for perfect multicollinearity or insufficient data

## 📖 References

This analysis framework is based on:
- Panel regression methodology from econometrics literature
- Graph centrality measures from network science
- Real estate capitalization studies
- London-specific transport and housing market research

## 👨‍💻 Author

**Andrey Zhuravlev**  
Master of Science in Data Science and Analytics  
Toronto Metropolitan University, 2025

---

*This framework provides a robust, academically-rigorous approach to analyzing the relationship between transit network changes and housing market dynamics in London.*
