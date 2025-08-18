import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import venn as venn_lib
import os
import glob
from pathlib import Path
import re

def get_data_path(relative_path):
    """Get the correct path to data files, whether running from AdditionalScripts/ or project root"""
    # Try relative to current directory first
    if os.path.exists(relative_path):
        return relative_path
    # If not found, try going up one level (if running from AdditionalScripts/)
    elif os.path.exists(os.path.join('..', relative_path)):
        return os.path.join('..', relative_path)
    else:
        raise FileNotFoundError(f"Could not find {relative_path}")

def load_house_price_data():
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

def load_station_borough_mappings():
    """Load borough names from all 4 station-borough mapping files"""
    mapping_files = {
        'DLR': 'Data/Station_Borough_Mappings/DLR_stations_by_borough.csv',
        'ELZ': 'Data/Station_Borough_Mappings/ELZ_stations_by_borough.csv',
        'LO': 'Data/Station_Borough_Mappings/LO_stations_by_borough.csv',
        'Tube': 'Data/Station_Borough_Mappings/london_tube_stations_by_borough.csv'
    }
    
    borough_sets = {}
    borough_dataframes = {}
    
    for system_name, file_path in mapping_files.items():
        try:
            full_path = get_data_path(file_path)
            df = pd.read_csv(full_path)
            
            # Clean borough names - remove any bracketed numbers and extra whitespace
            df['borough_clean'] = df['borough'].str.replace(r'\[.*?\]', '', regex=True).str.strip()
            
            # Get unique borough names
            borough_names = set(df['borough_clean'].dropna().unique())
            borough_sets[system_name] = borough_names
            borough_dataframes[system_name] = df
            
            print(f"Loaded {len(borough_names)} unique boroughs from {system_name}")
            
        except Exception as e:
            print(f"Error loading {system_name} data: {e}")
            borough_sets[system_name] = set()
            borough_dataframes[system_name] = pd.DataFrame()
    
    return borough_sets, borough_dataframes

def create_venn_diagrams(house_price_boroughs, borough_sets):
    """Create Venn diagrams for borough name comparisons"""
    
    # Save to Plots directory
    plots_path = get_data_path('Plots/')
    os.makedirs(plots_path, exist_ok=True)
    
    # Create figure with subplots for 2-way comparisons
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()
    
    # 1. House Price Index vs DLR
    venn2([house_price_boroughs, borough_sets['DLR']], 
          set_labels=('UK House Price Index', 'DLR Stations'), 
          ax=axes[0])
    axes[0].set_title('House Price Index vs DLR Boroughs', fontsize=12, fontweight='bold')
    
    # 2. House Price Index vs ELZ
    venn2([house_price_boroughs, borough_sets['ELZ']], 
          set_labels=('UK House Price Index', 'ELZ Stations'), 
          ax=axes[1])
    axes[1].set_title('House Price Index vs ELZ Boroughs', fontsize=12, fontweight='bold')
    
    # 3. House Price Index vs LO
    venn2([house_price_boroughs, borough_sets['LO']], 
          set_labels=('UK House Price Index', 'LO Stations'), 
          ax=axes[2])
    axes[2].set_title('House Price Index vs LO Boroughs', fontsize=12, fontweight='bold')
    
    # 4. House Price Index vs Tube
    venn2([house_price_boroughs, borough_sets['Tube']], 
          set_labels=('UK House Price Index', 'Tube Stations'), 
          ax=axes[3])
    axes[3].set_title('House Price Index vs Tube Boroughs', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_path, 'station_borough_compatibility_venn_diagrams.png'), dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create a comprehensive comparison with House Price Index and all station systems
    fig2, ax2 = plt.subplots(1, 1, figsize=(14, 10))
    
    # Combine all station systems
    all_station_boroughs = borough_sets['DLR'].union(borough_sets['ELZ']).union(borough_sets['LO']).union(borough_sets['Tube'])
    
    venn2([house_price_boroughs, all_station_boroughs], 
          set_labels=('UK House Price Index', 'All Station Systems Combined'), 
          ax=ax2)
    ax2.set_title('House Price Index vs All Station Systems Combined', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_path, 'house_price_vs_all_stations_venn.png'), 
               dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create a comprehensive 5-way Venn diagram using the venn library
    fig3, ax3 = plt.subplots(1, 1, figsize=(20, 16))
    
    # Create a 5-way Venn diagram
    all_sets = [house_price_boroughs, borough_sets['DLR'], borough_sets['ELZ'], 
               borough_sets['LO'], borough_sets['Tube']]
    all_labels = ['House Price Index', 'DLR', 'ELZ', 'LO', 'Tube']
    
    # Calculate all possible intersections for the 5 sets
    from itertools import combinations
    
    petal_labels = {}
    for i in range(1, 6):
        for combo in combinations(range(5), i):
            # Create a binary representation for the combination
            binary = ['0'] * 5
            for idx in combo:
                binary[idx] = '1'
            key = ''.join(binary)
            
            # Calculate the intersection
            intersection = all_sets[0]  # Start with first set
            for idx in combo:
                intersection = intersection.intersection(all_sets[idx])
            
            petal_labels[key] = len(intersection)
    
    # Use semi-transparent colors for better readability
    colors = ['#ff9999cc', '#66b3ffcc', '#99ff99cc', '#ffcc99cc', '#ff99cccc']  # Added alpha channel
    
    venn_lib.draw_venn(petal_labels=petal_labels, dataset_labels=all_labels, 
                      hint_hidden=False, colors=colors, 
                      figsize=(20, 16), fontsize=14, legend_loc='upper left', ax=ax3)
    ax3.set_title('Comprehensive Borough Names Comparison (All 5 Datasets)', 
                 fontsize=18, fontweight='bold', pad=20)
    
    # Add a subtitle with key statistics
    total_intersections = sum(petal_labels.values())
    ax3.text(0.5, 0.02, f'Total unique borough combinations: {total_intersections}', 
             transform=ax3.transAxes, ha='center', fontsize=12, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_path, 'station_borough_comprehensive_5way_venn.png'), 
               dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

