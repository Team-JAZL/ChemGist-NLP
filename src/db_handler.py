import sqlite3
import json
import os


DB_PATH = "data/chemical_dataset.db"

def init_db():
    """Initializes the SQLite database."""

    os.makedirs(os.path.dirname(DB_PATH), exist_ok = True)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Create main table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chemical_knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inchikey TEXT UNIQUE NOT NULL,      
                canonical_smiles TEXT NOT NULL,              
                common_name TEXT,                   
                synonyms_list JSON,                 -- Stored as a JSON Array
                theoretical_properties JSON,        -- Stored as a JSON Object
                physical_properties JSON,           -- Stored as a JSON Object
                descriptions JSON                   -- Stored as a JSON Object
            );
        ''')


        cursor.execute('CREATE INDEX IF NOT EXISTS idx_inchikey ON chemical_knowledge_base(inchikey);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_smiles ON chemical_knowledge_base(canonical_smiles);')
        conn.commit()
        return conn


def save_to_db(chemical_data):
    """Saves a single chemical dictionary to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO chemical_knowledge_base (
                inchikey, canonical_smiles, common_name, synonyms_list,
                theoretical_properties, physical_properties, descriptions
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(inchikey) DO UPDATE SET
                canonical_smiles=excluded.canonical_smiles,
                common_name=excluded.common_name,
                synonyms_list=excluded.synonyms_list,
                theoretical_properties=excluded.theoretical_properties,
                physical_properties=excluded.physical_properties,
                descriptions=excluded.descriptions;
        ''', (
            chemical_data.get('inchikey'),
            chemical_data.get('canonical_smiles'),
            chemical_data.get('common_name'),
            json.dumps(chemical_data.get('synonyms_list', [])),
            json.dumps(chemical_data.get('theoretical_properties', {})),
            json.dumps(chemical_data.get('physical_properties', {})),
            json.dumps(chemical_data.get('descriptions', {}))
        ))

        conn.commit()


def load_from_db(inchikey_val):
    """Loads a chemical by InChIKey and returns it as a Python dictionary."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fixed the variable name and added the trailing comma for the tuple
        cursor.execute("SELECT * FROM chemical_knowledge_base WHERE inchikey = ?", (inchikey_val,))
        row = cursor.fetchone()

        if row: 
            return {
                "id": row["id"],
                "inchikey": row["inchikey"],
                "canonical_smiles": row["canonical_smiles"],
                "common_name": row["common_name"],
                "synonyms_list": json.loads(row["synonyms_list"]) if row["synonyms_list"] else [],
                "theoretical_properties": json.loads(row["theoretical_properties"]) if row["theoretical_properties"] else {},
                "physical_properties": json.loads(row["physical_properties"]) if row["physical_properties"] else {},
                "descriptions": json.loads(row["descriptions"]) if row["descriptions"] else {}
            }
        
        return None