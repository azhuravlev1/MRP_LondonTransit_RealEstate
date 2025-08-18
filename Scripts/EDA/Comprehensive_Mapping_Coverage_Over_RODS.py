import pandas as pd
import os
from pathlib import Path
import glob

def extract_nlc_codes_and_names_from_rods_files(data_dir):
    """
    Extract unique NLC codes and their corresponding station names from all RODS OD matrix files.
    Reads from both the 1st and 3rd columns starting from row 5, with names in 2nd and 4th columns.
    """
    nlc_name_pairs = {}  # Dictionary to store NLC code -> station name mapping
    
    # Define the paths for both RODS directories
    rods_paths = [
        os.path.join(data_dir, "RODS_OD"),
        os.path.join(data_dir, "RODS_OD", "Rods_OD_2000-2002")
    ]
    
    for rods_path in rods_paths:
        if os.path.exists(rods_path):
            # Find all .xls files in the directory
            xls_files = glob.glob(os.path.join(rods_path, "*.xls"))
            
            for file_path in xls_files:
                print(f"Processing: {os.path.basename(file_path)}")
                
                try:
                    # Read the matrix sheet, skip first 4 rows (2 info rows + 2 header rows)
                    # Start reading from row 5 (index 4)
                    df = pd.read_excel(file_path, sheet_name="matrix", skiprows=4)
                    
                    # Extract NLC codes and names from 1st/2nd and 3rd/4th columns
                    if len(df.columns) >= 4:
                        # Clean up NLC codes: remove .0 suffix and convert to proper format
                        def clean_nlc_code(code):
                            # Remove .0 suffix if present
                            if code.endswith('.0'):
                                return code[:-2]
                            return code
                        
                        # Validate NLC codes: must be entirely numeric
                        def is_valid_nlc(code):
                            cleaned = clean_nlc_code(code)
                            # Check if the cleaned code consists only of digits
                            return cleaned.isdigit()
                        
                        # Process pairs from columns 1&2 (NLC codes and station names)
                        for idx, (nlc, name) in enumerate(zip(df.iloc[:, 0], df.iloc[:, 1])):
                            if pd.notna(nlc) and pd.notna(name):
                                nlc_str = str(nlc)
                                if is_valid_nlc(nlc_str):
                                    cleaned_nlc = clean_nlc_code(nlc_str)
                                    nlc_name_pairs[cleaned_nlc] = str(name).strip()
                        
                        # Process pairs from columns 3&4 (NLC codes and station names)
                        for idx, (nlc, name) in enumerate(zip(df.iloc[:, 2], df.iloc[:, 3])):
                            if pd.notna(nlc) and pd.notna(name):
                                nlc_str = str(nlc)
                                if is_valid_nlc(nlc_str):
                                    cleaned_nlc = clean_nlc_code(nlc_str)
                                    nlc_name_pairs[cleaned_nlc] = str(name).strip()
                        
                        print(f"  - Processed columns 1-2 and 3-4 for NLC-name pairs")
                    else:
                        print(f"  - Warning: File has fewer than 4 columns")
                        
                except Exception as e:
                    print(f"  - Error processing {file_path}: {str(e)}")
    
    return nlc_name_pairs

def load_comprehensive_mapping(data_dir):
    """
    Load the comprehensive station NLC mapping file.
    """
    mapping_file = os.path.join(data_dir, "comprehensive_station_nlc_mapping.csv")
    
    if not os.path.exists(mapping_file):
        print(f"Warning: Comprehensive mapping file not found at {mapping_file}")
        return set()
    
    try:
        # Read the mapping file, NLC codes are in the first column
        df = pd.read_csv(mapping_file)
        if len(df.columns) > 0:
            # Get NLC codes from first column and clean them
            raw_nlcs = df.iloc[:, 0].dropna().astype(str)
            
            # Clean up NLC codes: remove .0 suffix if present
            def clean_nlc_code(code):
                if code.endswith('.0'):
                    return code[:-2]
                return code
            
            # Validate NLC codes: must be entirely numeric
            def is_valid_nlc(code):
                cleaned = clean_nlc_code(code)
                # Check if the cleaned code consists only of digits
                return cleaned.isdigit()
            
            # Clean and validate NLC codes
            mapping_nlcs = set([clean_nlc_code(code) for code in raw_nlcs if is_valid_nlc(code)])
            print(f"Loaded {len(mapping_nlcs)} NLC codes from comprehensive mapping")
            return mapping_nlcs
        else:
            print("Warning: Comprehensive mapping file appears to be empty")
            return set()
    except Exception as e:
        print(f"Error loading comprehensive mapping: {str(e)}")
        return set()