def print_detailed_analysis(house_price_boroughs, borough_sets, borough_dataframes):
    """Print detailed analysis of borough name compatibility"""
    
    print("=" * 80)
    print("STATION-BOROUGH COMPATIBILITY ANALYSIS")
    print("=" * 80)
    
    # Overall statistics
    print("\n1. OVERALL STATISTICS")
    print("-" * 40)
    print(f"Number of boroughs in UK House Price Index: {len(house_price_boroughs)}")
    for system_name, borough_set in borough_sets.items():
        print(f"Number of boroughs in {system_name} stations: {len(borough_set)}")
    
    # Borough overlap analysis with House Price Index
    print("\n\n2. BOROUGH OVERLAP WITH HOUSE PRICE INDEX")
    print("-" * 50)
    
    for system_name, borough_set in borough_sets.items():
        intersection = house_price_boroughs.intersection(borough_set)
        only_in_house_price = house_price_boroughs - borough_set
        only_in_station = borough_set - house_price_boroughs
        
        print(f"\n{system_name} vs House Price Index:")
        print(f"  Boroughs in both: {len(intersection)}")
        print(f"  Boroughs only in House Price Index: {len(only_in_house_price)}")
        print(f"  Boroughs only in {system_name}: {len(only_in_station)}")
        print(f"  Overlap percentage: {len(intersection)/len(borough_set)*100:.1f}% of {system_name} boroughs")
        
        if only_in_station:
            print(f"  Boroughs only in {system_name}:")
            for borough in sorted(only_in_station):
                print(f"    - {borough}")
    
    # Cross-station system comparison
    print("\n\n3. CROSS-STATION SYSTEM COMPARISON")
    print("-" * 40)
    
    station_systems = list(borough_sets.keys())
    for i, system1 in enumerate(station_systems):
        for system2 in station_systems[i+1:]:
            intersection = borough_sets[system1].intersection(borough_sets[system2])
            print(f"\n{system1} vs {system2}:")
            print(f"  Common boroughs: {len(intersection)}")
            print(f"  Only in {system1}: {len(borough_sets[system1] - borough_sets[system2])}")
            print(f"  Only in {system2}: {len(borough_sets[system2] - borough_sets[system1])}")
    
    # Boroughs in all station systems
    print("\n\n4. BOROUGHS IN ALL STATION SYSTEMS")
    print("-" * 40)
    all_station_boroughs = borough_sets['DLR'].intersection(borough_sets['ELZ']).intersection(borough_sets['LO']).intersection(borough_sets['Tube'])
    print(f"Boroughs present in all 4 station systems: {len(all_station_boroughs)}")
    if all_station_boroughs:
        for borough in sorted(all_station_boroughs):
            print(f"  - {borough}")
    
    # Boroughs in all 5 datasets (including House Price Index)
    print("\n\n5. BOROUGHS IN ALL 5 DATASETS")
    print("-" * 40)
    all_datasets_boroughs = house_price_boroughs.intersection(all_station_boroughs)
    print(f"Boroughs present in all 5 datasets: {len(all_datasets_boroughs)}")
    if all_datasets_boroughs:
        for borough in sorted(all_datasets_boroughs):
            print(f"  - {borough}")
    
    # Unique boroughs by system
    print("\n\n6. UNIQUE BOROUGHS BY SYSTEM")
    print("-" * 40)
    
    for system_name, borough_set in borough_sets.items():
        other_systems = [s for s in borough_sets.keys() if s != system_name]
        other_boroughs = set().union(*[borough_sets[s] for s in other_systems])
        unique_to_system = borough_set - other_boroughs
        
        print(f"\nBoroughs unique to {system_name}: {len(unique_to_system)}")
        if unique_to_system:
            for borough in sorted(unique_to_system):
                print(f"  - {borough}")

