import pandas as pd
import os
import re

def get_data_path(relative_path):
    """Get the correct path to data files, whether running from EDA/ or project root"""
    # Try relative to current directory first
    if os.path.exists(relative_path):
        return relative_path
    # If not found, try going up one level (if running from EDA/)
    elif os.path.exists(os.path.join('..', relative_path)):
        return os.path.join('..', relative_path)
    else:
        raise FileNotFoundError(f"Could not find {relative_path}")

def load_house_price_boroughs():
    """Load borough names from UK_House_price_index.xlsx"""
    try:
        file_path = get_data_path('Data/UK_House_price_index.xlsx')
        # Read the third sheet (Average Price)
        df = pd.read_excel(file_path, sheet_name=2)
        # Get borough names from column headers (row 0), columns B to AH
        borough_names = df.columns[1:34].tolist()  # B to AH is columns 1-33 (0-indexed)
        return set(borough_names)
    except Exception as e:
        print(f"Error loading house price data: {e}")
        return set()

def create_standardization_mapping():
    """Create mapping for standardizing borough names"""
    
    # Define compound borough name mappings to primary administrative boroughs
    compound_to_primary = {
        'Tower Hamlets & Hackney': 'Tower Hamlets',
        'Bexley & Royal Borough of Greenwich': 'Greenwich',
        'Armada Riverside': 'Tower Hamlets',  # Based on location
        'Thameside West': 'Tower Hamlets',    # Based on location
        'Thamesmead Central': 'Greenwich'     # Based on location
    }
    
    # Define out-of-London locations that should be categorized as "Out of London"
    out_of_london_locations = {
        # Elizabeth Line stations outside London
        'Reading': 'Out of London',
        'Slough': 'Out of London', 
        'Maidenhead': 'Out of London',
        'Twyford': 'Out of London',
        'Burnham': 'Out of London',
        'Taplow': 'Out of London',
        'Iver': 'Out of London',
        'Langley': 'Out of London',
        'Borough of Brentwood': 'Out of London',
        'Buckinghamshire': 'Out of London',
        
        # London Overground stations outside London
        'Borough of Watford': 'Out of London',
        'Borough of Broxbourne': 'Out of London',
        'District of Three Rivers': 'Out of London',
        
        # Other non-London locations
        'Unknown': 'Out of London'  # Categorize unknown locations as out of London
    }
    
    return compound_to_primary, out_of_london_locations

def standardize_borough_name(borough_name, compound_mapping, out_of_london_mapping):
    """Standardize a borough name according to the mapping rules"""
    
    # First check if it's an out-of-London location
    if borough_name in out_of_london_mapping:
        return out_of_london_mapping[borough_name]
    
    # Then check if it's a compound borough name
    if borough_name in compound_mapping:
        return compound_mapping[borough_name]
    
    # If it's already a standard London borough name, return as is
    return borough_name

def process_station_borough_file(input_file, output_file, compound_mapping, out_of_london_mapping):
    """Process a single station-borough mapping file"""
    
    print(f"Processing {input_file}...")
    
    # Load the data
    df = pd.read_csv(input_file)
    
    # Create a copy for the standardized version
    df_standardized = df.copy()
    
    # Apply standardization
    try:
        df_standardized['borough_standardized'] = df_standardized['borough'].apply(
            lambda x: standardize_borough_name(x, compound_mapping, out_of_london_mapping)
        )
        print(f"  Successfully applied standardization to {len(df_standardized)} rows")
    except Exception as e:
        print(f"  Error applying standardization: {e}")
        print(f"  Sample borough names: {df_standardized['borough'].head().tolist()}")
        return None
    
    # Show what changes were made
    try:
        changes = df[df['borough'] != df_standardized['borough_standardized']]
        if not changes.empty:
            print(f"  Made {len(changes)} standardization changes:")
            for _, row in changes.iterrows():
                print(f"    '{row['borough']}' → '{row['borough_standardized']}'")
        else:
            print("  No changes needed")
    except Exception as e:
        print(f"  Error comparing changes: {e}")
        # Continue anyway since the standardization was successful
    
    # Ensure the standardized column exists
    if 'borough_standardized' not in df_standardized.columns:
        print(f"  Error: borough_standardized column not created")
        return None
    
    # Save the standardized version
    if df_standardized is not None:
        df_standardized.to_csv(output_file, index=False)
        print(f"  Saved standardized data to {output_file}")
        return df_standardized
    else:
        print(f"  Failed to process file")
        return None

