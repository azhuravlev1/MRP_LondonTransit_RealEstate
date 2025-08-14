import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import pandas as pd
from urllib.parse import urljoin

def clean_station_name(station_name):
    """
    Clean station names by removing all variations of station suffixes,
    and always remove ' railway station' at the end.
    """
    cleaned = station_name.strip()
    
    # Remove common station suffixes (case insensitive)
    patterns_to_remove = [
        r'\s+railway\s+station',
        r'\s+station',
        r'\s+\(railway\s+station\)',
        r'\s+\(station\)',
        r'\s+\(London\)',
        r'\s+\(England\)'
    ]
    
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up any extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def clean_borough_name(borough_name):
    """
    Clean borough names according to specific rules:
    1. City of Westminster -> Westminster (but City of London stays as City of London)
    2. Remove "London Borough of " and "Royal Borough of " prefixes
    3. Standardize "and" to "&" for consistency with UK House Price Index
    """
    cleaned = borough_name.strip()
    
    # Special case: City of Westminster -> Westminster
    if cleaned == "City of Westminster":
        return "Westminster"
    
    # Remove "London Borough of " prefix
    cleaned = re.sub(r'^London Borough of\s+', '', cleaned, flags=re.IGNORECASE)
    
    # Remove "Royal Borough of " prefix
    cleaned = re.sub(r'^Royal Borough of\s+', '', cleaned, flags=re.IGNORECASE)
    
    # Standardize "and" to "&" for consistency with UK House Price Index
    cleaned = re.sub(r'\s+and\s+', ' & ', cleaned)
    
    # Clean up any extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def clean_station_name_for_od_compatibility(station_name):
    """
    Clean station names to match OD 2017 naming patterns.
    This function applies specific transformations for DLR stations.
    """
    cleaned = station_name.strip()
    
    # Remove location clarifications in parentheses
    # Kew Gardens (London) -> Kew Gardens
    # Queen's Park (England) -> Queen's Park  
    # Richmond (London) -> Richmond
    cleaned = re.sub(r'\s+\(London\)$', '', cleaned)
    cleaned = re.sub(r'\s+\(England\)$', '', cleaned)
    
    # Handle specific DLR station naming patterns
    # Bank / Monument -> Bank / Monument (keep as is)
    # Canary Wharf -> Canary Wharf (keep as is)
    
    # Add line abbreviation for specific stations if needed
    if cleaned == "Bank":
        return "Bank (DLR)"
    
    return cleaned

