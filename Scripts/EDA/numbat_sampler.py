import os
from pathlib import Path
import pandas as pd
import random

# Constants
ROOT_DIR = Path("/Users/andrey/Desktop/TMU/MRP/Code/Data")
NUMBAT_DIR = ROOT_DIR / "NUMBAT"
SAMPLE_DIR = ROOT_DIR / "NUMBAT samples"
NUMBAT_SAMPLE_YEARS = ['16', '17', '18', '19', '20', '21', '22', '23']

def create_sample_file(input_file: Path, output_file: Path):
    """Create a sampled version of a NUMBAT file."""
    print(f"Processing {input_file.name}...")
    
    # Read the Excel file
    xls = pd.ExcelFile(input_file)
    sheet_names = xls.sheet_names
    
    # Create a dictionary to store all sheets
    sheets_dict = {}
    
    # Process each sheet
    for sheet_name in sheet_names:
        if sheet_name == sheet_names[0]:  # First sheet (metadata)
            # Keep metadata sheet exactly as is
            sheets_dict[sheet_name] = pd.read_excel(input_file, sheet_name=sheet_name)
        else:
            # For other sheets, keep first 4 rows and sample 10 rows from the rest
            df = pd.read_excel(input_file, sheet_name=sheet_name)
            
            if len(df) <= 14:  # If file has 14 or fewer rows, keep it as is
                sheets_dict[sheet_name] = df
            else:
                # Keep first 4 rows
                first_part = df.iloc[:4]
                
                # Sample 10 rows from the rest
                remaining_rows = df.iloc[4:]
                sampled_rows = remaining_rows.sample(n=10, random_state=42)
                
                # Combine the parts
                sheets_dict[sheet_name] = pd.concat([first_part, sampled_rows])
    
    # Save the sampled file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in sheets_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"Created sample file: {output_file.name}")

def main():
    # Create sample directory if it doesn't exist
    SAMPLE_DIR.mkdir(exist_ok=True)
    
    # Get all NUMBAT files
    numbat_files = sorted([
        f for f in NUMBAT_DIR.glob("*.xlsx") 
        if any(f"NBT{y}" in f.name for y in NUMBAT_SAMPLE_YEARS)
    ])
    
    print(f"Found {len(numbat_files)} NUMBAT files to process")
    
    # Process each file
    for input_file in numbat_files:
        output_file = SAMPLE_DIR / input_file.name
        create_sample_file(input_file, output_file)
    
    print(f"✅ All sample files have been created in {SAMPLE_DIR}")

if __name__ == "__main__":
    main() 