def find_missing_nlcs(rods_nlcs, mapping_nlcs):
    """
    Find RODS NLC codes that are not in the comprehensive mapping.
    """
    return rods_nlcs - mapping_nlcs

def main():
    # Set up paths
    data_dir = "/Users/andrey/Desktop/TMU/MRP/Code/Data"
    
    print("=== RODS NLC Code Analysis ===\n")
    
    # Extract unique NLC codes and names from RODS files
    print("1. Extracting NLC codes and station names from RODS files...")
    rods_nlc_name_pairs = extract_nlc_codes_and_names_from_rods_files(data_dir)
    rods_nlcs = set(rods_nlc_name_pairs.keys())
    print(f"\nTotal unique NLC codes found in RODS files: {len(rods_nlcs)}")
    
    # Load comprehensive mapping
    print("\n2. Loading comprehensive station mapping...")
    mapping_nlcs = load_comprehensive_mapping(data_dir)
    
    # Find missing NLC codes
    print("\n3. Comparing RODS codes with comprehensive mapping...")
    missing_nlcs = find_missing_nlcs(rods_nlcs, mapping_nlcs)
    print(f"RODS NLC codes not found in comprehensive mapping: {len(missing_nlcs)}")
    
    # Save results
    print("\n4. Saving results...")
    
    # Save all unique RODS NLC codes with their station names
    rods_output_file = os.path.join(data_dir, "all_unique_NUMBAT_OD_nlc_codes.csv")
    rods_data = [(nlc, rods_nlc_name_pairs[nlc]) for nlc in sorted(rods_nlcs)]
    rods_df = pd.DataFrame(rods_data, columns=['NLC_Code', 'Station_Name'])
    rods_df.to_csv(rods_output_file, index=False)
    print(f"Saved {len(rods_nlcs)} unique RODS NLC codes with station names to: {rods_output_file}")
    
    # Save missing NLC codes with their station names
    if missing_nlcs:
        missing_output_file = os.path.join(data_dir, "RODS_missing_NLCs.csv")
        missing_data = [(nlc, rods_nlc_name_pairs[nlc]) for nlc in sorted(missing_nlcs)]
        missing_df = pd.DataFrame(missing_data, columns=['NLC_Code', 'Station_Name'])
        missing_df.to_csv(missing_output_file, index=False)
        print(f"Saved {len(missing_nlcs)} missing NLC codes with station names to: {missing_output_file}")
        
        # Print first 20 missing codes as examples
        print(f"\nFirst 20 missing NLC codes with station names:")
        for i, nlc in enumerate(sorted(list(missing_nlcs))[:20]):
            station_name = rods_nlc_name_pairs.get(nlc, "Unknown")
            print(f"  {i+1:2d}. {nlc} - {station_name}")
        if len(missing_nlcs) > 20:
            print(f"  ... and {len(missing_nlcs) - 20} more")
    else:
        print("All RODS NLC codes are found in the comprehensive mapping!")
    
    # Summary statistics
    print(f"\n=== Summary ===")
    print(f"Total unique RODS NLC codes: {len(rods_nlcs)}")
    print(f"Total comprehensive mapping NLC codes: {len(mapping_nlcs)}")
    print(f"RODS codes missing from mapping: {len(missing_nlcs)}")
    print(f"Coverage: {((len(rods_nlcs) - len(missing_nlcs)) / len(rods_nlcs) * 100):.1f}%")

if __name__ == "__main__":
    main()
