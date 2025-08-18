# Accessibility Analysis Scripts

This folder contains scripts to calculate network accessibility metrics from the constructed graphs for panel regression analysis.

## Overview

The scripts calculate centrality measures and community structure metrics from the time series of directed, weighted graphs to quantify each borough's importance within London's transport network.

## Scripts

### 1. `calculate_centrality.py`
Calculates centrality metrics for all GraphML files in the input directory.

**Centrality Measures:**
- **Weighted In-Degree (Arrivals)**: Total passenger arrivals to each borough
- **Weighted Out-Degree (Departures)**: Total passenger departures from each borough  
- **Betweenness Centrality**: Borough's role as a "pass-through" corridor
- **Closeness Centrality**: Borough's overall reachability in the network
- **Eigenvector Centrality**: Borough's connection to other influential hubs

**Output:** `Data/Outputs/Metrics/centrality_metrics.csv`

### 2. `calculate_community_metrics.py`
Performs community detection and calculates community-based metrics.

**Community Metrics:**
- **Community ID**: Which functional travel cluster each borough belongs to
- **Participation Coefficient**: How evenly a borough's flows are distributed across communities

**Algorithm:** Leiden algorithm (high-quality refinement of Louvain method)

**Output:** `Data/Outputs/Metrics/community_metrics.csv`

### 3. `aggregate_results.py`
Merges centrality and community metrics into a comprehensive dataset.

**Merge Strategy:** Outer merge on key columns to identify any mismatches

**Output:** `Data/Outputs/Metrics/all_metrics_timeseries.csv`

## Usage

### Step 1: Calculate Centrality Metrics
```bash
cd Scripts/Accessibility_Analysis
python calculate_centrality.py
```

### Step 2: Calculate Community Metrics
```bash
python calculate_community_metrics.py
```

### Step 3: Aggregate Results
```bash
python aggregate_results.py
```

## File Structure

```
Data/
├── Graphs/                    # Input: GraphML files
│   ├── RODS/                 # 2000-2017
│   └── NUMBAT/               # 2017-2023
└── Outputs/
    └── Metrics/
        ├── centrality_metrics.csv
        ├── community_metrics.csv
        └── all_metrics_timeseries.csv
```

## Output Format

### Centrality Metrics CSV
| Column | Description |
|--------|-------------|
| Year | Year of the graph |
| DayType | Day type (MTT, FRI, SAT, SUN, etc.) |
| TimeBand | Time period (Total, AM_Peak, qhr_slot_XX, etc.) |
| Borough | Borough name |
| Weighted_In_Degree | Total passenger arrivals |
| Weighted_Out_Degree | Total passenger departures |
| Betweenness_Centrality | Betweenness centrality score |
| Closeness_Centrality | Closeness centrality score |
| Eigenvector_Centrality | Eigenvector centrality score |

### Community Metrics CSV
| Column | Description |
|--------|-------------|
| Year | Year of the graph |
| DayType | Day type |
| TimeBand | Time period |
| Borough | Borough name |
| Community_ID | Community cluster ID |
| Participation_Coefficient | Participation coefficient (0-1) |

### All Metrics CSV
Combined dataset with all centrality and community metrics for panel regression analysis.

## Technical Details

### Filename Parsing
The scripts automatically parse GraphML filenames to extract:
- **Year**: 4-digit year (e.g., "2015")
- **DayType**: Day type from filename (e.g., "MTT", "FRI", "SAT")
- **TimeBand**: Time period (e.g., "Total", "AM_Peak", "qhr_slot-29_0700-0715")

### Participation Coefficient
The participation coefficient P_i for node i is calculated as:
```
P_i = 1 - Σ_c (k_ic / k_i)^2
```
Where:
- k_i = total weighted degree of node i
- k_ic = sum of weights of links from node i to community c
- Sum is over all communities c

### Error Handling
- Graceful handling of disconnected graphs
- Fallback values for failed centrality calculations
- Comprehensive error reporting and logging

## Dependencies

Required Python packages:
- `pandas` - Data manipulation
- `igraph` - Graph analysis and centrality calculations
- `numpy` - Numerical operations
- `os`, `glob`, `re` - File operations and parsing

## Next Steps

After running these scripts, you will have a comprehensive dataset ready for:
1. Panel regression analysis with borough and year fixed effects
2. Temporal analysis of network evolution
3. Spatial analysis of accessibility impacts
4. Integration with housing price data for causal inference
