# Modeling Scripts

This folder contains the panel regression analysis scripts for the London Transit Network and Housing Market Analysis.

## Scripts

- **01_prepare_final_dataset.py**: Prepares the final dataset by merging centrality metrics with housing price data and creating lagged variables
- **02_run_panel_regression.py**: Runs panel regression analysis with fixed effects and comprehensive diagnostics
- **03_visualize_results.py**: Creates publication-quality visualizations and interpretation reports
- **run_complete_analysis.py**: Master script that runs all three scripts in sequence

## Usage

Run the complete analysis pipeline:
```bash
python Scripts/Modeling/run_complete_analysis.py
```

Or run individual scripts:
```bash
python Scripts/Modeling/01_prepare_final_dataset.py
python Scripts/Modeling/02_run_panel_regression.py
python Scripts/Modeling/03_visualize_results.py
```

## Outputs

All outputs are saved to the `modeling/` folder:
- `modeling/data/` - Final dataset and summaries
- `modeling/outputs/` - Regression results and visualizations

See `modeling/README.md` for detailed documentation.
