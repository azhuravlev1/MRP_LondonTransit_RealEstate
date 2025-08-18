import pandas as pd
import numpy as np
import igraph as ig
import os
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

def load_station_borough_mapping(mapping_file_path):
    """
    Load the station to borough mapping from CSV file.
    
    Args:
        mapping_file_path (str): Path to the station-borough mapping CSV file
        
    Returns:
        dict: Dictionary mapping NLC codes to borough names
    """
    mapping_df = pd.read_csv(mapping_file_path)
    # Create dictionary mapping NLC to Borough
    nlc_to_borough = dict(zip(mapping_df['NLC'], mapping_df['Borough']))
    return nlc_to_borough

def read_rods_excel_file(file_path):
    """
    Read RODS Excel file and extract the matrix data.
    
    Args:
        file_path (str): Path to the RODS Excel file
        
    Returns:
        tuple: (dataframe with OD matrix, list of time band names)
    """
    # Read the matrix sheet
    df = pd.read_excel(file_path, sheet_name='matrix', header=None)
    
    # The first 4 rows contain metadata and headers
    # Row 3 (index 2) contains the time band names
    time_bands = df.iloc[2, 2:8].tolist()  # Columns 2-7 contain time band names
    
    # Data starts from row 5 (index 4)
    # Column 0: Origin NLC, Column 2: Destination NLC
    # Columns 4-9: Flow data for each time band (Early, AM Peak, Midday, PM Peak, Evening, Late)
    data = df.iloc[4:, [0, 2, 4, 5, 6, 7, 8, 9]].copy()
    data.columns = ['origin_nlc', 'dest_nlc', 'early', 'am_peak', 'midday', 'pm_peak', 'evening', 'late']
    
    # Convert NLC codes to numeric, handling any non-numeric values
    data['origin_nlc'] = pd.to_numeric(data['origin_nlc'], errors='coerce')
    data['dest_nlc'] = pd.to_numeric(data['dest_nlc'], errors='coerce')
    
    # Convert flow columns to numeric
    for col in ['early', 'am_peak', 'midday', 'pm_peak', 'evening', 'late']:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
    
    # Remove rows where either NLC is NaN
    data = data.dropna(subset=['origin_nlc', 'dest_nlc'])
    
    return data, time_bands

def aggregate_station_flows_to_borough_flows(od_data, nlc_to_borough_mapping):
    """
    Aggregate station-to-station flows to borough-to-borough flows.
    
    Args:
        od_data (DataFrame): Station-to-station OD matrix
        nlc_to_borough_mapping (dict): Mapping from NLC codes to borough names
        
    Returns:
        DataFrame: Borough-to-borough OD matrix
    """
    # Add borough information
    od_data['origin_borough'] = od_data['origin_nlc'].map(nlc_to_borough_mapping)
    od_data['dest_borough'] = od_data['dest_nlc'].map(nlc_to_borough_mapping)
    
    # Remove rows where borough mapping is missing
    od_data = od_data.dropna(subset=['origin_borough', 'dest_borough'])
    
    # Aggregate by borough pairs
    flow_columns = ['early', 'am_peak', 'midday', 'pm_peak', 'evening', 'late']
    borough_flows = od_data.groupby(['origin_borough', 'dest_borough'])[flow_columns].sum().reset_index()
    
    return borough_flows

