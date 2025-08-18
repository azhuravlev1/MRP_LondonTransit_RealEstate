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
    This function applies specific transformations for Overground stations.
    """
    cleaned = station_name.strip()
    
    # Remove location clarifications in parentheses
    # Kew Gardens (London) -> Kew Gardens
    # Queen's Park (England) -> Queen's Park  
    # Richmond (London) -> Richmond
    cleaned = re.sub(r'\s+\(London\)$', '', cleaned)
    cleaned = re.sub(r'\s+\(England\)$', '', cleaned)
    
    # Handle specific Overground station naming patterns
    # Caledonian Road & Barnsbury -> Caledonian Road & Barnsbury (keep as is)
    # Highbury & Islington -> Highbury & Islington (keep as is)
    # Harrow & Wealdstone -> Harrow & Wealdstone (keep as is)
    
    # Add line abbreviation for Shepherd's Bush if it doesn't have one
    if cleaned == "Shepherd's Bush":
        return "Shepherd's Bush (Ovr)"
    
    # Handle specific station name variations
    if cleaned == "St. James Street":
        return "St. James Street"
    
    return cleaned

def scrape_overground_stations(main_url):
    """
    Scrape all London Overground station names from the main category page
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(main_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the pages section
        pages_section = soup.find('div', id='mw-pages')
        if not pages_section:
            print("No pages section found")
            return []
        
        # Find all station links within the category
        station_links = pages_section.find_all('a', href=True)
        
        stations = []
        for link in station_links:
            href = link.get('href', '')
            # Only get links that are actual station pages
            if '/wiki/' in href and 'Wikipedia:' not in href and 'Category:' not in href:
                station_name = link.get_text().strip()
                
                # Clean station name - remove ALL common suffixes and variations
                clean_name = clean_station_name(station_name)
                
                stations.append({
                    'station_name': clean_name,
                    'full_name': station_name,
                    'url': urljoin(main_url, href)
                })
        
        return stations
    
    except Exception as e:
        print(f"Error scraping Overground stations: {e}")
        return []

def scrape_borough_from_station_page(station_info):
    """
    Scrape the borough information from a specific station page
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(station_info['url'], headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the infobox
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            print(f"No infobox found for {station_info['station_name']}")
            return None
        
        # Look for the "Local authority" row
        rows = infobox.find_all('tr')
        for row in rows:
            # Find the header cell
            header_cell = row.find('th')
            if header_cell:
                header_text = header_cell.get_text().strip()
                if 'Local authority' in header_text:
                    # Find the data cell
                    data_cell = row.find('td')
                    if data_cell:
                        # Get the text content, which should be the borough name
                        borough_name = data_cell.get_text().strip()
                        return borough_name
        
        print(f"No local authority found for {station_info['station_name']}")
        return None
    
    except Exception as e:
        print(f"Error scraping borough for {station_info['station_name']}: {e}")
        return None

def scrape_all_overground_stations():
    """
    Main function to scrape all London Overground stations and their boroughs
    """
    main_url = "https://en.wikipedia.org/wiki/Category:Railway_stations_served_by_London_Overground"
    
    print("Scraping London Overground stations...")
    stations = scrape_overground_stations(main_url)
    
    print(f"Found {len(stations)} stations")
    
    all_stations_with_boroughs = []
    
    for i, station_info in enumerate(stations, 1):
        print(f"Scraping borough for {i}/{len(stations)}: {station_info['station_name']}")
        
        borough = scrape_borough_from_station_page(station_info)
        
        station_data = {
            'station_name': station_info['station_name'],
            'borough': borough if borough else 'Unknown',
            'full_name': station_info['full_name'],
            'url': station_info['url']
        }
        
        all_stations_with_boroughs.append(station_data)
        
        # Be respectful - add a small delay between requests
        time.sleep(1)
    
    return all_stations_with_boroughs

def save_to_csv(stations, filename='LO_stations_by_borough.csv'):
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
        "Acton Central railway station",
        "Barking station", 
        "Caledonian Road & Barnsbury railway station",
        "Canada Water station",
        "Dalston Junction railway station",
        "Euston railway station",
        "Finchley Road & Frognal railway station",
        "Gunnersbury station",
        "Hackney Central railway station",
        "Imperial Wharf railway station",
        "Kew Gardens station (London)",
        "Liverpool Street station",
        "Queen's Park station (England)",
        "Richmond station (London)",
        "Shepherd's Bush railway station",
        "St. James Street railway station",
        "Walthamstow Central station",
        "Whitechapel station"
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
    Test the OD compatibility station name cleaning function with Overground examples
    """
    test_cases = [
        ("Kew Gardens (London)", "Kew Gardens"),
        ("Queen's Park (England)", "Queen's Park"),
        ("Richmond (London)", "Richmond"),
        ("Shepherd's Bush", "Shepherd's Bush (Ovr)"),
        ("St. James Street", "St. James Street"),
        # Test cases that should remain unchanged
        ("Acton Central", "Acton Central"),
        ("Barking", "Barking"),
        ("Caledonian Road & Barnsbury", "Caledonian Road & Barnsbury"),
        ("Canada Water", "Canada Water"),
        ("Dalston Junction", "Dalston Junction"),
        ("Euston", "Euston"),
        ("Finchley Road & Frognal", "Finchley Road & Frognal"),
        ("Gunnersbury", "Gunnersbury"),
        ("Hackney Central", "Hackney Central"),
        ("Imperial Wharf", "Imperial Wharf"),
        ("Liverpool Street", "Liverpool Street"),
        ("Whitechapel", "Whitechapel")
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
    print("Starting London Overground Stations scraper...")
    
    # Test the cleaning functions
    test_station_name_cleaning()
    print()
    test_borough_name_cleaning()
    print()
    test_od_compatibility_cleaning()
    print()

    # Scrape all stations
    stations = scrape_all_overground_stations()
    
    if stations:
        # Save to CSV
        save_to_csv(stations)
        
        # Also save detailed version with URLs for reference
        df_detailed = pd.DataFrame(stations)
        # Apply borough cleaning to detailed version too
        df_detailed['borough'] = df_detailed['borough'].apply(clean_borough_name)
        df_detailed.to_csv('london_overground_stations_detailed.csv', index=False)
        print("Also saved detailed version with URLs to london_overground_stations_detailed.csv")
        
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
