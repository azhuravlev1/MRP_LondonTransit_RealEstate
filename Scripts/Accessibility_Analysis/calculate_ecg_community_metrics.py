import pandas as pd
import igraph as ig
import os
import glob
import re
from tqdm import tqdm

def is_annual_aggregate_graph(filename):
    """
    Check if a filename represents an annual aggregate graph.
    
    Annual aggregate graphs are those that contain only the year and no additional
    time band specifications (like 'tb_', 'qhr_', 'am-peak', etc.).
    
    Args:
        filename (str): The filename to check
        
    Returns:
        bool: True if it's an annual aggregate graph, False otherwise
    """
    # Convert to lowercase for case-insensitive matching
    filename_lower = filename.lower()
    
    # Exclude files with time band specifications
    time_band_indicators = [
        'tb_', 'qhr_', 'am-peak', 'pm-peak', 'early', 'midday', 
        'evening', 'late', 'mtt', 'fri', 'sat', 'sun', 'mon', 'twt', 'mtf'
    ]
    
    # Check if any time band indicator is present
    for indicator in time_band_indicators:
        if indicator in filename_lower:
            return False
    
    # Check if it's a simple year file (e.g., "2013.graphml")
    # This pattern matches files that are just the year followed by .graphml
    year_pattern = r'^\d{4}\.graphml$'
    if re.match(year_pattern, os.path.basename(filename)):
        return True
    
    return False

def extract_year_from_filename(filename):
    """
    Extract the year from an annual aggregate graph filename.
    
    Args:
        filename (str): The filename to extract year from
        
    Returns:
        str: The year as a string, or 'Unknown' if not found
    """
    # Extract year from filename using regex
    year_match = re.search(r'(\d{4})', os.path.basename(filename))
    if year_match:
        return year_match.group(1)
    else:
        return 'Unknown'

def calculate_ecg_community_metrics():
    """
    Calculate ECG community detection metrics for annual aggregate graphs.
    
    This function:
    1. Finds all GraphML files in the input directory
    2. Filters to only annual aggregate graphs
    3. Runs ECG community detection on each graph
    4. Saves results to CSV file
    """
    print("=" * 60)
    print("LEIDEN COMMUNITY DETECTION ANALYSIS")
    print("=" * 60)
    
    # Define file paths
    input_directory = '../../Data/Graphs'
    output_file = '../../Data/Outputs/Metrics/community_metrics_ECG_annual.csv'
    
    # Check if input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Input directory '{input_directory}' not found")
        return False
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all GraphML files
    print(f"Scanning for GraphML files in: {input_directory}")
    all_graph_files = glob.glob(os.path.join(input_directory, '**/*.graphml'), recursive=True)
    print(f"Found {len(all_graph_files)} total GraphML files")
    
    # Filter to only annual aggregate graphs
    annual_graph_files = [f for f in all_graph_files if is_annual_aggregate_graph(f)]
    print(f"Identified {len(annual_graph_files)} annual aggregate graphs")
    
    if len(annual_graph_files) == 0:
        print("Error: No annual aggregate graphs found")
        return False
    
    # Display the annual graphs found
    print("\nAnnual aggregate graphs identified:")
    for file_path in sorted(annual_graph_files):
        year = extract_year_from_filename(file_path)
        print(f"  {year}: {os.path.basename(file_path)}")
    
    # Initialize results list
    results = []
    
    # Process each annual graph with progress bar
    print(f"\nProcessing {len(annual_graph_files)} annual graphs with Leiden algorithm...")
    for file_path in tqdm(annual_graph_files, desc="Processing annual graphs"):
        try:
            # Extract year from filename
            year = extract_year_from_filename(file_path)
            
            # Load the graph
            graph = ig.Graph.Read_GraphML(file_path)
            
            # Convert to undirected graph for ECG algorithm
            # ECG requires undirected graphs, so we combine bidirectional edges
            undirected_graph = graph.as_undirected(combine_edges='sum')
            
            # Run Leiden community detection algorithm
            # Leiden is a high-quality community detection method that optimizes modularity
            communities = undirected_graph.community_leiden(weights='weight', objective_function='modularity')
            
            # Get borough names from the original directed graph
            borough_names = [v['name'] for v in graph.vs]
            
            # Create results for each borough
            for i, borough_name in enumerate(borough_names):
                result_dict = {
                    'Year': year,
                    'Borough': borough_name,
                    'Leiden_CommunityID': communities.membership[i]
                }
                results.append(result_dict)
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    # Convert results to DataFrame
    print(f"\nConverting {len(results)} results to DataFrame...")
    results_df = pd.DataFrame(results)
    
    # Check if we have any results
    if len(results_df) == 0:
        print("Warning: No results generated. Check if the community detection algorithm is available.")
        return False
    
    # Save to CSV
    print(f"Saving results to: {output_file}")
    results_df.to_csv(output_file, index=False)
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("LEIDEN COMMUNITY DETECTION COMPLETED")
    print("=" * 60)
    print(f"✅ Results saved to: {output_file}")
    print(f"📊 Total records: {len(results_df)}")
    print(f"📅 Years covered: {sorted(results_df['Year'].unique())}")
    print(f"🏘️  Boroughs: {len(results_df['Borough'].unique())}")
    print(f"👥 Number of communities detected: {results_df['Leiden_CommunityID'].nunique()}")
    
    # Show community distribution
    print(f"\n📈 Community distribution:")
    community_counts = results_df['Leiden_CommunityID'].value_counts().sort_index()
    for community_id, count in community_counts.items():
        print(f"   Community {community_id}: {count} boroughs")
    
    return True

def main():
    """
    Main execution function.
    """
    success = calculate_ecg_community_metrics()
    
    if success:
        print("\n🎉 Leiden community detection analysis completed successfully!")
    else:
        print("\n❌ Leiden community detection analysis failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
