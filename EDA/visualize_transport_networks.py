import igraph as ig
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('default')
sns.set_palette("husl")

def load_graph(graph_path):
    """
    Load a graph from GraphML file.
    
    Args:
        graph_path (str): Path to the graph file
        
    Returns:
        igraph.Graph: Loaded graph object
    """
    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Graph file not found: {graph_path}")
    
    return ig.Graph.Read_GraphML(graph_path)

def get_self_loop_weights(graph):
    """
    Get the weight of self-loops for each node.
    
    Args:
        graph (igraph.Graph): Graph object
        
    Returns:
        dict: Dictionary mapping node names to their self-loop weights
    """
    self_loops = {}
    for edge in graph.es:
        if edge.source == edge.target:  # Self-loop
            node_name = graph.vs[edge.source]['name']
            self_loops[node_name] = edge['weight']
    
    # Add 0 for nodes without self-loops
    for node in graph.vs:
        node_name = node['name']
        if node_name not in self_loops:
            self_loops[node_name] = 0
    
    return self_loops

def create_snapshot_graph(graph_path, output_path, title="Transport Network Snapshot"):
    """
    Create a snapshot visualization of a single graph.
    
    Args:
        graph_path (str): Path to the graph file
        output_path (str): Path to save the visualization
        title (str): Title for the plot
    """
    print(f"Creating snapshot graph: {title}")
    
    # Load graph
    g = load_graph(graph_path)
    
    # Get self-loop weights for node sizing
    self_loops = get_self_loop_weights(g)
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Calculate layout
    layout = g.layout_fruchterman_reingold()
    
    # Prepare node sizes based on self-loop weights
    node_sizes = []
    for node in g.vs:
        node_name = node['name']
        self_loop_weight = self_loops.get(node_name, 0)
        # Scale the size (log scale to handle large variations)
        size = max(50, 20 + np.log1p(self_loop_weight) * 30)
        node_sizes.append(size)
    
    # Prepare edge weights for visualization
    edge_weights = [edge['weight'] for edge in g.es]
    max_weight = max(edge_weights) if edge_weights else 1
    
    # Draw edges with varying thickness and color
    edge_colors = []
    edge_widths = []
    for weight in edge_weights:
        # Color based on weight (red for high, blue for low)
        normalized_weight = weight / max_weight
        edge_colors.append(plt.cm.Reds(normalized_weight))
        # Width based on weight (log scale)
        edge_widths.append(max(0.5, np.log1p(weight) * 0.5))
    
    # Plot the graph
    ig.plot(g, target=ax, layout=layout, 
            vertex_size=node_sizes,
            vertex_color='lightblue',
            vertex_label=g.vs['name'],
            vertex_label_size=8,
            edge_color=edge_colors,
            edge_width=edge_widths,
            edge_curved=0.2)
    
    # Customize the plot
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Network Layout (Force-directed)', fontsize=12)
    ax.set_ylabel('Node size ∝ Internal travel volume', fontsize=12)
    
    # Add legend for edge weights
    legend_elements = [
        plt.Line2D([0], [0], color='red', linewidth=3, label='High Flow'),
        plt.Line2D([0], [0], color='orange', linewidth=2, label='Medium Flow'),
        plt.Line2D([0], [0], color='lightcoral', linewidth=1, label='Low Flow')
    ]
    ax.legend(handles=legend_elements, loc='upper right', title='Edge Weight')
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Snapshot graph saved to: {output_path}")

def create_before_after_comparison(graph1_path, graph2_path, output_path, 
                                 title1="Before", title2="After"):
    """
    Create a before/after comparison visualization.
    
    Args:
        graph1_path (str): Path to the first graph (before)
        graph2_path (str): Path to the second graph (after)
        output_path (str): Path to save the visualization
        title1 (str): Title for the first graph
        title2 (str): Title for the second graph
    """
    print(f"Creating before/after comparison: {title1} vs {title2}")
    
    # Load both graphs
    g1 = load_graph(graph1_path)
    g2 = load_graph(graph2_path)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Process both graphs
    graphs = [g1, g2]
    axes = [ax1, ax2]
    titles = [title1, title2]
    
    for i, (g, ax, title) in enumerate(zip(graphs, axes, titles)):
        # Get self-loop weights
        self_loops = get_self_loop_weights(g)
        
        # Calculate layout
        layout = g.layout_fruchterman_reingold()
        
        # Prepare node sizes
        node_sizes = []
        for node in g.vs:
            node_name = node['name']
            self_loop_weight = self_loops.get(node_name, 0)
            size = max(50, 20 + np.log1p(self_loop_weight) * 30)
            node_sizes.append(size)
        
        # Prepare edge weights
        edge_weights = [edge['weight'] for edge in g.es]
        max_weight = max(edge_weights) if edge_weights else 1
        
        edge_colors = []
        edge_widths = []
        for weight in edge_weights:
            normalized_weight = weight / max_weight
            edge_colors.append(plt.cm.Reds(normalized_weight))
            edge_widths.append(max(0.5, np.log1p(weight) * 0.5))
        
        # Plot the graph
        ig.plot(g, target=ax, layout=layout,
                vertex_size=node_sizes,
                vertex_color='lightblue',
                vertex_label=g.vs['name'],
                vertex_label_size=8,
                edge_color=edge_colors,
                edge_width=edge_widths,
                edge_curved=0.2)
        
        ax.set_title(f"{title}\nNodes: {g.vcount()}, Edges: {g.ecount()}", 
                    fontsize=14, fontweight='bold')
    
    # Add overall title
    fig.suptitle("Transport Network Comparison", fontsize=18, fontweight='bold', y=0.95)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Before/after comparison saved to: {output_path}")

