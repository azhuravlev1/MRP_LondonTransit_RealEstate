#!/usr/bin/env python3
"""
Complete Panel Regression Analysis Pipeline
London Transit Network and Housing Market Analysis (2000-2023)

This master script runs the complete analysis pipeline:
1. Prepare final dataset (01_prepare_final_dataset.py)
2. Run panel regression (02_run_panel_regression.py)
3. Visualize results (03_visualize_results.py)

Author: Andrey Zhuravlev
Date: 2025
"""

import subprocess
import sys
from pathlib import Path
import time

def run_script(script_path, script_name):
    """Run a Python script and handle any errors."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR running {script_name}:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Run the complete analysis pipeline."""
    print("🚀 LONDON TRANSIT NETWORK AND HOUSING MARKET ANALYSIS")
    print("=" * 60)
    print("Complete Panel Regression Analysis Pipeline")
    print("=" * 60)
    
    # Get the scripts directory
    scripts_dir = Path(__file__).parent
    
    # Define the scripts to run in order
    scripts = [
        ("01_prepare_final_dataset.py", "Dataset Preparation"),
        ("02_run_panel_regression.py", "Panel Regression Analysis"),
        ("03_visualize_results.py", "Results Visualization")
    ]
    
    start_time = time.time()
    
    # Run each script
    for script_file, script_name in scripts:
        script_path = scripts_dir / script_file
        
        if not script_path.exists():
            print(f"❌ ERROR: Script not found: {script_path}")
            return False
        
        success = run_script(script_path, script_name)
        
        if not success:
            print(f"❌ FAILED: {script_name}")
            print("Pipeline stopped due to error.")
            return False
        
        print(f"✅ COMPLETED: {script_name}")
    
    # Calculate total time
    total_time = time.time() - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    
    print(f"\n{'='*60}")
    print("🎉 ANALYSIS PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"Total execution time: {minutes}m {seconds}s")
    print(f"\n📁 Output files created in:")
    print(f"   • modeling/data/ - Final dataset and summaries")
    print(f"   • modeling/outputs/ - Regression results and visualizations")
    print(f"\n📊 Key outputs:")
    print(f"   • final_modeling_dataset.csv - Merged dataset with lagged variables")
    print(f"   • regression_summary.txt - Detailed regression results")
    print(f"   • coefficients.csv - Coefficient estimates and statistics")
    print(f"   • coefficient_plot.png - Main results visualization")
    print(f"   • results_dashboard.png - Comprehensive results summary")
    print(f"   • interpretation_report.txt - Results interpretation")
    print(f"\n🔍 Next steps:")
    print(f"   • Review the interpretation report for key findings")
    print(f"   • Examine coefficient plots for significant effects")
    print(f"   • Use results in your MRP analysis and discussion")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