def print_station_counts_by_borough(borough_dataframes):
    """Print station counts by borough for each system"""
    
    print("\n\n7. STATION COUNTS BY BOROUGH")
    print("-" * 40)
    
    for system_name, df in borough_dataframes.items():
        if not df.empty:
            print(f"\n{system_name} Stations by Borough:")
            borough_counts = df['borough_clean'].value_counts().sort_index()
            for borough, count in borough_counts.items():
                print(f"  {borough}: {count} stations")

def print_5way_venn_details(house_price_boroughs, borough_sets):
    """Print detailed breakdown of the 5-way Venn diagram intersections"""
    
    print("\n\n9. DETAILED 5-WAY VENN DIAGRAM BREAKDOWN")
    print("-" * 50)
    
    all_sets = [house_price_boroughs, borough_sets['DLR'], borough_sets['ELZ'], 
               borough_sets['LO'], borough_sets['Tube']]
    all_labels = ['House Price Index', 'DLR', 'ELZ', 'LO', 'Tube']
    
    from itertools import combinations
    
    # Group intersections by number of sets
    intersections_by_count = {}
    
    for i in range(1, 6):
        intersections_by_count[i] = []
        for combo in combinations(range(5), i):
            # Calculate the intersection
            intersection = all_sets[0]  # Start with first set
            for idx in combo:
                intersection = intersection.intersection(all_sets[idx])
            
            if intersection:  # Only show non-empty intersections
                set_names = [all_labels[idx] for idx in combo]
                intersections_by_count[i].append((set_names, intersection))
    
    # Print results organized by intersection count
    for count in range(1, 6):
        if intersections_by_count[count]:
            print(f"\nIntersections of {count} dataset(s):")
            for set_names, intersection in intersections_by_count[count]:
                print(f"  {' + '.join(set_names)}: {len(intersection)} boroughs")
                if count <= 3:  # Show actual borough names for smaller intersections
                    print(f"    Boroughs: {sorted(intersection)}")

def check_standardized_all_stations_overlap():
    """Check overlap between all standardized stations and UK House Price Index"""
    
    print("\n" + "="*80)
    print("ALL STANDARDIZED STATIONS vs UK HOUSE PRICE INDEX OVERLAP")
    print("="*80)
    
    try:
        # Load all standardized stations data
        all_stations_file = get_data_path('Data/Station_Borough_Mappings/Standardized/all_stations_by_borough_standardized.csv')
        all_stations_df = pd.read_csv(all_stations_file)
        
        # Load house price boroughs
        house_price_boroughs = load_house_price_data()
        
        # Get unique standardized boroughs from all stations data
        all_stations_boroughs = set(all_stations_df['borough_standardized'].unique())
        
        # Calculate overlaps
        overlapping = house_price_boroughs.intersection(all_stations_boroughs)
        only_in_house_price = house_price_boroughs - all_stations_boroughs
        only_in_stations = all_stations_boroughs - house_price_boroughs
        
        # Print results
        print(f"\nAll Stations Analysis:")
        print(f"  Total stations: {len(all_stations_df)}")
        print(f"  Unique standardized boroughs: {len(all_stations_boroughs)}")
        print(f"  Boroughs: {sorted(all_stations_boroughs)}")
        
        print(f"\nHouse Price Index Analysis:")
        print(f"  Total boroughs: {len(house_price_boroughs)}")
        print(f"  Boroughs: {sorted(house_price_boroughs)}")
        
        print(f"\nOverlap Analysis:")
        print(f"  Overlapping boroughs: {len(overlapping)}")
        print(f"  Overlap percentage: {len(overlapping)/len(house_price_boroughs)*100:.1f}% of House Price Index boroughs")
        print(f"  Overlap percentage: {len(overlapping)/len(all_stations_boroughs)*100:.1f}% of Station boroughs")
        
        if overlapping:
            print(f"  Overlapping boroughs: {sorted(overlapping)}")
        
        if only_in_house_price:
            print(f"\nBoroughs only in House Price Index ({len(only_in_house_price)}):")
            for borough in sorted(only_in_house_price):
                print(f"  - {borough}")
        
        if only_in_stations:
            print(f"\nBoroughs only in Station data ({len(only_in_stations)}):")
            for borough in sorted(only_in_stations):
                print(f"  - {borough}")
        
        # Station counts by borough
        print(f"\nAll Station Counts by Borough:")
        borough_counts = all_stations_df['borough_standardized'].value_counts().sort_index()
        for borough, count in borough_counts.items():
            status = "✓" if borough in overlapping else "✗"
            print(f"  {status} {borough}: {count} stations")
        
        # Station counts by system
        print(f"\nStation Counts by System:")
        system_counts = all_stations_df['system'].value_counts().sort_index()
        for system, count in system_counts.items():
            print(f"  {system}: {count} stations")
        
        return all_stations_df, house_price_boroughs, overlapping, only_in_house_price, only_in_stations
        
    except Exception as e:
        print(f"Error checking standardized all stations overlap: {e}")
        return None, None, None, None, None