def create_heatmap(graph_path, output_path, title="Transport Flow Heatmap"):
    """
    Create a heatmap visualization of the adjacency matrix.
    
    Args:
        graph_path (str): Path to the graph file
        output_path (str): Path to save the visualization
        title (str): Title for the plot
    """
    print(f"Creating heatmap: {title}")
    
    # Load graph
    g = load_graph(graph_path)
    
    # Get borough names
    boroughs = [v['name'] for v in g.vs]
    n_boroughs = len(boroughs)
    
    # Create adjacency matrix
    adjacency_matrix = np.zeros((n_boroughs, n_boroughs))
    
    # Fill the matrix with edge weights
    for edge in g.es:
        source_idx = edge.source
        target_idx = edge.target
        weight = edge['weight']
        adjacency_matrix[source_idx, target_idx] = weight
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    
    # Create heatmap
    sns.heatmap(adjacency_matrix, 
                xticklabels=boroughs,
                yticklabels=boroughs,
                cmap='Reds',
                annot=False,  # Don't show numbers to avoid clutter
                cbar_kws={'label': 'Passenger Flow'},
                ax=ax)
    
    # Customize the plot
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Destination Borough', fontsize=12)
    ax.set_ylabel('Origin Borough', fontsize=12)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Heatmap saved to: {output_path}")