def create_summary_report(original_files, standardized_files, house_price_boroughs):
    """Create a summary report of the standardization process"""
    
    print("\n" + "="*80)
    print("STANDARDIZATION SUMMARY REPORT")
    print("="*80)
    
    # Load all standardized data
    all_standardized_boroughs = set()
    station_counts = {}
    
    for system_name, file_path in standardized_files.items():
        df = pd.read_csv(file_path)
        boroughs = set(df['borough_standardized'].unique())
        all_standardized_boroughs.update(boroughs)
        station_counts[system_name] = len(df)
        
        print(f"\n{system_name} System:")
        print(f"  Total stations: {station_counts[system_name]}")
        print(f"  Unique boroughs: {len(boroughs)}")
        print(f"  Boroughs: {sorted(boroughs)}")
    
    # Check compatibility with House Price Index
    print(f"\nCompatibility with UK House Price Index:")
    print(f"  House Price Index boroughs: {len(house_price_boroughs)}")
    print(f"  Standardized station boroughs: {len(all_standardized_boroughs)}")
    
    # Find overlapping and non-overlapping boroughs
    overlapping = house_price_boroughs.intersection(all_standardized_boroughs)
    only_in_house_price = house_price_boroughs - all_standardized_boroughs
    only_in_stations = all_standardized_boroughs - house_price_boroughs
    
    print(f"  Overlapping boroughs: {len(overlapping)}")
    print(f"  Only in House Price Index: {len(only_in_house_price)}")
    print(f"  Only in station data: {len(only_in_stations)}")
    
    if only_in_stations:
        print(f"  Non-overlapping station boroughs: {sorted(only_in_stations)}")
    
    # Check if "Out of London" is present
    if 'Out of London' in all_standardized_boroughs:
        print(f"\nOut of London stations detected and properly categorized.")
    
    print(f"\nStandardization complete! All files saved to Data/Station_Borough_Mappings/Standardized/")

def main():
    """Main function to run the standardization process"""
    
    print("Starting borough mapping standardization...")
    
    # Load reference borough names from House Price Index
    house_price_boroughs = load_house_price_boroughs()
    print(f"Loaded {len(house_price_boroughs)} boroughs from UK House Price Index")
    
    # Create standardization mappings
    compound_mapping, out_of_london_mapping = create_standardization_mapping()
    
    # Define input and output files
    input_files = {
        'DLR': 'Data/Station_Borough_Mappings/DLR_stations_by_borough.csv',
        'ELZ': 'Data/Station_Borough_Mappings/ELZ_stations_by_borough.csv',
        'LO': 'Data/Station_Borough_Mappings/LO_stations_by_borough.csv',
        'Tube': 'Data/Station_Borough_Mappings/london_tube_stations_by_borough.csv'
    }
    
    # Create output directory
    output_dir = get_data_path('Data/Station_Borough_Mappings/')
    output_dir = os.path.join(output_dir, 'Standardized')
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output files
    output_files = {
        'DLR': os.path.join(output_dir, 'DLR_stations_by_borough_standardized.csv'),
        'ELZ': os.path.join(output_dir, 'ELZ_stations_by_borough_standardized.csv'),
        'LO': os.path.join(output_dir, 'LO_stations_by_borough_standardized.csv'),
        'Tube': os.path.join(output_dir, 'london_tube_stations_by_borough_standardized.csv')
    }
    
    # Process each file
    successful_files = {}
    for system_name, input_file in input_files.items():
        try:
            input_path = get_data_path(input_file)
            output_path = output_files[system_name]
            
            process_station_borough_file(
                input_path, 
                output_path, 
                compound_mapping, 
                out_of_london_mapping
            )
            successful_files[system_name] = output_path
            
        except Exception as e:
            print(f"Error processing {system_name}: {e}")
            continue
    
    # Create summary report
    create_summary_report(input_files, successful_files, house_price_boroughs)
    
    # Create a combined standardized file
    if successful_files:
        combined_data = []
        for system_name, output_file in successful_files.items():
            df = pd.read_csv(output_file)
            df['system'] = system_name
            combined_data.append(df)
        
        combined_df = pd.concat(combined_data, ignore_index=True)
        combined_output = os.path.join(output_dir, 'all_stations_by_borough_standardized.csv')
        combined_df.to_csv(combined_output, index=False)
        print(f"\nCreated combined standardized file: {combined_output}")
    else:
        print("\nNo files were successfully processed.")
    
    return successful_files, combined_output if successful_files else None

if __name__ == "__main__":
    main()
