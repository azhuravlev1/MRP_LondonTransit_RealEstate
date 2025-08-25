import pandas as pd
import os

def merge_metrics_dataframes(centrality_file, community_file, output_file):
    """
    Merge centrality and community metrics DataFrames into a comprehensive dataset.
    
    Args:
        centrality_file (str): Path to centrality metrics CSV file
        community_file (str): Path to community metrics CSV file
        output_file (str): Path to output merged CSV file
    """
    print("=" * 60)
    print("MERGING METRICS DATAFRAMES")
    print("=" * 60)
    
    # Check if input files exist
    if not os.path.exists(centrality_file):
        print(f"Error: Centrality file '{centrality_file}' not found")
        return False
    
    if not os.path.exists(community_file):
        print(f"Error: Community file '{community_file}' not found")
        return False
    
    print(f"Loading centrality metrics from: {centrality_file}")
    print(f"Loading community metrics from: {community_file}")
    
    try:
        # Load both CSV files
        centrality_df = pd.read_csv(centrality_file)
        community_df = pd.read_csv(community_file)
        
        print(f"Centrality metrics shape: {centrality_df.shape}")
        print(f"Community metrics shape: {community_df.shape}")
        
        # Display sample of each dataset
        print("\nCentrality metrics columns:")
        print(centrality_df.columns.tolist())
        print("\nCommunity metrics columns:")
        print(community_df.columns.tolist())
        
        # Define key columns for merging
        key_columns = ['Year', 'DayType', 'TimeBand', 'Borough']
        
        print(f"\nMerging on key columns: {key_columns}")
        
        # Check for any missing key columns
        missing_centrality = [col for col in key_columns if col not in centrality_df.columns]
        missing_community = [col for col in key_columns if col not in community_df.columns]
        
        if missing_centrality:
            print(f"Warning: Missing key columns in centrality file: {missing_centrality}")
        if missing_community:
            print(f"Warning: Missing key columns in community file: {missing_community}")
        
        # Perform outer merge to identify any mismatches
        merged_df = pd.merge(
            centrality_df, 
            community_df, 
            on=key_columns, 
            how='outer',
            indicator=True
        )
        
        # Check merge results
        merge_stats = merged_df['_merge'].value_counts()
        print(f"\nMerge statistics:")
        print(merge_stats)
        
        # Remove the merge indicator column
        merged_df = merged_df.drop('_merge', axis=1)
        
        # Check for missing values that might indicate merge issues
        missing_values = merged_df.isnull().sum()
        if missing_values.sum() > 0:
            print(f"\nWarning: Found missing values after merge:")
            print(missing_values[missing_values > 0])
        else:
            print(f"\n✅ No missing values found after merge")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save merged DataFrame
        merged_df.to_csv(output_file, index=False)
        
        print(f"\n✅ Merge successful! Results saved to: {output_file}")
        print(f"Final dataset shape: {merged_df.shape}")
        print(f"Final columns: {merged_df.columns.tolist()}")
        
        # Display summary statistics
        print(f"\nDataset summary:")
        print(f"Years covered: {sorted(merged_df['Year'].unique())}")
        print(f"Day types: {sorted(merged_df['DayType'].unique())}")
        print(f"Time bands: {sorted(merged_df['TimeBand'].unique())}")
        print(f"Boroughs: {len(merged_df['Borough'].unique())}")
        
        return True
        
    except Exception as e:
        print(f"Error during merge: {str(e)}")
        return False

def main():
    """
    Main function to execute the metrics aggregation.
    """
    # Define file paths
    centrality_file = '../../Data/Outputs/Metrics/centrality_metrics.csv'
    community_file = '../../Data/Outputs/Metrics/community_metrics.csv'
    output_file = '../../Data/Outputs/Metrics/all_metrics_timeseries.csv'
    
    print("=" * 60)
    print("METRICS AGGREGATION")
    print("=" * 60)
    print(f"Centrality file: {centrality_file}")
    print(f"Community file: {community_file}")
    print(f"Output file: {output_file}")
    print("=" * 60)
    
    # Execute merge
    success = merge_metrics_dataframes(centrality_file, community_file, output_file)
    
    if success:
        print("\n" + "=" * 60)
        print("AGGREGATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("The merged dataset contains:")
        print("- Centrality metrics (Weighted In/Out Degree, Betweenness, Closeness, Eigenvector)")
        print("- Community metrics (Community ID, Participation Coefficient)")
        print("- Metadata (Year, DayType, TimeBand, Borough)")
        print("\nThis comprehensive dataset is ready for panel regression analysis.")
    else:
        print("\n" + "=" * 60)
        print("AGGREGATION FAILED")
        print("=" * 60)
        print("Please check the error messages above and ensure both input files exist.")

if __name__ == "__main__":
    main()
