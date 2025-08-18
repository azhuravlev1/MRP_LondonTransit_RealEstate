import os
import pandas as pd
import glob
from collections import defaultdict

def get_nlc_codes_from_file(file_path, year):
    """
    Extract NLC codes from the first two columns of a NUMBAT OD matrix file.
    
    Args:
        file_path (str): Path to the CSV file
        year (int): Year of the data (to determine column names)
    
    Returns:
        set: Set of unique NLC codes found in the file
    """
    try:
        # Determine column names based on year
        if year in [2017, 2018, 2020, 2021, 2023]:
            col1, col2 = 'mode_mnlc_o', 'mode_mnlc_d'
        elif year in [2019, 2022]:
            col1, col2 = 'mnlc_o', 'mnlc_d'
        else:
            print(f"Warning: Unknown year {year} for file {file_path}")
            return set()
        
        # Read only the first two columns to save memory
        df = pd.read_csv(file_path, usecols=[col1, col2])
        
        # Extract unique NLC codes from both columns
        nlc_codes = set()
        nlc_codes.update(df[col1].dropna().unique())
        nlc_codes.update(df[col2].dropna().unique())
        
        return nlc_codes
    
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return set()

def load_station_mapping_nlcs():
    """
    Load NLC codes from the station mapping file.
    
    Returns:
        set: Set of NLC codes from the station mapping file
    """
    try:
        mapping_file = "Data/comprehensive_station_nlc_mapping.csv"
        df = pd.read_csv(mapping_file)
        
        # Get NLC codes from the NLC column
        nlc_codes = set(df['NLC'].dropna().unique())
        print(f"Loaded {len(nlc_codes)} unique NLC codes from station mapping file")
        return nlc_codes
    
    except Exception as e:
        print(f"Error reading station mapping file: {e}")
        return set()

def categorize_files(file_nlc_codes, station_nlcs):
    """
    Categorize files into covered, almost covered, and not covered groups.
    
    Args:
        file_nlc_codes (dict): Dictionary mapping filenames to their NLC codes
        station_nlcs (set): Set of NLC codes from station mapping
    
    Returns:
        tuple: (covered_files, almost_covered_files, not_covered_files)
    """
    covered_files = []
    almost_covered_files = []
    not_covered_files = []
    
    for filename, nlc_codes in file_nlc_codes.items():
        # Find NLC codes not in station mapping
        uncovered_nlcs = nlc_codes - station_nlcs
        uncovered_count = len(uncovered_nlcs)
        
        if uncovered_count == 0:
            # All NLC codes are covered
            covered_files.append(filename)
        elif uncovered_count <= 3:
            # Almost covered (3 or fewer uncovered codes)
            almost_covered_files.append((filename, list(uncovered_nlcs)))
        else:
            # Not covered (more than 3 uncovered codes)
            not_covered_files.append((filename, uncovered_count))
    
    return covered_files, almost_covered_files, not_covered_files

def main():
    # Load station mapping NLC codes
    print("Loading station mapping NLC codes...")
    station_nlcs = load_station_mapping_nlcs()
    
    if not station_nlcs:
        print("Failed to load station mapping NLC codes. Exiting.")
        return
    
    # Base directory for NUMBAT OD matrices
    base_dir = "Data/NUMBAT/OD_Matrices"
    
    # Dictionary to store NLC codes for each file
    file_nlc_codes = {}
    
    # Process each year directory
    for year_dir in sorted(os.listdir(base_dir)):
        year_path = os.path.join(base_dir, year_dir)
        
        # Skip if not a directory or if it's a zip file
        if not os.path.isdir(year_path) or year_dir.endswith('.zip'):
            continue
        
        try:
            year = int(year_dir)
        except ValueError:
            continue
        
        print(f"Processing year {year}...")
        
        # Find all CSV files in the year directory
        csv_files = glob.glob(os.path.join(year_path, "*.csv"))
        
        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            print(f"  Processing {filename}...")
            
            # Extract NLC codes from the file
            nlc_codes = get_nlc_codes_from_file(csv_file, year)
            
            if nlc_codes:
                file_nlc_codes[filename] = nlc_codes
    
    # Categorize files
    print("\nCategorizing files...")
    covered_files, almost_covered_files, not_covered_files = categorize_files(file_nlc_codes, station_nlcs)
    
    # Print results
    print("\n" + "="*80)
    print("COVERAGE ANALYSIS RESULTS")
    print("="*80)
    
    # 1. Covered files
    print(f"\n1. COVERED FILES ({len(covered_files)} files)")
    print("-" * 50)
    if covered_files:
        for filename in sorted(covered_files):
            print(f"  {filename}")
    else:
        print("  No files found in this category.")
    
    # 2. Almost covered files
    print(f"\n2. ALMOST COVERED FILES ({len(almost_covered_files)} files)")
    print("-" * 50)
    if almost_covered_files:
        for filename, uncovered_nlcs in sorted(almost_covered_files):
            print(f"  {filename}")
            print(f"    Uncovered NLC codes: {uncovered_nlcs}")
    else:
        print("  No files found in this category.")
    
    # 3. Not covered files
    print(f"\n3. NOT COVERED FILES ({len(not_covered_files)} files)")
    print("-" * 50)
    if not_covered_files:
        for filename, uncovered_count in sorted(not_covered_files, key=lambda x: x[1], reverse=True):
            print(f"  {filename}: {uncovered_count} uncovered NLC codes")
    else:
        print("  No files found in this category.")
    
    # Summary statistics
    total_files = len(file_nlc_codes)
    print(f"\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total files processed: {total_files}")
    print(f"Covered files: {len(covered_files)} ({len(covered_files)/total_files*100:.1f}%)")
    print(f"Almost covered files: {len(almost_covered_files)} ({len(almost_covered_files)/total_files*100:.1f}%)")
    print(f"Not covered files: {len(not_covered_files)} ({len(not_covered_files)/total_files*100:.1f}%)")

if __name__ == "__main__":
    main()
