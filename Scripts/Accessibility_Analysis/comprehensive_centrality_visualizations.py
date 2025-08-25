#!/usr/bin/env python3
"""
Comprehensive Centrality and Community Detection Visualizations
for London Transit Network Analysis (2000-2023)

This script creates a comprehensive set of visualizations for analyzing
centrality measures and community structure in London's transit network.
It includes time series analysis, infrastructure impact assessment,
COVID-19 effects, and comparative borough analysis.

Author: Andrey Zhuravlev
Date: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class CentralityVisualizer:
    def __init__(self, data_path, output_dir):
        """
        Initialize the visualizer with data and output directory.
        
        Args:
            data_path (str): Path to the all_metrics_timeseries.csv file
            output_dir (str): Directory to save all plots
        """
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.df = pd.read_csv(data_path)
        
        # Define centrality measures (matching actual column names in data)
        self.centrality_measures = [
            'Weighted_In_Degree', 'Weighted_Out_Degree', 'Betweenness_Centrality',
            'Closeness_Centrality', 'Eigenvector_Centrality'
        ]
        
        # Define key years for analysis
        self.key_years = {
            'pre_covid': 2019,
            'post_covid': 2022,
            'elizabeth_line': 2022,
            'overground': 2007,
            'dlr_extension': 2011
        }
        
        # Define top boroughs for detailed analysis
        self.top_boroughs = [
            'Westminster', 'Camden', 'Tower Hamlets', 'Hackney', 'Islington',
            'Lambeth', 'Southwark', 'Greenwich', 'Newham', 'Brent'
        ]
        
        print(f"Loaded data with {len(self.df)} records")
        print(f"Years: {sorted(self.df['Year'].unique())}")
        print(f"Boroughs: {len(self.df['Borough'].unique())}")

    def create_summary_tables(self):
        """Create comprehensive summary tables comparing pre/post COVID periods."""
        print("Creating summary tables...")
        
        # Pre/post COVID comparison
        pre_covid = self.df[self.df['Year'] == self.key_years['pre_covid']].groupby('Borough')[self.centrality_measures].mean()
        post_covid = self.df[self.df['Year'] == self.key_years['post_covid']].groupby('Borough')[self.centrality_measures].mean()
        
        # Calculate percentage changes
        pct_change = ((post_covid - pre_covid) / pre_covid * 100).fillna(0)
        
        # Create comprehensive summary table
        summary_table = pd.DataFrame()
        for measure in self.centrality_measures:
            summary_table[f'{measure}_2019'] = pre_covid[measure]
            summary_table[f'{measure}_2022'] = post_covid[measure]
            summary_table[f'{measure}_pct_change'] = pct_change[measure]
        
        # Save summary table
        summary_table.to_csv(self.output_dir / 'centrality_summary_table.csv')
        
        # Create a formatted table for display
        display_table = summary_table.round(3)
        display_table.to_csv(self.output_dir / 'centrality_summary_display.csv')
        
        print(f"Summary tables saved to {self.output_dir}")
        return summary_table

    def create_ranking_bar_charts(self):
        """Create bar charts showing borough rankings by centrality measures."""
        print("Creating ranking bar charts...")
        
        # Get average centrality for each borough across all years
        borough_rankings = self.df.groupby('Borough')[self.centrality_measures].mean()
        
        # Create bar charts for each centrality measure
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Top 10 Boroughs by Centrality Measures (2000-2023 Average)', fontsize=16, fontweight='bold')
        
        for i, measure in enumerate(self.centrality_measures):
            row, col = i // 3, i % 3
            top_10 = borough_rankings[measure].sort_values(ascending=False).head(10)
            
            colors = plt.cm.viridis(np.linspace(0, 1, len(top_10)))
            bars = axes[row, col].barh(range(len(top_10)), top_10.values, color=colors)
            axes[row, col].set_yticks(range(len(top_10)))
            axes[row, col].set_yticklabels(top_10.index, fontsize=10)
            axes[row, col].set_title(f'{measure.replace("_", " ").title()}', fontweight='bold')
            axes[row, col].set_xlabel('Centrality Value')
            
            # Add value labels on bars
            for j, (bar, value) in enumerate(zip(bars, top_10.values)):
                axes[row, col].text(value + value*0.01, bar.get_y() + bar.get_height()/2, 
                                  f'{value:.3f}', va='center', fontsize=9)
        
        # Remove the last subplot if we have 5 measures
        if len(self.centrality_measures) == 5:
            fig.delaxes(axes[1, 2])
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '01_borough_rankings.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_winners_losers_chart(self):
        """Create 'winners and losers' chart showing COVID impact."""
        print("Creating winners and losers chart...")
        
        # Calculate percentage change between 2019 and 2022
        pre_covid = self.df[self.df['Year'] == self.key_years['pre_covid']].groupby('Borough')[self.centrality_measures].mean()
        post_covid = self.df[self.df['Year'] == self.key_years['post_covid']].groupby('Borough')[self.centrality_measures].mean()
        pct_change = ((post_covid - pre_covid) / pre_covid * 100).fillna(0)
        
        # Focus on weighted in-degree (passenger arrivals) for the main story
        measure = 'Weighted_In_Degree'
        changes = pct_change[measure].sort_values()
        
        # Create divergent bar chart
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Color bars based on positive/negative change
        colors = ['red' if x < 0 else 'green' for x in changes.values]
        
        bars = ax.barh(range(len(changes)), changes.values, color=colors, alpha=0.7)
        ax.set_yticks(range(len(changes)))
        ax.set_yticklabels(changes.index, fontsize=10)
        ax.set_xlabel('Percentage Change in Passenger Arrivals (%)', fontsize=12)
        ax.set_title('COVID-19 Impact: Winners and Losers\n(2019 vs 2022)', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='--', linewidth=2)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, changes.values)):
            ax.text(value + (1 if value >= 0 else -1), bar.get_y() + bar.get_height()/2, 
                   f'{value:.1f}%', va='center', fontsize=9, fontweight='bold')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='green', alpha=0.7, label='Winners (Increase)'),
                          Patch(facecolor='red', alpha=0.7, label='Losers (Decrease)')]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '02_covid_winners_losers.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_distribution_plots(self):
        """Create violin and box plots for distribution analysis."""
        print("Creating distribution plots...")
        
        # Time band analysis (if available)
        if 'TimeBand' in self.df.columns:
            fig, axes = plt.subplots(2, 3, figsize=(20, 12))
            fig.suptitle('Centrality Distribution by Time Band (2022)', fontsize=16, fontweight='bold')
            
            for i, measure in enumerate(self.centrality_measures):
                row, col = i // 3, i % 3
                data_2022 = self.df[self.df['Year'] == 2022]
                
                # Create violin plot
                sns.violinplot(data=data_2022, x='TimeBand', y=measure, ax=axes[row, col])
                axes[row, col].set_title(f'{measure.replace("_", " ").title()}')
                axes[row, col].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(self.output_dir / '03_time_band_distributions.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # Overall distribution plots
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Distribution of Centrality Measures (All Years)', fontsize=16, fontweight='bold')
        
        for i, measure in enumerate(self.centrality_measures):
            row, col = i // 3, i % 3
            axes[row, col].hist(self.df[measure], bins=30, alpha=0.7, edgecolor='black', color='skyblue')
            axes[row, col].set_title(f'Distribution of {measure.replace("_", " ").title()}')
            axes[row, col].set_xlabel(measure.replace("_", " ").title())
            axes[row, col].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '04_centrality_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_correlation_heatmap(self):
        """Create correlation matrix heatmap."""
        print("Creating correlation heatmap...")
        
        # Calculate correlations between centrality measures
        correlation_matrix = self.df[self.centrality_measures].corr()
        
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.3f', mask=mask, cbar_kws={"shrink": .8})
        plt.title('Correlation Matrix of Centrality Measures\n(All Years)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / '05_correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_evolution_heatmap(self):
        """Create 24-year evolution heatmap."""
        print("Creating evolution heatmap...")
        
        # Create pivot table for heatmap
        pivot_data = self.df.groupby(['Year', 'Borough'])['Betweenness_Centrality'].mean().unstack()
        
        plt.figure(figsize=(20, 12))
        sns.heatmap(pivot_data, cmap='YlOrRd', cbar_kws={'label': 'Betweenness Centrality'})
        plt.title('24-Year Evolution of Betweenness Centrality\n(2000-2023)', fontsize=16, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Borough', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / '06_evolution_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_scatter_plots(self):
        """Create scatter plots for relationship analysis."""
        print("Creating scatter plots...")
        
        # Borough roles scatter plot
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Borough Roles Analysis (2022)', fontsize=16, fontweight='bold')
        
        # Betweenness vs Degree
        data_2022 = self.df[self.df['Year'] == 2022].groupby('Borough')[self.centrality_measures].mean()
        
        # Plot 1: Betweenness vs In-Degree
        axes[0, 0].scatter(data_2022['Weighted_In_Degree'], data_2022['Betweenness_Centrality'], alpha=0.7)
        axes[0, 0].set_xlabel('Weighted In-Degree (Passenger Arrivals)')
        axes[0, 0].set_ylabel('Betweenness Centrality')
        axes[0, 0].set_title('Borough Roles: Betweenness vs Arrivals')
        
        # Add labels for top boroughs
        for borough in self.top_boroughs[:5]:
            if borough in data_2022.index:
                x, y = data_2022.loc[borough, 'Weighted_In_Degree'], data_2022.loc[borough, 'Betweenness_Centrality']
                axes[0, 0].annotate(borough, (x, y), xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Plot 2: Eigenvector vs Closeness
        axes[0, 1].scatter(data_2022['Closeness_Centrality'], data_2022['Eigenvector_Centrality'], alpha=0.7)
        axes[0, 1].set_xlabel('Closeness Centrality')
        axes[0, 1].set_ylabel('Eigenvector Centrality')
        axes[0, 1].set_title('Borough Roles: Closeness vs Eigenvector')
        
        # Plot 3: In vs Out Degree
        axes[1, 0].scatter(data_2022['Weighted_In_Degree'], data_2022['Weighted_Out_Degree'], alpha=0.7)
        axes[1, 0].plot([data_2022['Weighted_In_Degree'].min(), data_2022['Weighted_In_Degree'].max()], 
                       [data_2022['Weighted_In_Degree'].min(), data_2022['Weighted_In_Degree'].max()], 'r--')
        axes[1, 0].set_xlabel('Weighted In-Degree (Arrivals)')
        axes[1, 0].set_ylabel('Weighted Out-Degree (Departures)')
        axes[1, 0].set_title('Arrivals vs Departures')
        
        # Plot 4: Pre vs Post COVID
        pre_covid = self.df[self.df['Year'] == 2019].groupby('Borough')['Weighted_In_Degree'].mean()
        post_covid = self.df[self.df['Year'] == 2022].groupby('Borough')['Weighted_In_Degree'].mean()
        
        axes[1, 1].scatter(pre_covid, post_covid, alpha=0.7)
        axes[1, 1].plot([pre_covid.min(), pre_covid.max()], [pre_covid.min(), pre_covid.max()], 'r--')
        axes[1, 1].set_xlabel('Pre-COVID Arrivals (2019)')
        axes[1, 1].set_ylabel('Post-COVID Arrivals (2022)')
        axes[1, 1].set_title('COVID Impact: Pre vs Post')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '07_scatter_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_time_series_plots(self):
        """Create time series plots for key boroughs."""
        print("Creating time series plots...")
        
        # Evolution of centrality measures over time
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Centrality Evolution Over Time (Top Boroughs)', fontsize=16, fontweight='bold')
        
        for i, measure in enumerate(self.centrality_measures):
            row, col = i // 3, i % 3
            
            for borough in self.top_boroughs[:5]:  # Top 5 boroughs
                borough_data = self.df[self.df['Borough'] == borough].groupby('Year')[measure].mean()
                axes[row, col].plot(borough_data.index, borough_data.values, label=borough, marker='o', linewidth=2)
            
            axes[row, col].set_title(f'{measure.replace("_", " ").title()}')
            axes[row, col].legend()
            axes[row, col].set_xlabel('Year')
            axes[row, col].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '08_time_series_evolution.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_infrastructure_impact_analysis(self):
        """Create infrastructure impact analysis."""
        print("Creating infrastructure impact analysis...")
        
        # Define infrastructure events
        infrastructure_events = {
            'Elizabeth Line (2022)': 2022,
            'London Overground (2007)': 2007,
            'DLR Extension (2011)': 2011
        }
        
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        fig.suptitle('Infrastructure Impact Analysis', fontsize=16, fontweight='bold')
        
        for i, (event, year) in enumerate(infrastructure_events.items()):
            # Get data before and after the event
            before = self.df[self.df['Year'] < year].groupby('Borough')['Weighted_In_Degree'].mean()
            after = self.df[self.df['Year'] >= year].groupby('Borough')['Weighted_In_Degree'].mean()
            
            # Calculate percentage change
            change = ((after - before) / before * 100).fillna(0)
            
            # Get top 10 changes
            top_changes = change.abs().sort_values(ascending=False).head(10)
            
            # Color bars
            colors = ['red' if change.loc[borough] < 0 else 'green' for borough in top_changes.index]
            
            bars = axes[i].barh(range(len(top_changes)), change.loc[top_changes.index], color=colors, alpha=0.7)
            axes[i].set_yticks(range(len(top_changes)))
            axes[i].set_yticklabels(top_changes.index, fontsize=9)
            axes[i].set_title(f'{event} Impact')
            axes[i].set_xlabel('Percentage Change (%)')
            axes[i].axvline(x=0, color='black', linestyle='--')
            
            # Add value labels
            for j, (bar, value) in enumerate(zip(bars, change.loc[top_changes.index])):
                axes[i].text(value + (1 if value >= 0 else -1), bar.get_y() + bar.get_height()/2, 
                           f'{value:.1f}%', va='center', fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '09_infrastructure_impact.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_community_analysis(self):
        """Create community structure analysis (if community data available)."""
        print("Creating community analysis...")
        
        if 'Community_ID' in self.df.columns:
            # Community evolution over time
            community_evolution = self.df.groupby(['Year', 'Community_ID'])['Borough'].count().unstack(fill_value=0)
            
            plt.figure(figsize=(15, 8))
            community_evolution.plot(kind='area', stacked=True, alpha=0.7)
            plt.title('Evolution of Travel Communities Over Time', fontsize=14, fontweight='bold')
            plt.xlabel('Year', fontsize=12)
            plt.ylabel('Number of Boroughs', fontsize=12)
            plt.legend(title='Community ID')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(self.output_dir / '10_community_evolution.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            # Community characteristics
            if 'Participation_Coefficient' in self.df.columns:
                fig, axes = plt.subplots(1, 2, figsize=(16, 6))
                
                # Box plot of participation coefficient by community
                data_2022 = self.df[self.df['Year'] == 2022]
                sns.boxplot(data=data_2022, x='Community_ID', y='Participation_Coefficient', ax=axes[0])
                axes[0].set_title('Participation Coefficient by Community (2022)')
                axes[0].set_xlabel('Community ID')
                axes[0].set_ylabel('Participation Coefficient')
                
                # Community size distribution
                community_sizes = data_2022.groupby('Community_ID')['Borough'].count()
                axes[1].bar(community_sizes.index, community_sizes.values)
                axes[1].set_title('Community Size Distribution (2022)')
                axes[1].set_xlabel('Community ID')
                axes[1].set_ylabel('Number of Boroughs')
                
                plt.tight_layout()
                plt.savefig(self.output_dir / '11_community_characteristics.png', dpi=300, bbox_inches='tight')
                plt.show()

    def create_stability_analysis(self):
        """Create ranking stability analysis."""
        print("Creating stability analysis...")
        
        def calculate_ranking_stability(df, measure, years):
            """Calculate ranking stability for a given measure."""
            rankings = {}
            for year in years:
                year_data = df[df['Year'] == year].groupby('Borough')[measure].mean()
                rankings[year] = year_data.rank(ascending=False)
            
            ranking_df = pd.DataFrame(rankings)
            stability = ranking_df.std(axis=1)  # Lower std = more stable ranking
            return stability
        
        years = sorted(self.df['Year'].unique())
        stability_analysis = {}
        
        for measure in self.centrality_measures:
            stability_analysis[measure] = calculate_ranking_stability(self.df, measure, years)
        
        stability_df = pd.DataFrame(stability_analysis)
        stability_df = stability_df.sort_values('Betweenness_Centrality')
        
        plt.figure(figsize=(12, 8))
        stability_df.head(15).plot(kind='bar', figsize=(12, 6))
        plt.title('Borough Ranking Stability (Lower = More Stable)', fontsize=14, fontweight='bold')
        plt.xlabel('Borough', fontsize=12)
        plt.ylabel('Standard Deviation of Ranking', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / '12_ranking_stability.png', dpi=300, bbox_inches='tight')
        plt.show()

    def create_summary_dashboard(self):
        """Create a comprehensive summary dashboard."""
        print("Creating summary dashboard...")
        
        # Create a summary heatmap
        mean_centrality = self.df.groupby('Borough')[self.centrality_measures].mean()
        
        plt.figure(figsize=(14, 10))
        sns.heatmap(mean_centrality.T, annot=True, cmap='YlOrRd', fmt='.3f', cbar_kws={'label': 'Centrality Value'})
        plt.title('Average Centrality Measures by Borough (2000-2023)', fontsize=16, fontweight='bold')
        plt.xlabel('Borough', fontsize=12)
        plt.ylabel('Centrality Measure', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / '13_summary_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()

    def run_all_visualizations(self):
        """Run all visualization methods."""
        print("Starting comprehensive centrality visualization analysis...")
        print("=" * 60)
        
        # Create all visualizations
        self.create_summary_tables()
        self.create_ranking_bar_charts()
        self.create_winners_losers_chart()
        self.create_distribution_plots()
        self.create_correlation_heatmap()
        self.create_evolution_heatmap()
        self.create_scatter_plots()
        self.create_time_series_plots()
        self.create_infrastructure_impact_analysis()
        self.create_community_analysis()
        self.create_stability_analysis()
        self.create_summary_dashboard()
        
        print("=" * 60)
        print(f"All visualizations completed! Files saved to: {self.output_dir}")
        print("Generated files:")
        for file in sorted(self.output_dir.glob("*.png")):
            print(f"  - {file.name}")
        for file in sorted(self.output_dir.glob("*.csv")):
            print(f"  - {file.name}")


def main():
    """Main function to run the visualization analysis."""
    # Define paths
    data_path = "Data/Outputs/Metrics/all_metrics_timeseries.csv"
    output_dir = "Plots/Centrality_Analysis"
    
    # Check if data file exists
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        print("Please ensure the all_metrics_timeseries.csv file exists in the specified location.")
        return
    
    # Create visualizer and run analysis
    visualizer = CentralityVisualizer(data_path, output_dir)
    visualizer.run_all_visualizations()


if __name__ == "__main__":
    main()
