import pandas as pd
import numpy as np
import igraph as ig
import os
import glob
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

def get_column_names_for_year(year):
    """
    Get the correct column names for origin and destination based on year.
    
    Args:
        year (int): Year to determine column names for
        
    Returns:
        tuple: (origin_column_name, destination_column_name)
    """
    if year in [2019, 2022]:
        return 'mnlc_o', 'mnlc_d'
    else:
        return 'mode_mnlc_o', 'mode_mnlc_d'

def get_time_band_mapping():
    """
    Get mapping for time bands (tb) to quarter-hour slots (qhr).
    
    Returns:
        dict: Mapping from time band names to lists of quarter-hour slot numbers
    """
    return {
        'early': list(range(21, 29)),      # 05:00-07:00 (slots 21-28)
        'am_peak': list(range(29, 45)),    # 07:00-11:00 (slots 29-44)
        'midday': list(range(45, 61)),     # 11:00-15:00 (slots 45-60)
        'pm_peak': list(range(61, 77)),    # 15:00-19:00 (slots 61-76)
        'evening': list(range(77, 93)),    # 19:00-23:00 (slots 77-92)
        'late': list(range(93, 117))       # 23:00-05:00 (slots 93-116)
    }

def get_quarter_hour_slot_time_range(slot_number):
    """
    Convert quarter-hour slot number to time range string.
    
    Args:
        slot_number (int): Quarter-hour slot number (21-116)
        
    Returns:
        str: Time range string (e.g., "0500-0515")
    """
    # Slot 21 = 05:00, slot 22 = 05:15, etc.
    hour = ((slot_number - 21) // 4) + 5
    minute = ((slot_number - 21) % 4) * 15
    
    # Handle hour overflow (after 23:59)
    if hour >= 24:
        hour -= 24
    
    # Calculate end time
    end_minute = minute + 15
    end_hour = hour
    if end_minute >= 60:
        end_minute -= 60
        end_hour += 1
    if end_hour >= 24:
        end_hour -= 24
    
    # Format as HHMM-HHMM
    start_time = f"{hour:02d}{minute:02d}"
    end_time = f"{end_hour:02d}{end_minute:02d}"
    
    return f"{start_time}-{end_time}"

def read_numbat_csv_file(file_path, year):
    """
    Read NUMBAT CSV file and extract the OD matrix data.
    
    Args:
        file_path (str): Path to the NUMBAT CSV file
        year (int): Year to determine column names
        
    Returns:
        DataFrame: OD matrix with origin, destination, and flow columns
    """
    # Get column names for this year
    origin_col, dest_col = get_column_names_for_year(year)
    
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Extract origin and destination columns
    od_data = df[[origin_col, dest_col]].copy()
    od_data.columns = ['origin_nlc', 'dest_nlc']
    
    # Add flow columns (starting from column 3)
    flow_columns = df.columns[2:].tolist()
    for col in flow_columns:
        od_data[col] = df[col]
    
    # Convert NLC codes to numeric, handling any non-numeric values
    od_data['origin_nlc'] = pd.to_numeric(od_data['origin_nlc'], errors='coerce')
    od_data['dest_nlc'] = pd.to_numeric(od_data['dest_nlc'], errors='coerce')
    
    # Convert flow columns to numeric
    for col in flow_columns:
        od_data[col] = pd.to_numeric(od_data[col], errors='coerce').fillna(0)
    
    # Remove rows where either NLC is NaN
    od_data = od_data.dropna(subset=['origin_nlc', 'dest_nlc'])
    
    return od_data, flow_columns

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
    
    # Get flow columns (all columns except origin_nlc, dest_nlc, origin_borough, dest_borough)
    flow_columns = [col for col in od_data.columns if col not in ['origin_nlc', 'dest_nlc', 'origin_borough', 'dest_borough']]
    
    # Aggregate by borough pairs
    borough_flows = od_data.groupby(['origin_borough', 'dest_borough'])[flow_columns].sum().reset_index()
    
    return borough_flows

def create_graph_from_borough_flows(borough_flows, flow_columns=None, specific_columns=None):
    """
    Create an igraph Graph object from borough-to-borough flows.
    
    Args:
        borough_flows (DataFrame): Borough-to-borough OD matrix
        flow_columns (list, optional): List of flow column names to sum
        specific_columns (list, optional): Specific columns to use for weights
        
    Returns:
        igraph.Graph: Directed weighted graph
    """
    # Create a copy for manipulation
    graph_data = borough_flows.copy()
    
    if specific_columns is not None:
        # Use specific columns
        graph_data['weight'] = graph_data[specific_columns].sum(axis=1)
    elif flow_columns is not None:
        # Sum specified flow columns
        graph_data['weight'] = graph_data[flow_columns].sum(axis=1)
    else:
        # Sum all flow columns (excluding metadata columns)
        flow_cols = [col for col in graph_data.columns if col not in ['origin_borough', 'dest_borough']]
        graph_data['weight'] = graph_data[flow_cols].sum(axis=1)
    
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

def get_day_groups_from_filenames(year_directory):
    """
    Extract day groups from filenames in a year directory.
    
    Args:
        year_directory (str): Path to year directory containing NUMBAT files
        
    Returns:
        dict: Mapping from day group to list of file paths
    """
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(year_directory, "*.csv"))
    
    day_groups = {}
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        
        # Extract day group from filename
        # Examples: NBT17MTT2b_od_mode_LU_qhr_wf_o.csv -> MTT
        #           NBT19FRI2a_od__network_qhr_wf.csv -> FRI
        parts = filename.split('_')
        
        # Extract day group from the first part (e.g., NBT17MTF2b -> MTF)
        day_group = None
        if parts:
            first_part = parts[0]  # e.g., "NBT17MTF2b"
            # Look for day group patterns in the first part
            for pattern in ['MTT', 'MTF', 'FRI', 'SAT', 'SUN', 'MON', 'TWT']:
                if pattern in first_part:
                    day_group = pattern
                    break
        
        if day_group:
            if day_group not in day_groups:
                day_groups[day_group] = []
            day_groups[day_group].append(file_path)
    
    return day_groups

