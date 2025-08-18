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
        file_path = get_data_path('Data/Station_Borough_Mappings/london_tube_stations_by_borough.csv')
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
    """Load station names from comprehensive_station_nlc_mapping_no_tramlink.csv"""
    try:
        file_path = get_data_path('Data/comprehensive_station_nlc_mapping_no_tramlink.csv')
        df = pd.read_csv(file_path)
        # Get unique station names from the Station column
        station_names = set(df['Station'].dropna().unique())
        return station_names
    except Exception as e:
        print(f"Error loading comprehensive station NLC mapping data (no tramlink): {e}")
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
    """Load NLC codes from comprehensive_station_nlc_mapping_no_tramlink.csv as strings"""
    try:
        file_path = get_data_path('Data/comprehensive_station_nlc_mapping_no_tramlink.csv')
        df = pd.read_csv(file_path)
        nlc_codes = set(df['NLC'].dropna().astype(str))
        return nlc_codes
    except Exception as e:
        print(f"Error loading comprehensive station NLC mapping codes (no tramlink): {e}")
        return set()

def load_station_borough_nlc_mapping_codes():
    """Load NLC codes from station_borough_nlc_mapping.csv as strings"""
    try:
        file_path = get_data_path('Data/station_borough_nlc_mapping.csv')
        df = pd.read_csv(file_path)
        nlc_codes = set(df['NLC'].dropna().astype(str))
        return nlc_codes
    except Exception as e:
        print(f"Error loading station borough NLC mapping codes: {e}")
        return set()

def load_nlc_to_station_mapping():
    """Return a dict mapping NLC code (as string) to station name from comprehensive_station_nlc_mapping_no_tramlink.csv"""
    try:
        file_path = get_data_path('Data/comprehensive_station_nlc_mapping_no_tramlink.csv')
        df = pd.read_csv(file_path)
        mapping = dict(zip(df['NLC'].astype(str), df['Station']))
        return mapping
    except Exception as e:
        print(f"Error loading comprehensive NLC to station mapping (no tramlink): {e}")
        return {}

def load_all_stations_by_borough():
    """Load station names from the all stations by borough file (with standardized borough names)"""
    try:
        file_path = get_data_path('Data/Station_Borough_Mappings/Standardized/all_stations_by_borough_standardized.csv')
        df = pd.read_csv(file_path)
        # Get unique station names from the station_name column
        station_names = set(df['station_name'].dropna().unique())
        print(f"Loaded {len(station_names)} unique stations from all stations by borough file")
        return station_names
    except Exception as e:
        print(f"Error loading all stations by borough: {e}")
        return set()

