import os
import pandas as pd
from pathlib import Path

def check_numbat_od_column_names():
    """
    Check the first two column names of all NUMBAT OD matrix CSV files.
    Returns files that don't have 'mnlc_o' and 'mnlc_d' as their first two columns.
    """
    # Base directory for NUMBAT OD matrices
    base_dir = Path("Data/NUMBAT/OD_Matrices")
    
    # Expected first two column names
    expected_col1 = "mode_mnlc_o"
    expected_col2 = "mode_mnlc_d"
    
    # Store files that don't match the expected column names
    mismatched_files = []
    
    # Walk through all subdirectories
    for year_dir in base_dir.iterdir():
        if year_dir.is_dir() and year_dir.name.isdigit():
            print(f"Checking year: {year_dir.name}")
            
            for csv_file in year_dir.glob("*.csv"):
                try:
                    # Read just the header to get column names
                    df = pd.read_csv(csv_file, nrows=0)
                    
                    if len(df.columns) < 2:
                        mismatched_files.append({
                            'file': str(csv_file),
                            'reason': f"File has fewer than 2 columns: {list(df.columns)}"
                        })
                        continue
                    
                    col1, col2 = df.columns[0], df.columns[1]
                    
                    if col1 != expected_col1 or col2 != expected_col2:
                        mismatched_files.append({
                            'file': str(csv_file),
                            'col1': col1,
                            'col2': col2,
                            'expected_col1': expected_col1,
                            'expected_col2': expected_col2
                        })
                        
                except Exception as e:
                    mismatched_files.append({
                        'file': str(csv_file),
                        'reason': f"Error reading file: {str(e)}"
                    })
    
    return mismatched_files

def main():
    print("Checking NUMBAT OD matrix column names...")
    print("Expected first two columns: 'mode_mnlc_o', 'mode_mnlc_d'")
    print("-" * 60)
    
    mismatched_files = check_numbat_od_column_names()
    
    if not mismatched_files:
        print("✅ All files have the expected first two column names!")
    else:
        print(f"❌ Found {len(mismatched_files)} files with unexpected column names:")
        print()
        
        for file_info in mismatched_files:
            print(f"File: {file_info['file']}")
            
            if 'reason' in file_info:
                print(f"  Issue: {file_info['reason']}")
            else:
                print(f"  Expected: '{file_info['expected_col1']}', '{file_info['expected_col2']}'")
                print(f"  Found:    '{file_info['col1']}', '{file_info['col2']}'")
            print()

if __name__ == "__main__":
    main()
