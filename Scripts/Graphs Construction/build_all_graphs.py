import subprocess
import sys
import os
from pathlib import Path
from tqdm import tqdm
import time

def run_script_with_progress(script_name, description):
    """
    Run a Python script with progress tracking and error handling.
    
    Args:
        script_name (str): Name of the script to run
        description (str): Description for progress display
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Starting {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Run the script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"\n✅ {description} completed successfully!")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            if result.stdout:
                print(f"📋 Output:\n{result.stdout}")
            return True
        else:
            print(f"\n❌ {description} failed!")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            if result.stderr:
                print(f"🚨 Error:\n{result.stderr}")
            if result.stdout:
                print(f"📋 Output:\n{result.stdout}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running {description}: {str(e)}")
        return False

def check_dependencies():
    """
    Check if required Python packages are installed.
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    required_packages = ['pandas', 'numpy', 'igraph', 'tqdm']
    missing_packages = []
    
    print("Checking dependencies...")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are available!")
    return True

def check_data_files():
    """
    Check if required data files and directories exist.
    
    Returns:
        bool: True if all required files exist, False otherwise
    """
    required_paths = [
        "../Data/RODS_OD",
        "../Data/NUMBAT/OD_Matrices",
        "../Data/station_borough_nlc_mapping.csv"
    ]
    
    print("\nChecking data files...")
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"✅ {path}")
        else:
            print(f"❌ {path}")
            return False
    
    print("✅ All required data files exist!")
    return True

def create_output_directory():
    """
    Create the output directory for graphs.
    
    Returns:
        bool: True if successful, False otherwise
    """
    output_dir = "../Data/Graphs"
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"✅ Created output directory: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create output directory: {str(e)}")
        return False

def main():
    """
    Main function to run both graph construction scripts.
    """
    print("🚀 London Transport Network Graph Construction")
    print("=" * 60)
    print("This script will build graphs from RODS and NUMBAT datasets")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        return
    
    # Check data files
    if not check_data_files():
        print("\n❌ Please ensure all required data files are present and try again.")
        return
    
    # Create output directory
    if not create_output_directory():
        print("\n❌ Failed to create output directory.")
        return
    
    # Define scripts to run
    scripts = [
        ("build_rods_graphs.py", "RODS Graph Construction (2000-2017)"),
        ("build_numbat_graphs.py", "NUMBAT Graph Construction (2017-2023)")
    ]
    
    # Track overall progress
    successful_scripts = 0
    total_scripts = len(scripts)
    
    print(f"\n📊 Will process {total_scripts} datasets")
    print("=" * 60)
    
    # Run each script
    for script_name, description in scripts:
        success = run_script_with_progress(script_name, description)
        if success:
            successful_scripts += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 GRAPH CONSTRUCTION SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {successful_scripts}/{total_scripts}")
    print(f"❌ Failed: {total_scripts - successful_scripts}/{total_scripts}")
    
    if successful_scripts == total_scripts:
        print("\n🎉 All graph construction completed successfully!")
        print("📁 Graphs are saved in: Data/Graphs/")
        print("\n📂 Directory structure:")
        print("   Data/Graphs/")
        print("   ├── RODS/")
        print("   │   ├── 2000/")
        print("   │   │   ├── 2000.graphml")
        print("   │   │   └── time_bands/tb/")
        print("   │   └── ... (2001-2017)")
        print("   └── NUMBAT/")
        print("       ├── 2017/")
        print("       │   ├── 2017.graphml")
        print("       │   ├── MTT/")
        print("       │   ├── FRI/")
        print("       │   ├── SAT/")
        print("       │   └── SUN/")
        print("       └── ... (2018-2023)")
    else:
        print(f"\n⚠️  {total_scripts - successful_scripts} script(s) failed.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
