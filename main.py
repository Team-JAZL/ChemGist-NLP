import os
import time
from src.rdkit_parser import generate_inchikey
from src.fetchers import fetch_pubchem_properties, get_chebi_description, get_chembl_description, get_wikipedia_description
from src.db_handler import init_db, save_to_db, load_from_db
from tqdm import tqdm 


def automate_pipeline(smiles_list):
    print("Initializing Database...")
    init_db()

    for smiles in tqdm(smiles_list, desc="Processing Chemicals"):
        inchikey = generate_inchikey(smiles)
        if not inchikey:
            continue

        # SKIP IF ALREADY IN DATABASE
        if load_from_db(inchikey):
            continue
    
        # Fetch data from APIs
        properties_data = fetch_pubchem_properties(smiles)

        common_name = properties_data.get("common_name")
        synonyms = properties_data.get("synonyms_list", [])

        # If common_name exists, use it. If not, try to use the first synonym.
        if common_name:
            wiki_search_term = common_name
        elif synonyms:
            wiki_search_term = synonyms[0]
        else:
            wiki_search_term = None # If we have absolutely no names, give up on Wikipedia
            
        print(f"\n[DEBUG] Searching Wikipedia for: '{wiki_search_term}'")

        chebi_description = get_chebi_description(inchikey)
        chembl_description = get_chembl_description(inchikey)
        wikipedia_description = get_wikipedia_description(wiki_search_term)
        
        # Compile the final dictionary matching the DB schema
        chemical_data = {
            "inchikey": inchikey,                        
            "canonical_smiles": smiles,                   
            "common_name": properties_data.get("common_name"),
            "synonyms_list": properties_data.get("synonyms_list", []),
            "theoretical_properties": properties_data.get("theoretical_properties", {}),
            "physical_properties": properties_data.get("physical_properties", {}),
            "descriptions": {
                "pubchem": properties_data.get("description"),
                "chebi": chebi_description,
                "chembl": chembl_description,
                "wikipedia": wikipedia_description
            }
        }
        
        # Save to Database
        save_to_db(chemical_data)

        time.sleep(1) # Sleep to avoid hitting API rate limits (adjust as needed)
        
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    import pandas as pd
    
    # TODO: Update this path with the actual dataset 
    dataset_path = "data/cleaned_wiki_chon.csv" 
    
    # Check if dataset has been added to the folder
    if os.path.exists(dataset_path):
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        real_dataset = df['Molecule'].dropna().tolist() 
        
        # # Batch Processing
        # START_INDEX = 0 
        # END_INDEX = 50

        # current_batch = real_dataset[START_INDEX:END_INDEX]

        # print(f"\n[BATCH INFO] Running molecules from index {START_INDEX} to {END_INDEX}")
        # print(f"Total molecules in this batch: {len(current_batch)}")

        # automate_pipeline(current_batch)

        print(f"\n[FULL RUN] Starting pipeline for all {len(real_dataset)} molecules.")
        automate_pipeline(real_dataset)
        print("\n[SUCCESS] Entire dataset has been processed and saved.")
    else:
        print(f"[NOTICE] Pipeline ready. Waiting for dataset.")
        print(f"Please place your CSV file at: {dataset_path}")