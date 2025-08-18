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
    Create a before/after comparison visualization with fixed layout.
    
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
        
        # Calculate layout for each graph individually
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

def create_network_statistics_excel(graph_path, output_path, title="Network Statistics"):
    """
    Create an Excel file with comprehensive network statistics.
    
    Args:
        graph_path (str): Path to the graph file
        output_path (str): Path to save the Excel file
        title (str): Title for the analysis
    """
    print(f"Creating network statistics Excel: {title}")
    
    # Load graph
    g = load_graph(graph_path)
    
    # Calculate basic statistics
    total_flow = sum(edge['weight'] for edge in g.es)
    avg_flow = total_flow / g.ecount() if g.ecount() > 0 else 0
    max_flow = max(edge['weight'] for edge in g.es) if g.ecount() > 0 else 0
    min_flow = min(edge['weight'] for edge in g.es) if g.ecount() > 0 else 0
    
    # Get self-loop statistics
    self_loops = get_self_loop_weights(g)
    internal_flows = [weight for weight in self_loops.values() if weight > 0]
    total_internal = sum(internal_flows)
    
    # Calculate borough-level statistics
    borough_stats = []
    for node in g.vs:
        node_name = node['name']
        
        # Incoming flows
        incoming_edges = g.incident(node, mode="in")
        total_in = sum(g.es[incoming_edges]['weight'])
        
        # Outgoing flows
        outgoing_edges = g.incident(node, mode="out")
        total_out = sum(g.es[outgoing_edges]['weight'])
        
        # Internal flow (self-loop)
        internal_flow = self_loops.get(node_name, 0)
        
        # Degree (number of connections)
        degree = g.degree(node)
        
        borough_stats.append({
            'Borough': node_name,
            'Total_Incoming_Flow': round(total_in, 1),
            'Total_Outgoing_Flow': round(total_out, 1),
            'Internal_Flow': round(internal_flow, 1),
            'Total_Flow': round(total_in + total_out, 1),
            'Degree': degree,
            'Average_Incoming_Flow': round(total_in / len(incoming_edges), 1) if incoming_edges else 0,
            'Average_Outgoing_Flow': round(total_out / len(outgoing_edges), 1) if outgoing_edges else 0
        })
    
    # Sort by total flow
    borough_stats.sort(key=lambda x: x['Total_Flow'], reverse=True)
    
    # Create Excel file
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary statistics
        summary_data = {
            'Metric': [
                'Nodes (Boroughs)',
                'Edges (Flows)',
                'Total Flow',
                'Average Flow',
                'Maximum Flow',
                'Minimum Flow',
                'Total Internal Flow',
                'Average Internal Flow per Borough',
                'Network Density',
                'Average Degree'
            ],
            'Value': [
                g.vcount(),
                g.ecount(),
                f"{round(total_flow, 1):,.0f}",
                f"{round(avg_flow, 1):,.0f}",
                f"{round(max_flow, 1):,.0f}",
                f"{round(min_flow, 1):,.0f}",
                f"{round(total_internal, 1):,.0f}",
                f"{round(total_internal/g.vcount(), 1):,.0f}",
                f"{round(g.ecount()/(g.vcount()*(g.vcount()-1)), 4)}",
                f"{round(sum(g.degree())/g.vcount(), 1)}"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
        
        # Borough-level statistics
        borough_df = pd.DataFrame(borough_stats)
        borough_df.to_excel(writer, sheet_name='Borough_Statistics', index=False)
        
        # Top flows
        edge_data = []
        for edge in g.es:
            source_name = g.vs[edge.source]['name']
            target_name = g.vs[edge.target]['name']
            edge_data.append({
                'Origin': source_name,
                'Destination': target_name,
                'Flow_Weight': round(edge['weight'], 1)
            })
        
        edge_df = pd.DataFrame(edge_data)
        edge_df = edge_df.sort_values('Flow_Weight', ascending=False)
        edge_df.to_excel(writer, sheet_name='Top_Flows', index=False)
        
        # Internal flows only
        internal_df = edge_df[edge_df['Origin'] == edge_df['Destination']].copy()
        internal_df.to_excel(writer, sheet_name='Internal_Flows', index=False)
    
    print(f"Network statistics Excel saved to: {output_path}")

def create_combined_network_statistics(graph1_path, graph2_path, output_path):
    """
    Create a combined Excel file comparing network statistics between two years.
    
    Args:
        graph1_path (str): Path to the first graph (2019)
        graph2_path (str): Path to the second graph (2022)
        output_path (str): Path to save the combined Excel file
    """
    print(f"Creating combined network statistics comparison...")
    
    # Load both graphs
    g1 = load_graph(graph1_path)
    g2 = load_graph(graph2_path)
    
    # Calculate statistics for both graphs
    def calculate_graph_stats(g):
        total_flow = sum(edge['weight'] for edge in g.es)
        avg_flow = total_flow / g.ecount() if g.ecount() > 0 else 0
        max_flow = max(edge['weight'] for edge in g.es) if g.ecount() > 0 else 0
        min_flow = min(edge['weight'] for edge in g.es) if g.ecount() > 0 else 0
        
        # Get self-loop statistics
        self_loops = get_self_loop_weights(g)
        total_internal = sum(self_loops.values())
        
        return {
            'Nodes (Boroughs)': g.vcount(),
            'Edges (Flows)': g.ecount(),
            'Total Flow': total_flow,
            'Average Flow': avg_flow,
            'Maximum Flow': max_flow,
            'Minimum Flow': min_flow,
            'Total Internal Flow': total_internal,
            'Average Internal Flow per Borough': total_internal / g.vcount(),
            'Network Density': g.ecount() / (g.vcount() * (g.vcount() - 1)),
            'Average Degree': sum(g.degree()) / g.vcount()
        }
    
    stats_2019 = calculate_graph_stats(g1)
    stats_2022 = calculate_graph_stats(g2)
    
    # Create comparison DataFrame
    comparison_data = {
        'Metric': list(stats_2019.keys()),
        '2019': [round(stats_2019[key], 1) for key in stats_2019.keys()],
        '2022': [round(stats_2022[key], 1) for key in stats_2022.keys()],
        'Change (%)': [round(((stats_2022[key] - stats_2019[key]) / stats_2019[key] * 100), 1) if stats_2019[key] != 0 else 0 for key in stats_2019.keys()]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Calculate borough-level statistics for both years
    def calculate_borough_stats(g):
        borough_stats = []
        for node in g.vs:
            node_name = node['name']
            
            # Incoming flows
            incoming_edges = g.incident(node, mode="in")
            total_in = sum(g.es[incoming_edges]['weight'])
            
            # Outgoing flows
            outgoing_edges = g.incident(node, mode="out")
            total_out = sum(g.es[outgoing_edges]['weight'])
            
            # Internal flow (self-loop)
            self_loops = get_self_loop_weights(g)
            internal_flow = self_loops.get(node_name, 0)
            
            borough_stats.append({
                'Borough': node_name,
                'Total_Incoming_Flow': round(total_in, 1),
                'Total_Outgoing_Flow': round(total_out, 1),
                'Internal_Flow': round(internal_flow, 1),
                'Total_Flow': round(total_in + total_out, 1),
                'Degree': g.degree(node)
            })
        
        return pd.DataFrame(borough_stats).sort_values('Total_Flow', ascending=False)
    
    borough_stats_2019 = calculate_borough_stats(g1)
    borough_stats_2022 = calculate_borough_stats(g2)
    
    # Merge borough statistics
    borough_comparison = borough_stats_2019.merge(
        borough_stats_2022, 
        on='Borough', 
        suffixes=('_2019', '_2022')
    )
    
    # Calculate percentage changes for borough statistics
    for col in ['Total_Incoming_Flow', 'Total_Outgoing_Flow', 'Internal_Flow', 'Total_Flow']:
        borough_comparison[f'{col}_Change_%'] = round(
            (borough_comparison[f'{col}_2022'] - borough_comparison[f'{col}_2019']) / 
            borough_comparison[f'{col}_2019'] * 100, 1
        ).fillna(0)
    
    # Create Excel file
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary comparison
        comparison_df.to_excel(writer, sheet_name='Summary_Comparison', index=False)
        
        # Borough comparison
        borough_comparison.to_excel(writer, sheet_name='Borough_Comparison', index=False)
        
        # Top flows comparison
        def get_top_flows(g, year):
            edge_data = []
            for edge in g.es:
                source_name = g.vs[edge.source]['name']
                target_name = g.vs[edge.target]['name']
                edge_data.append({
                    'Origin': source_name,
                    'Destination': target_name,
                    f'Flow_Weight_{year}': round(edge['weight'], 1)
                })
            return pd.DataFrame(edge_data).sort_values(f'Flow_Weight_{year}', ascending=False)
        
        top_flows_2019 = get_top_flows(g1, '2019')
        top_flows_2022 = get_top_flows(g2, '2022')
        
        # Merge top flows (only for flows that exist in both years)
        top_flows_comparison = top_flows_2019.merge(
            top_flows_2022,
            on=['Origin', 'Destination'],
            how='outer'
        ).fillna(0)
        
        # Calculate percentage change
        top_flows_comparison['Flow_Weight_Change_%'] = round(
            (top_flows_comparison['Flow_Weight_2022'] - top_flows_comparison['Flow_Weight_2019']) / 
            top_flows_comparison['Flow_Weight_2019'] * 100, 1
        ).fillna(0)
        
        top_flows_comparison.to_excel(writer, sheet_name='Top_Flows_Comparison', index=False)
    
    print(f"Combined network statistics comparison saved to: {output_path}")

def create_statistical_summary(graph_path, output_path, title="Network Statistics", reference_graph_path=None):
    """
    Create a statistical summary visualization.
    
    Args:
        graph_path (str): Path to the graph file
        output_path (str): Path to save the visualization
        title (str): Title for the plot
        reference_graph_path (str): Path to reference graph for consistent scales
    """
    print(f"Creating statistical summary: {title}")
    
    # Load graph
    g = load_graph(graph_path)
    
    # Load reference graph for consistent scales if provided
    reference_g = None
    if reference_graph_path and os.path.exists(reference_graph_path):
        reference_g = load_graph(reference_graph_path)
    
    # Calculate statistics
    total_flow = sum(edge['weight'] for edge in g.es)
    avg_flow = total_flow / g.ecount() if g.ecount() > 0 else 0
    max_flow = max(edge['weight'] for edge in g.es) if g.ecount() > 0 else 0
    
    # Get self-loop statistics
    self_loops = get_self_loop_weights(g)
    internal_flows = [weight for weight in self_loops.values() if weight > 0]
    total_internal = sum(internal_flows)
    
    # Get reference statistics for consistent scales
    if reference_g:
        reference_self_loops = get_self_loop_weights(reference_g)
        reference_edge_weights = [edge['weight'] for edge in reference_g.es]
        reference_degrees = reference_g.degree()
        
        # Calculate reference ranges
        max_internal_flow_ref = max(reference_self_loops.values()) if reference_self_loops else 0
        max_flow_weight_ref = max(reference_edge_weights) if reference_edge_weights else 0
        max_degree_ref = max(reference_degrees) if reference_degrees else 0
    else:
        max_internal_flow_ref = max(self_loops.values()) if self_loops else 0
        max_flow_weight_ref = max_flow
        max_degree_ref = max(g.degree()) if g.degree() else 0
    
    # Create figure with subplots (only top row)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: Top 10 boroughs by internal flow
    sorted_internal = sorted(self_loops.items(), key=lambda x: x[1], reverse=True)[:10]
    boroughs, flows = zip(*sorted_internal)
    
    ax1.barh(range(len(boroughs)), flows, color='skyblue')
    ax1.set_yticks(range(len(boroughs)))
    ax1.set_yticklabels(boroughs)
    ax1.set_xlabel('Internal Flow Volume')
    ax1.set_title('Top 10 Boroughs by Internal Travel')
    ax1.invert_yaxis()
    
    # Set consistent x-axis scale for internal flows
    if reference_g:
        ax1.set_xlim(0, max_internal_flow_ref * 1.1)  # 10% margin
    
    # Plot 2: Flow distribution histogram
    edge_weights = [edge['weight'] for edge in g.es]

    # Set consistent x-axis scale for flow weights first
    if reference_g:
        x_max = max_flow_weight_ref * 1.1  # 10% margin based on reference
    else:
        x_max = (max(edge_weights) * 1.1) if edge_weights else 1.0

    # Create exactly 50 bins from 0 to x_max
    bin_width = x_max / 50 if x_max > 0 else 1.0
    bin_centers = np.arange(bin_width / 2, x_max, bin_width)  # Center of each bin
    bin_edges = np.arange(0, x_max + bin_width, bin_width)  # Edges of bins

    # Manual histogram with exact control over bar positions for both cases
    hist, _ = np.histogram(edge_weights, bins=bin_edges)
    # Filter out zero counts to avoid log(0) issues
    non_zero_mask = hist > 0
    ax2.bar(bin_centers[non_zero_mask], hist[non_zero_mask],
            width=bin_width * 0.9, alpha=0.7, color='lightcoral', edgecolor='black')

    ax2.set_xlabel('Flow Weight')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Distribution of Flow Weights')
    ax2.set_yscale('log')

    # Enforce x-axis starting at 0 and ending at x_max
    ax2.set_xlim(0, x_max)
    
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
    
    # Get the script's directory and determine the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from EDA to Code
    
    print(f"Script directory: {script_dir}")
    print(f"Project root: {project_root}")
    
    # Create output directory
    output_dir = os.path.join(project_root, "Plots", "network_visualizations")
    os.makedirs(output_dir, exist_ok=True)
    
    # Define graph paths using absolute paths
    graphs = {
        "RODS_2015_total": os.path.join(project_root, "Data", "Graphs", "RODS", "2015", "2015.graphml"),
        "RODS_2015_am_peak": os.path.join(project_root, "Data", "Graphs", "RODS", "2015", "time_bands", "tb", "2015_tb_am-peak.graphml"),
        "RODS_2017_total": os.path.join(project_root, "Data", "Graphs", "RODS", "2017", "2017.graphml"),
        "NUMBAT_2017_total": os.path.join(project_root, "Data", "Graphs", "NUMBAT", "2017", "2017.graphml"),
        "NUMBAT_2019_total": os.path.join(project_root, "Data", "Graphs", "NUMBAT", "2019", "2019.graphml"),
        "NUMBAT_2019_MTT": os.path.join(project_root, "Data", "Graphs", "NUMBAT", "2019", "MTT", "2019_MTT.graphml"),
        "NUMBAT_2022_total": os.path.join(project_root, "Data", "Graphs", "NUMBAT", "2022", "2022.graphml"),
        "NUMBAT_2022_MON": os.path.join(project_root, "Data", "Graphs", "NUMBAT", "2022", "MON", "2022_MON.graphml"),
        "NUMBAT_2021_total": os.path.join(project_root, "Data", "Graphs", "NUMBAT", "2021", "2021.graphml"),
        "NUMBAT_2021_MTT_am_peak": os.path.join(project_root, "Data", "Graphs", "NUMBAT", "2021", "MTT", "time_bands", "tb", "2021_MTT_tb_am-peak.graphml")
    }
    
    # 1. Snapshot Graph - NUMBAT 2019 (pre-COVID stable year)
    print("\n1. Creating Snapshot Graph...")
    create_snapshot_graph(
        graphs["NUMBAT_2019_total"],
        f"{output_dir}/snapshot_numbat_2019_total.png",
        "London Transport Network 2019 (Pre-COVID)\nTotal Weekday Flow"
    )
    
    # 2. General Network Examples
    print("\n2. Creating General Network Examples...")
    create_snapshot_graph(
        graphs["RODS_2017_total"],
        f"{output_dir}/example_rods_network_2017.png",
        "RODS Network Example 2017\n(Survey-based Data)"
    )
    
    create_snapshot_graph(
        graphs["NUMBAT_2017_total"],
        f"{output_dir}/example_numbat_network_2017.png",
        "NUMBAT Network Example 2017\n(Smartcard-based Data)"
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
    
    # 4. Network Statistics Excel Files
    print("\n4. Creating Network Statistics Excel Files...")
    
    # Create individual year files
    create_network_statistics_excel(
        graphs["NUMBAT_2019_total"],
        f"{output_dir}/network_statistics_2019.xlsx",
        "Network Statistics 2019 (Pre-COVID)"
    )
    
    create_network_statistics_excel(
        graphs["NUMBAT_2022_total"],
        f"{output_dir}/network_statistics_2022.xlsx",
        "Network Statistics 2022 (Post-COVID)"
    )
    
    # Create combined comparison file
    print("Creating combined network statistics comparison...")
    create_combined_network_statistics(
        graphs["NUMBAT_2019_total"],
        graphs["NUMBAT_2022_total"],
        f"{output_dir}/network_statistics_comparison.xlsx"
    )
    
    # 4b. Simplified Statistical Summary Plots (top 2 plots only)
    print("\n4b. Creating Simplified Statistical Summary Plots...")
    create_statistical_summary(
        graphs["NUMBAT_2019_total"],
        f"{output_dir}/stats_numbat_2019_total.png",
        "Network Statistics 2019 (Pre-COVID)"
    )
    
    create_statistical_summary(
        graphs["NUMBAT_2022_total"],
        f"{output_dir}/stats_numbat_2022_total.png",
        "Network Statistics 2022 (Post-COVID)",
        reference_graph_path=graphs["NUMBAT_2019_total"]  # Use 2019 as reference for consistent scales
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
    
    # COVID-19 impact comparison (2019 vs 2022) with fixed layout
    create_before_after_comparison(
        graphs["NUMBAT_2019_total"],
        graphs["NUMBAT_2022_total"],
        f"{output_dir}/covid_impact_2019_vs_2022.png",
        "2019 (Pre-COVID)\nTotal Weekday Flow",
        "2022 (Post-COVID)\nTotal Weekday Flow"
    )
    
    print(f"\n{'='*60}")
    print("✅ ALL VISUALIZATIONS COMPLETED!")
    print(f"{'='*60}")
    print(f"📁 Visualizations saved to: {output_dir}")
    print("\n📊 Generated visualizations:")
    print("   1. Snapshot Graph (NUMBAT 2019)")
    print("   2. General Network Examples (RODS 2017 & NUMBAT 2017)")
    print("   3. Heatmaps (2019 and 2022)")
    print("   4. Network Statistics Excel Files (2019 and 2022)")
    print("   5. COVID-19 Impact Comparison (2019 vs 2022)")
    print("   6. RODS vs NUMBAT Comparison")
    print("   7. AM Peak Comparison")
    print("\n🎯 Key insights to look for:")
    print("   - Node size indicates internal borough activity")
    print("   - Edge thickness/color shows flow intensity")
    print("   - Layout reveals spatial clustering")
    print("   - Heatmaps show flow patterns clearly")
    print("   - Statistics reveal network evolution")

if __name__ == "__main__":
    main()
