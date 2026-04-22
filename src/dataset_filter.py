from rdkit import Chem



# filter for ZINC dataset
ALLOWED_ATOMS = {'C', 'H', 'O', 'N'}

def is_chon_only(smiles):
    """
    Checks if a SMILES string consists of C, H, O, and N atoms only.
    """
    mol = Chem.MolFromSmiles(smiles)
    
    if mol is None:
        return False
        
    for atom in mol.GetAtoms():
        if atom.GetSymbol() not in ALLOWED_ATOMS:
            return False
            
    return True

def filter_chon_dataset(smiles_list):
    """
    Returns the filtered list containing only molecules with C, H, O, N atoms.
    """
    print("Filtering dataset for CHON-only molecules...")
    filtered_list = [smiles for smiles in smiles_list if is_chon_only(smiles)]
    
    print(f"Original size: {len(smiles_list)} | Filtered size: {len(filtered_list)}")
    return filtered_list