def process_numbat_day_group(year, day_group, file_paths, nlc_to_borough_mapping, output_base_path):
    """
    Process all files for a specific day group and create graphs.
    
    Args:
        year (int): Year being processed
        day_group (str): Day group (e.g., 'MTT', 'FRI', 'SAT', 'SUN')
        file_paths (list): List of file paths for this day group
        nlc_to_borough_mapping (dict): Station to borough mapping
        output_base_path (str): Base path for output graphs
    """
    # Create output directory for this day group
    day_group_dir = os.path.join(output_base_path, 'NUMBAT', str(year), day_group)
    tb_dir = os.path.join(day_group_dir, 'time_bands', 'tb')
    qhr_dir = os.path.join(day_group_dir, 'time_bands', 'qhr')
    
    # Combine all files for this day group
    all_borough_flows = None
    all_flow_columns = []
    
    for file_path in file_paths:
        od_data, flow_columns = read_numbat_csv_file(file_path, year)
        borough_flows = aggregate_station_flows_to_borough_flows(od_data, nlc_to_borough_mapping)
        
        if all_borough_flows is None:
            all_borough_flows = borough_flows
            all_flow_columns = flow_columns
        else:
            # Merge with existing data, summing flows for same borough pairs
            all_borough_flows = pd.concat([all_borough_flows, borough_flows])
            all_borough_flows = all_borough_flows.groupby(['origin_borough', 'dest_borough']).sum().reset_index()
    
    if all_borough_flows is None or all_borough_flows.empty:
        print(f"Warning: No data found for year {year}, day group {day_group}")
        return
    
    # Create overall graph for this day group
    overall_graph = create_graph_from_borough_flows(all_borough_flows, all_flow_columns)
    overall_graph_path = os.path.join(day_group_dir, f'{year}_{day_group}.graphml')
    save_graph(overall_graph, overall_graph_path)
    
    # Create time band graphs
    time_band_mapping = get_time_band_mapping()
    time_band_names = ['early', 'am_peak', 'midday', 'pm_peak', 'evening', 'late']
    time_band_labels = ['early', 'am-peak', 'midday', 'pm-peak', 'evening', 'late']
    
    for time_band, label in zip(time_band_names, time_band_labels):
        # Get column indices for this time band
        slot_indices = time_band_mapping[time_band]
        
        # Map slot indices to actual column names
        time_band_columns = []
        for slot in slot_indices:
            # Column names are 1-indexed, starting from column 3
            col_index = slot - 20  # Adjust for 1-indexing and offset
            if col_index < len(all_flow_columns):
                time_band_columns.append(all_flow_columns[col_index])
        
        if time_band_columns:
            time_graph = create_graph_from_borough_flows(all_borough_flows, specific_columns=time_band_columns)
            time_graph_path = os.path.join(tb_dir, f'{year}_{day_group}_tb_{label}.graphml')
            save_graph(time_graph, time_graph_path)
    
    # Create quarter-hour slot graphs
    for i, flow_col in enumerate(all_flow_columns):
        slot_number = i + 21  # Slot numbers start at 21
        time_range = get_quarter_hour_slot_time_range(slot_number)
        
        slot_graph = create_graph_from_borough_flows(all_borough_flows, specific_columns=[flow_col])
        slot_graph_path = os.path.join(qhr_dir, f'{year}_{day_group}_qhr_slot-{slot_number}_{time_range}.graphml')
        save_graph(slot_graph, slot_graph_path)

