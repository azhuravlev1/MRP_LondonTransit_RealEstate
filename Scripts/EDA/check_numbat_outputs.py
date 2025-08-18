import pandas as pd
import os
import glob

def get_data_path(relative_path):
    """Get the correct path to data files"""
    if os.path.exists(relative_path):
        return relative_path
    elif os.path.exists(os.path.join('..', relative_path)):
        return os.path.join('..', relative_path)
    else:
        raise FileNotFoundError(f"Could not find {relative_path}")

def check_numbat_2022_outputs():
    """Check if the missing NLC codes are in NUMBAT 2022 output files"""
    print("=== Checking NUMBAT 2022 Output Files ===")
    
    target_codes = ['6070', '6073', '8204']
    
    # Get all 2022 output files
    outputs_path = get_data_path('Data/NUMBAT/Outputs/')
    numbat_2022_files = glob.glob(os.path.join(outputs_path, 'NBT22*_Outputs.xlsx'))
    
    print(f"Found {len(numbat_2022_files)} NUMBAT 2022 output files:")
    for file in numbat_2022_files:
        print(f"  - {os.path.basename(file)}")
    
    all_nlcs_from_outputs = set()
    
    for file_path in numbat_2022_files:
        print(f"\n--- Checking {os.path.basename(file_path)} ---")
        try:
            # Read the Station_Entries sheet
            df = pd.read_excel(file_path, sheet_name='Station_Entries')
            print(f"  Columns: {list(df.columns)}")
            print(f"  Shape: {df.shape}")
            
            # Check if we have the expected columns
            if len(df.columns) >= 3:
                nlc_col = df.columns[0]  # First column
                station_col = df.columns[2]  # Third column
                
                print(f"  NLC column: {nlc_col}")
                print(f"  Station column: {station_col}")
                
                # Get unique NLCs
                nlcs = set(df[nlc_col].dropna().astype(str))
                all_nlcs_from_outputs.update(nlcs)
                
                print(f"  Total unique NLCs: {len(nlcs)}")
                
                # Check for our target codes
                for code in target_codes:
                    if code in nlcs:
                        station_name = df[df[nlc_col].astype(str) == code][station_col].iloc[0]
                        print(f"  NLC {code}: {station_name} - FOUND!")
                    else:
                        print(f"  NLC {code}: NOT FOUND")
            else:
                print(f"  Warning: Only {len(df.columns)} columns found, expected at least 3")
                
        except Exception as e:
            print(f"  Error reading file: {e}")
    
    print(f"\n=== Summary ===")
    print(f"Total unique NLCs across all 2022 output files: {len(all_nlcs_from_outputs)}")
    
    # Check if our target codes are in the combined set
    for code in target_codes:
        if code in all_nlcs_from_outputs:
            print(f"NLC {code}: FOUND in 2022 outputs")
        else:
            print(f"NLC {code}: NOT FOUND in 2022 outputs")
    
    # Let's also check what NLCs are in the comprehensive mapping
    print(f"\n=== Checking Comprehensive Mapping ===")
    try:
        comp_file = get_data_path('Data/comprehensive_station_nlc_mapping.csv')
        comp_df = pd.read_csv(comp_file)
        comp_nlcs = set(comp_df['NLC'].dropna().astype(str))
        print(f"Total NLCs in comprehensive mapping: {len(comp_nlcs)}")
        
        for code in target_codes:
            if code in comp_nlcs:
                station_name = comp_df[comp_df['NLC'].astype(str) == code]['Station'].iloc[0]
                print(f"NLC {code}: {station_name} - FOUND in comprehensive mapping")
            else:
                print(f"NLC {code}: NOT FOUND in comprehensive mapping")
                
    except Exception as e:
        print(f"Error checking comprehensive mapping: {e}")

if __name__ == "__main__":
    check_numbat_2022_outputs() 