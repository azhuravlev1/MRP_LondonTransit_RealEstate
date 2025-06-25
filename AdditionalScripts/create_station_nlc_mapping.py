import pandas as pd
import os

def create_station_nlc_mapping():
    """
    Extract unique Station-NLC pairs from StationNodesDescription.xls
    and save them as a CSV file for mapping NLC codes to station names.
    """
    
    # Define file paths
    input_file = "Data/StationNodesDescription.xls"
    output_file = "Data/station_nlc_mapping.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found!")
        return
    
    try:
        # Read the file as CSV (since it's actually CSV format)
        print(f"Reading {input_file} as CSV...")
        df = pd.read_csv(input_file)
        
        # Display basic info about the data
        print(f"Total rows in file: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Check if required columns exist
        required_columns = ['Station', 'NLC']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            return
        
        # Extract unique Station-NLC pairs
        print("Extracting unique Station-NLC pairs...")
        unique_pairs = df[['Station', 'NLC']].drop_duplicates()
        
        # Sort by Station name for better readability
        unique_pairs = unique_pairs.sort_values('Station')
        
        # Display statistics
        print(f"Total unique Station-NLC pairs: {len(unique_pairs)}")
        print(f"Number of unique stations: {unique_pairs['Station'].nunique()}")
        print(f"Number of unique NLC codes: {unique_pairs['NLC'].nunique()}")
        
        # Check for any missing values
        missing_stations = unique_pairs['Station'].isna().sum()
        missing_nlc = unique_pairs['NLC'].isna().sum()
        
        if missing_stations > 0:
            print(f"Warning: {missing_stations} rows have missing Station names")
        if missing_nlc > 0:
            print(f"Warning: {missing_nlc} rows have missing NLC codes")
        
        # Remove rows with missing values
        unique_pairs_clean = unique_pairs.dropna()
        print(f"After removing missing values: {len(unique_pairs_clean)} unique pairs")
        
        # Save to CSV
        print(f"Saving to {output_file}...")
        unique_pairs_clean.to_csv(output_file, index=False)
        
        # Display first few entries as preview
        print("\nFirst 10 entries:")
        print(unique_pairs_clean.head(10).to_string(index=False))
        
        print(f"\nSuccessfully created {output_file} with {len(unique_pairs_clean)} unique Station-NLC pairs!")
        
        # Additional analysis
        print(f"\nSummary statistics:")
        print(f"- Total unique stations: {unique_pairs_clean['Station'].nunique()}")
        print(f"- Total unique NLC codes: {unique_pairs_clean['NLC'].nunique()}")
        
        # Check for stations with multiple NLC codes
        station_counts = unique_pairs_clean.groupby('Station')['NLC'].nunique()
        stations_with_multiple_nlc = station_counts[station_counts > 1]
        if len(stations_with_multiple_nlc) > 0:
            print(f"- Stations with multiple NLC codes: {len(stations_with_multiple_nlc)}")
            print("  Examples:")
            for station, count in stations_with_multiple_nlc.head(5).items():
                print(f"    {station}: {count} NLC codes")
        
        # Check for NLC codes with multiple stations
        nlc_counts = unique_pairs_clean.groupby('NLC')['Station'].nunique()
        nlc_with_multiple_stations = nlc_counts[nlc_counts > 1]
        if len(nlc_with_multiple_stations) > 0:
            print(f"- NLC codes with multiple stations: {len(nlc_with_multiple_stations)}")
            print("  Examples:")
            for nlc, count in nlc_with_multiple_stations.head(5).items():
                print(f"    NLC {nlc}: {count} stations")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def create_station_nlc_mapping_from_numbat(numbat_file, output_file=None):
    """
    Extract unique Station-NLC pairs from NUMBAT outputs Excel file
    from the Station_Entries sheet (6th sheet) and save them as a CSV file.
    
    Parameters:
    - numbat_file: Path to the NUMBAT outputs Excel file
    - output_file: Output CSV file path (optional, will auto-generate if not provided)
    """
    
    # Check if input file exists
    if not os.path.exists(numbat_file):
        print(f"Error: Input file {numbat_file} not found!")
        return
    
    # Auto-generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(numbat_file))[0]
        output_file = f"Data/station_nlc_mapping_{base_name}.csv"
    
    try:
        # Read the Excel file
        print(f"Reading {numbat_file}...")
        
        # Get sheet names to verify Station_Entries exists
        xl_file = pd.ExcelFile(numbat_file)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Check if Station_Entries sheet exists (should be 6th sheet)
        if len(xl_file.sheet_names) >= 6:
            station_entries_sheet = xl_file.sheet_names[5]  # 6th sheet (0-indexed)
            print(f"Using sheet: {station_entries_sheet}")
        else:
            print(f"Warning: File has only {len(xl_file.sheet_names)} sheets, need at least 6, skipping...")
            return
        
        # Read the Station_Entries sheet with header in row 2 (3rd row, 0-indexed)
        print("Reading Station_Entries sheet with headers in row 2...")
        df = pd.read_excel(numbat_file, sheet_name=station_entries_sheet, header=2)
        
        # Display basic info about the data
        print(f"Total rows in Station_Entries sheet: {len(df)}")
        
        # Check if required columns exist (NLC should be 1st column, Station should be 3rd column)
        if len(df.columns) < 3:
            print(f"Warning: Not enough columns. Expected at least 3, got {len(df.columns)}, skipping...")
            return
        
        # Get column names for NLC (1st column) and Station (3rd column)
        nlc_column = df.columns[0]  # 1st column
        station_column = df.columns[2]  # 3rd column
        
        # Additional validation: check if the columns look like NLC and Station
        # NLC should typically be numeric or contain numeric codes
        # Station should typically be text
        try:
            # Check if NLC column contains numeric values (at least some)
            nlc_sample = df[nlc_column].dropna().head(10)
            station_sample = df[station_column].dropna().head(10)
            
            # If NLC column contains mostly non-numeric values and Station column contains mostly numeric,
            # we might have the wrong sheet or wrong column order
            nlc_numeric_count = sum(1 for x in nlc_sample if str(x).replace('.', '').isdigit())
            station_numeric_count = sum(1 for x in station_sample if str(x).replace('.', '').isdigit())
            
            if nlc_numeric_count < len(nlc_sample) * 0.3 and station_numeric_count > len(station_sample) * 0.7:
                print(f"Warning: Column order might be wrong. NLC column '{nlc_column}' has few numeric values, Station column '{station_column}' has many numeric values.")
                print("This might indicate we're reading the wrong sheet or columns are in wrong order.")
                return
                
        except Exception as e:
            print(f"Warning: Could not validate column types: {e}")
        
        print(f"Using NLC column: {nlc_column}")
        print(f"Using Station column: {station_column}")
        
        # Extract unique Station-NLC pairs
        print("Extracting unique Station-NLC pairs...")
        unique_pairs = df[[nlc_column, station_column]].drop_duplicates()
        
        # Rename columns for consistency
        unique_pairs.columns = ['NLC', 'Station']
        
        # Sort by Station name for better readability
        unique_pairs = unique_pairs.sort_values('Station')
        
        # Display statistics
        print(f"Total unique Station-NLC pairs: {len(unique_pairs)}")
        print(f"Number of unique stations: {unique_pairs['Station'].nunique()}")
        print(f"Number of unique NLC codes: {unique_pairs['NLC'].nunique()}")
        
        # Check for any missing values
        missing_stations = unique_pairs['Station'].isna().sum()
        missing_nlc = unique_pairs['NLC'].isna().sum()
        
        if missing_stations > 0:
            print(f"Warning: {missing_stations} rows have missing Station names")
        if missing_nlc > 0:
            print(f"Warning: {missing_nlc} rows have missing NLC codes")
        
        # Remove rows with missing values
        unique_pairs_clean = unique_pairs.dropna()
        print(f"After removing missing values: {len(unique_pairs_clean)} unique pairs")
        
        # Save to CSV
        print(f"Saving to {output_file}...")
        unique_pairs_clean.to_csv(output_file, index=False)
        
        # Display first few entries as preview
        print("\nFirst 10 entries:")
        print(unique_pairs_clean.head(10).to_string(index=False))
        
        print(f"\nSuccessfully created {output_file} with {len(unique_pairs_clean)} unique Station-NLC pairs!")
        
        # Additional analysis
        print(f"\nSummary statistics:")
        print(f"- Total unique stations: {unique_pairs_clean['Station'].nunique()}")
        print(f"- Total unique NLC codes: {unique_pairs_clean['NLC'].nunique()}")
        
        # Check for stations with multiple NLC codes
        station_counts = unique_pairs_clean.groupby('Station')['NLC'].nunique()
        stations_with_multiple_nlc = station_counts[station_counts > 1]
        if len(stations_with_multiple_nlc) > 0:
            print(f"- Stations with multiple NLC codes: {len(stations_with_multiple_nlc)}")
            print("  Examples:")
            for station, count in stations_with_multiple_nlc.head(5).items():
                print(f"    {station}: {count} NLC codes")
        
        # Check for NLC codes with multiple stations
        nlc_counts = unique_pairs_clean.groupby('NLC')['Station'].nunique()
        nlc_with_multiple_stations = nlc_counts[nlc_counts > 1]
        if len(nlc_with_multiple_stations) > 0:
            print(f"- NLC codes with multiple stations: {len(nlc_with_multiple_stations)}")
            print("  Examples:")
            for nlc, count in nlc_with_multiple_stations.head(5).items():
                print(f"    NLC {nlc}: {count} stations")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()

def create_station_nlc_mapping_2019():
    """
    Create station_NLC_mapping_2019.csv specifically from NBT19MTT_Outputs.xlsx
    """
    numbat_file = "Data/NUMBAT/Outputs/NBT19MTT_Outputs.xlsx"
    output_file = "Data/station_NLC_mapping_2019.csv"
    
    print("=== Creating station_NLC_mapping_2019 from NBT19MTT_Outputs.xlsx ===")
    create_station_nlc_mapping_from_numbat(numbat_file, output_file)

def create_comprehensive_station_nlc_mapping():
    """
    Create a comprehensive station-NLC mapping by extracting data from all NUMBAT outputs files
    (2016-2023) and combining all unique pairs.
    """
    
    # Define the files to process from the Outputs folder
    numbat_files_2019 = [
        "Data/NUMBAT/Outputs/NBT19FRI_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT19MTT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT19SAT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT19SUN_Outputs.xlsx"
    ]
    
    numbat_files_2022 = [
        "Data/NUMBAT/Outputs/NBT22FRI_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT22MON_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT22SAT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT22SUN_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT22TWT_Outputs.xlsx"
    ]
    
    # Add all other years for comprehensive coverage
    numbat_files_2016 = [
        "Data/NUMBAT/Outputs/NBT16MTT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT16SAT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT16SUN_Outputs.xlsx"
    ]
    
    numbat_files_2017 = [
        "Data/NUMBAT/Outputs/NBT17MTT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT17SAT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT17SUN_Outputs.xlsx"
    ]
    
    numbat_files_2018 = [
        "Data/NUMBAT/Outputs/NBT18MTT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT18FRI_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT18SAT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT18SUN_Outputs.xlsx"
    ]
    
    numbat_files_2020 = [
        "Data/NUMBAT/Outputs/NBT20FRI_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT20MTT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT20SAT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT20SUN_Outputs.xlsx"
    ]
    
    numbat_files_2021 = [
        "Data/NUMBAT/Outputs/NBT21FRI_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT21MTT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT21SAT_Outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT21SUN_Outputs.xlsx"
    ]
    
    numbat_files_2023 = [
        "Data/NUMBAT/Outputs/NBT23FRI_outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT23MON_outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT23SAT_outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT23SUN_outputs.xlsx",
        "Data/NUMBAT/Outputs/NBT23TWT_outputs.xlsx"
    ]
    
    all_files = (numbat_files_2016 + numbat_files_2017 + numbat_files_2018 + 
                 numbat_files_2019 + numbat_files_2020 + numbat_files_2021 + 
                 numbat_files_2022 + numbat_files_2023)
    output_file = "Data/comprehensive_station_nlc_mapping.csv"
    
    print("=== Creating comprehensive station-NLC mapping from all NUMBAT Outputs files ===")
    print(f"Processing {len(all_files)} files...")
    
    # List to store all unique pairs from all files
    all_unique_pairs = []
    
    for i, file_path in enumerate(all_files, 1):
        print(f"\n--- Processing file {i}/{len(all_files)}: {os.path.basename(file_path)} ---")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found, skipping...")
            continue
        
        try:
            # Read the Excel file
            print(f"Reading {file_path}...")
            
            # Get sheet names to verify Station_Entries exists
            xl_file = pd.ExcelFile(file_path)
            print(f"Available sheets: {xl_file.sheet_names}")
            
            # Check if Station_Entries sheet exists (should be 6th sheet)
            if len(xl_file.sheet_names) >= 6:
                station_entries_sheet = xl_file.sheet_names[5]  # 6th sheet (0-indexed)
                print(f"Using sheet: {station_entries_sheet}")
            else:
                print(f"Warning: File has only {len(xl_file.sheet_names)} sheets, need at least 6, skipping...")
                continue
            
            # Read the Station_Entries sheet with header in row 2 (3rd row, 0-indexed)
            print("Reading Station_Entries sheet with headers in row 2...")
            df = pd.read_excel(file_path, sheet_name=station_entries_sheet, header=2)
            
            # Display basic info about the data
            print(f"Total rows in Station_Entries sheet: {len(df)}")
            
            # Check if required columns exist (NLC should be 1st column, Station should be 3rd column)
            if len(df.columns) < 3:
                print(f"Warning: Not enough columns. Expected at least 3, got {len(df.columns)}, skipping...")
                continue
            
            # Get column names for NLC (1st column) and Station (3rd column)
            nlc_column = df.columns[0]  # 1st column
            station_column = df.columns[2]  # 3rd column
            
            # Additional validation: check if the columns look like NLC and Station
            # NLC should typically be numeric or contain numeric codes
            # Station should typically be text
            try:
                # Check if NLC column contains numeric values (at least some)
                nlc_sample = df[nlc_column].dropna().head(10)
                station_sample = df[station_column].dropna().head(10)
                
                # If NLC column contains mostly non-numeric values and Station column contains mostly numeric,
                # we might have the wrong sheet or wrong column order
                nlc_numeric_count = sum(1 for x in nlc_sample if str(x).replace('.', '').isdigit())
                station_numeric_count = sum(1 for x in station_sample if str(x).replace('.', '').isdigit())
                
                if nlc_numeric_count < len(nlc_sample) * 0.3 and station_numeric_count > len(station_sample) * 0.7:
                    print(f"Warning: Column order might be wrong. NLC column '{nlc_column}' has few numeric values, Station column '{station_column}' has many numeric values.")
                    print("This might indicate we're reading the wrong sheet or columns are in wrong order.")
                    continue
                    
            except Exception as e:
                print(f"Warning: Could not validate column types: {e}")
            
            print(f"Using NLC column: {nlc_column}")
            print(f"Using Station column: {station_column}")
            
            # Extract unique Station-NLC pairs
            print("Extracting unique Station-NLC pairs...")
            unique_pairs = df[[nlc_column, station_column]].drop_duplicates()
            
            # Rename columns for consistency
            unique_pairs.columns = ['NLC', 'Station']
            
            # Remove rows with missing values
            unique_pairs_clean = unique_pairs.dropna()
            
            print(f"Found {len(unique_pairs_clean)} unique pairs in this file")
            
            # Add to the collection
            all_unique_pairs.append(unique_pairs_clean)
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    if not all_unique_pairs:
        print("Error: No valid data found in any of the files!")
        return
    
    # Combine all unique pairs
    print(f"\n--- Combining data from all files ---")
    combined_df = pd.concat(all_unique_pairs, ignore_index=True)
    
    # Remove duplicates across all files
    print("Removing duplicates across all files...")
    final_unique_pairs = combined_df.drop_duplicates()
    
    # Convert Station column to string to handle mixed data types for sorting
    final_unique_pairs['Station'] = final_unique_pairs['Station'].astype(str)
    
    # Sort by Station name for better readability
    final_unique_pairs = final_unique_pairs.sort_values('Station')
    
    # Display statistics
    print(f"\n--- Final Statistics ---")
    print(f"Total unique Station-NLC pairs across all files: {len(final_unique_pairs)}")
    print(f"Number of unique stations: {final_unique_pairs['Station'].nunique()}")
    print(f"Number of unique NLC codes: {final_unique_pairs['NLC'].nunique()}")
    
    # Check for any missing values
    missing_stations = final_unique_pairs['Station'].isna().sum()
    missing_nlc = final_unique_pairs['NLC'].isna().sum()
    
    if missing_stations > 0:
        print(f"Warning: {missing_stations} rows have missing Station names")
    if missing_nlc > 0:
        print(f"Warning: {missing_nlc} rows have missing NLC codes")
    
    # Remove rows with missing values (should be 0 at this point, but just in case)
    final_clean = final_unique_pairs.dropna()
    print(f"After final cleaning: {len(final_clean)} unique pairs")
    
    # Save to CSV
    print(f"\nSaving to {output_file}...")
    final_clean.to_csv(output_file, index=False)
    
    # Display first few entries as preview
    print("\nFirst 10 entries:")
    print(final_clean.head(10).to_string(index=False))
    
    print(f"\nSuccessfully created {output_file} with {len(final_clean)} unique Station-NLC pairs!")
    
    # Additional analysis
    print(f"\nSummary statistics:")
    print(f"- Total unique stations: {final_clean['Station'].nunique()}")
    print(f"- Total unique NLC codes: {final_clean['NLC'].nunique()}")
    
    # Check for stations with multiple NLC codes
    station_counts = final_clean.groupby('Station')['NLC'].nunique()
    stations_with_multiple_nlc = station_counts[station_counts > 1]
    if len(stations_with_multiple_nlc) > 0:
        print(f"- Stations with multiple NLC codes: {len(stations_with_multiple_nlc)}")
        print("  Examples:")
        for station, count in stations_with_multiple_nlc.head(5).items():
            print(f"    {station}: {count} NLC codes")
    
    # Check for NLC codes with multiple stations
    nlc_counts = final_clean.groupby('NLC')['Station'].nunique()
    nlc_with_multiple_stations = nlc_counts[nlc_counts > 1]
    if len(nlc_with_multiple_stations) > 0:
        print(f"- NLC codes with multiple stations: {len(nlc_with_multiple_stations)}")
        print("  Examples:")
        for nlc, count in nlc_with_multiple_stations.head(5).items():
            print(f"    NLC {nlc}: {count} stations")
    
    # Year-wise breakdown
    print(f"\n--- Year-wise Breakdown ---")
    year_2016_files = [f for f in all_files if "NBT16" in f]
    year_2017_files = [f for f in all_files if "NBT17" in f]
    year_2018_files = [f for f in all_files if "NBT18" in f]
    year_2019_files = [f for f in all_files if "NBT19" in f]
    year_2020_files = [f for f in all_files if "NBT20" in f]
    year_2021_files = [f for f in all_files if "NBT21" in f]
    year_2022_files = [f for f in all_files if "NBT22" in f]
    year_2023_files = [f for f in all_files if "NBT23" in f]
    
    print(f"Files from 2016: {len(year_2016_files)}")
    print(f"Files from 2017: {len(year_2017_files)}")
    print(f"Files from 2018: {len(year_2018_files)}")
    print(f"Files from 2019: {len(year_2019_files)}")
    print(f"Files from 2020: {len(year_2020_files)}")
    print(f"Files from 2021: {len(year_2021_files)}")
    print(f"Files from 2022: {len(year_2022_files)}")
    print(f"Files from 2023: {len(year_2023_files)}")

if __name__ == "__main__":
    # Original function for StationNodesDescription.xls
    print("=== Creating station-NLC mapping from StationNodesDescription.xls ===")
    create_station_nlc_mapping()
    
    print("\n" + "="*80 + "\n")
    
    # New function for NUMBAT outputs
    print("=== Creating station-NLC mapping from NUMBAT outputs ===")
    numbat_file = "Data/NUMBAT/Outputs/NBT19MTT_Outputs.xlsx"
    create_station_nlc_mapping_from_numbat(numbat_file)
    
    print("\n" + "="*80 + "\n")
    
    # Specific function for 2019 mapping
    create_station_nlc_mapping_2019()
    
    print("\n" + "="*80 + "\n")
    
    # Comprehensive function for all NUMBAT OD files
    create_comprehensive_station_nlc_mapping() 