import os
import pandas as pd
import glob
from collections import defaultdict, Counter

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

def main():
    # Base directory for NUMBAT OD matrices
    base_dir = "Data/NUMBAT/OD_Matrices"
    
    # Dictionary to store NLC codes for each file
    file_nlc_codes = {}
    all_nlc_codes = set()
    
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
                all_nlc_codes.update(nlc_codes)
    
    # Print total number of unique NLC codes across all files
    print(f"\nTotal number of unique NLC codes across all files: {len(all_nlc_codes)}")
    
    # Save all unique NLC codes to CSV
    output_file = "Data/all_unique_NUMBAT_OD_nlc_codes.csv"
    nlc_df = pd.DataFrame(sorted(all_nlc_codes), columns=['NLC_Code'])
    nlc_df.to_csv(output_file, index=False)
    print(f"All unique NLC codes saved to: {output_file}")
    
    # Find files with unique NLC codes not found in other files
    files_with_unique_nlcs = {}
    
    for filename, nlc_codes in file_nlc_codes.items():
        # Find NLC codes that are unique to this file
        unique_to_file = set()
        for nlc in nlc_codes:
            # Check if this NLC code appears in any other file
            appears_in_other_files = False
            for other_filename, other_nlcs in file_nlc_codes.items():
                if other_filename != filename and nlc in other_nlcs:
                    appears_in_other_files = True
                    break
            
            if not appears_in_other_files:
                unique_to_file.add(nlc)
        
        if unique_to_file:
            files_with_unique_nlcs[filename] = len(unique_to_file)
    
    # Print results
    if files_with_unique_nlcs:
        print("\nFiles with NLC codes not found in any other files:")
        print("=" * 60)
        print(f"{'Filename':<50} {'Unique NLCs':<10}")
        print("-" * 60)
        
        for filename, count in sorted(files_with_unique_nlcs.items(), key=lambda x: x[1], reverse=True):
            print(f"{filename:<50} {count:<10}")
    else:
        print("\nNo files found with unique NLC codes.")

if __name__ == "__main__":
    main()
