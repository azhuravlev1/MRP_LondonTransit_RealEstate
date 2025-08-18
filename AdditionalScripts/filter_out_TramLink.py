#!/usr/bin/env python3
"""
Script to filter out Tramlink station names from comprehensive_station_nlc_mapping.csv
This script removes all stations that are part of the London Tramlink network.
"""

import pandas as pd
import os

def filter_out_tramlink_stations():
    """
    Filter out Tramlink stations from the comprehensive station NLC mapping file.
    """
    
    # Define the set of Tramlink stations to exclude
    tram_exclusion_set = {
        'Addington Village',
        'Addiscombe',
        'Ampere Way',
        'Arena',
        'Avenue Road',
        'Beckenham Junction Trams',
        'Beckenham Road',
        'Beddington Lane',
        'Belgrave Walk',
        'Birkbeck Trams',
        'Blackhorse Lane',
        'Centrale',
        'Church Street',
        'Coombe Lane',
        'Dundonald Road',
        'East Croydon Trams',
        'Elmers End',
        'Fieldway',
        'George Street',
        'Gravel Hill',
        'Harrington Road',
        'King Henry\'s Drive',
        'Lebanon Road',
        'Lloyd Park',
        'Merton Park',
        'Mitcham',
        'Mitcham Junction',
        'Morden Road',
        'New Addington',
        'Phipps Bridge',
        'Reeves Corner',
        'Sandilands',
        'Therapia Lane',
        'Waddon Marsh',
        'Wandle Park',
        'Wellesley Road',
        'West Croydon Trams',
        'Wimbledon Trams',
        'Woodside'
    }
    
    # File paths
    input_file = '/Users/andrey/Desktop/TMU/MRP/Code/Data/comprehensive_station_nlc_mapping.csv'
    output_file = '/Users/andrey/Desktop/TMU/MRP/Code/Data/comprehensive_station_nlc_mapping_no_tramlink.csv'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    try:
        # Read the CSV file
        print(f"Reading data from: {input_file}")
        df = pd.read_csv(input_file)
        
        # Display initial statistics
        print(f"Original dataset contains {len(df)} stations")
        
        # Filter out Tramlink stations
        print("Filtering out Tramlink stations...")
        filtered_df = df[~df['Station'].isin(tram_exclusion_set)]
        
        # Display filtering statistics
        removed_count = len(df) - len(filtered_df)
        print(f"Removed {removed_count} Tramlink stations")
        print(f"Remaining stations: {len(filtered_df)}")
        
        # Save the filtered data
        print(f"Saving filtered data to: {output_file}")
        filtered_df.to_csv(output_file, index=False)
        
        # Display some statistics about what was removed
        removed_stations = df[df['Station'].isin(tram_exclusion_set)]
        if not removed_stations.empty:
            print("\nRemoved Tramlink stations:")
            for _, row in removed_stations.iterrows():
                print(f"  - {row['Station']} (NLC: {row['NLC']})")
        
        print(f"\nSuccessfully created filtered file: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    filter_out_tramlink_stations()
