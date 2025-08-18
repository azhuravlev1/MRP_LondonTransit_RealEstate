import pandas as pd
import os

def get_data_path(relative_path):
    """Get the correct path to data files"""
    if os.path.exists(relative_path):
        return relative_path
    elif os.path.exists(os.path.join('..', relative_path)):
        return os.path.join('..', relative_path)
    else:
        raise FileNotFoundError(f"Could not find {relative_path}")

def load_data():
    """Load the input CSV files into pandas DataFrames"""
    print("Loading input files...")
    
    # Load primary input file
    primary_file = get_data_path('Data/comprehensive_station_nlc_mapping_no_tramlink.csv')
    primary_df = pd.read_csv(primary_file)
    print(f"Loaded {len(primary_df)} stations from comprehensive_station_nlc_mapping_no_tramlink.csv")
    
    # Load lookup input file
    lookup_file = get_data_path('Data/Station_Borough_Mappings/Standardized/all_stations_by_borough_standardized.csv')
    lookup_df = pd.read_csv(lookup_file)
    print(f"Loaded {len(lookup_df)} stations from all_stations_by_borough_standardized.csv")
    
    return primary_df, lookup_df

def initialize_borough_column(primary_df):
    """Initialize the Borough column as empty for all rows"""
    print("Initializing Borough column...")
    primary_df['Borough'] = ''
    return primary_df

def step1_perfect_match(primary_df, lookup_df):
    """Step 1: Perfect Match - Direct merge based on exact Station Name match"""
    print("\nStep 1: Performing perfect match...")
    
    # Create a mapping dictionary from lookup_df
    station_borough_map = dict(zip(lookup_df['station_name'], lookup_df['borough_standardized']))
    
    # Apply perfect matches
    initial_unmapped = primary_df['Borough'].isna() | (primary_df['Borough'] == '')
    perfect_matches = 0
    
    for idx in primary_df[initial_unmapped].index:
        station_name = primary_df.loc[idx, 'Station']
        if station_name in station_borough_map:
            primary_df.loc[idx, 'Borough'] = station_borough_map[station_name]
            perfect_matches += 1
    
    print(f"Perfect matches found: {perfect_matches}")
    return primary_df

def step2_suffix_stripping_match(primary_df, lookup_df):
    """Step 2: Suffix-Stripping Match - Remove common service-related suffixes"""
    print("\nStep 2: Performing suffix-stripping match...")
    
    # Define suffixes to strip
    suffixes = [' LU', ' LO', ' EL', ' DLR', ' NR', ' TfL', ' (DIS)', ' (Cen)']
    
    # Create a mapping dictionary from lookup_df
    station_borough_map = dict(zip(lookup_df['station_name'], lookup_df['borough_standardized']))
    
    # Find unmapped stations
    unmapped_mask = primary_df['Borough'].isna() | (primary_df['Borough'] == '')
    suffix_matches = 0
    
    for idx in primary_df[unmapped_mask].index:
        station_name = primary_df.loc[idx, 'Station']
        
        # Try stripping each suffix
        for suffix in suffixes:
            if station_name.endswith(suffix):
                base_name = station_name[:-len(suffix)]
                if base_name in station_borough_map:
                    primary_df.loc[idx, 'Borough'] = station_borough_map[base_name]
                    suffix_matches += 1
                    break
    
    print(f"Suffix-stripping matches found: {suffix_matches}")
    return primary_df

def step3_manual_alias_match(primary_df):
    """Step 3: Manual Alias Match - Use predefined dictionary for known inconsistencies"""
    print("\nStep 3: Performing manual alias match...")
    
    # Define alias mapping
    alias_map = {
        'Bank and Monument': 'Bank / Monument',
        'Cutty Sark': 'Cutty Sark for Maritime Greenwich',
        'Shepherd\'s Bush LU': 'Shepherd\'s Bush (Cen)',
        'Shepherd\'s Bush NR': 'Shepherd\'s Bush (Ovr)',
        'Victoria LU': 'Victoria',
        'Royal Victoria': 'Royal Victoria (from IFS Cloud Royal Docks)',
        'West India Quay': 'West India Quay (from Canary Wharf)',
        'Woolwich EL': 'Woolwich',
        'Woolwich Arsenal': 'Woolwich Arsenal (from Woolwich)'
    }
    
    # Load lookup data for borough assignment
    lookup_file = get_data_path('Data/Station_Borough_Mappings/Standardized/all_stations_by_borough_standardized.csv')
    lookup_df = pd.read_csv(lookup_file)
    station_borough_map = dict(zip(lookup_df['station_name'], lookup_df['borough_standardized']))
    
    # Find unmapped stations
    unmapped_mask = primary_df['Borough'].isna() | (primary_df['Borough'] == '')
    alias_matches = 0
    
    for idx in primary_df[unmapped_mask].index:
        station_name = primary_df.loc[idx, 'Station']
        
        if station_name in alias_map:
            alias_name = alias_map[station_name]
            if alias_name in station_borough_map:
                primary_df.loc[idx, 'Borough'] = station_borough_map[alias_name]
                alias_matches += 1
    
    print(f"Manual alias matches found: {alias_matches}")
    return primary_df

