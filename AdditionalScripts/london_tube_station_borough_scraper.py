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
    and always remove ' tube' at the end.
    """
    cleaned = station_name.strip()
    
    # Remove common station suffixes (case insensitive)
    patterns_to_remove = [
        r'\s+tube\s+station',
        r'\s+underground\s+station',
        r'\s+station',
        r'\s+\(tube\s+station\)',
        r'\s+\(underground\s+station\)',
        r'\s+\(station\)',
        r'\s+\(London\s+Underground\)',
        r'\s+\(London\s+Underground\s+station\)'
    ]
    
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Always remove ' tube' at the end (case insensitive)
    cleaned = re.sub(r'\s+tube$', '', cleaned, flags=re.IGNORECASE)
    
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
    This function applies specific transformations based on the examples provided.
    """
    cleaned = station_name.strip()
    
    # 1. Bank and Monuments -> Bank / Monument
    if cleaned == "Bank and Monuments":
        return "Bank / Monument"
    
    # 2. Heathrow Terminals 2 & 3 -> Heathrow Terminals 123
    if cleaned == "Heathrow Terminals 2 & 3":
        return "Heathrow Terminals 123"
    
    # 3. King's Cross St Pancras -> King's Cross St. Pancras (add apostrophe)
    if cleaned == "King's Cross St Pancras":
        return "King's Cross St. Pancras"
    
    # 4. Paddington stations -> Paddington (unify the complex)
    if cleaned.startswith("Paddington ("):
        return "Paddington"
    
    # 5. Remove location clarifications in parentheses
    # Kew Gardens (London) -> Kew Gardens
    # Queen's Park (England) -> Queen's Park  
    # Richmond (London) -> Richmond
    cleaned = re.sub(r'\s+\(London\)$', '', cleaned)
    cleaned = re.sub(r'\s+\(England\)$', '', cleaned)
    
    # 6. Handle Edgware Road stations with line descriptions
    if cleaned.startswith("Edgware Road ("):
        if "Bakerloo line" in cleaned:
            return "Edgware Road (Bak)"
        elif "Circle, District and Hammersmith & City lines" in cleaned:
            return "Edgware Road (Cir)"
    
    # 7. Handle Hammersmith stations with line descriptions
    if cleaned.startswith("Hammersmith ("):
        if "District and Piccadilly lines" in cleaned:
            return "Hammersmith (Dis)"
        elif "Circle and Hammersmith & City lines" in cleaned:
            return "Hammersmith (H&C)"
    
    # 8. Add line abbreviation for Shepherd's Bush if it doesn't have one
    if cleaned == "Shepherd's Bush":
        return "Shepherd's Bush (Cen)"
    
    # 9. Add apostrophes to St. names that are missing them
    # St James's Park -> St. James's Park
    # St John's Wood -> St. John's Wood  
    # St Paul's -> St. Paul's
    if cleaned == "St James's Park":
        return "St. James's Park"
    if cleaned == "St John's Wood":
        return "St. John's Wood"
    if cleaned == "St Paul's":
        return "St. Paul's"
    
    return cleaned

def scrape_borough_categories(main_url):
    """
    Scrape the main category page to get all borough subcategories
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(main_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all subcategory links
        borough_categories = []
        
        # Look for category links in the subcategories section
        subcategories_section = soup.find('div', id='mw-subcategories')
        if subcategories_section:
            category_links = subcategories_section.find_all('a', href=True)
            
            for link in category_links:
                href = link.get('href', '')
                if '/wiki/Category:Tube_stations_in_the_' in href:
                    full_url = urljoin(main_url, href)
                    category_name = link.get_text().strip()
                    
                    # Extract borough name from category title
                    borough_match = re.search(r'Tube stations in the (.+)', category_name)
                    if borough_match:
                        borough_name = borough_match.group(1).strip()
                        borough_categories.append({
                            'borough': borough_name,
                            'category_name': category_name,
                            'url': full_url
                        })
        
        # Also look for City of London link in the main content area
        content_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
        
        if content_div:
            # Look for any link that contains "City of London" in the main content
            all_links = content_div.find_all('a', href=True)
            for link in all_links:
                link_text = link.get_text().strip()
                href = link.get('href', '')
                
                # Check if this is a City of London tube stations link
                if (re.search(r'City of London', link_text, re.IGNORECASE) and 
                    '/wiki/Category:Tube_stations_in_the_City_of_London' in href):
                    full_url = urljoin(main_url, href)
                    borough_categories.append({
                        'borough': 'City of London',
                        'category_name': 'Tube stations in the City of London',
                        'url': full_url
                    })
                    print("Found City of London category link in main content")
                    break  # Found it, no need to continue searching
        
        return borough_categories
    
    except Exception as e:
        print(f"Error scraping borough categories: {e}")
        return []

def scrape_stations_from_borough(borough_info):
    """
    Scrape tube station names from a specific borough category page
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(borough_info['url'], headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the pages section
        pages_section = soup.find('div', id='mw-pages')
        if not pages_section:
            print(f"No pages section found for {borough_info['borough']}")
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
                    'borough': borough_info['borough'],
                    'full_name': station_name,
                    'url': urljoin(borough_info['url'], href)
                })
        
        return stations
    
    except Exception as e:
        print(f"Error scraping stations for {borough_info['borough']}: {e}")
        return []

