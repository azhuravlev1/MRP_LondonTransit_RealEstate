#!/usr/bin/env python3
"""
Prepare Final Dataset for Panel Regression Analysis
London Transit Network and Housing Market Analysis (2000-2023)

This script:
1. Loads centrality metrics from all_metrics_timeseries.csv
2. Loads housing price data from UK House Price Index
3. Merges the datasets by Year and Borough
4. Creates lagged variables for causality analysis
5. Saves the final modeling dataset

Author: Andrey Zhuravlev
Date: 2025
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class DatasetPreparer:
    def __init__(self):
        """Initialize the dataset preparer with file paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "Data"
        self.output_dir = self.project_root / "modeling" / "data"
        
        # Input files
        self.centrality_file = self.data_dir / "Outputs" / "Metrics" / "all_metrics_timeseries.csv"
        self.housing_file = self.data_dir / "UK_House_price_index.xlsx"
        
        # Output file
        self.final_dataset_file = self.output_dir / "final_modeling_dataset.csv"
        
        # Centrality measures to include in the model
        self.centrality_measures = [
            'Weighted_In_Degree', 'Weighted_Out_Degree', 'Betweenness_Centrality',
            'Closeness_Centrality', 'Eigenvector_Centrality'
        ]
        
        # Community measures (if available)
        self.community_measures = ['Community_ID', 'Participation_Coefficient']
        
    def load_centrality_data(self):
        """Load and preprocess centrality metrics data."""
        print("Loading centrality metrics data...")
        
        # Load the centrality data
        df = pd.read_csv(self.centrality_file)
        
        print(f"Loaded {len(df)} records from centrality data")
        print(f"Columns: {list(df.columns)}")
        print(f"Years: {sorted(df['Year'].unique())}")
        print(f"Boroughs: {len(df['Borough'].unique())}")
        
        # Filter to include only the measures we need
        columns_to_keep = ['Year', 'Borough', 'DayType', 'TimeBand'] + self.centrality_measures
        
        # Add community measures if they exist
        for measure in self.community_measures:
            if measure in df.columns:
                columns_to_keep.append(measure)
        
        df = df[columns_to_keep]
        
        # Aggregate by year and borough (average across day types and time bands)
        print("Aggregating data by year and borough...")
        agg_columns = self.centrality_measures.copy()
        for measure in self.community_measures:
            if measure in df.columns:
                agg_columns.append(measure)
        
        df_agg = df.groupby(['Year', 'Borough'])[agg_columns].mean().reset_index()
        
        print(f"Aggregated to {len(df_agg)} year-borough combinations")
        
        return df_agg
    
    def load_housing_data(self):
        """Load and preprocess housing price data."""
        print("Loading housing price data...")
        
        # Load the Excel file
        housing_df = pd.read_excel(self.housing_file, sheet_name='Average price')
        
        print(f"Loaded housing data with shape: {housing_df.shape}")
        print(f"Columns: {list(housing_df.columns)}")
        
        # The housing data has a specific structure:
        # Column names: Borough names
        # First row: Administrative codes
        # Second row onwards: Monthly data starting from Jan-95
        
        # Skip the first row (administrative codes) and start from the second row
        housing_df = housing_df.iloc[1:].reset_index(drop=True)
        
        # The first column contains dates
        housing_df = housing_df.rename(columns={housing_df.columns[0]: 'Date'})
        
        # Convert date column to datetime - handle format like "Jan-95", "Feb-95"
        housing_df['Date'] = pd.to_datetime(housing_df['Date'], format='%b-%y', errors='coerce')
        
        # Filter to only include London boroughs (exclude regional and national data)
        london_boroughs = [
            'Barking & Dagenham', 'Barnet', 'Bexley', 'Brent', 'Bromley', 'Camden',
            'Croydon', 'Ealing', 'Enfield', 'Greenwich', 'Hackney', 'Hammersmith & Fulham',
            'Haringey', 'Harrow', 'Havering', 'Hillingdon', 'Hounslow', 'Islington',
            'Kensington & Chelsea', 'Kingston upon Thames', 'Lambeth', 'Lewisham',
            'Merton', 'Newham', 'Redbridge', 'Richmond upon Thames', 'Southwark',
            'Sutton', 'Tower Hamlets', 'Waltham Forest', 'Wandsworth', 'Westminster',
            'City of London'
        ]
        
        # Filter columns to only include London boroughs
        borough_columns = [col for col in housing_df.columns if col in london_boroughs]
        housing_df = housing_df[['Date'] + borough_columns]
        
        # Melt the data to long format
        housing_df_long = housing_df.melt(
            id_vars=['Date'], 
            value_vars=borough_columns,
            var_name='Borough', 
            value_name='Average_House_Price'
        )
        
        # Convert price to numeric, removing any non-numeric values
        housing_df_long['Average_House_Price'] = pd.to_numeric(
            housing_df_long['Average_House_Price'], errors='coerce'
        )
        
        # Add year column
        housing_df_long['Year'] = housing_df_long['Date'].dt.year
        
        # Aggregate to annual data (average across months)
        housing_annual = housing_df_long.groupby(['Year', 'Borough'])['Average_House_Price'].mean().reset_index()
        
        # Filter to years that match our centrality data
        housing_annual = housing_annual[housing_annual['Year'] >= 2000]
        
        print(f"Processed housing data: {len(housing_annual)} year-borough combinations")
        print(f"Years: {sorted(housing_annual['Year'].unique())}")
        print(f"Boroughs: {len(housing_annual['Borough'].unique())}")
        
        return housing_annual
    
    def standardize_borough_names(self, df, borough_column='Borough'):
        """Standardize borough names to ensure consistent matching."""
        # Borough names should already match between datasets
        # This function is kept for potential future use if needed
        return df
    
    def create_lagged_variables(self, df):
        """Create lagged versions of centrality measures for causality analysis."""
        print("Creating lagged variables...")
        
        # Sort by borough and year
        df = df.sort_values(['Borough', 'Year']).reset_index(drop=True)
        
        # Create lagged variables for each centrality measure
        for measure in self.centrality_measures:
            if measure in df.columns:
                lagged_col = f"{measure}_Lag1"
                df[lagged_col] = df.groupby('Borough')[measure].shift(1)
                print(f"Created {lagged_col}")
        
        # Create lagged variables for community measures if available
        for measure in self.community_measures:
            if measure in df.columns:
                lagged_col = f"{measure}_Lag1"
                df[lagged_col] = df.groupby('Borough')[measure].shift(1)
                print(f"Created {lagged_col}")
        
        # Remove rows with missing lagged values (first year for each borough)
        initial_rows = len(df)
        df = df.dropna(subset=[col for col in df.columns if col.endswith('_Lag1')])
        final_rows = len(df)
        
        print(f"Removed {initial_rows - final_rows} rows with missing lagged values")
        
        return df
    
    def merge_datasets(self, centrality_df, housing_df):
        """Merge centrality and housing datasets."""
        print("Merging centrality and housing datasets...")
        
        # Standardize borough names in both datasets
        centrality_df = self.standardize_borough_names(centrality_df)
        housing_df = self.standardize_borough_names(housing_df)
        
        # Merge on Year and Borough
        merged_df = pd.merge(
            centrality_df, 
            housing_df, 
            on=['Year', 'Borough'], 
            how='inner'
        )
        
        print(f"Merged dataset has {len(merged_df)} observations")
        print(f"Years: {sorted(merged_df['Year'].unique())}")
        print(f"Boroughs: {len(merged_df['Borough'].unique())}")
        
        # Check for missing values
        missing_housing = merged_df['Average_House_Price'].isna().sum()
        if missing_housing > 0:
            print(f"Warning: {missing_housing} missing housing price values")
        
        return merged_df
    
    def create_additional_variables(self, df):
        """Create additional variables that might be useful for the analysis."""
        print("Creating additional variables...")
        
        # Create year fixed effects (dummy variables for each year)
        year_dummies = pd.get_dummies(df['Year'], prefix='Year')
        df = pd.concat([df, year_dummies], axis=1)
        
        # Create borough fixed effects (dummy variables for each borough)
        borough_dummies = pd.get_dummies(df['Borough'], prefix='Borough')
        df = pd.concat([df, borough_dummies], axis=1)
        
        # Create interaction terms between centrality measures and year
        for measure in self.centrality_measures:
            if f"{measure}_Lag1" in df.columns:
                # Interaction with year (centered)
                df[f"{measure}_Lag1_Year_Interaction"] = (
                    df[f"{measure}_Lag1"] * (df['Year'] - df['Year'].mean())
                )
        
        # Create a COVID indicator (2020 onwards)
        df['COVID_Period'] = (df['Year'] >= 2020).astype(int)
        
        # Create interaction terms with COVID period
        for measure in self.centrality_measures:
            if f"{measure}_Lag1" in df.columns:
                df[f"{measure}_Lag1_COVID_Interaction"] = (
                    df[f"{measure}_Lag1"] * df['COVID_Period']
                )
        
        print("Created additional variables including:")
        print("- Year fixed effects")
        print("- Borough fixed effects") 
        print("- Year interactions")
        print("- COVID period indicator and interactions")
        
        return df
    
    def save_final_dataset(self, df):
        """Save the final dataset for modeling."""
        print(f"Saving final dataset to {self.final_dataset_file}")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the dataset
        df.to_csv(self.final_dataset_file, index=False)
        
        # Create a summary of the final dataset
        summary_file = self.output_dir / "dataset_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("FINAL MODELING DATASET SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total observations: {len(df)}\n")
            f.write(f"Years: {sorted(df['Year'].unique())}\n")
            f.write(f"Boroughs: {len(df['Borough'].unique())}\n")
            f.write(f"Columns: {len(df.columns)}\n\n")
            
            f.write("CENTRALITY MEASURES:\n")
            for measure in self.centrality_measures:
                if measure in df.columns:
                    f.write(f"- {measure}\n")
                if f"{measure}_Lag1" in df.columns:
                    f.write(f"- {measure}_Lag1\n")
            
            f.write("\nHOUSING DATA:\n")
            f.write("- Average_House_Price\n")
            
            f.write("\nADDITIONAL VARIABLES:\n")
            f.write("- Year fixed effects\n")
            f.write("- Borough fixed effects\n")
            f.write("- COVID_Period indicator\n")
            f.write("- Interaction terms\n")
            
            f.write(f"\nMissing values:\n")
            for col in df.columns:
                missing = df[col].isna().sum()
                if missing > 0:
                    f.write(f"- {col}: {missing} missing values\n")
        
        print(f"Dataset summary saved to {summary_file}")
        print("Dataset preparation completed successfully!")
        
        return df
    
    def run(self):
        """Run the complete dataset preparation process."""
        print("=" * 60)
        print("PREPARING FINAL DATASET FOR PANEL REGRESSION ANALYSIS")
        print("=" * 60)
        
        # Step 1: Load centrality data
        centrality_df = self.load_centrality_data()
        
        # Step 2: Load housing data
        housing_df = self.load_housing_data()
        
        # Step 3: Merge datasets
        merged_df = self.merge_datasets(centrality_df, housing_df)
        
        # Step 4: Create lagged variables
        lagged_df = self.create_lagged_variables(merged_df)
        
        # Step 5: Create additional variables
        final_df = self.create_additional_variables(lagged_df)
        
        # Step 6: Save final dataset
        self.save_final_dataset(final_df)
        
        return final_df

if __name__ == "__main__":
    preparer = DatasetPreparer()
    final_dataset = preparer.run()
    
    print("\n" + "=" * 60)
    print("DATASET PREPARATION COMPLETED")
    print("=" * 60)
    print(f"Final dataset shape: {final_dataset.shape}")
    print(f"Years: {sorted(final_dataset['Year'].unique())}")
    print(f"Boroughs: {len(final_dataset['Borough'].unique())}")
    print(f"Output file: {preparer.final_dataset_file}")
