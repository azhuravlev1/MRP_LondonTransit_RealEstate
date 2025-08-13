import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import os
import glob
from pathlib import Path
import re

def get_data_path(relative_path):
    """Get the correct path to data files, whether running from EDA/ or project root"""
    # Try relative to current directory first
    if os.path.exists(relative_path):
        return relative_path
    # If not found, try going up one level (if running from EDA/)
    elif os.path.exists(os.path.join('..', relative_path)):
        return os.path.join('..', relative_path)
    else:
        raise FileNotFoundError(f"Could not find {relative_path}")

def load_house_price_data():
    """Load borough names from UK_House_price_index.xlsx"""
    try:
        file_path = get_data_path('Data/UK_House_price_index.xlsx')
        # Read the third sheet (Average Price)
        df = pd.read_excel(file_path, sheet_name=2)
        # Get borough names from column headers (row 0), columns B to AH
        borough_names = df.columns[1:34].tolist()  # B to AH is columns 1-33 (0-indexed)
        return set(borough_names)
    except Exception as e:
        print(f"Error loading house price data: {e}")
        return set()

def load_tube_stations_data():
    """Load borough names from london_tube_stations_by_borough.csv"""
    try:
        # Try multiple possible locations for the file
        possible_paths = [
            'london_tube_stations_by_borough.csv',  # Root directory
            'Data/london_tube_stations_by_borough.csv',  # Data directory
            '../london_tube_stations_by_borough.csv',  # If running from EDA/
            '../Data/london_tube_stations_by_borough.csv'  # If running from EDA/
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if file_path is None:
            raise FileNotFoundError("Could not find london_tube_stations_by_borough.csv")
            
        df = pd.read_csv(file_path)
        borough_names = set(df['borough'].dropna().unique())
        return borough_names, df
    except Exception as e:
        print(f"Error loading tube stations data: {e}")
        return set(), pd.DataFrame()

def load_od_matrix_data():
    """Load station names from OD matrix files"""
    station_names_by_year = {}
    
    # Load from RODS_OD folder (2003-2017)
    rods_od_path = get_data_path('Data/RODS_OD/')
    if os.path.exists(rods_od_path):
        for file_path in glob.glob(os.path.join(rods_od_path, 'ODmatrix_*.xls')):
            try:
                year = file_path.split('_')[-1].replace('.xls', '')
                df = pd.read_excel(file_path, sheet_name='matrix')
                # Get station names from columns 2 and 4, starting from row 5
                # Strip whitespace to handle padding issues
                origin_stations = set(df.iloc[4:, 1].dropna().str.strip().unique())  # Column 2 (0-indexed)
                dest_stations = set(df.iloc[4:, 3].dropna().str.strip().unique())    # Column 4 (0-indexed)
                all_stations = origin_stations.union(dest_stations)
                station_names_by_year[year] = all_stations
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    # Load from Rods_OD_2000-2002 folder
    rods_2000_2002_path = get_data_path('Data/RODS_OD/Rods_OD_2000-2002/')
    if os.path.exists(rods_2000_2002_path):
        for file_path in glob.glob(os.path.join(rods_2000_2002_path, 'ODmatrix_*.xls')):
            try:
                year = file_path.split('_')[-1].replace('.xls', '')
                df = pd.read_excel(file_path, sheet_name='matrix')
                # Get station names from columns 2 and 4, starting from row 5
                # Strip whitespace to handle padding issues
                origin_stations = set(df.iloc[4:, 1].dropna().str.strip().unique())  # Column 2 (0-indexed)
                dest_stations = set(df.iloc[4:, 3].dropna().str.strip().unique())    # Column 4 (0-indexed)
                all_stations = origin_stations.union(dest_stations)
                station_names_by_year[year] = all_stations
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    return station_names_by_year

def load_station_nlc_mapping():
    """Load station names from comprehensive_station_nlc_mapping.csv"""
    try:
        file_path = get_data_path('Data/comprehensive_station_nlc_mapping.csv')
        df = pd.read_csv(file_path)
        # Get unique station names from the Station column
        station_names = set(df['Station'].dropna().unique())
        return station_names
    except Exception as e:
        print(f"Error loading comprehensive station NLC mapping data: {e}")
        return set()

def load_numbat_nlc_codes():
    """Load NLC codes from the two NUMBAT OD matrix files for 2019 and 2022"""
    try:
        # 2022 file
        file_2022 = get_data_path('Data/NUMBAT/OD_Matrices/2022/NBT22TWT5d_od_network_qhr_wf_o.csv')
        df_2022 = pd.read_csv(file_2022)
        nlc_2022 = set(df_2022['mnlc_o'].dropna().astype(str)).union(set(df_2022['mnlc_d'].dropna().astype(str)))
        # 2019 file
        file_2019 = get_data_path('Data/NUMBAT/OD_Matrices/2019/NBT19MTT2a_od__network_qhr_wf.csv')
        df_2019 = pd.read_csv(file_2019)
        nlc_2019 = set(df_2019['mnlc_o'].dropna().astype(str)).union(set(df_2019['mnlc_d'].dropna().astype(str)))
        return nlc_2019, nlc_2022
    except Exception as e:
        print(f"Error loading NUMBAT NLC codes: {e}")
        return set(), set()

def load_station_nlc_mapping_codes():
    """Load NLC codes from comprehensive_station_nlc_mapping.csv as strings"""
    try:
        file_path = get_data_path('Data/comprehensive_station_nlc_mapping.csv')
        df = pd.read_csv(file_path)
        nlc_codes = set(df['NLC'].dropna().astype(str))
        return nlc_codes
    except Exception as e:
        print(f"Error loading comprehensive station NLC mapping codes: {e}")
        return set()

def load_nlc_to_station_mapping():
    """Return a dict mapping NLC code (as string) to station name from comprehensive_station_nlc_mapping.csv"""
    try:
        file_path = get_data_path('Data/comprehensive_station_nlc_mapping.csv')
        df = pd.read_csv(file_path)
        mapping = dict(zip(df['NLC'].astype(str), df['Station']))
        return mapping
    except Exception as e:
        print(f"Error loading comprehensive NLC to station mapping: {e}")
        return {}

def create_venn_diagrams():
    """Create Venn diagrams for borough, station, and NLC code comparisons"""
    
    # Load data
    house_price_boroughs = load_house_price_data()
    tube_boroughs, tube_stations_df = load_tube_stations_data()
    od_stations_by_year = load_od_matrix_data()
    nlc_stations = load_station_nlc_mapping()
    nlc_2019, nlc_2022 = load_numbat_nlc_codes()
    nlc_mapping_codes = load_station_nlc_mapping_codes()
    
    # Create figure with three subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(28, 8))
    
    # Borough comparison Venn diagram
    venn2([house_price_boroughs, tube_boroughs], 
          set_labels=('UK House Price Index\nBoroughs', 'Tube Stations\nBoroughs'), 
          ax=ax1)
    ax1.set_title('Borough Names Comparison', fontsize=14, fontweight='bold')
    
    # Station comparison Venn diagram (using most recent year) - now with 3 circles
    if od_stations_by_year:
        most_recent_year = max(od_stations_by_year.keys())
        od_stations = set(od_stations_by_year[most_recent_year])
        tube_stations = set(tube_stations_df['station_name'].dropna().unique())
        venn3([od_stations, tube_stations, nlc_stations], 
              set_labels=(f'OD Matrix {most_recent_year}\nStations', 'Tube Stations CSV\nStations', 'Comprehensive Station NLC Mapping\nStations'), 
              ax=ax2)
        ax2.set_title('Station Names Comparison (3 Datasets)', fontsize=14, fontweight='bold')
    
    # NLC code comparison Venn diagram
    venn3([nlc_mapping_codes, nlc_2019, nlc_2022],
          set_labels=('Comprehensive NLC Mapping', 'NUMBAT 2019 (MTT2a)', 'NUMBAT 2022 (TWT5d)'),
          ax=ax3)
    ax3.set_title('NLC Code Comparison', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save to Plots directory
    plots_path = get_data_path('Plots/')
    os.makedirs(plots_path, exist_ok=True)
    plt.savefig(os.path.join(plots_path, 'data_compatibility_venn_diagrams.png'), dpi=300, bbox_inches='tight')
    plt.show()
    
    return house_price_boroughs, tube_boroughs, od_stations_by_year, tube_stations_df, nlc_stations, nlc_mapping_codes, nlc_2019, nlc_2022

def print_detailed_analysis(house_price_boroughs, tube_boroughs, od_stations_by_year, tube_stations_df, nlc_stations):
    """Print detailed analysis of the data"""
    
    print("=" * 80)
    print("DATA COMPATIBILITY ANALYSIS")
    print("=" * 80)
    
    # Borough analysis
    print("\n1. BOROUGH NAMES ANALYSIS")
    print("-" * 40)
    print(f"Number of boroughs in UK House Price Index: {len(house_price_boroughs)}")
    print(f"Number of boroughs in Tube Stations CSV: {len(tube_boroughs)}")
    print(f"Boroughs in both datasets: {len(house_price_boroughs.intersection(tube_boroughs))}")
    print(f"Boroughs only in House Price Index: {len(house_price_boroughs - tube_boroughs)}")
    print(f"Boroughs only in Tube Stations CSV: {len(tube_boroughs - house_price_boroughs)}")
    
    print("\nBoroughs only in UK House Price Index:")
    for borough in sorted(house_price_boroughs - tube_boroughs):
        print(f"  - {borough}")
    
    print("\nBoroughs only in Tube Stations CSV:")
    for borough in sorted(tube_boroughs - house_price_boroughs):
        print(f"  - {borough}")
    
    # Station analysis
    print("\n\n2. STATION NAMES ANALYSIS")
    print("-" * 40)
    
    tube_stations = set(tube_stations_df['station_name'].dropna().unique())
    print(f"Number of unique stations in Tube Stations CSV: {len(tube_stations)}")
    print(f"Number of unique stations in Comprehensive Station NLC Mapping: {len(nlc_stations)}")
    
    if od_stations_by_year:
        print(f"\nNumber of unique stations by year in OD Matrix files:")
        for year in sorted(od_stations_by_year.keys()):
            print(f"  {year}: {len(od_stations_by_year[year])}")
        
        # Compare with most recent year
        most_recent_year = max(od_stations_by_year.keys())
        od_stations = set(od_stations_by_year[most_recent_year])
        
        print(f"\nComparison with {most_recent_year} OD Matrix:")
        print(f"Stations in all three datasets: {len(od_stations.intersection(tube_stations).intersection(nlc_stations))}")
        print(f"Stations in OD Matrix {most_recent_year} and Tube Stations CSV: {len(od_stations.intersection(tube_stations))}")
        print(f"Stations in OD Matrix {most_recent_year} and Comprehensive NLC Mapping: {len(od_stations.intersection(nlc_stations))}")
        print(f"Stations in Tube Stations CSV and Comprehensive NLC Mapping: {len(tube_stations.intersection(nlc_stations))}")
        print(f"Stations only in OD Matrix {most_recent_year}: {len(od_stations - tube_stations - nlc_stations)}")
        print(f"Stations only in Tube Stations CSV: {len(tube_stations - od_stations - nlc_stations)}")
        print(f"Stations only in Comprehensive NLC Mapping: {len(nlc_stations - od_stations - tube_stations)}")
        
        print(f"\nStations only in OD Matrix {most_recent_year}:")
        for station in sorted(od_stations - tube_stations - nlc_stations):
            print(f"  - {station}")
        
        print(f"\nStations only in Tube Stations CSV:")
        for station in sorted(tube_stations - od_stations - nlc_stations):
            print(f"  - {station}")
            
        print(f"\nStations only in Comprehensive NLC Mapping:")
        for station in sorted(nlc_stations - od_stations - tube_stations):
            print(f"  - {station}")

def print_station_overlap_details(od_stations, tube_stations, nlc_stations):
    print("\nStations in all three datasets:")
    print(sorted(od_stations & tube_stations & nlc_stations))

    print("\nStations only in OD Matrix 2017:")
    print(sorted(od_stations - tube_stations - nlc_stations))

    print("\nStations only in Tube Stations CSV:")
    print(sorted(tube_stations - od_stations - nlc_stations))

    print("\nStations only in NLC Mapping:")
    print(sorted(nlc_stations - od_stations - tube_stations))

    print("\nStations in OD Matrix 2017 and Tube Stations CSV only:")
    print(sorted((od_stations & tube_stations) - nlc_stations))

    print("\nStations in OD Matrix 2017 and NLC Mapping only:")
    print(sorted((od_stations & nlc_stations) - tube_stations))

    print("\nStations in Tube Stations CSV and NLC Mapping only:")
    print(sorted((tube_stations & nlc_stations) - od_stations))

def print_nlc_overlap_details(nlc_mapping_codes, nlc_2019, nlc_2022):
    nlc_to_station = load_nlc_to_station_mapping()
    def format_nlc(nlc):
        name = nlc_to_station.get(nlc, None)
        return f"{nlc}: {name}" if name else nlc

    print("\nNLC CODE OVERLAP ANALYSIS (with station names where possible)")
    print("-" * 40)
    print(f"NLCs in all three datasets: {len(nlc_mapping_codes & nlc_2019 & nlc_2022)}")
    print(f"NLCs only in Comprehensive NLC Mapping: {len(nlc_mapping_codes - nlc_2019 - nlc_2022)}")
    print(f"NLCs only in NUMBAT 2019: {len(nlc_2019 - nlc_mapping_codes - nlc_2022)}")
    print(f"NLCs only in NUMBAT 2022: {len(nlc_2022 - nlc_mapping_codes - nlc_2019)}")
    print(f"NLCs in Comprehensive NLC Mapping and NUMBAT 2019 only: {len((nlc_mapping_codes & nlc_2019) - nlc_2022)}")
    print(f"NLCs in Comprehensive NLC Mapping and NUMBAT 2022 only: {len((nlc_mapping_codes & nlc_2022) - nlc_2019)}")
    print(f"NLCs in NUMBAT 2019 and NUMBAT 2022 only: {len((nlc_2019 & nlc_2022) - nlc_mapping_codes)}")

    print(f"\nNLCs in all three datasets:")
    for nlc in sorted(nlc_mapping_codes & nlc_2019 & nlc_2022):
        print(f"  - {format_nlc(nlc)}")
    print(f"\nNLCs only in Comprehensive NLC Mapping:")
    for nlc in sorted(nlc_mapping_codes - nlc_2019 - nlc_2022):
        print(f"  - {format_nlc(nlc)}")
    print(f"\nNLCs only in NUMBAT 2019:")
    for nlc in sorted(nlc_2019 - nlc_mapping_codes - nlc_2022):
        print(f"  - {format_nlc(nlc)}")
    print(f"\nNLCs only in NUMBAT 2022:")
    for nlc in sorted(nlc_2022 - nlc_mapping_codes - nlc_2019):
        print(f"  - {format_nlc(nlc)}")
    print(f"\nNLCs in Comprehensive NLC Mapping and NUMBAT 2019 only:")
    for nlc in sorted((nlc_mapping_codes & nlc_2019) - nlc_2022):
        print(f"  - {format_nlc(nlc)}")
    print(f"\nNLCs in Comprehensive NLC Mapping and NUMBAT 2022 only:")
    for nlc in sorted((nlc_mapping_codes & nlc_2022) - nlc_2019):
        print(f"  - {format_nlc(nlc)}")
    print(f"\nNLCs in NUMBAT 2019 and NUMBAT 2022 only:")
    for nlc in sorted((nlc_2019 & nlc_2022) - nlc_mapping_codes):
        print(f"  - {format_nlc(nlc)}")

def main():
    """Main function to run the analysis"""
    print("Starting data compatibility analysis...")
    
    # Create Venn diagrams and get data
    house_price_boroughs, tube_boroughs, od_stations_by_year, tube_stations_df, nlc_stations, nlc_mapping_codes, nlc_2019, nlc_2022 = create_venn_diagrams()
    
    # Print detailed analysis
    print_detailed_analysis(house_price_boroughs, tube_boroughs, od_stations_by_year, tube_stations_df, nlc_stations)
    print_nlc_overlap_details(nlc_mapping_codes, nlc_2019, nlc_2022)
    
    print("\nAnalysis complete! Venn diagrams saved to Plots/data_compatibility_venn_diagrams.png")

if __name__ == "__main__":
    main() 