def scrape_all_tube_stations():
    """
    Main function to scrape all tube stations and their boroughs
    """
    main_url = "https://en.wikipedia.org/wiki/Category:Tube_stations_in_London_by_borough"
    
    print("Scraping borough categories...")
    borough_categories = scrape_borough_categories(main_url)
    
    print(f"Found {len(borough_categories)} borough categories")
    
    all_stations = []
    
    for i, borough_info in enumerate(borough_categories, 1):
        print(f"Scraping {i}/{len(borough_categories)}: {borough_info['borough']}")
        
        stations = scrape_stations_from_borough(borough_info)
        all_stations.extend(stations)
        
        print(f"  Found {len(stations)} stations")
        
        # Be respectful - add a small delay between requests
        time.sleep(1)
    
    return all_stations

def save_to_csv(stations, filename='london_tube_stations_by_borough.csv'):
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
    df_output = df_output[['station_name', 'borough', 'full_name']].copy()
    
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
        "Kentish Town station",
        "Hampstead tube station", 
        "King's Cross St. Pancras underground station",
        "Baker Street (tube station)",
        "Oxford Circus (London Underground)",
        "Bond Street (London Underground station)",
        "Piccadilly Circus station",
        "Leicester Square",  # Already clean
        "Covent Garden (station)",
        "Holborn underground station"
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
    Test the OD compatibility station name cleaning function with the specific examples provided
    """
    test_cases = [
        ("Bank and Monuments", "Bank / Monument"),
        ("Edgware Road (Bakerloo line)", "Edgware Road (Bak)"),
        ("Edgware Road (Circle, District and Hammersmith & City lines)", "Edgware Road (Cir)"),
        ("Hammersmith (District and Piccadilly lines)", "Hammersmith (Dis)"),
        ("Hammersmith (Circle and Hammersmith & City lines)", "Hammersmith (H&C)"),
        ("Heathrow Terminals 2 & 3", "Heathrow Terminals 123"),
        ("King's Cross St Pancras", "King's Cross St. Pancras"),
        ("Kew Gardens (London)", "Kew Gardens"),
        ("Queen's Park (England)", "Queen's Park"),
        ("Richmond (London)", "Richmond"),
        ("Shepherd's Bush", "Shepherd's Bush (Cen)"),
        ("St James's Park", "St. James's Park"),
        ("St John's Wood", "St. John's Wood"),
        ("St Paul's", "St. Paul's"),
        # Paddington test cases
        ("Paddington (Bakerloo, Circle and District lines)", "Paddington"),
        ("Paddington (Circle and Hammersmith & City lines)", "Paddington"),
        # Test cases that should remain unchanged
        ("Oxford Circus", "Oxford Circus"),
        ("Waterloo", "Waterloo"),
        ("Piccadilly Circus", "Piccadilly Circus")
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
    print("Starting London Tube Stations scraper...")
    
    # Test the OD compatibility cleaning function
    test_od_compatibility_cleaning()
    print()

    # Scrape all stations
    stations = scrape_all_tube_stations()
    
    if stations:
        # Save to CSV
        save_to_csv(stations)
        
        # Also save detailed version with URLs for reference
        df_detailed = pd.DataFrame(stations)
        # Apply borough cleaning to detailed version too
        df_detailed['borough'] = df_detailed['borough'].apply(clean_borough_name)
        df_detailed.to_csv('london_tube_stations_detailed.csv', index=False)
        print("Also saved detailed version with URLs to london_tube_stations_detailed.csv")
        
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