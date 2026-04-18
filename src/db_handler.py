import sqlite3
import json
import os


DB_PATH = "data/chemical_dataset.db"

def init_db():
    """Initializes the SQLite database."""

    os.makedirs(os.path.dirname(DB_PATH), exist_ok = True)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Molecule_Document (
                _id TEXT PRIMARY KEY,
                smiles_key TEXT UNIQUE,
                iupac_name TEXT,
                molecular_formula TEXT, 
                functional_class TEXT,
                n_rot_baseline INTEGER,
                common_name TEXT,
                synonyms_list TEXT,           -- JSON Array
                theoretical_properties TEXT,  -- JSON Object
                physical_properties TEXT,     -- JSON Object
                descriptions TEXT,            -- JSON Object
                atom_nodes TEXT,              -- JSON Array
                bond_edges TEXT               -- JSON Array
            )
        ''')

        conn.commit()
        return conn


def save_to_db(chemical_data):
    """Saves a single chemical dictionary to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO Molecule_Document (
                _id, smiles_key, iupac_name, molecular_formula, 
                functional_class, n_rot_baseline, common_name, synonyms_list,
                theoretical_properties, physical_properties, descriptions,
                atom_nodes, bond_edges
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            chemical_data.get('_id'),
            chemical_data.get('smiles_key'),
            chemical_data.get('iupac_name'),
            chemical_data.get('molecular_formula'),
            chemical_data.get('functional_class'),
            chemical_data.get('n_rot_baseline'),
            chemical_data.get('common_name'),
            json.dumps(chemical_data.get('synonyms_list', [])),
            json.dumps(chemical_data.get('theoretical_properties', {})),
            json.dumps(chemical_data.get('physical_properties', {})),
            json.dumps(chemical_data.get('descriptions', {})),
            json.dumps(chemical_data.get('atom_nodes', [])),
            json.dumps(chemical_data.get('bond_edges', []))
        ))

        conn.commit()


def load_from_db(_id):
    """Loads a chemical by InChIKey (_id) and returns it as a Python dictionary."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Molecule_Document WHERE _id = ?", (_id,))
        row = cursor.fetchone()

        if row: 
            return {
                "_id": row["_id"],
                "smiles_key": row["smiles_key"],
                "iupac_name": row["iupac_name"],
                "molecular_formula": row["molecular_formula"], 
                "functional_class": row["functional_class"],
                "n_rot_baseline": row["n_rot_baseline"],
                "common_name": row["common_name"],
                "synonyms_list": json.loads(row["synonyms_list"]) if row["synonyms_list"] else [],
                "theoretical_properties": json.loads(row["theoretical_properties"]) if row["theoretical_properties"] else {},
                "physical_properties": json.loads(row["physical_properties"]) if row["physical_properties"] else {},
                "descriptions": json.loads(row["descriptions"]) if row["descriptions"] else {},
                "atom_nodes": json.loads(row["atom_nodes"]) if row["atom_nodes"] else [],
                "bond_edges": json.loads(row["bond_edges"]) if row["bond_edges"] else []
            }
        
        return None