# London Transport Network Graph Construction

This folder contains scripts to build directed, weighted graphs from London's transport data (RODS and NUMBAT) for network analysis.

## Overview

The scripts convert station-to-station passenger flow data into borough-to-borough network graphs, creating a comprehensive dataset for analyzing London's transport network evolution from 2000 to 2023.

## Scripts

### 1. `build_all_graphs.py` (Master Script)
**Recommended starting point** - Runs both RODS and NUMBAT graph construction with comprehensive error checking and progress tracking.

### 2. `build_rods_graphs.py`
Processes RODS (Rolling Origin-Destination Survey) data from 2000-2017.
- Reads Excel files from `Data/RODS_OD/`
- Creates borough-level aggregation of station flows
- Generates overall graphs and time-band specific graphs

### 3. `build_numbat_graphs.py`
Processes NUMBAT (Network Usage Model) data from 2017-2023.
- Reads CSV files from `Data/NUMBAT/OD_Matrices/`
- Handles both mode-specific and network-level files
- Creates complex directory structure with different time periods

## Usage

### Quick Start
```bash
cd "Graphs Construction"
python build_all_graphs.py
```

### Individual Scripts
```bash
# Build RODS graphs only
python build_rods_graphs.py

# Build NUMBAT graphs only  
python build_numbat_graphs.py
```

## Output Structure

### RODS Graphs (2000-2017)
```
Data/Graphs/RODS/
├── 2000/
│   ├── 2000.graphml                    # All time bands combined
│   └── time_bands/tb/
│       ├── 2000_tb_early.graphml
│       ├── 2000_tb_am-peak.graphml
│       ├── 2000_tb_midday.graphml
│       ├── 2000_tb_pm-peak.graphml
│       ├── 2000_tb_evening.graphml
│       └── 2000_tb_late.graphml
└── ... (2001-2017)
```

### NUMBAT Graphs (2017-2023)
```
Data/Graphs/NUMBAT/
├── 2017/
│   ├── 2017.graphml                    # All days combined
│   ├── MTT/                            # Tuesday-Thursday
│   │   ├── 2017_MTT.graphml
│   │   └── time_bands/
│   │       ├── tb/                     # 6 time bands
│   │       │   ├── 2017_MTT_tb_early.graphml
│   │       │   └── ...
│   │       └── qhr/                    # 96 quarter-hour slots
│   │           ├── 2017_MTT_qhr_slot-21_0500-0515.graphml
│   │           └── ...
│   ├── FRI/                            # Friday
│   ├── SAT/                            # Saturday  
│   └── SUN/                            # Sunday
└── ... (2018-2023)
```

## Graph Properties

- **Type**: Directed, weighted graphs
- **Nodes**: London boroughs (33) + "Out of London"
- **Edges**: Borough-to-borough passenger flows
- **Weights**: Passenger counts for the specified time period
- **Format**: GraphML (compatible with igraph, NetworkX, Gephi)

## Dependencies

Required Python packages:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `igraph` - Graph construction and analysis
- `tqdm` - Progress bars
- `openpyxl` - Excel file reading (for RODS)

Install with:
```bash
pip install pandas numpy igraph tqdm openpyxl
```

## Data Requirements

The scripts expect the following data structure:
```
Data/
├── RODS_OD/                           # RODS Excel files (2000-2017)
├── NUMBAT/OD_Matrices/                # NUMBAT CSV files (2017-2023)
└── station_borough_nlc_mapping.csv    # Station to borough mapping
```

## Time Periods

### RODS Time Bands
- **Early**: Before 7am
- **AM Peak**: 7am-10am  
- **Midday**: 10am-4pm
- **PM Peak**: 4pm-7pm
- **Evening**: 7pm-10pm
- **Late**: After 10pm

### NUMBAT Time Bands
- **Early**: 05:00-07:00 (slots 21-28)
- **AM Peak**: 07:00-11:00 (slots 29-44)
- **Midday**: 11:00-15:00 (slots 45-60)
- **PM Peak**: 15:00-19:00 (slots 61-76)
- **Evening**: 19:00-23:00 (slots 77-92)
- **Late**: 23:00-05:00 (slots 93-116)

## Error Handling

The scripts include comprehensive error handling:
- Missing files are reported but don't stop processing
- Invalid data is filtered out with warnings
- Progress bars show completion status
- Detailed error messages for debugging

## Performance Notes

- Processing time varies by year and data size
- NUMBAT years (2017-2023) take longer due to more granular data
- Memory usage scales with the number of unique station pairs
- Progress bars show estimated completion time

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Run `pip install pandas numpy igraph tqdm openpyxl`
2. **File not found errors**: Ensure data files are in the correct locations
3. **Memory errors**: Process years individually if memory is limited
4. **Permission errors**: Ensure write access to the output directory

### Debug Mode

For detailed debugging, run individual scripts and check the console output for specific error messages.

## Next Steps

After graph construction, you can:
1. Load graphs using igraph: `g = ig.Graph.Read_GraphML("path/to/graph.graphml")`
2. Calculate network metrics (centrality, betweenness, etc.)
3. Perform temporal analysis across years
4. Visualize network evolution using Gephi or similar tools