def process_numbat_year(year, numbat_data_path, mapping_file_path, output_base_path):
    """
    Process all NUMBAT files for a specific year.
    
    Args:
        year (int): Year to process
        numbat_data_path (str): Path to NUMBAT data directory
        mapping_file_path (str): Path to station-borough mapping file
        output_base_path (str): Base path for output graphs
    """
    # Load station-borough mapping
    nlc_to_borough_mapping = load_station_borough_mapping(mapping_file_path)
    
    # Determine year directory path
    year_directory = os.path.join(numbat_data_path, 'OD_Matrices', str(year))
    
    if not os.path.exists(year_directory):
        print(f"Warning: Directory not found for year {year}: {year_directory}")
        return
    
    # Get day groups from filenames
    day_groups = get_day_groups_from_filenames(year_directory)
    
    if not day_groups:
        print(f"Warning: No valid files found for year {year}")
        return
    
    print(f"Processing NUMBAT data for year {year} with day groups: {list(day_groups.keys())}")
    
    # Process each day group
    for day_group, file_paths in day_groups.items():
        process_numbat_day_group(year, day_group, file_paths, nlc_to_borough_mapping, output_base_path)
    
    # Create overall year graph (combining all day groups)
    all_year_borough_flows = None
    
    for day_group, file_paths in day_groups.items():
        for file_path in file_paths:
            od_data, flow_columns = read_numbat_csv_file(file_path, year)
            borough_flows = aggregate_station_flows_to_borough_flows(od_data, nlc_to_borough_mapping)
            
            if all_year_borough_flows is None:
                all_year_borough_flows = borough_flows
            else:
                # Merge with existing data, summing flows for same borough pairs
                all_year_borough_flows = pd.concat([all_year_borough_flows, borough_flows])
                all_year_borough_flows = all_year_borough_flows.groupby(['origin_borough', 'dest_borough']).sum().reset_index()
    
    if all_year_borough_flows is not None and not all_year_borough_flows.empty:
        overall_year_graph = create_graph_from_borough_flows(all_year_borough_flows)
        overall_year_path = os.path.join(output_base_path, 'NUMBAT', str(year), f'{year}.graphml')
        save_graph(overall_year_graph, overall_year_path)

def main():
    """
    Main function to process all NUMBAT years and create graphs.
    """
    # Define paths
    numbat_data_path = "../Data/NUMBAT"
    mapping_file_path = "../Data/station_borough_nlc_mapping.csv"
    output_base_path = "../Data/Graphs"
    
    # Define years to process (2017-2023)
    years = list(range(2017, 2024))
    
    print("Building NUMBAT graphs...")
    print(f"Processing {len(years)} years: {years[0]} to {years[-1]}")
    
    # Process each year with progress bar
    for year in tqdm(years, desc="Processing NUMBAT years"):
        try:
            process_numbat_year(year, numbat_data_path, mapping_file_path, output_base_path)
        except Exception as e:
            print(f"Error processing year {year}: {str(e)}")
            continue
    
    print("NUMBAT graph construction completed!")

if __name__ == "__main__":
    main()
