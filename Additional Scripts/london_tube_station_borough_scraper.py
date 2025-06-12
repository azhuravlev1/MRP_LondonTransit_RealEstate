import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import pandas as pd
from urllib.parse import urljoin

def clean_station_name(station_name):
    """
    Clean station names by removing all variations of station suffixes
    """
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
    
    cleaned = station_name.strip()
    
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up any extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
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
    
    # Select and reorder columns
    df_output = df[['station_name', 'borough', 'full_name']].copy()
    
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

def main():
    """
    Main execution function
    """
    print("Starting London Tube Stations scraper...")
    
    # Show cleaning examples
    test_station_name_cleaning()
    
    # Scrape all stations
    stations = scrape_all_tube_stations()
    
    if stations:
        # Save to CSV
        save_to_csv(stations)
        
        # Also save detailed version with URLs for reference
        df_detailed = pd.DataFrame(stations)
        df_detailed.to_csv('london_tube_stations_detailed.csv', index=False)
        print("Also saved detailed version with URLs to london_tube_stations_detailed.csv")
        
        # Show some examples of cleaned names
        print("\nExample of cleaned station names:")
        df = pd.DataFrame(stations)
        sample = df[['full_name', 'station_name', 'borough']].sample(min(10, len(df)))
        for _, row in sample.iterrows():
            print(f"  '{row['full_name']}' -> '{row['station_name']}' ({row['borough']})")
    else:
        print("No stations were scraped")

if __name__ == "__main__":
    main()