def create_graph_from_borough_flows(borough_flows, time_band=None):
    """
    Create an igraph Graph object from borough-to-borough flows.
    
    Args:
        borough_flows (DataFrame): Borough-to-borough OD matrix
        time_band (str, optional): Specific time band to use. If None, sum all time bands.
        
    Returns:
        igraph.Graph: Directed weighted graph
    """
    # Create a copy for manipulation
    graph_data = borough_flows.copy()
    
    if time_band is not None:
        # Use specific time band
        graph_data['weight'] = graph_data[time_band]
    else:
        # Sum all time bands
        flow_columns = ['early', 'am_peak', 'midday', 'pm_peak', 'evening', 'late']
        graph_data['weight'] = graph_data[flow_columns].sum(axis=1)
    
    # Remove zero-weight edges
    graph_data = graph_data[graph_data['weight'] > 0]
    
    if graph_data.empty:
        # Create empty graph with all boroughs as vertices
        all_boroughs = set(borough_flows['origin_borough'].unique()) | set(borough_flows['dest_borough'].unique())
        graph = ig.Graph(directed=True)
        graph.add_vertices(list(all_boroughs))
        return graph
    
    # Create graph
    graph = ig.Graph.DataFrame(
        graph_data[['origin_borough', 'dest_borough', 'weight']],
        directed=True,
        use_vids=False
    )
    
    return graph

def save_graph(graph, output_path):
    """
    Save graph to GraphML format.
    
    Args:
        graph (igraph.Graph): Graph to save
        output_path (str): Path where to save the graph
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save graph
    graph.write_graphml(output_path)

def process_rods_year(year, rods_data_path, mapping_file_path, output_base_path):
    """
    Process all RODS files for a specific year.
    
    Args:
        year (int): Year to process
        rods_data_path (str): Path to RODS data directory
        mapping_file_path (str): Path to station-borough mapping file
        output_base_path (str): Base path for output graphs
    """
    # Load station-borough mapping
    nlc_to_borough_mapping = load_station_borough_mapping(mapping_file_path)
    
    # Determine file path for this year
    if year <= 2002:
        file_path = os.path.join(rods_data_path, 'Rods_OD_2000-2002', f'ODmatrix_{year}.xls')
    else:
        file_path = os.path.join(rods_data_path, f'ODmatrix_{year}.xls')
    
    if not os.path.exists(file_path):
        print(f"Warning: File not found for year {year}: {file_path}")
        return
    
    # Read RODS data
    print(f"Processing RODS data for year {year}...")
    od_data, time_bands = read_rods_excel_file(file_path)
    
    # Aggregate to borough level
    borough_flows = aggregate_station_flows_to_borough_flows(od_data, nlc_to_borough_mapping)
    
    # Create output directory structure
    year_output_dir = os.path.join(output_base_path, 'RODS', str(year))
    time_bands_dir = os.path.join(year_output_dir, 'time_bands', 'tb')
    
    # Create overall graph (all time bands combined)
    overall_graph = create_graph_from_borough_flows(borough_flows)
    overall_graph_path = os.path.join(year_output_dir, f'{year}.graphml')
    save_graph(overall_graph, overall_graph_path)
    
    # Create time band specific graphs
    time_band_names = ['early', 'am_peak', 'midday', 'pm_peak', 'evening', 'late']
    time_band_labels = ['early', 'am-peak', 'midday', 'pm-peak', 'evening', 'late']
    
    for time_band, label in zip(time_band_names, time_band_labels):
        time_graph = create_graph_from_borough_flows(borough_flows, time_band)
        time_graph_path = os.path.join(time_bands_dir, f'{year}_tb_{label}.graphml')
        save_graph(time_graph, time_graph_path)

def main():
    """
    Main function to process all RODS years and create graphs.
    """
    # Define paths
    rods_data_path = "../Data/RODS_OD"
    mapping_file_path = "../Data/station_borough_nlc_mapping.csv"
    output_base_path = "../Data/Graphs"
    
    # Define years to process (2000-2017)
    years = list(range(2000, 2018))
    
    print("Building RODS graphs...")
    print(f"Processing {len(years)} years: {years[0]} to {years[-1]}")
    
    # Process each year with progress bar
    for year in tqdm(years, desc="Processing RODS years"):
        try:
            process_rods_year(year, rods_data_path, mapping_file_path, output_base_path)
        except Exception as e:
            print(f"Error processing year {year}: {str(e)}")
            continue
    
    print("RODS graph construction completed!")

if __name__ == "__main__":
    main()
