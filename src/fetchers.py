""" This handles the Auto-downloading of properties, names, and descriptions. 
"""
import requests
import time


def fetch_pubchem_properties(smiles):
    """
    Downloads the theoretical/physical properties, common_name, and synonyms."""

    base_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles}"
    data = {
        "common_name": None, 
        "synonyms_list": [],
        "theoretical_properties": {},
        "physical_properties": {}
    }

    try: 
        #Get Synonyms and Common Name

        syn_res = requests.get(f"{base_url}/synonyms/JSON", timeout=10)

        if syn_res.status_code == 200:
            syns = syn_res.json().get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])
            data["synonyms_list"] = syns
            data["common_name"] = syns[0] if syns else None

        time.sleep(0.5)

        # Get Properties

        prop_res = requests.get(f"{base_url}/property/MolecularWeight,XLogP,TPSA,ExactMass/JSON", timeout=10)
        if prop_res.status_code == 200:
            props_list = prop_res.json()\
                .get('PropertyTable', {})\
                .get('Properties', [])
            
            if props_list:
                props = props_list[0]
            else:
                props = {}

            data["theoretical_properties"] = {"ExactMass": props.get("ExactMass"), "TPSA": props.get("TPSA")}
            data["physical_properties"] = {"MolecularWeight": props.get("MolecularWeight"), "XLogP": props.get("XLogP")}

    except Exception as e:
        print(f"[ERROR] Fetching properties for {smiles}: {e}")

    return data



def fetch_description(inchikey):
    """
    Downloads the descriptions from open-source databases (PubChem/ChEBI)"""

    descriptions = {}

    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{inchikey}/description/JSON"
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            info_list = res.json().get('InformationList', {}).get('Information', [])
            for info in info_list:
                if 'Description' in info:
                    source = info.get('SourceName', 'PubChem')
                    descriptions[source] = info['Description']

        time.sleep(0.5)

    except requests.exceptions.RequestException as e:
        print(f"[WARN] PubChem failed for {inchikey}: {e}")

    return descriptions
