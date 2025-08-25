#!/usr/bin/env python3
"""
Panel Regression Analysis for London Transit Network and Housing Market
London Transit Network and Housing Market Analysis (2000-2023)

This script:
1. Loads the final modeling dataset
2. Runs panel regression with fixed effects
3. Analyzes the relationship between centrality measures and housing prices
4. Saves detailed regression results and diagnostics

Author: Andrey Zhuravlev
Date: 2025
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from statsmodels.stats.diagnostic import het_breuschpagan, het_white
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class PanelRegressionAnalyzer:
    def __init__(self):
        """Initialize the panel regression analyzer."""
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "modeling" / "data"
        self.output_dir = self.project_root / "modeling" / "outputs"
        
        # Input file
        self.dataset_file = self.data_dir / "final_modeling_dataset.csv"
        
        # Output files
        self.regression_summary_file = self.output_dir / "regression_summary.txt"
        self.coefficients_file = self.output_dir / "coefficients.csv"
        self.diagnostics_file = self.output_dir / "diagnostics.txt"
        self.residuals_plot_file = self.output_dir / "residuals_plot.png"
        
        # Centrality measures (lagged versions) - REMOVED Weighted_Out_Degree_Lag1 due to multicollinearity
        self.centrality_measures = [
            'Weighted_In_Degree_Lag1',  # Keep only in-degree (total flow)
            'Betweenness_Centrality_Lag1', 'Closeness_Centrality_Lag1', 
            'Eigenvector_Centrality_Lag1'
        ]
        
        # Community measures (if available)
        self.community_measures = ['Community_ID_Lag1', 'Participation_Coefficient_Lag1']
        
        # Additional variables - REMOVED COVID_Period due to perfect collinearity with year dummies
        self.additional_vars = []
        
    def load_data(self):
        """Load the final modeling dataset."""
        print("Loading final modeling dataset...")
        
        df = pd.read_csv(self.dataset_file)
        
        print(f"Loaded dataset with {len(df)} observations")
        print(f"Years: {sorted(df['Year'].unique())}")
        print(f"Boroughs: {len(df['Borough'].unique())}")
        print(f"Columns: {len(df.columns)}")
        
        # Check for missing values
        missing_summary = df.isnull().sum()
        if missing_summary.sum() > 0:
            print("Missing values found:")
            print(missing_summary[missing_summary > 0])
        
        return df
    
    def prepare_regression_data(self, df):
        """Prepare data for regression analysis."""
        print("Preparing data for regression analysis...")
        
        # Select variables for the model
        model_vars = ['Average_House_Price', 'Year', 'Borough'] + self.centrality_measures
        
        # Add community measures if available
        for measure in self.community_measures:
            if measure in df.columns:
                model_vars.append(measure)
        
        # Add additional variables
        for var in self.additional_vars:
            if var in df.columns:
                model_vars.append(var)
        
        # Filter to only include available variables
        available_vars = [var for var in model_vars if var in df.columns]
        model_df = df[available_vars].copy()
        
        # Remove rows with missing values
        initial_rows = len(model_df)
        model_df = model_df.dropna()
        final_rows = len(model_df)
        
        print(f"Removed {initial_rows - final_rows} rows with missing values")
        print(f"Final model dataset: {len(model_df)} observations")
        
        # Log transform housing prices (common in real estate analysis)
        model_df['Log_Average_House_Price'] = np.log(model_df['Average_House_Price'])
        
        # Standardize centrality measures (z-score normalization)
        for measure in self.centrality_measures:
            if measure in model_df.columns:
                mean_val = model_df[measure].mean()
                std_val = model_df[measure].std()
                model_df[f"{measure}_Standardized"] = (model_df[measure] - mean_val) / std_val
        
        return model_df
    
    def run_basic_regression(self, df):
        """Run basic OLS regression without fixed effects."""
        print("Running basic OLS regression...")
        
        # Prepare variables
        y = df['Log_Average_House_Price']
        
        # Get standardized centrality measures
        centrality_vars = [col for col in df.columns if col.endswith('_Standardized')]
        
        # Add other variables
        other_vars = []
        for var in self.additional_vars:
            if var in df.columns:
                other_vars.append(var)
        
        X_vars = centrality_vars + other_vars
        X = df[X_vars]
        
        # Add constant
        X = sm.add_constant(X)
        
        # Run regression
        model = OLS(y, X)
        results = model.fit(cov_type='cluster', cov_kwds={'groups': df['Borough']})
        
        return results, X_vars
    
    def run_fixed_effects_regression(self, df):
        """Run panel regression with fixed effects."""
        print("Running panel regression with fixed effects...")
        
        # Prepare variables
        y = df['Log_Average_House_Price']
        
        # Get standardized centrality measures
        centrality_vars = [col for col in df.columns if col.endswith('_Standardized')]
        
        # Add other variables
        other_vars = []
        for var in self.additional_vars:
            if var in df.columns:
                other_vars.append(var)
        
        X_vars = centrality_vars + other_vars
        X = df[X_vars]
        
        # Add constant
        X = sm.add_constant(X)
        
        # Create fixed effects
        # Year fixed effects
        year_dummies = pd.get_dummies(df['Year'], prefix='Year', drop_first=True)
        year_dummies = year_dummies.astype(float)  # Convert to numeric
        X = pd.concat([X, year_dummies], axis=1)
        
        # Borough fixed effects - clean borough names first
        df['Borough_Clean'] = df['Borough'].str.replace('&', 'and').str.replace(' ', '_')
        borough_dummies = pd.get_dummies(df['Borough_Clean'], prefix='Borough', drop_first=True)
        borough_dummies = borough_dummies.astype(float)  # Convert to numeric
        X = pd.concat([X, borough_dummies], axis=1)
        
        # Run regression with clustered standard errors
        model = OLS(y, X)
        results = model.fit(cov_type='cluster', cov_kwds={'groups': df['Borough']})
        
        return results, X_vars
    
    # REMOVED: run_interaction_models function due to multicollinearity issues
    
    def calculate_diagnostics(self, results, df):
        """Calculate regression diagnostics."""
        print("Calculating regression diagnostics...")
        
        diagnostics = {}
        
        # R-squared and adjusted R-squared
        diagnostics['R_squared'] = results.rsquared
        diagnostics['Adj_R_squared'] = results.rsquared_adj
        
        # F-statistic
        diagnostics['F_statistic'] = results.fvalue
        diagnostics['F_pvalue'] = results.f_pvalue
        
        # Number of observations
        diagnostics['N_observations'] = results.nobs
        
        # Degrees of freedom
        diagnostics['DF_model'] = results.df_model
        diagnostics['DF_residuals'] = results.df_resid
        
        # Residual analysis
        residuals = results.resid
        fitted_values = results.fittedvalues
        
        # Normality test (Jarque-Bera)
        from scipy import stats
        jb_stat, jb_pvalue = stats.jarque_bera(residuals)
        diagnostics['Jarque_Bera_stat'] = jb_stat
        diagnostics['Jarque_Bera_pvalue'] = jb_pvalue
        
        # Heteroscedasticity tests
        try:
            bp_stat, bp_pvalue, bp_f, bp_f_pvalue = het_breuschpagan(residuals, results.model.exog)
            diagnostics['Breusch_Pagan_stat'] = bp_stat
            diagnostics['Breusch_Pagan_pvalue'] = bp_pvalue
        except:
            diagnostics['Breusch_Pagan_stat'] = None
            diagnostics['Breusch_Pagan_pvalue'] = None
        
        # Multicollinearity (VIF)
        try:
            vif_data = []
            for i in range(1, len(results.model.exog_names)):  # Skip constant
                vif = variance_inflation_factor(results.model.exog, i)
                vif_data.append((results.model.exog_names[i], vif))
            diagnostics['VIF'] = vif_data
        except:
            diagnostics['VIF'] = None
        
        return diagnostics
    
    def save_results(self, basic_results, fe_results, diagnostics, df):
        """Save all regression results and diagnostics."""
        print("Saving regression results...")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed regression summary
        with open(self.regression_summary_file, 'w') as f:
            f.write("PANEL REGRESSION ANALYSIS RESULTS\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("DATASET SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total observations: {len(df)}\n")
            f.write(f"Years: {sorted(df['Year'].unique())}\n")
            f.write(f"Boroughs: {len(df['Borough'].unique())}\n")
            f.write(f"Time period: {df['Year'].min()} - {df['Year'].max()}\n\n")
            
            f.write("BASIC OLS REGRESSION (No Fixed Effects)\n")
            f.write("-" * 50 + "\n")
            f.write(basic_results.summary().as_text())
            f.write("\n\n")
            
            f.write("PANEL REGRESSION WITH FIXED EFFECTS\n")
            f.write("-" * 50 + "\n")
            f.write(fe_results.summary().as_text())
            f.write("\n\n")
            
            f.write("DIAGNOSTICS\n")
            f.write("-" * 20 + "\n")
            for key, value in diagnostics.items():
                if key == 'VIF' and value:
                    f.write(f"\nVIF (Variance Inflation Factor):\n")
                    for var, vif in value:
                        f.write(f"  {var}: {vif:.3f}\n")
                else:
                    f.write(f"{key}: {value}\n")
        
        # Save coefficients to CSV
        coefficients_df = pd.DataFrame({
            'Variable': fe_results.params.index,
            'Coefficient': fe_results.params.values,
            'Std_Error': fe_results.bse.values,
            't_statistic': fe_results.tvalues.values,
            'p_value': fe_results.pvalues.values,
            'CI_Lower': fe_results.conf_int().iloc[:, 0],
            'CI_Upper': fe_results.conf_int().iloc[:, 1]
        })
        coefficients_df.to_csv(self.coefficients_file, index=False)
        
        # Save diagnostics
        with open(self.diagnostics_file, 'w') as f:
            f.write("REGRESSION DIAGNOSTICS\n")
            f.write("=" * 30 + "\n\n")
            
            f.write("MODEL FIT\n")
            f.write("-" * 15 + "\n")
            f.write(f"R-squared: {diagnostics['R_squared']:.4f}\n")
            f.write(f"Adjusted R-squared: {diagnostics['Adj_R_squared']:.4f}\n")
            f.write(f"F-statistic: {diagnostics['F_statistic']:.4f}\n")
            f.write(f"F p-value: {diagnostics['F_pvalue']:.4f}\n")
            f.write(f"Observations: {diagnostics['N_observations']}\n\n")
            
            f.write("RESIDUAL ANALYSIS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Jarque-Bera statistic: {diagnostics['Jarque_Bera_stat']:.4f}\n")
            f.write(f"Jarque-Bera p-value: {diagnostics['Jarque_Bera_pvalue']:.4f}\n")
            
            if diagnostics['Breusch_Pagan_pvalue'] is not None:
                f.write(f"Breusch-Pagan statistic: {diagnostics['Breusch_Pagan_stat']:.4f}\n")
                f.write(f"Breusch-Pagan p-value: {diagnostics['Breusch_Pagan_pvalue']:.4f}\n")
            
            f.write("\nMULTICOLLINEARITY\n")
            f.write("-" * 20 + "\n")
            if diagnostics['VIF']:
                for var, vif in diagnostics['VIF']:
                    f.write(f"{var}: {vif:.3f}\n")
        
        print(f"Results saved to {self.regression_summary_file}")
        print(f"Coefficients saved to {self.coefficients_file}")
        print(f"Diagnostics saved to {self.diagnostics_file}")
    
    def create_residuals_plot(self, results, df):
        """Create diagnostic plots for residuals."""
        print("Creating residual diagnostic plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Regression Diagnostics', fontsize=16, fontweight='bold')
        
        residuals = results.resid
        fitted_values = results.fittedvalues
        
        # Residuals vs Fitted
        axes[0, 0].scatter(fitted_values, residuals, alpha=0.6)
        axes[0, 0].axhline(y=0, color='red', linestyle='--')
        axes[0, 0].set_xlabel('Fitted Values')
        axes[0, 0].set_ylabel('Residuals')
        axes[0, 0].set_title('Residuals vs Fitted')
        
        # Q-Q Plot
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Q-Q Plot')
        
        # Residuals histogram
        axes[1, 0].hist(residuals, bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Residuals')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Residuals Distribution')
        
        # Residuals over time
        axes[1, 1].scatter(df['Year'], residuals, alpha=0.6)
        axes[1, 1].axhline(y=0, color='red', linestyle='--')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Residuals')
        axes[1, 1].set_title('Residuals vs Time')
        
        plt.tight_layout()
        plt.savefig(self.residuals_plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Residuals plot saved to {self.residuals_plot_file}")
    
    def run(self):
        """Run the complete panel regression analysis."""
        print("=" * 60)
        print("PANEL REGRESSION ANALYSIS")
        print("=" * 60)
        
        # Step 1: Load data
        df = self.load_data()
        
        # Step 2: Prepare regression data
        model_df = self.prepare_regression_data(df)
        
        # Step 3: Run basic regression
        basic_results, basic_vars = self.run_basic_regression(model_df)
        
        # Step 4: Run fixed effects regression
        fe_results, fe_vars = self.run_fixed_effects_regression(model_df)
        
        # Step 5: Calculate diagnostics
        diagnostics = self.calculate_diagnostics(fe_results, model_df)
        
        # Step 6: Save results
        self.save_results(basic_results, fe_results, diagnostics, model_df)
        
        # Step 8: Create diagnostic plots
        self.create_residuals_plot(fe_results, model_df)
        
        return fe_results, diagnostics

if __name__ == "__main__":
    analyzer = PanelRegressionAnalyzer()
    results, diagnostics = analyzer.run()
    
    print("\n" + "=" * 60)
    print("PANEL REGRESSION ANALYSIS COMPLETED")
    print("=" * 60)
    print(f"R-squared: {diagnostics['R_squared']:.4f}")
    print(f"Adjusted R-squared: {diagnostics['Adj_R_squared']:.4f}")
    print(f"F-statistic: {diagnostics['F_statistic']:.4f}")
    print(f"Observations: {diagnostics['N_observations']}")
    print(f"Output files saved to: {analyzer.output_dir}")
