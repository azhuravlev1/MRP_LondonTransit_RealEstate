import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def get_unique_stations_count(file_path):
    """Get the number of unique stations in a RODS file."""
    try:
        df = pd.read_excel(file_path, sheet_name='matrix')
        # Get unique stations from both 'From' and 'To' columns
        from_stations = set(df.iloc[2:, 1].dropna().str.strip())
        to_stations = set(df.iloc[2:, 3].dropna().str.strip())
        all_stations = from_stations | to_stations
        return len(all_stations)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def analyze_rods_stations():
    """Analyze the number of unique stations in all RODS files."""
    # Get all RODS files
    root_dir = Path("/Users/andrey/Desktop/TMU/MRP/Code/Data")
    rods_files = []
    
    # First check the main RODS OD directory
    main_rods_dir = root_dir / "RODS OD"
    if main_rods_dir.exists():
        rods_files.extend(list(main_rods_dir.glob("*.xls")))
    
    # Then check the 2000-2002 directory
    old_rods_dir = root_dir / "Rods OD 2000-2002"
    if old_rods_dir.exists():
        rods_files.extend(list(old_rods_dir.glob("*.xls")))
    
    # Sort files by year
    rods_files.sort()
    
    # Analyze each file
    results = []
    for file_path in rods_files:
        year = file_path.stem.split('_')[1]  # Extract year from filename
        station_count = get_unique_stations_count(file_path)
        if station_count is not None:
            results.append({
                'year': year,
                'stations': station_count,
                'file': file_path.name
            })
    
    # Convert to DataFrame for easier analysis
    df_results = pd.DataFrame(results)
    
    # Print results
    print("\nRODS Station Count Analysis:")
    print("=" * 50)
    print(df_results.to_string(index=False))
    
    # Create a plot
    plt.figure(figsize=(12, 6))
    plt.plot(df_results['year'], df_results['stations'], marker='o')
    plt.title('Number of Unique Stations in RODS Files Over Time')
    plt.xlabel('Year')
    plt.ylabel('Number of Unique Stations')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('rods_station_counts.png')
    print("\nPlot saved as 'rods_station_counts.png'")
    
    # Additional analysis
    print("\nSummary Statistics:")
    print(f"Average number of stations: {df_results['stations'].mean():.2f}")
    print(f"Minimum number of stations: {df_results['stations'].min()}")
    print(f"Maximum number of stations: {df_results['stations'].max()}")
    print(f"Standard deviation: {df_results['stations'].std():.2f}")
    
    # Print years with changes in station count
    df_results['station_change'] = df_results['stations'].diff()
    changes = df_results[df_results['station_change'] != 0]
    if not changes.empty:
        print("\nYears with changes in station count:")
        for _, row in changes.iterrows():
            change = row['station_change']
            direction = "increased" if change > 0 else "decreased"
            print(f"{row['year']}: {direction} by {abs(change)} stations")

if __name__ == "__main__":
    analyze_rods_stations()
