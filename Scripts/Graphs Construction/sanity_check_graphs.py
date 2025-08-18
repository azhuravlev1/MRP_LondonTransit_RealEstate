import igraph as ig
import os
import pandas as pd
from pathlib import Path

def analyze_graph(graph_path, description):
    """
    Analyze a graph and print key statistics.
    
    Args:
        graph_path (str): Path to the graph file
        description (str): Description of the graph
    """
    print(f"\n{'='*60}")
    print(f"ANALYZING: {description}")
    print(f"File: {graph_path}")
    print(f"{'='*60}")
    
    if not os.path.exists(graph_path):
        print(f"❌ File not found: {graph_path}")
        return
    
    try:
        # Load graph
        g = ig.Graph.Read_GraphML(graph_path)
        
        # Basic statistics
        print(f"✅ Graph loaded successfully")
        print(f"📊 Nodes (boroughs): {g.vcount()}")
        print(f"📊 Edges (flows): {g.ecount()}")
        print(f"📊 Directed: {g.is_directed()}")
        print(f"📊 Weighted: {g.is_weighted()}")
        
        # Node information
        print(f"\n🏘️  Boroughs (nodes):")
        boroughs = sorted([v['name'] for v in g.vs])
        for i, borough in enumerate(boroughs, 1):
            print(f"   {i:2d}. {borough}")
        
        # Edge weight statistics
        if g.is_weighted():
            weights = g.es['weight']
            print(f"\n⚖️  Edge weight statistics:")
            print(f"   Min weight: {min(weights):,.0f}")
            print(f"   Max weight: {max(weights):,.0f}")
            print(f"   Mean weight: {sum(weights)/len(weights):,.0f}")
            print(f"   Total flow: {sum(weights):,.0f}")
            
            # Top 5 heaviest edges
            print(f"\n🔝 Top 5 heaviest flows:")
            edge_data = []
            for edge in g.es:
                source = g.vs[edge.source]['name']
                target = g.vs[edge.target]['name']
                weight = edge['weight']
                edge_data.append((source, target, weight))
            
            edge_data.sort(key=lambda x: x[2], reverse=True)
            for i, (source, target, weight) in enumerate(edge_data[:5], 1):
                print(f"   {i}. {source} → {target}: {weight:,.0f}")
        
        # Check for self-loops (borough to itself)
        self_loops = [e for e in g.es if e.source == e.target]
        if self_loops:
            print(f"\n⚠️  Self-loops found: {len(self_loops)}")
            for loop in self_loops:
                borough = g.vs[loop.source]['name']
                weight = loop['weight']
                print(f"   {borough} → {borough}: {weight:,.0f}")
        else:
            print(f"\n✅ No self-loops found")
        
        # Check for isolated nodes
        isolated = [v for v in g.vs if v.degree() == 0]
        if isolated:
            print(f"\n⚠️  Isolated boroughs: {len(isolated)}")
            for node in isolated:
                print(f"   {node['name']}")
        else:
            print(f"\n✅ No isolated boroughs")
            
    except Exception as e:
        print(f"❌ Error analyzing graph: {str(e)}")

def main():
    """
    Perform sanity checks on sample graphs.
    """
    print("🔍 GRAPH SANITY CHECK")
    print("=" * 60)
    print("This script analyzes sample graphs to verify construction quality")
    print("=" * 60)
    
    # Define sample files to check
    sample_files = [
        # RODS samples
        {
            "path": "../Data/Graphs/RODS/2015/2015.graphml",
            "description": "RODS 2015 - All time bands combined"
        },
        {
            "path": "../Data/Graphs/RODS/2015/time_bands/tb/2015_tb_am-peak.graphml",
            "description": "RODS 2015 - AM Peak only"
        },
        {
            "path": "../Data/Graphs/RODS/2010/2010.graphml",
            "description": "RODS 2010 - All time bands combined"
        },
        
        # NUMBAT samples
        {
            "path": "../Data/Graphs/NUMBAT/2021/2021.graphml",
            "description": "NUMBAT 2021 - All days combined"
        },
        {
            "path": "../Data/Graphs/NUMBAT/2021/MTT/2021_MTT.graphml",
            "description": "NUMBAT 2021 - Tuesday-Thursday only"
        },
        {
            "path": "../Data/Graphs/NUMBAT/2021/MTT/time_bands/tb/2021_MTT_tb_am-peak.graphml",
            "description": "NUMBAT 2021 - MTT AM Peak only"
        },
        {
            "path": "../Data/Graphs/NUMBAT/2021/MTT/time_bands/qhr/2021_MTT_qhr_slot-29_0700-0715.graphml",
            "description": "NUMBAT 2021 - MTT 07:00-07:15 slot only"
        },
        {
            "path": "../Data/Graphs/NUMBAT/2019/2019.graphml",
            "description": "NUMBAT 2019 - Network level (all days)"
        },
        {
            "path": "../Data/Graphs/NUMBAT/2022/2022.graphml",
            "description": "NUMBAT 2022 - Network level (all days)"
        }
    ]
    
    # Analyze each sample
    for sample in sample_files:
        analyze_graph(sample["path"], sample["description"])
    
    print(f"\n{'='*60}")
    print("🏁 SANITY CHECK COMPLETED")
    print(f"{'='*60}")
    print("✅ Check the output above for any anomalies:")
    print("   - Expected: ~34 nodes (33 boroughs + 'Out of London')")
    print("   - Expected: Directed, weighted graphs")
    print("   - Expected: Reasonable flow values")
    print("   - Expected: No self-loops (borough to itself)")
    print("   - Expected: No isolated boroughs")

if __name__ == "__main__":
    main()