def create_station_names_venn_diagram():
    """Create Venn diagram comparing station names from borough mappings with comprehensive NLC mapping"""
    
    # Load station names from the two key datasets
    borough_stations = load_all_stations_by_borough()
    nlc_stations = load_station_nlc_mapping()
    
    # Create single Venn diagram
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    venn2([nlc_stations, borough_stations], 
          set_labels=('Comprehensive NLC\nMapping', 'All Stations by Borough\n(with standardized borough names)'), 
          ax=ax)
    ax.set_title('Station Names: Borough Mappings vs Comprehensive NLC Mapping', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add statistics as text
    overlapping = nlc_stations.intersection(borough_stations)
    only_in_nlc = nlc_stations - borough_stations
    only_in_borough = borough_stations - nlc_stations
    
    stats_text = f'Total NLC Mapping Stations: {len(nlc_stations)}\n'
    stats_text += f'Total Borough Mapping Stations: {len(borough_stations)}\n'
    stats_text += f'Overlap: {len(overlapping)} stations\n'
    stats_text += f'Only in NLC Mapping: {len(only_in_nlc)}\n'
    stats_text += f'Only in Borough Mappings: {len(only_in_borough)}'
    
    ax.text(0.5, 0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=12, 
           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    
    # Save to Plots directory
    plots_path = get_data_path('Plots/')
    os.makedirs(plots_path, exist_ok=True)
    plt.savefig(os.path.join(plots_path, 'borough_vs_nlc_station_names_venn.png'), 
               dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print(f"\nStation names Venn diagram saved to: Plots/borough_vs_nlc_station_names_venn.png")
    
    return borough_stations, nlc_stations

def print_station_names_analysis(borough_stations, nlc_stations):
    """Print detailed analysis of station names compatibility between borough mappings and NLC mapping"""
    
    print("\n" + "="*80)
    print("STATION NAMES: BOROUGH MAPPINGS vs COMPREHENSIVE NLC MAPPING ANALYSIS")
    print("="*80)
    
    print(f"\nComprehensive NLC Mapping contains {len(nlc_stations)} unique station names")
    print(f"All Stations by Borough contains {len(borough_stations)} unique station names")
    
    # Calculate overlaps
    overlapping = nlc_stations.intersection(borough_stations)
    only_in_nlc = nlc_stations - borough_stations
    only_in_borough = borough_stations - nlc_stations
    
    print(f"\nOverlap Analysis:")
    print(f"  Overlapping stations: {len(overlapping)} ({len(overlapping)/len(borough_stations)*100:.1f}% of borough mapping stations)")
    print(f"  Overlap percentage: {len(overlapping)/len(nlc_stations)*100:.1f}% of NLC mapping stations")
    print(f"  Only in NLC mapping: {len(only_in_nlc)}")
    print(f"  Only in borough mappings: {len(only_in_borough)}")
    
    if overlapping:
        print(f"\nSample overlapping stations (first 10):")
        for station in sorted(overlapping)[:10]:
            print(f"  - {station}")
        if len(overlapping) > 10:
            print(f"  ... and {len(overlapping) - 10} more")
    
    if only_in_borough:
        print(f"\nStations only in borough mappings ({len(only_in_borough)} total):")
        for station in sorted(only_in_borough):
            print(f"  - {station}")
    
    if only_in_nlc:
        print(f"\nStations only in NLC mapping ({len(only_in_nlc)} total):")
        for station in sorted(only_in_nlc):
            print(f"  - {station}")
    
    # Load the full dataframes for more detailed analysis
    try:
        borough_file = get_data_path('Data/Station_Borough_Mappings/Standardized/all_stations_by_borough_standardized.csv')
        borough_df = pd.read_csv(borough_file)
        
        nlc_file = get_data_path('Data/comprehensive_station_nlc_mapping_no_tramlink.csv')
        nlc_df = pd.read_csv(nlc_file)
        
        print(f"\nDetailed Statistics:")
        print(f"  Total rows in borough mapping file: {len(borough_df)}")
        print(f"  Total rows in NLC mapping file: {len(nlc_df)}")
        
        # System breakdown for borough stations
        if 'system' in borough_df.columns:
            print(f"\nBorough mapping stations by system:")
            system_counts = borough_df['system'].value_counts().sort_index()
            for system, count in system_counts.items():
                print(f"  {system}: {count} stations")
        
    except Exception as e:
        print(f"Error loading detailed data: {e}")

def create_venn_diagrams():
    """Create Venn diagrams for borough, station, and NLC code comparisons"""
    
    # Load data
    house_price_boroughs = load_house_price_data()
    tube_boroughs, tube_stations_df = load_tube_stations_data()
    od_stations_by_year = load_od_matrix_data()
    nlc_stations = load_station_nlc_mapping()
    nlc_2019, nlc_2022 = load_numbat_nlc_codes()
    nlc_mapping_codes = load_station_nlc_mapping_codes()
    station_borough_nlc_codes = load_station_borough_nlc_mapping_codes()
    
    # Create figure with four subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(24, 16))
    
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
    
    # NLC code comparison Venn diagram (original 3-way)
    venn3([nlc_mapping_codes, nlc_2019, nlc_2022],
          set_labels=('Comprehensive NLC Mapping', 'NUMBAT 2019 (MTT2a)', 'NUMBAT 2022 (TWT5d)'),
          ax=ax3)
    ax3.set_title('NLC Code Comparison (Original)', fontsize=14, fontweight='bold')
    
    # NLC code comparison Venn diagram (including station_borough_nlc_mapping)
    venn3([nlc_mapping_codes, station_borough_nlc_codes, nlc_2019],
          set_labels=('Comprehensive NLC Mapping', 'Station Borough NLC Mapping', 'NUMBAT 2019 (MTT2a)'),
          ax=ax4)
    ax4.set_title('NLC Code Comparison (with Station Borough Mapping)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save to Plots directory
    plots_path = get_data_path('Plots/')
    os.makedirs(plots_path, exist_ok=True)
    plt.savefig(os.path.join(plots_path, 'data_compatibility_venn_diagrams.png'), dpi=300, bbox_inches='tight')
    plt.show()
    
    return house_price_boroughs, tube_boroughs, od_stations_by_year, tube_stations_df, nlc_stations, nlc_mapping_codes, nlc_2019, nlc_2022, station_borough_nlc_codes

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

def print_station_borough_nlc_coverage_analysis(nlc_mapping_codes, station_borough_nlc_codes, nlc_2019, nlc_2022):
    """Analyze coverage of station_borough_nlc_mapping.csv against other NLC datasets"""
    nlc_to_station = load_nlc_to_station_mapping()
    def format_nlc(nlc):
        name = nlc_to_station.get(nlc, None)
        return f"{nlc}: {name}" if name else nlc

    print("\n" + "="*80)
    print("STATION BOROUGH NLC MAPPING COVERAGE ANALYSIS")
    print("="*80)
    
    print(f"\nStation Borough NLC Mapping contains {len(station_borough_nlc_codes)} NLC codes")
    print(f"Comprehensive NLC Mapping contains {len(nlc_mapping_codes)} NLC codes")
    print(f"NUMBAT 2019 contains {len(nlc_2019)} NLC codes")
    print(f"NUMBAT 2022 contains {len(nlc_2022)} NLC codes")
    
    # Check if station_borough_nlc_mapping contains all NLC codes from comprehensive mapping
    missing_from_station_borough = nlc_mapping_codes - station_borough_nlc_codes
    extra_in_station_borough = station_borough_nlc_codes - nlc_mapping_codes
    
    print(f"\nCOVERAGE ANALYSIS:")
    print(f"  NLC codes in Comprehensive Mapping but missing from Station Borough Mapping: {len(missing_from_station_borough)}")
    print(f"  NLC codes in Station Borough Mapping but not in Comprehensive Mapping: {len(extra_in_station_borough)}")
    print(f"  Coverage percentage: {len(station_borough_nlc_codes.intersection(nlc_mapping_codes))/len(nlc_mapping_codes)*100:.1f}%")
    
    # Check coverage against NUMBAT datasets
    numbat_2019_missing = nlc_2019 - station_borough_nlc_codes
    numbat_2022_missing = nlc_2022 - station_borough_nlc_codes
    
    print(f"\nNUMBAT COVERAGE:")
    print(f"  NUMBAT 2019 NLC codes missing from Station Borough Mapping: {len(numbat_2019_missing)}")
    print(f"  NUMBAT 2022 NLC codes missing from Station Borough Mapping: {len(numbat_2022_missing)}")
    print(f"  NUMBAT 2019 coverage: {len(station_borough_nlc_codes.intersection(nlc_2019))/len(nlc_2019)*100:.1f}%")
    print(f"  NUMBAT 2022 coverage: {len(station_borough_nlc_codes.intersection(nlc_2022))/len(nlc_2022)*100:.1f}%")
    
    if missing_from_station_borough:
        print(f"\nNLC codes missing from Station Borough Mapping:")
        for nlc in sorted(missing_from_station_borough):
            print(f"  - {format_nlc(nlc)}")
    
    if extra_in_station_borough:
        print(f"\nNLC codes in Station Borough Mapping but not in Comprehensive Mapping:")
        for nlc in sorted(extra_in_station_borough):
            print(f"  - {nlc}")
    
    if numbat_2019_missing:
        print(f"\nNUMBAT 2019 NLC codes missing from Station Borough Mapping:")
        for nlc in sorted(numbat_2019_missing):
            print(f"  - {format_nlc(nlc)}")
    
    if numbat_2022_missing:
        print(f"\nNUMBAT 2022 NLC codes missing from Station Borough Mapping:")
        for nlc in sorted(numbat_2022_missing):
            print(f"  - {format_nlc(nlc)}")
    
    # Check if station_borough_nlc_mapping contains ALL NLC codes from comprehensive mapping
    if len(missing_from_station_borough) == 0:
        print(f"\n✅ SUCCESS: Station Borough NLC Mapping contains ALL NLC codes from Comprehensive NLC Mapping!")
    else:
        print(f"\n❌ WARNING: Station Borough NLC Mapping is missing {len(missing_from_station_borough)} NLC codes from Comprehensive NLC Mapping")
    
    # Check if station_borough_nlc_mapping contains ALL NLC codes from NUMBAT datasets
    if len(numbat_2019_missing) == 0:
        print(f"✅ SUCCESS: Station Borough NLC Mapping contains ALL NUMBAT 2019 NLC codes!")
    else:
        print(f"❌ WARNING: Station Borough NLC Mapping is missing {len(numbat_2019_missing)} NUMBAT 2019 NLC codes")
    
    if len(numbat_2022_missing) == 0:
        print(f"✅ SUCCESS: Station Borough NLC Mapping contains ALL NUMBAT 2022 NLC codes!")
    else:
        print(f"❌ WARNING: Station Borough NLC Mapping is missing {len(numbat_2022_missing)} NUMBAT 2022 NLC codes")

def main():
    """Main function to run the analysis"""
    print("Starting data compatibility analysis...")
    
    # Create Venn diagrams and get data
    house_price_boroughs, tube_boroughs, od_stations_by_year, tube_stations_df, nlc_stations, nlc_mapping_codes, nlc_2019, nlc_2022, station_borough_nlc_codes = create_venn_diagrams()
    
    # Print detailed analysis
    print_detailed_analysis(house_price_boroughs, tube_boroughs, od_stations_by_year, tube_stations_df, nlc_stations)
    print_nlc_overlap_details(nlc_mapping_codes, nlc_2019, nlc_2022)
    
    # Create station names Venn diagram and analysis
    print("\n" + "="*80)
    print("STATION NAMES: BOROUGH MAPPINGS vs COMPREHENSIVE NLC MAPPING ANALYSIS")
    print("="*80)
    borough_stations, nlc_stations_for_analysis = create_station_names_venn_diagram()
    print_station_names_analysis(borough_stations, nlc_stations_for_analysis)
    
    # Add station borough NLC mapping coverage analysis
    print_station_borough_nlc_coverage_analysis(nlc_mapping_codes, station_borough_nlc_codes, nlc_2019, nlc_2022)
    
    print("\nAnalysis complete! Venn diagrams saved to Plots/ directory")

if __name__ == "__main__":
    main() 
