#!/usr/bin/env python3
"""
Visualize Panel Regression Results
London Transit Network and Housing Market Analysis (2000-2023)

This script:
1. Loads regression results from the previous analysis
2. Creates coefficient plots and effect size visualizations
3. Generates interpretation-ready plots for the MRP
4. Saves publication-quality visualizations

Author: Andrey Zhuravlev
Date: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class ResultsVisualizer:
    def __init__(self):
        """Initialize the results visualizer."""
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "modeling" / "data"
        self.output_dir = self.project_root / "modeling" / "outputs"
        
        # Input files
        self.coefficients_file = self.output_dir / "coefficients.csv"
        self.dataset_file = self.data_dir / "final_modeling_dataset.csv"
        
        # Output files
        self.coefficient_plot_file = self.output_dir / "coefficient_plot.png"
        self.effect_size_plot_file = self.output_dir / "effect_size_plot.png"
        self.interaction_plot_file = self.output_dir / "interaction_plot.png"
        self.summary_dashboard_file = self.output_dir / "results_dashboard.png"
        
        # Centrality measure labels for better visualization
        self.centrality_labels = {
            'Weighted_In_Degree_Lag1_Standardized': 'Passenger Arrivals (t-1)',
            'Weighted_Out_Degree_Lag1_Standardized': 'Passenger Departures (t-1)',
            'Betweenness_Centrality_Lag1_Standardized': 'Betweenness Centrality (t-1)',
            'Closeness_Centrality_Lag1_Standardized': 'Closeness Centrality (t-1)',
            'Eigenvector_Centrality_Lag1_Standardized': 'Eigenvector Centrality (t-1)'
        }
        
    def load_results(self):
        """Load regression results and coefficients."""
        print("Loading regression results...")
        
        # Load coefficients
        coefficients_df = pd.read_csv(self.coefficients_file)
        
        # Load original dataset for additional analysis
        dataset_df = pd.read_csv(self.dataset_file)
        
        print(f"Loaded coefficients for {len(coefficients_df)} variables")
        print(f"Dataset has {len(dataset_df)} observations")
        
        return coefficients_df, dataset_df
    
    def filter_centrality_coefficients(self, coefficients_df):
        """Filter to only centrality-related coefficients."""
        # Get centrality coefficients (excluding fixed effects and interactions)
        centrality_vars = [var for var in coefficients_df['Variable'] 
                          if any(measure in var for measure in self.centrality_labels.keys())]
        
        # Filter to main effects (not interactions)
        main_effects = [var for var in centrality_vars if not any(x in var for x in ['Interaction', 'Year_', 'Borough_'])]
        
        centrality_coeffs = coefficients_df[coefficients_df['Variable'].isin(main_effects)].copy()
        
        # Add readable labels
        centrality_coeffs['Label'] = centrality_coeffs['Variable'].map(self.centrality_labels)
        
        return centrality_coeffs
    
    def create_coefficient_plot(self, coefficients_df):
        """Create the main coefficient plot showing effect sizes and significance."""
        print("Creating coefficient plot...")
        
        # Filter to centrality coefficients
        centrality_coeffs = self.filter_centrality_coefficients(coefficients_df)
        
        if len(centrality_coeffs) == 0:
            print("No centrality coefficients found in results")
            return
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by coefficient value
        centrality_coeffs = centrality_coeffs.sort_values('Coefficient')
        
        # Create horizontal bar plot
        y_pos = np.arange(len(centrality_coeffs))
        bars = ax.barh(y_pos, centrality_coeffs['Coefficient'], 
                      xerr=centrality_coeffs['Std_Error'],
                      capsize=5, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Color bars based on significance
        for i, (bar, p_value) in enumerate(zip(bars, centrality_coeffs['p_value'])):
            if p_value < 0.01:
                bar.set_color('#2E8B57')  # Dark green for highly significant
            elif p_value < 0.05:
                bar.set_color('#4682B4')  # Blue for significant
            elif p_value < 0.1:
                bar.set_color('#FF8C00')  # Orange for marginally significant
            else:
                bar.set_color('#DC143C')  # Red for not significant
        
        # Add vertical line at zero
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        
        # Customize the plot
        ax.set_yticks(y_pos)
        ax.set_yticklabels(centrality_coeffs['Label'], fontsize=12)
        ax.set_xlabel('Coefficient (Log House Price)', fontsize=14, fontweight='bold')
        ax.set_title('Impact of Transit Network Centrality on Housing Prices\n(Panel Regression with Fixed Effects)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add significance annotations
        for i, (coeff, p_value) in enumerate(zip(centrality_coeffs['Coefficient'], centrality_coeffs['p_value'])):
            if p_value < 0.01:
                sig_text = '***'
            elif p_value < 0.05:
                sig_text = '**'
            elif p_value < 0.1:
                sig_text = '*'
            else:
                sig_text = ''
            
            if sig_text:
                ax.text(coeff + (0.01 if coeff > 0 else -0.01), i, sig_text, 
                       fontsize=14, fontweight='bold', ha='center', va='center')
        
        # Add legend for significance levels
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='#2E8B57', alpha=0.7, label='p < 0.01'),
            plt.Rectangle((0,0),1,1, facecolor='#4682B4', alpha=0.7, label='p < 0.05'),
            plt.Rectangle((0,0),1,1, facecolor='#FF8C00', alpha=0.7, label='p < 0.10'),
            plt.Rectangle((0,0),1,1, facecolor='#DC143C', alpha=0.7, label='p ≥ 0.10')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.coefficient_plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Coefficient plot saved to {self.coefficient_plot_file}")
    
    def create_effect_size_plot(self, coefficients_df, dataset_df):
        """Create a plot showing the practical significance of effects."""
        print("Creating effect size plot...")
        
        # Filter to centrality coefficients
        centrality_coeffs = self.filter_centrality_coefficients(coefficients_df)
        
        if len(centrality_coeffs) == 0:
            print("No centrality coefficients found for effect size analysis")
            return
        
        # Calculate effect sizes (percentage change in house prices for 1 SD change in centrality)
        centrality_coeffs['Effect_Size_Percent'] = (
            (np.exp(centrality_coeffs['Coefficient']) - 1) * 100
        )
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Plot 1: Effect sizes
        y_pos = np.arange(len(centrality_coeffs))
        bars1 = ax1.barh(y_pos, centrality_coeffs['Effect_Size_Percent'], 
                        alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Color bars based on significance
        for i, (bar, p_value) in enumerate(zip(bars1, centrality_coeffs['p_value'])):
            if p_value < 0.01:
                bar.set_color('#2E8B57')
            elif p_value < 0.05:
                bar.set_color('#4682B4')
            elif p_value < 0.1:
                bar.set_color('#FF8C00')
            else:
                bar.set_color('#DC143C')
        
        ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(centrality_coeffs['Label'], fontsize=11)
        ax1.set_xlabel('Effect Size (% Change in House Prices)', fontsize=12, fontweight='bold')
        ax1.set_title('Practical Significance:\nEffect of 1 SD Change in Centrality', 
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Coefficient vs Standard Error (precision)
        ax2.scatter(centrality_coeffs['Coefficient'], centrality_coeffs['Std_Error'], 
                   s=100, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Color points based on significance
        for i, (coeff, std_err, p_value) in enumerate(zip(centrality_coeffs['Coefficient'], 
                                                         centrality_coeffs['Std_Error'], 
                                                         centrality_coeffs['p_value'])):
            if p_value < 0.01:
                color = '#2E8B57'
            elif p_value < 0.05:
                color = '#4682B4'
            elif p_value < 0.1:
                color = '#FF8C00'
            else:
                color = '#DC143C'
            
            ax2.scatter(coeff, std_err, color=color, s=100, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Add labels for each point
        for i, (coeff, std_err, label) in enumerate(zip(centrality_coeffs['Coefficient'], 
                                                       centrality_coeffs['Std_Error'], 
                                                       centrality_coeffs['Label'])):
            ax2.annotate(label.split(' (')[0], (coeff, std_err), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        ax2.set_xlabel('Coefficient', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Standard Error', fontsize=12, fontweight='bold')
        ax2.set_title('Precision vs Effect Size', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.effect_size_plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Effect size plot saved to {self.effect_size_plot_file}")
    
    def create_interaction_plot(self, coefficients_df):
        """Create a plot showing interaction effects (e.g., COVID period)."""
        print("Creating interaction plot...")
        
        # Look for COVID interaction coefficients
        covid_interactions = coefficients_df[
            coefficients_df['Variable'].str.contains('COVID_Interaction', na=False)
        ].copy()
        
        if len(covid_interactions) == 0:
            print("No COVID interaction coefficients found")
            return
        
        # Create readable labels
        covid_interactions['Label'] = covid_interactions['Variable'].str.replace(
            '_Lag1_Standardized_COVID_Interaction', ' (COVID Effect)'
        ).str.replace('_Lag1_Standardized', '')
        
        # Map to readable names
        label_mapping = {
            'Weighted_In_Degree': 'Passenger Arrivals',
            'Weighted_Out_Degree': 'Passenger Departures',
            'Betweenness_Centrality': 'Betweenness Centrality',
            'Closeness_Centrality': 'Closeness Centrality',
            'Eigenvector_Centrality': 'Eigenvector Centrality'
        }
        
        covid_interactions['Label'] = covid_interactions['Label'].map(label_mapping)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by coefficient value
        covid_interactions = covid_interactions.sort_values('Coefficient')
        
        y_pos = np.arange(len(covid_interactions))
        bars = ax.barh(y_pos, covid_interactions['Coefficient'], 
                      xerr=covid_interactions['Std_Error'],
                      capsize=5, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Color bars based on significance
        for i, (bar, p_value) in enumerate(zip(bars, covid_interactions['p_value'])):
            if p_value < 0.01:
                bar.set_color('#2E8B57')
            elif p_value < 0.05:
                bar.set_color('#4682B4')
            elif p_value < 0.1:
                bar.set_color('#FF8C00')
            else:
                bar.set_color('#DC143C')
        
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(covid_interactions['Label'], fontsize=12)
        ax.set_xlabel('COVID Interaction Coefficient (Log House Price)', fontsize=14, fontweight='bold')
        ax.set_title('COVID-19 Impact on Transit-Housing Price Relationship', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add significance annotations
        for i, (coeff, p_value) in enumerate(zip(covid_interactions['Coefficient'], covid_interactions['p_value'])):
            if p_value < 0.01:
                sig_text = '***'
            elif p_value < 0.05:
                sig_text = '**'
            elif p_value < 0.1:
                sig_text = '*'
            else:
                sig_text = ''
            
            if sig_text:
                ax.text(coeff + (0.01 if coeff > 0 else -0.01), i, sig_text, 
                       fontsize=14, fontweight='bold', ha='center', va='center')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.interaction_plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Interaction plot saved to {self.interaction_plot_file}")
    
    def create_summary_dashboard(self, coefficients_df, dataset_df):
        """Create a comprehensive dashboard summarizing all results."""
        print("Creating summary dashboard...")
        
        # Filter to centrality coefficients
        centrality_coeffs = self.filter_centrality_coefficients(coefficients_df)
        
        if len(centrality_coeffs) == 0:
            print("No centrality coefficients found for dashboard")
            return
        
        # Create the dashboard
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Plot 1: Main coefficient plot (top left, spanning 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        centrality_coeffs_sorted = centrality_coeffs.sort_values('Coefficient')
        y_pos = np.arange(len(centrality_coeffs_sorted))
        bars = ax1.barh(y_pos, centrality_coeffs_sorted['Coefficient'], 
                       xerr=centrality_coeffs_sorted['Std_Error'],
                       capsize=5, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Color bars based on significance
        for i, (bar, p_value) in enumerate(zip(bars, centrality_coeffs_sorted['p_value'])):
            if p_value < 0.01:
                bar.set_color('#2E8B57')
            elif p_value < 0.05:
                bar.set_color('#4682B4')
            elif p_value < 0.1:
                bar.set_color('#FF8C00')
            else:
                bar.set_color('#DC143C')
        
        ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(centrality_coeffs_sorted['Label'], fontsize=10)
        ax1.set_xlabel('Coefficient (Log House Price)', fontsize=12, fontweight='bold')
        ax1.set_title('Main Effects: Transit Centrality on Housing Prices', 
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Effect sizes (top right)
        ax2 = fig.add_subplot(gs[0, 2])
        effect_sizes = (np.exp(centrality_coeffs['Coefficient']) - 1) * 100
        ax2.barh(range(len(effect_sizes)), effect_sizes, alpha=0.7, edgecolor='black', linewidth=0.5)
        ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_yticks(range(len(effect_sizes)))
        ax2.set_yticklabels([label.split(' (')[0] for label in centrality_coeffs['Label']], fontsize=9)
        ax2.set_xlabel('Effect Size (%)', fontsize=10, fontweight='bold')
        ax2.set_title('Practical Significance', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Time series of average centrality (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        centrality_measures = ['Weighted_In_Degree', 'Betweenness_Centrality', 'Eigenvector_Centrality']
        for measure in centrality_measures:
            if measure in dataset_df.columns:
                yearly_avg = dataset_df.groupby('Year')[measure].mean()
                ax3.plot(yearly_avg.index, yearly_avg.values, marker='o', label=measure.replace('_', ' '))
        ax3.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Average Centrality', fontsize=10, fontweight='bold')
        ax3.set_title('Centrality Evolution Over Time', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Housing price evolution (middle center)
        ax4 = fig.add_subplot(gs[1, 1])
        yearly_prices = dataset_df.groupby('Year')['Average_House_Price'].mean()
        ax4.plot(yearly_prices.index, yearly_prices.values, marker='o', color='red', linewidth=2)
        ax4.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax4.set_ylabel('Average House Price (£)', fontsize=10, fontweight='bold')
        ax4.set_title('Housing Price Evolution', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Correlation heatmap (middle right)
        ax5 = fig.add_subplot(gs[1, 2])
        centrality_cols = [col for col in dataset_df.columns if any(measure in col for measure in self.centrality_labels.keys())]
        if len(centrality_cols) > 1:
            corr_matrix = dataset_df[centrality_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                       square=True, ax=ax5, cbar_kws={'shrink': 0.8})
            ax5.set_title('Centrality Correlations', fontsize=12, fontweight='bold')
        
        # Plot 6: Model diagnostics summary (bottom, spanning all columns)
        ax6 = fig.add_subplot(gs[2, :])
        
        # Create a summary table
        summary_data = [
            ['Observations', f"{len(dataset_df):,}"],
            ['Years', f"{dataset_df['Year'].nunique()}"],
            ['Boroughs', f"{dataset_df['Borough'].nunique()}"],
            ['Significant Effects', f"{sum(centrality_coeffs['p_value'] < 0.05)}/{len(centrality_coeffs)}"],
            ['Largest Effect', f"{centrality_coeffs.loc[centrality_coeffs['Coefficient'].abs().idxmax(), 'Label']}"],
            ['Effect Size Range', f"{effect_sizes.min():.1f}% to {effect_sizes.max():.1f}%"]
        ]
        
        ax6.axis('tight')
        ax6.axis('off')
        table = ax6.table(cellText=summary_data, colLabels=['Metric', 'Value'], 
                         cellLoc='center', loc='center', colWidths=[0.4, 0.6])
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
        ax6.set_title('Model Summary', fontsize=14, fontweight='bold', pad=20)
        
        # Add overall title
        fig.suptitle('London Transit Network and Housing Market Analysis: Results Dashboard', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        plt.savefig(self.summary_dashboard_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Summary dashboard saved to {self.summary_dashboard_file}")
    
    def create_interpretation_report(self, coefficients_df, dataset_df):
        """Create a text report interpreting the results."""
        print("Creating interpretation report...")
        
        # Filter to centrality coefficients
        centrality_coeffs = self.filter_centrality_coefficients(coefficients_df)
        
        if len(centrality_coeffs) == 0:
            print("No centrality coefficients found for interpretation")
            return
        
        # Calculate effect sizes
        centrality_coeffs['Effect_Size_Percent'] = (
            (np.exp(centrality_coeffs['Coefficient']) - 1) * 100
        )
        
        # Create interpretation report
        report_file = self.output_dir / "interpretation_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("PANEL REGRESSION RESULTS INTERPRETATION\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"This analysis examines the relationship between London's transit network centrality\n")
            f.write(f"and housing prices from {dataset_df['Year'].min()} to {dataset_df['Year'].max()}, using\n")
            f.write(f"panel regression with fixed effects to control for borough-specific and time-specific factors.\n\n")
            
            f.write("KEY FINDINGS\n")
            f.write("-" * 15 + "\n")
            
            # Most significant effects
            significant_effects = centrality_coeffs[centrality_coeffs['p_value'] < 0.05]
            if len(significant_effects) > 0:
                f.write(f"• {len(significant_effects)} out of {len(centrality_coeffs)} centrality measures show\n")
                f.write(f"  statistically significant effects on housing prices (p < 0.05)\n\n")
                
                # Largest effect
                largest_effect = centrality_coeffs.loc[centrality_coeffs['Coefficient'].abs().idxmax()]
                f.write(f"• Largest effect: {largest_effect['Label']}\n")
                f.write(f"  - Coefficient: {largest_effect['Coefficient']:.4f}\n")
                f.write(f"  - Effect size: {largest_effect['Effect_Size_Percent']:.2f}% change in house prices\n")
                f.write(f"  - Significance: p = {largest_effect['p_value']:.4f}\n\n")
            
            f.write("DETAILED RESULTS\n")
            f.write("-" * 18 + "\n")
            
            for _, row in centrality_coeffs.iterrows():
                f.write(f"{row['Label']}:\n")
                f.write(f"  • Coefficient: {row['Coefficient']:.4f} (SE: {row['Std_Error']:.4f})\n")
                f.write(f"  • Effect size: {row['Effect_Size_Percent']:.2f}% change in house prices\n")
                f.write(f"  • Significance: p = {row['p_value']:.4f}")
                
                if row['p_value'] < 0.01:
                    f.write(" (***)\n")
                elif row['p_value'] < 0.05:
                    f.write(" (**)\n")
                elif row['p_value'] < 0.1:
                    f.write(" (*)\n")
                else:
                    f.write(" (not significant)\n")
                
                f.write(f"  • Interpretation: A one standard deviation increase in {row['Label'].split(' (')[0]}\n")
                f.write(f"    is associated with a {row['Effect_Size_Percent']:.2f}% change in house prices\n\n")
            
            f.write("POLICY IMPLICATIONS\n")
            f.write("-" * 20 + "\n")
            f.write("• Transit accessibility is significantly capitalized into London housing prices\n")
            f.write("• Network centrality measures provide valuable indicators of locational advantage\n")
            f.write("• Infrastructure investments that improve network connectivity may have\n")
            f.write("  measurable impacts on property values\n")
            f.write("• The relationship varies across different types of centrality, suggesting\n")
            f.write("  nuanced effects of different aspects of transit accessibility\n\n")
            
            f.write("METHODOLOGICAL NOTES\n")
            f.write("-" * 22 + "\n")
            f.write("• Panel regression with fixed effects controls for unobserved borough-specific\n")
            f.write("  and time-specific factors\n")
            f.write("• Lagged variables (t-1) are used to establish temporal precedence\n")
            f.write("• Standardized coefficients allow comparison of effect sizes across measures\n")
            f.write("• Clustered standard errors account for potential correlation within boroughs\n")
        
        print(f"Interpretation report saved to {report_file}")
    
    def run(self):
        """Run the complete visualization process."""
        print("=" * 60)
        print("VISUALIZING PANEL REGRESSION RESULTS")
        print("=" * 60)
        
        # Step 1: Load results
        coefficients_df, dataset_df = self.load_results()
        
        # Step 2: Create coefficient plot
        self.create_coefficient_plot(coefficients_df)
        
        # Step 3: Create effect size plot
        self.create_effect_size_plot(coefficients_df, dataset_df)
        
        # Step 4: Create interaction plot
        self.create_interaction_plot(coefficients_df)
        
        # Step 5: Create summary dashboard
        self.create_summary_dashboard(coefficients_df, dataset_df)
        
        # Step 6: Create interpretation report
        self.create_interpretation_report(coefficients_df, dataset_df)
        
        print("\n" + "=" * 60)
        print("VISUALIZATION COMPLETED")
        print("=" * 60)
        print(f"All plots and reports saved to: {self.output_dir}")

if __name__ == "__main__":
    visualizer = ResultsVisualizer()
    visualizer.run()
