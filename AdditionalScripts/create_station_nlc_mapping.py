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

if __name__ == "__main__":
    create_station_nlc_mapping() 