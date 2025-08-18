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

def analyze_numbat_patterns():
    """Analyze file naming patterns to understand column naming rules"""
    
    # Define the base path for NUMBAT OD matrices
    base_path = get_data_path('Data/NUMBAT/OD_Matrices')
    
    # Dictionary to store file patterns and their column structures
    file_patterns = defaultdict(lambda: {
        'files': [],
        'first_two_columns': set(),
        'column_ranges': set(),
        'total_columns': set()
    })
    
    print("Analyzing NUMBAT File Naming Patterns")
    print("=" * 60)
    
    # Check each year directory
    for year in ['2017', '2018', '2019', '2020', '2021', '2022', '2023']:
        year_path = os.path.join(base_path, year)
        if not os.path.exists(year_path):
            continue
            
        print(f"\nProcessing year {year}...")
        
        # Find all CSV files in the year directory
        csv_files = glob.glob(os.path.join(year_path, '*.csv'))
        
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            
            try:
                # Read just the header to get column names
                df = pd.read_csv(file_path, nrows=0)
                columns = list(df.columns)
                
                # Store file info
                file_patterns[filename]['files'].append({
                    'year': year,
                    'path': file_path,
                    'columns': columns,
                    'first_two': columns[:2] if len(columns) >= 2 else [],
                    'total_count': len(columns)
                })
                
                # Store patterns
                if len(columns) >= 2:
                    file_patterns[filename]['first_two_columns'].add(tuple(columns[:2]))
                
                file_patterns[filename]['total_columns'].add(len(columns))
                
                # Check column numbering range
                numeric_cols = []
                for col in columns[2:]:  # Skip first two columns
                    try:
                        numeric_cols.append(int(col))
                    except ValueError:
                        pass
                
                if numeric_cols:
                    col_range = f"{min(numeric_cols)}-{max(numeric_cols)}"
                    file_patterns[filename]['column_ranges'].add(col_range)
                
            except Exception as e:
                print(f"    ERROR reading {filename}: {e}")
    
    # Analyze patterns by file naming structure
    print("\n" + "=" * 60)
    print("FILE NAMING PATTERN ANALYSIS")
    print("=" * 60)
    
    # Group files by naming pattern
    pattern_groups = defaultdict(list)
    
    for filename, data in file_patterns.items():
        # Extract pattern components
        parts = filename.replace('.csv', '').split('_')
        
        if len(parts) >= 8:
            # NBT + year + day + od + mode/network + time + wf + o
            pattern_key = f"{parts[0]}_{parts[1]}_{parts[2]}_{parts[3]}_{parts[4]}_{parts[5]}_{parts[6]}_{parts[7]}"
            pattern_groups[pattern_key].append(filename)
        elif len(parts) >= 6:
            # For files with different structure (like 2019 and 2022)
            pattern_key = f"{parts[0]}_{parts[1]}_{parts[2]}_{parts[3]}_{parts[4]}_{parts[5]}"
            pattern_groups[pattern_key].append(filename)
    
    print("\nFile naming patterns found:")
    for pattern, files in pattern_groups.items():
        print(f"\nPattern: {pattern}")
        print(f"  Files: {len(files)}")
        
        # Check consistency within pattern
        first_two_cols = set()
        column_ranges = set()
        total_cols = set()
        
        for filename in files:
            data = file_patterns[filename]
            first_two_cols.update(data['first_two_columns'])
            column_ranges.update(data['column_ranges'])
            total_cols.update(data['total_columns'])
        
        print(f"  First two columns: {list(first_two_cols)}")
        print(f"  Column ranges: {list(column_ranges)}")
        print(f"  Total columns: {list(total_cols)}")
        
        # Show sample files
        print(f"  Sample files: {files[:3]}")
    
    # Analyze by year and mode/network
    print("\n" + "-" * 60)
    print("ANALYSIS BY YEAR AND MODE/NETWORK")
    print("-" * 60)
    
    year_mode_patterns = defaultdict(lambda: {
        'files': [],
        'first_two_columns': set(),
        'column_ranges': set(),
        'total_columns': set()
    })
    
    for filename, data in file_patterns.items():
        parts = filename.replace('.csv', '').split('_')
        if len(parts) >= 5:
            year = parts[1]
            mode_network = parts[4]  # mode_XXX or network
            key = f"{year}_{mode_network}"
            
            year_mode_patterns[key]['files'].append(filename)
            year_mode_patterns[key]['first_two_columns'].update(data['first_two_columns'])
            year_mode_patterns[key]['column_ranges'].update(data['column_ranges'])
            year_mode_patterns[key]['total_columns'].update(data['total_columns'])
    
    for key, data in sorted(year_mode_patterns.items()):
        print(f"\n{key}:")
        print(f"  Files: {len(data['files'])}")
        print(f"  First two columns: {list(data['first_two_columns'])}")
        print(f"  Column ranges: {list(data['column_ranges'])}")
        print(f"  Total columns: {list(data['total_columns'])}")
    
    return file_patterns, pattern_groups, year_mode_patterns

if __name__ == "__main__":
    file_patterns, pattern_groups, year_mode_patterns = analyze_numbat_patterns()
