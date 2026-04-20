import sqlite3
import json

DB_PATH = "data/chemical_dataset.db"

def view_data():
    # Connect to the database
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()
        
        # Get all records
        cursor.execute("SELECT * FROM chemical_knowledge_base")
        rows = cursor.fetchall()
        
        print(f"=== Found {len(rows)} chemicals in the database ===\n")
        
        for row in rows:
            print(f"Common Name : {row['common_name']}")
            print(f"SMILES      : {row['canonical_smiles']}")
            print(f"InChIKey    : {row['inchikey']}")
            
            synonyms = json.loads(row['synonyms_list'])
            theoretical = json.loads(row['theoretical_properties'])
            physical = json.loads(row['physical_properties'])
            descriptions = json.loads(row['descriptions'])
            
            # Print just the first 5 synonyms
            print(f"Synonyms    : {synonyms[:5]}") 

            #To see fetched descriptions from PubChem
            #print(f"Description : {descriptions.get('pubchem', 'None')}")
            
            print("Descriptions:")
            print(f"  PubChem: {descriptions.get('pubchem', 'None')}")
            print(f"  ChEBI  : {descriptions.get('chebi', 'None')}")

            # Pretty-print the properties
            print("Physical Properties:")
            print(json.dumps(physical, indent=2, ensure_ascii=False))
            
            print("Theoretical Properties:")
            print(json.dumps(theoretical, indent=2, ensure_ascii=False))
            
            print("-" * 50)

if __name__ == "__main__":
    view_data()