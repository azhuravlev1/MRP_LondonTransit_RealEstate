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

def check_original_mapping():
    """Check if the NLC codes appear in the original station_NLC_mapping_2019.csv"""
    print("=== Checking Original NLC Mapping ===")
    try:
        file_path = get_data_path('Data/station_NLC_mapping_2019.csv')
        df = pd.read_csv(file_path)
        nlc_codes = set(df['NLC'].dropna().astype(str))
        
        target_codes = ['6070', '6073', '8204']
        for code in target_codes:
            if code in nlc_codes:
                station_name = df[df['NLC'].astype(str) == code]['Station'].iloc[0]
                print(f"NLC {code}: {station_name} - FOUND in original mapping")
            else:
                print(f"NLC {code}: NOT FOUND in original mapping")
    except Exception as e:
        print(f"Error checking original mapping: {e}")

def check_comprehensive_mapping():
    """Check if the NLC codes appear in the comprehensive mapping"""
    print("\n=== Checking Comprehensive NLC Mapping ===")
    try:
        file_path = get_data_path('Data/comprehensive_station_nlc_mapping.csv')
        df = pd.read_csv(file_path)
        nlc_codes = set(df['NLC'].dropna().astype(str))
        
        target_codes = ['6070', '6073', '8204']
        for code in target_codes:
            if code in nlc_codes:
                station_name = df[df['NLC'].astype(str) == code]['Station'].iloc[0]
                print(f"NLC {code}: {station_name} - FOUND in comprehensive mapping")
            else:
                print(f"NLC {code}: NOT FOUND in comprehensive mapping")
    except Exception as e:
        print(f"Error checking comprehensive mapping: {e}")

def check_numbat_2022_data():
    """Check the NUMBAT 2022 data for these specific codes"""
    print("\n=== Checking NUMBAT 2022 Data ===")
    try:
        file_path = get_data_path('Data/NUMBAT/OD_Matrices/2022/NBT22TWT5d_od_network_qhr_wf_o.csv')
        df = pd.read_csv(file_path)
        
        target_codes = ['6070', '6073', '8204']
        
        print(f"Total rows in NUMBAT 2022: {len(df)}")
        print(f"Unique origin NLCs: {len(df['mnlc_o'].unique())}")
        print(f"Unique destination NLCs: {len(df['mnlc_d'].unique())}")
        
        # Get column names for flow data
        flow_columns = [col for col in df.columns if col not in ['mnlc_o', 'mnlc_d']]
        print(f"Flow columns (time periods): {len(flow_columns)}")
        print(f"Time range: {flow_columns[0]} to {flow_columns[-1]}")
        
        for code in target_codes:
            origin_count = len(df[df['mnlc_o'].astype(str) == code])
            dest_count = len(df[df['mnlc_d'].astype(str) == code])
            print(f"\nNLC {code}:")
            print(f"  - Appears as origin: {origin_count} times")
            print(f"  - Appears as destination: {dest_count} times")
            
            if origin_count > 0:
                sample_origins = df[df['mnlc_o'].astype(str) == code].head(3)
                print(f"  - Sample origin rows:")
                for _, row in sample_origins.iterrows():
                    # Calculate total flow across all time periods
                    total_flow = sum(row[flow_columns])
                    print(f"    Origin: {row['mnlc_o']}, Dest: {row['mnlc_d']}, Total Flow: {total_flow:.4f}")
            
            if dest_count > 0:
                sample_dests = df[df['mnlc_d'].astype(str) == code].head(3)
                print(f"  - Sample destination rows:")
                for _, row in sample_dests.iterrows():
                    # Calculate total flow across all time periods
                    total_flow = sum(row[flow_columns])
                    print(f"    Origin: {row['mnlc_o']}, Dest: {row['mnlc_d']}, Total Flow: {total_flow:.4f}")
                    
    except Exception as e:
        print(f"Error checking NUMBAT 2022 data: {e}")

def check_numbat_2019_data():
    """Check if these codes appear in NUMBAT 2019 data"""
    print("\n=== Checking NUMBAT 2019 Data ===")
    try:
        file_path = get_data_path('Data/NUMBAT/OD_Matrices/2019/NBT19MTT2a_od__network_qhr_wf.csv')
        df = pd.read_csv(file_path)
        
        target_codes = ['6070', '6073', '8204']
        
        for code in target_codes:
            origin_count = len(df[df['mnlc_o'].astype(str) == code])
            dest_count = len(df[df['mnlc_d'].astype(str) == code])
            print(f"NLC {code}: Origin={origin_count}, Destination={dest_count}")
            
    except Exception as e:
        print(f"Error checking NUMBAT 2019 data: {e}")