def create_statistical_summary(graph_path, output_path, title="Network Statistics"):
    """
    Create a statistical summary visualization.
    
    Args:
        graph_path (str): Path to the graph file
        output_path (str): Path to save the visualization
        title (str): Title for the plot
    """
    print(f"Creating statistical summary: {title}")
    
    # Load graph
    g = load_graph(graph_path)
    
    # Calculate statistics
    total_flow = sum(edge['weight'] for edge in g.es)
    avg_flow = total_flow / g.ecount() if g.ecount() > 0 else 0
    max_flow = max(edge['weight'] for edge in g.es) if g.ecount() > 0 else 0
    
    # Get self-loop statistics
    self_loops = get_self_loop_weights(g)
    internal_flows = [weight for weight in self_loops.values() if weight > 0]
    total_internal = sum(internal_flows)
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Top 10 boroughs by internal flow
    sorted_internal = sorted(self_loops.items(), key=lambda x: x[1], reverse=True)[:10]
    boroughs, flows = zip(*sorted_internal)
    
    ax1.barh(range(len(boroughs)), flows, color='skyblue')
    ax1.set_yticks(range(len(boroughs)))
    ax1.set_yticklabels(boroughs)
    ax1.set_xlabel('Internal Flow Volume')
    ax1.set_title('Top 10 Boroughs by Internal Travel')
    ax1.invert_yaxis()
    
    # Plot 2: Flow distribution histogram
    edge_weights = [edge['weight'] for edge in g.es]
    ax2.hist(edge_weights, bins=50, alpha=0.7, color='lightcoral', edgecolor='black')
    ax2.set_xlabel('Flow Weight')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Distribution of Flow Weights')
    ax2.set_yscale('log')
    
    # Plot 3: Network statistics
    stats_text = f"""
    Network Statistics:
    
    Nodes (Boroughs): {g.vcount()}
    Edges (Flows): {g.ecount()}
    Total Flow: {total_flow:,.0f}
    Average Flow: {avg_flow:,.0f}
    Maximum Flow: {max_flow:,.0f}
    Total Internal Flow: {total_internal:,.0f}
    """
    
    ax3.text(0.1, 0.5, stats_text, transform=ax3.transAxes, 
             fontsize=12, verticalalignment='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')
    ax3.set_title('Network Summary')
    
    # Plot 4: Borough connectivity (degree distribution)
    degrees = g.degree()
    ax4.hist(degrees, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
    ax4.set_xlabel('Degree (Number of Connections)')
    ax4.set_ylabel('Number of Boroughs')
    ax4.set_title('Borough Connectivity Distribution')
    
    # Overall title
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Statistical summary saved to: {output_path}")

def main():
    """
    Main function to generate all visualizations.
    """
    print("🚀 London Transport Network Visualizations")
    print("=" * 60)
    
    # Create output directory
    output_dir = "../Plots/network_visualizations"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define graph paths
    graphs = {
        "RODS_2015_total": "../Data/Graphs/RODS/2015/2015.graphml",
        "RODS_2015_am_peak": "../Data/Graphs/RODS/2015/time_bands/tb/2015_tb_am-peak.graphml",
        "NUMBAT_2019_total": "../Data/Graphs/NUMBAT/2019/2019.graphml",
        "NUMBAT_2019_MTT": "../Data/Graphs/NUMBAT/2019/MTT/2019_MTT.graphml",
        "NUMBAT_2022_total": "../Data/Graphs/NUMBAT/2022/2022.graphml",
        "NUMBAT_2022_MON": "../Data/Graphs/NUMBAT/2022/MON/2022_MON.graphml",
        "NUMBAT_2021_total": "../Data/Graphs/NUMBAT/2021/2021.graphml",
        "NUMBAT_2021_MTT_am_peak": "../Data/Graphs/NUMBAT/2021/MTT/time_bands/tb/2021_MTT_tb_am-peak.graphml"
    }
    
    # 1. Snapshot Graph - NUMBAT 2019 (pre-COVID stable year)
    print("\n1. Creating Snapshot Graph...")
    create_snapshot_graph(
        graphs["NUMBAT_2019_total"],
        f"{output_dir}/snapshot_numbat_2019_total.png",
        "London Transport Network 2019 (Pre-COVID)\nTotal Weekday Flow"
    )
    
    # 2. Before and After Comparison - AM Peak 2019 vs 2022
    print("\n2. Creating Before/After Comparison...")
    create_before_after_comparison(
        graphs["NUMBAT_2019_MTT"],
        graphs["NUMBAT_2022_MON"],
        f"{output_dir}/before_after_2019_vs_2022.png",
        "2019 (Pre-COVID)\nTuesday-Thursday",
        "2022 (Post-COVID)\nMonday"
    )
    
    # 3. Heatmaps
    print("\n3. Creating Heatmaps...")
    create_heatmap(
        graphs["NUMBAT_2019_total"],
        f"{output_dir}/heatmap_numbat_2019_total.png",
        "Transport Flow Heatmap 2019\n(Pre-COVID Total Weekday Flow)"
    )
    
    create_heatmap(
        graphs["NUMBAT_2022_total"],
        f"{output_dir}/heatmap_numbat_2022_total.png",
        "Transport Flow Heatmap 2022\n(Post-COVID Total Weekday Flow)"
    )
    
    # 4. Statistical Summaries
    print("\n4. Creating Statistical Summaries...")
    create_statistical_summary(
        graphs["NUMBAT_2019_total"],
        f"{output_dir}/stats_numbat_2019_total.png",
        "Network Statistics 2019 (Pre-COVID)"
    )
    
    create_statistical_summary(
        graphs["NUMBAT_2022_total"],
        f"{output_dir}/stats_numbat_2022_total.png",
        "Network Statistics 2022 (Post-COVID)"
    )
    
    # 5. Additional Comparisons
    print("\n5. Creating Additional Comparisons...")
    
    # RODS vs NUMBAT comparison (2015 vs 2019)
    create_before_after_comparison(
        graphs["RODS_2015_total"],
        graphs["NUMBAT_2019_total"],
        f"{output_dir}/rods_vs_numbat_2015_vs_2019.png",
        "RODS 2015\n(Survey-based)",
        "NUMBAT 2019\n(Smartcard-based)"
    )
    
    # AM Peak comparison
    create_before_after_comparison(
        graphs["RODS_2015_am_peak"],
        graphs["NUMBAT_2021_MTT_am_peak"],
        f"{output_dir}/am_peak_comparison_2015_vs_2021.png",
        "RODS 2015 AM Peak\n(Survey-based)",
        "NUMBAT 2021 AM Peak\n(Smartcard-based)"
    )
    
    print(f"\n{'='*60}")
    print("✅ ALL VISUALIZATIONS COMPLETED!")
    print(f"{'='*60}")
    print(f"📁 Visualizations saved to: {output_dir}")
    print("\n📊 Generated visualizations:")
    print("   1. Snapshot Graph (NUMBAT 2019)")
    print("   2. Before/After Comparison (2019 vs 2022)")
    print("   3. Heatmaps (2019 and 2022)")
    print("   4. Statistical Summaries (2019 and 2022)")
    print("   5. RODS vs NUMBAT Comparison")
    print("   6. AM Peak Comparison")
    print("\n🎯 Key insights to look for:")
    print("   - Node size indicates internal borough activity")
    print("   - Edge thickness/color shows flow intensity")
    print("   - Layout reveals spatial clustering")
    print("   - Heatmaps show flow patterns clearly")
    print("   - Statistics reveal network evolution")

if __name__ == "__main__":
    main()