def step4_manual_override(primary_df):
    """Step 4: Manual Override - Apply manual corrections for specific station-borough mappings"""
    print("\nStep 4: Performing manual override...")
    
    # Define manual override mapping
    manual_override_map = {
        'Battersea Power Station': 'Wandsworth',
        'Bow Church': 'Tower Hamlets',
        'Edgware Road (DIS)': 'Westminster',
        'Hammersmith (DIS)': 'Hammersmith & Fulham',
        'Heron Quays': 'Tower Hamlets',
        'Poplar': 'Tower Hamlets',
        'Royal Victoria': 'Newham',
        'St James Street': 'Waltham Forest',
        'Tower Gateway': 'Tower Hamlets',
        'West India Quay': 'Tower Hamlets',
        'Woolwich Arsenal': 'Greenwich'
    }
    
    # Apply manual overrides
    manual_override_matches = 0
    
    for idx in primary_df.index:
        station_name = primary_df.loc[idx, 'Station']
        
        if station_name in manual_override_map:
            primary_df.loc[idx, 'Borough'] = manual_override_map[station_name]
            manual_override_matches += 1
    
    print(f"Manual override assignments: {manual_override_matches}")
    return primary_df

def step5_out_of_london_assignment(primary_df):
    """Step 5: Out of London Assignment - Assign 'Out of London' to stations outside Greater London"""
    print("\nStep 5: Performing out of London assignment...")
    
    # Define out of London stations
    out_of_london_stations = [
        'Amersham', 'Buckhurst Hill', 'Chalfont & Latimer', 'Chesham',
        'Chigwell', 'Chorleywood', 'Croxley', 'Debden', 'Epping',
        'Grange Hill', 'Loughton', 'Moor Park', 'Rickmansworth',
        'Roding Valley', 'Theydon Bois', 'Watford'
    ]
    
    # Find unmapped stations
    unmapped_mask = primary_df['Borough'].isna() | (primary_df['Borough'] == '')
    out_of_london_matches = 0
    
    for idx in primary_df[unmapped_mask].index:
        station_name = primary_df.loc[idx, 'Station']
        
        if station_name in out_of_london_stations:
            primary_df.loc[idx, 'Borough'] = 'Out of London'
            out_of_london_matches += 1
    
    print(f"Out of London assignments: {out_of_london_matches}")
    return primary_df

def generate_report(primary_df):
    """Generate and print a summary report"""
    print("\n" + "="*80)
    print("MAPPING SUMMARY REPORT")
    print("="*80)
    
    total_stations = len(primary_df)
    mapped_stations = len(primary_df[primary_df['Borough'] != ''])
    unmapped_stations = total_stations - mapped_stations
    
    print(f"Total number of stations in dataset: {total_stations}")
    print(f"Number of stations successfully mapped: {mapped_stations}")
    print(f"Number of stations remaining unmapped: {unmapped_stations}")
    print(f"Mapping success rate: {mapped_stations/total_stations*100:.1f}%")
    
    if unmapped_stations > 0:
        print(f"\nUnmapped stations:")
        unmapped_df = primary_df[primary_df['Borough'] == '']
        for _, row in unmapped_df.iterrows():
            print(f"  - {row['Station']} (NLC: {row['NLC']})")
    
    # Borough distribution
    print(f"\nBorough distribution:")
    borough_counts = primary_df[primary_df['Borough'] != '']['Borough'].value_counts().sort_index()
    for borough, count in borough_counts.items():
        print(f"  {borough}: {count} stations")

def save_output(primary_df):
    """Save the final DataFrame to CSV"""
    print("\nSaving output file...")
    
    output_file = 'station_borough_nlc_mapping.csv'
    primary_df.to_csv(output_file, index=False)
    print(f"Output saved to: {output_file}")
    
    # Verify the output
    print(f"Output file contains {len(primary_df)} rows with columns: {list(primary_df.columns)}")

def main():
    """Main function to execute the mapping process"""
    print("Starting station borough NLC mapping process...")
    print("="*80)
    
    try:
        # Step 1: Setup and Initialization
        primary_df, lookup_df = load_data()
        primary_df = initialize_borough_column(primary_df)
        
        # Step 2: Perfect Match
        primary_df = step1_perfect_match(primary_df, lookup_df)
        
        # Step 3: Suffix-Stripping Match
        primary_df = step2_suffix_stripping_match(primary_df, lookup_df)
        
        # Step 4: Manual Alias Match
        primary_df = step3_manual_alias_match(primary_df)
        
        # Step 5: Manual Override
        primary_df = step4_manual_override(primary_df)
        
        # Step 6: Out of London Assignment
        primary_df = step5_out_of_london_assignment(primary_df)
        
        # Step 6: Reporting and Finalization
        generate_report(primary_df)
        save_output(primary_df)
        
        print("\n" + "="*80)
        print("MAPPING PROCESS COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"Error during mapping process: {e}")
        raise

if __name__ == "__main__":
    main()
