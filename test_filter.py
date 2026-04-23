import os
import pandas as pd
from src.dataset_filter import filter_chon_dataset

def test_the_filter():
    dataset_path = "data/ZINC-250k.csv"
    output_path = "data/filtered_test_results.csv"
    
    if not os.path.exists(dataset_path):
        print(f"Error: Could not find {dataset_path}")
        return

    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    raw_smiles = df['smiles'].dropna().tolist()
    
    filtered_smiles = filter_chon_dataset(raw_smiles)
    
    # Save the results to a new CSV for checking
    output_df = pd.DataFrame({'Filtered_SMILES': filtered_smiles})
    output_df.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] Saved the filtered dataset to: {output_path}")

if __name__ == "__main__":
    test_the_filter()