def create_standardized_venn_diagram():
    """Create Venn diagram comparing standardized all stations with UK House Price Index"""
    
    try:
        # Load all standardized stations data
        all_stations_file = get_data_path('Data/Station_Borough_Mappings/Standardized/all_stations_by_borough_standardized.csv')
        all_stations_df = pd.read_csv(all_stations_file)
        
        # Load house price boroughs
        house_price_boroughs = load_house_price_data()
        
        # Get unique standardized boroughs from all stations data
        all_stations_boroughs = set(all_stations_df['borough_standardized'].unique())
        
        # Create Venn diagram
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        venn2([house_price_boroughs, all_stations_boroughs], 
              set_labels=('UK House Price Index\nBoroughs', 'All Standardized Stations\nBoroughs'), 
              ax=ax)
        ax.set_title('Standardized All Stations vs UK House Price Index Boroughs', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add statistics as text
        overlapping = house_price_boroughs.intersection(all_stations_boroughs)
        only_in_house_price = house_price_boroughs - all_stations_boroughs
        only_in_stations = all_stations_boroughs - house_price_boroughs
        
        stats_text = f'Total Stations: {len(all_stations_df)}\n'
        stats_text += f'Overlap: {len(overlapping)} boroughs\n'
        stats_text += f'Only in House Price Index: {len(only_in_house_price)}\n'
        stats_text += f'Only in Stations: {len(only_in_stations)}'
        
        ax.text(0.5, 0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=12, 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        plt.tight_layout()
        
        # Save to Plots directory
        plots_path = get_data_path('Plots/')
        os.makedirs(plots_path, exist_ok=True)
        plt.savefig(os.path.join(plots_path, 'standardized_all_stations_vs_house_price_venn.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
        
        print(f"\nVenn diagram saved to: Plots/standardized_all_stations_vs_house_price_venn.png")
        
    except Exception as e:
        print(f"Error creating standardized Venn diagram: {e}")

def print_borough_name_variations(house_price_boroughs, borough_sets):
    """Print potential borough name variations and inconsistencies"""
    
    print("\n\n8. BOROUGH NAME VARIATIONS ANALYSIS")
    print("-" * 40)
    
    # Collect all borough names
    all_boroughs = set()
    for borough_set in borough_sets.values():
        all_boroughs.update(borough_set)
    all_boroughs.update(house_price_boroughs)
    
    # Look for potential variations (same borough, different names)
    borough_variations = {}
    
    for borough in all_boroughs:
        # Remove common prefixes/suffixes and normalize
        normalized = re.sub(r'\b(Borough of|Royal Borough of|City of)\s+', '', borough, flags=re.IGNORECASE)
        normalized = normalized.strip()
        
        if normalized not in borough_variations:
            borough_variations[normalized] = []
        borough_variations[normalized].append(borough)
    
    # Show variations
    print("Potential borough name variations:")
    found_variations = False
    for normalized, variations in borough_variations.items():
        if len(variations) > 1:
            print(f"  {normalized}: {variations}")
            found_variations = True
    
    if not found_variations:
        print("  No significant borough name variations found.")
        print("  All borough names appear to be consistent across datasets.")

def main():
    """Main function to run the analysis"""
    print("Starting station-borough compatibility analysis...")
    
    # Load data
    house_price_boroughs = load_house_price_data()
    borough_sets, borough_dataframes = load_station_borough_mappings()
    
    # Create Venn diagrams
    create_venn_diagrams(house_price_boroughs, borough_sets)
    
    # Print detailed analysis
    print_detailed_analysis(house_price_boroughs, borough_sets, borough_dataframes)
    print_station_counts_by_borough(borough_dataframes)
    print_borough_name_variations(house_price_boroughs, borough_sets)
    print_5way_venn_details(house_price_boroughs, borough_sets)
    
    # Check standardized all stations overlap
    check_standardized_all_stations_overlap()
    
    # Create Venn diagram for standardized data
    create_standardized_venn_diagram()
    
    print("\nAnalysis complete! Venn diagrams saved to Plots/ directory")
    
    return house_price_boroughs, borough_sets, borough_dataframes

if __name__ == "__main__":
    main()
