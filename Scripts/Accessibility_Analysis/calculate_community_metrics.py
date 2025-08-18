import pandas as pd
import igraph as ig
import os
import glob
from pathlib import Path
import re
import numpy as np

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

def calculate_participation_coefficient(graph, communities, vertex_index):
    """
    Calculate participation coefficient for a specific vertex.
    
    The participation coefficient P_i for node i is defined as:
    P_i = 1 - Σ_c (k_ic / k_i)^2
    
    Where:
    - k_i is the total weighted degree (strength) of node i
    - k_ic is the sum of weights of links from node i to other nodes in community c
    - The sum is over all communities c
    
    Args:
        graph (igraph.Graph): Directed weighted graph
        communities (igraph.VertexClustering): Community clustering object
        vertex_index (int): Index of the vertex to calculate participation coefficient for
        
    Returns:
        float: Participation coefficient value
    """
    # Get total weighted degree (strength) of the vertex
    total_strength = graph.strength(vertex_index, weights='weight')
    
    if total_strength == 0:
        return 0.0
    
    # Get all communities
    community_ids = set(communities.membership)
    
    # Calculate sum of squared ratios
    sum_squared_ratios = 0.0
    
    for community_id in community_ids:
        # Find all vertices in this community
        community_vertices = [i for i, comm in enumerate(communities.membership) if comm == community_id]
        
        # Calculate k_ic: sum of weights of links from vertex i to community c
        community_strength = 0.0
        
        # Get all edges from vertex i
        edges_from_vertex = graph.incident(vertex_index, mode='out')
        
        for edge_id in edges_from_vertex:
            edge = graph.es[edge_id]
            target_vertex = edge.target
            
            # Check if target vertex is in the current community
            if target_vertex in community_vertices:
                community_strength += edge['weight']
        
        # Calculate ratio and add to sum
        ratio = community_strength / total_strength
        sum_squared_ratios += ratio ** 2
    
    # Calculate participation coefficient
    participation_coefficient = 1.0 - sum_squared_ratios
    
    return participation_coefficient

def calculate_community_metrics(graph):
    """
    Calculate community detection metrics for a given graph.
    
    Args:
        graph (igraph.Graph): Directed weighted graph
        
    Returns:
        dict: Dictionary containing community metrics for each borough
    """
    # Get borough names
    boroughs = [v['name'] for v in graph.vs]
    
    try:
        # Perform community detection using Leiden algorithm
        communities = graph.community_leiden(weights='weight')
        
        # Calculate participation coefficient for each borough
        participation_coefficients = []
        for i in range(len(boroughs)):
            participation_coef = calculate_participation_coefficient(graph, communities, i)
            participation_coefficients.append(participation_coef)
        
        # Create results dictionary
        results = {}
        for i, borough in enumerate(boroughs):
            results[borough] = {
                'community_id': communities.membership[i],
                'participation_coefficient': participation_coefficients[i]
            }
        
        return results
        
    except Exception as e:
        print(f"Error in community detection: {str(e)}")
        # Return default values if community detection fails
        results = {}
        for borough in boroughs:
            results[borough] = {
                'community_id': 0,
                'participation_coefficient': 0.0
            }
        return results

def process_graph_files(input_directory, output_file):
    """
    Process all GraphML files and calculate community metrics.
    
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
            
            # Calculate community metrics
            community_metrics = calculate_community_metrics(graph)
            
            # Create results for each borough
            for borough, metrics in community_metrics.items():
                result_dict = {
                    'Year': metadata['Year'],
                    'DayType': metadata['DayType'],
                    'TimeBand': metadata['TimeBand'],
                    'Borough': borough,
                    'Community_ID': metrics['community_id'],
                    'Participation_Coefficient': metrics['participation_coefficient']
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
        print(f"Community metrics calculation complete. Results saved to {output_file}")
        print(f"Total records: {len(df)}")
        print(f"Years covered: {sorted(df['Year'].unique())}")
        print(f"Day types: {sorted(df['DayType'].unique())}")
        print(f"Time bands: {sorted(df['TimeBand'].unique())}")
        print(f"Number of communities detected: {df['Community_ID'].nunique()}")
    else:
        print("No results to save")

def main():
    """
    Main function to execute community metrics calculation.
    """
    # Define file paths
    input_directory = 'Data/Graphs'
    output_file = 'Data/Outputs/Metrics/community_metrics.csv'
    
    print("=" * 60)
    print("COMMUNITY METRICS CALCULATION")
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
