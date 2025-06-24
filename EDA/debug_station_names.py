import pandas as pd
import os
import glob

def get_data_path(relative_path):
    """Get the correct path to data files, whether running from EDA/ or project root"""
    if os.path.exists(relative_path):
        return relative_path
    elif os.path.exists(os.path.join('..', relative_path)):
        return os.path.join('..', relative_path)
    else:
        raise FileNotFoundError(f"Could not find {relative_path}")

def examine_station_names():
    """Examine the exact station names in both datasets"""
    
    # Load tube stations CSV
    tube_stations_df = pd.read_csv(get_data_path('london_tube_stations_by_borough.csv'))
    tube_stations = set(tube_stations_df['station_name'].dropna().unique())
    
    # Load OD matrix 2017
    od_file_path = get_data_path('Data/RODS_OD/ODmatrix_2017.xls')
    od_df = pd.read_excel(od_file_path, sheet_name='matrix')
    
    # Get station names from columns 2 and 4, starting from row 5
    origin_stations = set(od_df.iloc[4:, 1].dropna().unique())  # Column 2 (0-indexed)
    dest_stations = set(od_df.iloc[4:, 3].dropna().unique())    # Column 4 (0-indexed)
    od_stations = origin_stations.union(dest_stations)
    
    print("=" * 80)
    print("STATION NAME DEBUG ANALYSIS")
    print("=" * 80)
    
    print(f"\nTube Stations CSV has {len(tube_stations)} unique stations")
    print(f"OD Matrix 2017 has {len(od_stations)} unique stations")
    
    # Check for Acton Town specifically
    print(f"\nActon Town in Tube Stations CSV: {'Acton Town' in tube_stations}")
    print(f"Acton Town in OD Matrix 2017: {'Acton Town' in od_stations}")
    
    # Look for any variations of Acton Town
    acton_variations_tube = [s for s in tube_stations if 'Acton' in s]
    acton_variations_od = [s for s in od_stations if 'Acton' in s]
    
    print(f"\nActon variations in Tube Stations CSV: {acton_variations_tube}")
    print(f"Acton variations in OD Matrix 2017: {acton_variations_od}")
    
    # Check for exact matches
    intersection = tube_stations.intersection(od_stations)
    print(f"\nExact matches between datasets: {len(intersection)}")
    
    # Check for stations only in each dataset
    only_in_tube = tube_stations - od_stations
    only_in_od = od_stations - tube_stations
    
    print(f"\nStations only in Tube Stations CSV: {len(only_in_tube)}")
    print(f"Stations only in OD Matrix 2017: {len(only_in_od)}")
    
    # Look for potential formatting issues
    print(f"\nSample of stations only in Tube Stations CSV:")
    for station in sorted(list(only_in_tube)[:10]):
        print(f"  '{station}'")
    
    print(f"\nSample of stations only in OD Matrix 2017:")
    for station in sorted(list(only_in_od)[:10]):
        print(f"  '{station}'")
    
    # Check for whitespace issues
    print(f"\nChecking for whitespace issues...")
    tube_stations_stripped = {s.strip() for s in tube_stations}
    od_stations_stripped = {s.strip() for s in od_stations}
    
    intersection_stripped = tube_stations_stripped.intersection(od_stations_stripped)
    print(f"Exact matches after stripping whitespace: {len(intersection_stripped)}")
    
    # Check if Acton Town is in the intersection after stripping
    print(f"Acton Town in intersection after stripping: {'Acton Town' in intersection_stripped}")
    
    # Show some examples of the raw data
    print(f"\nRaw station names from OD Matrix (first 10):")
    for station in sorted(list(od_stations)[:10]):
        print(f"  '{station}' (length: {len(station)})")
    
    print(f"\nRaw station names from Tube Stations CSV (first 10):")
    for station in sorted(list(tube_stations)[:10]):
        print(f"  '{station}' (length: {len(station)})")

if __name__ == "__main__":
    examine_station_names() 