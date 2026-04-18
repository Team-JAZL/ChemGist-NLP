from src.rdkit_parser import generate_inchikey
from src.fetchers import fetch_pubchem_properties, fetch_description
from src.db_handler import init_db, save_to_db
from tqdm import tqdm # For a progress bar!

def automate_pipeline(smiles_list):
    print("Initializing Database...")
    init_db()
    
    print(f"Processing {len(smiles_list)} chemicals...")
    # tqdm provides a progress bar in the terminal
    for smiles in tqdm(smiles_list):
        
        # Generate InChIKey via RDKit
        inchikey = generate_inchikey(smiles)
        if not inchikey:
            continue
            
        # Fetch data from APIs
        properties_data = fetch_pubchem_properties(smiles)
        descriptions_data = fetch_description(inchikey)
        
        # Compile the final dictionary matching the DB schema
        chemical_data = {
            "_id": inchikey,                        
            "smiles_key": smiles,                   
            "common_name": properties_data.get("common_name"),
            "synonyms_list": properties_data.get("synonyms_list", []),
            "theoretical_properties": properties_data.get("theoretical_properties", {}),
            "physical_properties": properties_data.get("physical_properties", {}),
            "descriptions": descriptions_data,
            
            # Placeholders for the remaining schema columns
            "iupac_name": None,
            "molecular_formula": None,
            "functional_class": None,
            "n_rot_baseline": None,
            "atom_nodes": [],
            "bond_edges": []
        }
        
        # Save to Database
        save_to_db(chemical_data)
        
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    import os
    import pandas as pd
    
    # TODO: Update this path with the actual dataset 
    dataset_path = "data/raw_dataset.csv" 
    
    # Check if dataset has been added to the folder
    if os.path.exists(dataset_path):
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        
        # NOTE: Change 'SMILES' if the provided CSV uses a different column header
        real_dataset = df['SMILES'].dropna().tolist() 
        
        automate_pipeline(real_dataset)
    else:
        print(f"[NOTICE] Pipeline ready. Waiting for dataset.")
        print(f"Please place your CSV file at: {dataset_path}")