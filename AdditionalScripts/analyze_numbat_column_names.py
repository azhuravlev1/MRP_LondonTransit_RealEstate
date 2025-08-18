import pandas as pd
import os
import glob
from collections import defaultdict

def get_data_path(relative_path):
    """Get the correct path to data files"""
    if os.path.exists(relative_path):
        return relative_path
    elif os.path.exists(os.path.join('..', relative_path)):
        return os.path.join('..', relative_path)
    else:
        raise FileNotFoundError(f"Could not find {relative_path}")

def analyze_numbat_column_names():
    """Analyze column naming conventions for NUMBAT OD matrix files across different years"""
    
    # Define the base path for NUMBAT OD matrices
    base_path = get_data_path('Data/NUMBAT/OD_Matrices')
    
    # Dictionary to store column names by year
    year_columns = defaultdict(set)
    year_files = defaultdict(list)
    
    # Analyze files for each year
    for year in ['2017', '2018', '2019', '2020', '2021', '2022', '2023']:
        year_path = os.path.join(base_path, year)
        if os.path.exists(year_path):
            # Find all CSV files in the year directory
            csv_files = glob.glob(os.path.join(year_path, '*.csv'))
            
            for file_path in csv_files:
                try:
                    # Read just the header to get column names
                    df = pd.read_csv(file_path, nrows=0)
                    columns = list(df.columns)
                    
                    # Store unique column names for this year
                    year_columns[year].update(columns)
                    year_files[year].append(os.path.basename(file_path))
                    
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    # Print summary
    print("NUMBAT OD Matrix Column Naming Convention Analysis")
    print("=" * 60)
    
    for year in sorted(year_columns.keys()):
        print(f"\nYear {year}:")
        print(f"  Files analyzed: {len(year_files[year])}")
        print(f"  Sample files: {year_files[year][:3]}")  # Show first 3 files
        
        columns = sorted(year_columns[year])
        print(f"  Column names ({len(columns)} total):")
        for col in columns:
            print(f"    - {col}")
    
    # Identify patterns
    print("\n" + "=" * 60)
    print("COLUMN NAMING CONVENTIONS SUMMARY:")
    print("=" * 60)
    
    # Check origin/destination column patterns
    origin_cols = {}
    dest_cols = {}
    
    for year in year_columns:
        cols = year_columns[year]
        origin_col = None
        dest_col = None
        
        for col in cols:
            if 'mnlc_o' in col.lower():
                origin_col = col
            elif 'mnlc_d' in col.lower():
                dest_col = col
        
        origin_cols[year] = origin_col
        dest_cols[year] = dest_col
    
    print("\nOrigin/Destination Column Patterns:")
    for year in sorted(origin_cols.keys()):
        print(f"  {year}: Origin='{origin_cols[year]}', Destination='{dest_cols[year]}'")
    
    # Analyze time period columns
    print("\nTime Period Column Patterns:")
    time_patterns = defaultdict(set)
    
    for year in year_columns:
        for col in year_columns[year]:
            if any(time_indicator in col.lower() for time_indicator in ['qhr', 'tb']):
                time_patterns[year].add(col)
    
    for year in sorted(time_patterns.keys()):
        print(f"  {year}: {sorted(time_patterns[year])}")
    
    # Check for other common patterns
    print("\nOther Column Patterns:")
    mode_patterns = defaultdict(set)
    network_patterns = defaultdict(set)
    
    for year in year_columns:
        for col in year_columns[year]:
            if 'mode' in col.lower():
                mode_patterns[year].add(col)
            elif 'network' in col.lower():
                network_patterns[year].add(col)
    
    for year in sorted(mode_patterns.keys()):
        if mode_patterns[year]:
            print(f"  {year} - Mode columns: {sorted(mode_patterns[year])}")
    
    for year in sorted(network_patterns.keys()):
        if network_patterns[year]:
            print(f"  {year} - Network columns: {sorted(network_patterns[year])}")
    
    return year_columns, year_files

if __name__ == "__main__":
    year_columns, year_files = analyze_numbat_column_names()