def check_od_matrix_files():
    """Check if these codes appear in any OD matrix files"""
    print("\n=== Checking OD Matrix Files ===")
    try:
        # Check RODS_OD files
        rods_od_path = get_data_path('Data/RODS_OD/')
        if os.path.exists(rods_od_path):
            for file_path in glob.glob(os.path.join(rods_od_path, 'ODmatrix_*.xls')):
                try:
                    year = file_path.split('_')[-1].replace('.xls', '')
                    df = pd.read_excel(file_path, sheet_name='matrix')
                    
                    # Get station names from columns 2 and 4, starting from row 5
                    origin_stations = set(df.iloc[4:, 1].dropna().str.strip().unique())
                    dest_stations = set(df.iloc[4:, 3].dropna().str.strip().unique())
                    all_stations = origin_stations.union(dest_stations)
                    
                    # Check if any station names might correspond to our NLC codes
                    # This is a bit of a stretch, but worth checking
                    target_codes = ['6070', '6073', '8204']
                    for code in target_codes:
                        # Look for any station that might contain this number
                        matching_stations = [s for s in all_stations if code in str(s)]
                        if matching_stations:
                            print(f"Year {year}, NLC {code}: Found potential matches: {matching_stations}")
                            
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
    except Exception as e:
        print(f"Error checking OD matrix files: {e}")

def analyze_nlc_code_patterns():
    """Analyze patterns in NLC codes to understand what these might be"""
    print("\n=== Analyzing NLC Code Patterns ===")
    
    target_codes = ['6070', '6073', '8204']
    
    # Load comprehensive mapping to see patterns
    try:
        file_path = get_data_path('Data/comprehensive_station_nlc_mapping.csv')
        df = pd.read_csv(file_path)
        
        print("NLC code ranges in comprehensive mapping:")
        nlc_codes = df['NLC'].dropna().astype(int).sort_values()
        print(f"Min NLC: {nlc_codes.min()}")
        print(f"Max NLC: {nlc_codes.max()}")
        
        # Check what's around our target codes
        for code in target_codes:
            code_int = int(code)
            nearby_codes = nlc_codes[(nlc_codes >= code_int - 10) & (nlc_codes <= code_int + 10)]
            print(f"\nNLC {code} - nearby codes in mapping:")
            for nearby in nearby_codes:
                station = df[df['NLC'] == nearby]['Station'].iloc[0]
                print(f"  {nearby}: {station}")
                
    except Exception as e:
        print(f"Error analyzing patterns: {e}")

def analyze_connections():
    """Analyze the most common connections for these NLC codes"""
    print("\n=== Analyzing Connections for Target NLC Codes ===")
    try:
        file_path = get_data_path('Data/NUMBAT/OD_Matrices/2022/NBT22TWT5d_od_network_qhr_wf_o.csv')
        df = pd.read_csv(file_path)
        
        # Get flow columns
        flow_columns = [col for col in df.columns if col not in ['mnlc_o', 'mnlc_d']]
        
        target_codes = ['6070', '6073', '8204']
        
        for code in target_codes:
            print(f"\nNLC {code} - Top 10 destinations (when used as origin):")
            
            # Filter for this code as origin
            origin_data = df[df['mnlc_o'].astype(str) == code].copy()
            if len(origin_data) > 0:
                # Calculate total flow for each destination
                origin_data['total_flow'] = origin_data[flow_columns].sum(axis=1)
                top_destinations = origin_data.nlargest(10, 'total_flow')[['mnlc_d', 'total_flow']]
                
                for _, row in top_destinations.iterrows():
                    print(f"  -> NLC {row['mnlc_d']}: {row['total_flow']:.4f}")
            
            print(f"\nNLC {code} - Top 10 origins (when used as destination):")
            
            # Filter for this code as destination
            dest_data = df[df['mnlc_d'].astype(str) == code].copy()
            if len(dest_data) > 0:
                # Calculate total flow for each origin
                dest_data['total_flow'] = dest_data[flow_columns].sum(axis=1)
                top_origins = dest_data.nlargest(10, 'total_flow')[['mnlc_o', 'total_flow']]
                
                for _, row in top_origins.iterrows():
                    print(f"  NLC {row['mnlc_o']} ->: {row['total_flow']:.4f}")
                    
    except Exception as e:
        print(f"Error analyzing connections: {e}")

def main():
    """Main function to run all investigations"""
    print("Investigating NLC codes: 6070, 6073, 8204")
    print("=" * 50)
    
    check_original_mapping()
    check_comprehensive_mapping()
    check_numbat_2022_data()
    check_numbat_2019_data()
    check_od_matrix_files()
    analyze_nlc_code_patterns()
    analyze_connections()
    
    print("\n" + "=" * 50)
    print("Investigation complete!")

if __name__ == "__main__":
    main() 