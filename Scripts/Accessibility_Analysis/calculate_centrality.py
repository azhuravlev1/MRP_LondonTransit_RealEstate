import pandas as pd
import igraph as ig
import os
import glob
from pathlib import Path
import re

def parse_filename_metadata(filename):
    """
    Parse filename to extract metadata: Year, DayType, and TimeBand.
    
    Args:
        filename (str): GraphML filename
        
    Returns:
        dict: Dictionary containing Year, DayType, and TimeBand
    """
    # Remove .graphml extension
    name = filename.replace('.graphml', '')
    
    # Extract year (4-digit number)
    year_match = re.search(r'(\d{4})', name)
    year = year_match.group(1) if year_match else 'Unknown'
    
    # Extract day type
    day_types = ['MTT', 'MTF', 'FRI', 'SAT', 'SUN', 'MON', 'TWT']
    day_type = 'Unknown'
    for dt in day_types:
        if dt in name:
            day_type = dt
            break
    
    # Extract time band
    time_band = 'Total'  # Default
    
    # Check for specific time bands
    if 'tb_' in name:
        # Extract time band from tb_ pattern
        tb_match = re.search(r'tb_([^_]+)', name)
        if tb_match:
            time_band = tb_match.group(1)
    elif 'qhr_' in name:
        # Extract quarter-hour slot
        qhr_match = re.search(r'qhr_slot-(\d+)_(\d{4}-\d{4})', name)
        if qhr_match:
            slot_num = qhr_match.group(1)
            time_range = qhr_match.group(2)
            time_band = f'qhr_slot-{slot_num}_{time_range}'
    
    return {
        'Year': year,
        'DayType': day_type,
        'TimeBand': time_band
    }

def calculate_centrality_metrics(graph):
    """
    Calculate centrality metrics for a given graph.
    
    Args:
        graph (igraph.Graph): Directed weighted graph
        
    Returns:
        dict: Dictionary containing centrality metrics for each borough
    """
    # Get borough names
    boroughs = [v['name'] for v in graph.vs]
    
    # Calculate centrality measures
    try:
        # Weighted In-Degree (Arrivals)
        in_degree = graph.strength(weights='weight', mode='in')
    except:
        in_degree = [0] * len(boroughs)
    
    try:
        # Weighted Out-Degree (Departures)
        out_degree = graph.strength(weights='weight', mode='out')
    except:
        out_degree = [0] * len(boroughs)
    
    try:
        # Betweenness Centrality
        # Convert flow weights to distance weights for proper betweenness calculation
        # Betweenness is based on shortest paths, so high flow should be treated as "shorter" distance
        flow_weights = graph.es['weight']
        distance_weights = []
        
        for flow_weight in flow_weights:
            if flow_weight > 0:
                # Convert flow to distance: higher flow = lower distance
                distance_weight = 1 / flow_weight
            else:
                # Handle zero flow as infinite distance
                distance_weight = float('inf')
            distance_weights.append(distance_weight)
        
        # Calculate betweenness centrality using distance weights
        betweenness = graph.betweenness(weights=distance_weights)
    except:
        betweenness = [0] * len(boroughs)
    
    try:
        # Closeness Centrality
        # Convert flow weights to distance weights for proper closeness calculation
        # Flow weights (higher = better) need to be converted to distance weights (lower = better)
        flow_weights = graph.es['weight']
        distance_weights = []
        
        for flow_weight in flow_weights:
            if flow_weight > 0:
                # Convert flow to distance: higher flow = lower distance
                distance_weight = 1 / flow_weight
            else:
                # Handle zero flow as infinite distance
                distance_weight = float('inf')
            distance_weights.append(distance_weight)
        
        # Calculate closeness centrality using distance weights
        closeness = graph.closeness(weights=distance_weights)
    except:
        closeness = [0] * len(boroughs)
    
    try:
        # Eigenvector Centrality
        eigenvector = graph.eigenvector_centrality(weights='weight')
    except:
        eigenvector = [0] * len(boroughs)
    
    # Create results dictionary
    results = {}
    for i, borough in enumerate(boroughs):
        results[borough] = {
            'weighted_in_degree': in_degree[i],
            'weighted_out_degree': out_degree[i],
            'betweenness_centrality': betweenness[i],
            'closeness_centrality': closeness[i],
            'eigenvector_centrality': eigenvector[i]
        }
    
    return results

def process_graph_files(input_directory, output_file):
    """
    Process all GraphML files and calculate centrality metrics.
    
    Args:
        input_directory (str): Directory containing GraphML files
        output_file (str): Output CSV file path
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Find all GraphML files
    graph_files = glob.glob(os.path.join(input_directory, '**/*.graphml'), recursive=True)
    
    if not graph_files:
        print(f"No GraphML files found in {input_directory}")
        return
    
    print(f"Found {len(graph_files)} GraphML files to process")
    
    # Initialize results list
    results = []
    
    # Process each graph file
    for i, filepath in enumerate(graph_files, 1):
        filename = os.path.basename(filepath)
        print(f"Processing [{i}/{len(graph_files)}]: {filename}...")
        
        try:
            # Parse filename metadata
            metadata = parse_filename_metadata(filename)
            
            # Load graph
            graph = ig.Graph.Read_GraphML(filepath)
            
            # Calculate centrality metrics
            centrality_metrics = calculate_centrality_metrics(graph)
            
            # Create results for each borough
            for borough, metrics in centrality_metrics.items():
                result_dict = {
                    'Year': metadata['Year'],
                    'DayType': metadata['DayType'],
                    'TimeBand': metadata['TimeBand'],
                    'Borough': borough,
                    'Weighted_In_Degree': metrics['weighted_in_degree'],
                    'Weighted_Out_Degree': metrics['weighted_out_degree'],
                    'Betweenness_Centrality': metrics['betweenness_centrality'],
                    'Closeness_Centrality': metrics['closeness_centrality'],
                    'Eigenvector_Centrality': metrics['eigenvector_centrality']
                }
                results.append(result_dict)
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    # Convert to DataFrame
    if results:
        df = pd.DataFrame(results)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"Centrality calculation complete. Results saved to {output_file}")
        print(f"Total records: {len(df)}")
        print(f"Years covered: {sorted(df['Year'].unique())}")
        print(f"Day types: {sorted(df['DayType'].unique())}")
        print(f"Time bands: {sorted(df['TimeBand'].unique())}")
    else:
        print("No results to save")

def main():
    """
    Main function to execute centrality calculation.
    """
    # Define file paths
    input_directory = '../../Data/Graphs'
    output_file = '../../Data/Outputs/Metrics/centrality_metrics.csv'
    
    print("=" * 60)
    print("CENTRALITY METRICS CALCULATION")
    print("=" * 60)
    print(f"Input directory: {input_directory}")
    print(f"Output file: {output_file}")
    print("=" * 60)
    
    # Check if input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Input directory '{input_directory}' not found")
        return
    
    # Process graph files
    process_graph_files(input_directory, output_file)

if __name__ == "__main__":
    main()
