""" This handles the Auto-downloading of properties, names, and descriptions. 
"""
import requests
import time
#from chembl_webresource_client.new_client import new_client


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

        # Get Properties
        prop_res = requests.get(
            f"{base_url}/property/MolecularWeight,XLogP,TPSA,ExactMass,Charge,Complexity,MolecularFormula/JSON",
            timeout=10
        )

        if prop_res.status_code == 200:
            props_list = prop_res.json() \
                .get('PropertyTable', {}) \
                .get('Properties', [])

            props = props_list[0] if props_list else {}

            # =========================
            # THEORETICAL PROPERTIES
            # =========================
            data["theoretical_properties"] = {
                "molecular_formula": props.get("MolecularFormula"),
                "exact_mass": props.get("ExactMass"),
                "topological_polar_surface_area": props.get("TPSA"),
                "complexity": props.get("Complexity"),
            }

            # =========================
            # PHYSICAL PROPERTIES
            # =========================
            data["physical_properties"] = {
                "molecular_weight": props.get("MolecularWeight"),
                "xlogp": props.get("XLogP"),
                "charge": props.get("Charge"),
            }

    except Exception as e:
        print(f"[ERROR] Fetching properties for {smiles}: {e}")

    return data