def scrape_dlr_stations_and_boroughs(main_url):
    """
    Scrape all DLR station names and their boroughs from the main page
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(main_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        stations = []
        
        # Find all tables on the page
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            # Look for tables that contain station information
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 3:  # Ensure we have enough columns
                    # Extract station name from the first column
                    station_cell = cells[0]
                    station_link = station_cell.find('a')
                    
                    if station_link:
                        station_name = station_link.get_text().strip()
                        
                        # Extract borough from the Local authority column (usually 3rd column)
                        borough_cell = cells[2] if len(cells) > 2 else cells[1]
                        borough_name = borough_cell.get_text().strip()
                        
                        # Clean station name
                        clean_name = clean_station_name(station_name)
                        
                        # Only add if we have both station name and borough
                        if clean_name and borough_name and borough_name != "Local authority":
                            stations.append({
                                'station_name': clean_name,
                                'borough': borough_name,
                                'full_name': station_name,
                                'url': urljoin(main_url, station_link.get('href', ''))
                            })
        
        return stations
    
    except Exception as e:
        print(f"Error scraping DLR stations: {e}")
        return []

def scrape_all_dlr_stations():
    """
    Main function to scrape all DLR stations and their boroughs
    """
    main_url = "https://en.wikipedia.org/wiki/List_of_Docklands_Light_Railway_stations"
    
    print("Scraping DLR stations...")
    stations = scrape_dlr_stations_and_boroughs(main_url)
    
    print(f"Found {len(stations)} stations")
    
    return stations

def save_to_csv(stations, filename='DLR_stations_by_borough.csv'):
    """
    Save the station data to a CSV file
    """
    if not stations:
        print("No stations to save")
        return
    
    # Create DataFrame
    df = pd.DataFrame(stations)
    
    # Clean borough names
    df['borough'] = df['borough'].apply(clean_borough_name)
    
    # Apply OD compatibility cleaning to station names
    df['station_name'] = df['station_name'].apply(clean_station_name_for_od_compatibility)
    
    # Remove duplicates based on station_name, keeping the first occurrence
    df_output = df.drop_duplicates(subset=['station_name'], keep='first')
    
    # Select and reorder columns
    df_output = df_output[['station_name', 'borough']].copy()
    
    # Sort by borough, then by station name
    df_output = df_output.sort_values(['borough', 'station_name'])
    
    # Save to CSV
    df_output.to_csv(filename, index=False)
    
    print(f"Saved {len(df_output)} stations to {filename}")
    
    # Print summary statistics
    print(f"\nSummary:")
    print(f"Total stations: {len(df_output)}")
    print(f"Total boroughs: {df_output['borough'].nunique()}")
    print(f"\nStations per borough:")
    borough_counts = df_output['borough'].value_counts().sort_index()
    for borough, count in borough_counts.items():
        print(f"  {borough}: {count}")

def test_station_name_cleaning():
    """
    Test the station name cleaning function with various examples
    """
    test_names = [
        "Bank station",
        "Canary Wharf station", 
        "Custom House station",
        "Deptford Bridge station",
        "East India station",
        "Elverson Road station",
        "Gallions Reach station",
        "Greenwich station",
        "Heron Quays station",
        "Island Gardens station",
        "King George V station",
        "Lewisham station",
        "Limehouse station",
        "Mudchute station",
        "Pontoon Dock station",
        "Poplar station",
        "Prince Regent station",
        "Royal Albert station",
        "Royal Victoria station",
        "Shadwell station",
        "South Quay station",
        "Stratford station",
        "Stratford High Street station",
        "Stratford International station",
        "Tower Gateway station",
        "West India Quay station",
        "West Silvertown station",
        "Westferry station",
        "Woolwich Arsenal station"
    ]
    
    print("Testing station name cleaning:")
    print("-" * 50)
    for name in test_names:
        cleaned = clean_station_name(name)
        print(f"'{name}' -> '{cleaned}'")
    print("-" * 50)

def test_borough_name_cleaning():
    """
    Test the borough name cleaning function with various examples
    """
    test_boroughs = [
        "City of Westminster",
        "City of London",
        "London Borough of Camden",
        "Royal Borough of Kensington and Chelsea",
        "London Borough of Islington",
        "Royal Borough of Greenwich",
        "Hackney",  # Already clean
        "Tower Hamlets",  # Already clean
        "Barking and Dagenham",
        "Hammersmith and Fulham",
        "Kensington and Chelsea"
    ]
    
    print("Testing borough name cleaning:")
    print("-" * 50)
    for borough in test_boroughs:
        cleaned = clean_borough_name(borough)
        print(f"'{borough}' -> '{cleaned}'")
    print("-" * 50)

def test_od_compatibility_cleaning():
    """
    Test the OD compatibility station name cleaning function with DLR examples
    """
    test_cases = [
        ("Bank", "Bank (DLR)"),
        ("Canary Wharf", "Canary Wharf"),
        ("Custom House", "Custom House"),
        ("Deptford Bridge", "Deptford Bridge"),
        ("East India", "East India"),
        ("Elverson Road", "Elverson Road"),
        ("Gallions Reach", "Gallions Reach"),
        ("Greenwich", "Greenwich"),
        ("Heron Quays", "Heron Quays"),
        ("Island Gardens", "Island Gardens"),
        ("King George V", "King George V"),
        ("Lewisham", "Lewisham"),
        ("Limehouse", "Limehouse"),
        ("Mudchute", "Mudchute"),
        ("Pontoon Dock", "Pontoon Dock"),
        ("Poplar", "Poplar"),
        ("Prince Regent", "Prince Regent"),
        ("Royal Albert", "Royal Albert"),
        ("Royal Victoria", "Royal Victoria"),
        ("Shadwell", "Shadwell"),
        ("South Quay", "South Quay"),
        ("Stratford", "Stratford"),
        ("Stratford High Street", "Stratford High Street"),
        ("Stratford International", "Stratford International"),
        ("Tower Gateway", "Tower Gateway"),
        ("West India Quay", "West India Quay"),
        ("West Silvertown", "West Silvertown"),
        ("Westferry", "Westferry"),
        ("Woolwich Arsenal", "Woolwich Arsenal")
    ]
    
    print("Testing OD compatibility station name cleaning:")
    print("-" * 70)
    for original, expected in test_cases:
        result = clean_station_name_for_od_compatibility(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{original}' -> '{result}' (expected: '{expected}')")
    print("-" * 70)

def main():
    """
    Main execution function
    """
    print("Starting DLR Stations scraper...")
    
    # Test the cleaning functions
    test_station_name_cleaning()
    print()
    test_borough_name_cleaning()
    print()
    test_od_compatibility_cleaning()
    print()

    # Scrape all stations
    stations = scrape_all_dlr_stations()
    
    if stations:
        # Save to CSV
        save_to_csv(stations)
        
        # Also save detailed version with URLs for reference
        df_detailed = pd.DataFrame(stations)
        # Apply borough cleaning to detailed version too
        df_detailed['borough'] = df_detailed['borough'].apply(clean_borough_name)
        df_detailed.to_csv('london_dlr_stations_detailed.csv', index=False)
        print("Also saved detailed version with URLs to london_dlr_stations_detailed.csv")
        
        # Show some examples of cleaned names
        print("\nExample of cleaned station names:")
        df = pd.DataFrame(stations)
        df['borough'] = df['borough'].apply(clean_borough_name)
        sample = df[['full_name', 'station_name', 'borough']].sample(min(10, len(df)))
        for _, row in sample.iterrows():
            print(f"  '{row['full_name']}' -> '{row['station_name']}' ({row['borough']})")
    else:
        print("No stations were scraped")

if __name__ == "__main__":
    main()
