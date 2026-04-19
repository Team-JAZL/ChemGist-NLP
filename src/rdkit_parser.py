""" This is for converting from SMILES to get InChIKey"""

from rdkit import Chem


def generate_inchikey(smiles):
    """ Parses SMILE string using RDKit and returns the InChiKey.
        Returns None if the SMILES string is invalid.
    """

    mol = Chem.MolFromSmiles(smiles)

    if mol:
        return Chem.MolToInchiKey(mol)
    else:
        print(f"[WARNING] RDKit could not parse SMILES: {smiles}")
        return None