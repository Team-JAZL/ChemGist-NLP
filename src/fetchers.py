# """ This handles the Auto-downloading of properties, names, and descriptions. 
# """
# import requests
# import time
# import urllib.parse
# #from chembl_webresource_client.new_client import new_client

# def get_pug_view_val(experimental_sections, heading):
#     """helper to dig through PubChem's nested PUG View JSON and pull out the text string for a specific property."""

#     if not experimental_sections:
#         return None

#     for section in experimental_sections:
#         if section.get('TOCHeading') == heading:
#             try: 
#                 return section['Information'][0]['Value']['StringWithMarkup'][0]['String']
#             except (KeyError, IndexError):
#                 return None
#     return None


# def fetch_pubchem_properties(smiles):
#     """
#     Downloads the theoretical/physical properties, common_name, and synonyms."""

#     safe_smiles = urllib.parse.quote(smiles)
#     base_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{safe_smiles}"
#     data = {
#         "common_name": None, 
#         "synonyms_list": [],
#         "description": None,
#         "theoretical_properties": {},
#         "physical_properties": {
#             "physical_state": None,
#             "color": None,
#             "odor": None,
#             "boiling_point": None,
#             "melting_point": None,
#             "density": None,
#             "solubility": None,
#             "flash_point": None,
#             "vapor_pressure": None
#         }
#     }

#     try: 
#         #Get Synonyms and Common Name

#         syn_res = requests.get(f"{base_url}/synonyms/JSON", timeout=10)

#         if syn_res.status_code == 200:
#             syns = syn_res.json().get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])
#             data["synonyms_list"] = syns
#             data["common_name"] = syns[0] if syns else None

#         time.sleep(0.5)

#         # Get Theoretical Properties and the Compound ID (CID)

#         #API Call (PUG REST API)
#         prop_res = requests.get(
#             f"{base_url}/property/MolecularFormula,MolecularWeight,ExactMass,Charge,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,HeavyAtomCount,TPSA,Complexity,IsotopeAtomCount,CovalentUnitCount/JSON",
#             timeout=10
#         )

#         cid = None

#         if prop_res.status_code == 200:
#             props_list = prop_res.json() \
#                 .get('PropertyTable', {}) \
#                 .get('Properties', [])

#             props = props_list[0] if props_list else {}
#             cid = props.get("CID")

#             # =========================
#             # THEORETICAL PROPERTIES
#             # =========================

#             mol_weight = props.get("MolecularWeight")
#             exact_mass = props.get("ExactMass")
#             tpsa = props.get("TPSA")

#             data["theoretical_properties"] = {
#                 "molecular_formula": props.get("MolecularFormula"),
#                 "molecular_weight": f"{mol_weight} g/mol" if mol_weight else None,
#                 "exact_mass": f"{exact_mass} g/mol" if exact_mass else None,
#                 "formal_charge": props.get("Charge"),
#                 "hydrogen_bond_donor_count": props.get("HBondDonorCount"),
#                 "hydrogen_bond_acceptor_count": props.get("HBondAcceptorCount"), 
#                 "rotatable_bond_count": props.get("RotatableBondCount"),
#                 "heavy_atom_count": props.get("HeavyAtomCount"),
#                 "topological_polar_surface_area": f"{tpsa} Å²" if tpsa else None,
#                 "isotope_atom_count": props.get("IsotopeAtomCount"),
#                 "covalently_bonded_unit_count": props.get("CovalentUnitCount")
#             }

#             time.sleep(0.5)

#             # =========================
#             # PHYSICAL PROPERTIES
#             # =========================

#             #API Call (PUG VIEW API)

#             if cid:
#                 phy_prop_res = requests.get(
#                     f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading=Experimental+Properties",
#                     timeout=10
#                 )

#                 if phy_prop_res.status_code == 200:
#                     try:
#                         sections = phy_prop_res.json()['Record']['Section'][0]['Section'][0]['Section']

#                         #PubChem combines color and state into one string
#                         color_form = get_pug_view_val(sections, "Color/Form")
                        
#                         data["physical_properties"] = {
#                             "physical_state": color_form,               
#                             "color": color_form,                  
#                             "odor": get_pug_view_val(sections, "Odor"),                    
#                             "boiling_point": get_pug_view_val(sections, "Boiling Point"),           
#                             "melting_point": get_pug_view_val(sections, "Melting Point"),           
#                             "density": get_pug_view_val(sections, "Density"),       
#                             "solubility": get_pug_view_val(sections, "Solubility"),
#                             "flash_point": get_pug_view_val(sections, "Flash Point"),                 
#                             "vapor_pressure": get_pug_view_val(sections, "Vapor Pressure")
#                         }
#                     except KeyError:
#                         print(f"[WARNING] Could not parse physical properties for CID {cid}")


#     except Exception as e:
#         print(f"[ERROR] Fetching properties for {smiles}: {e}")

#     return data

# def get_pubchem_description(record):
#     if not record:
#         return None

#     try:
#         rec = record.get("Record", {})

#         # -------------------------
#         # Case 1: direct field
#         # -------------------------
#         desc = rec.get("Description")
#         if isinstance(desc, list) and desc:
#             val = desc[0]
#             if isinstance(val, dict):
#                 return val.get("Description")
#             return val

#         if isinstance(desc, str):
#             return desc

#         # -------------------------
#         # Case 2: Section search (safe)
#         # -------------------------
#         sections = rec.get("Section", [])
#         if not isinstance(sections, list):
#             return None

#         for sec in sections:
#             if sec.get("TOCHeading") == "Description":
#                 try:
#                     return sec["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
#                 except Exception:
#                     continue

#     except Exception:
#         return None

#     return None


""" This handles the Auto-downloading of properties, names, and descriptions. """
import requests
import time
import urllib.parse

def get_pug_view_val(experimental_sections, heading):
    """Helper to dig through PubChem's nested PUG View JSON and pull out the text string."""
    if not experimental_sections:
        return None

    for section in experimental_sections:
        if section.get('TOCHeading') == heading:
            try: 
                return section['Information'][0]['Value']['StringWithMarkup'][0]['String']
            except (KeyError, IndexError):
                return None
    return None

def get_pubchem_description(cid):
    """Fetches the best available description for a CID from PUG View."""
    if not cid:
        return None
        
    #url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON"

    try:
            response = requests.get(url, timeout=10)
            
            # A 404 status code here usually just means PubChem has no description for this CID
            if response.status_code != 200:
                return None
                
            info_list = response.json().get("InformationList", {}).get("Information", [])
            
            # PubChem often returns multiple descriptions from different sources. 
            # We loop through and grab the first valid string we find.
            for info in info_list:
                desc = info.get("Description")
                if desc:
                    return desc
                    
    except Exception as e:
            print(f"[WARNING] Could not fetch description for CID {cid}: {e}")
            
    return None

def get_chebi_description(inchikey):
    """
    Fetches the description (called a 'definition' in ChEBI) 
    using the modern ChEBI REST API.
    """
    if not inchikey:
        return None
        
    url = "https://www.ebi.ac.uk/chebi/backend/api/public/es_search/"
    
    # We pass the InChIKey as the search term and limit results to 1
    params = {
        "term": inchikey, 
        "size": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            
            if results:
                # The chemical data is stored inside the '_source' block
                source_data = results[0].get("_source", {})
                
                # ChEBI uses the key 'definition' for their text descriptions
                return source_data.get("definition")
                
    except Exception as e:
        print(f"[WARNING] Could not fetch ChEBI data for {inchikey}: {e}")
        
    return None

def fetch_pubchem_properties(smiles):
    """Downloads the theoretical/physical properties, common_name, synonyms, and description."""
    safe_smiles = urllib.parse.quote(smiles)
    base_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{safe_smiles}"
    
    data = {
        "common_name": None, 
        "synonyms_list": [],
        "description": None,
        "theoretical_properties": {},
        "physical_properties": {}
    }

    try: 
        # 1. Get Synonyms and Common Name
        syn_res = requests.get(f"{base_url}/synonyms/JSON", timeout=10)
        if syn_res.status_code == 200:
            syns = syn_res.json().get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])
            data["synonyms_list"] = syns
            data["common_name"] = syns[0] if syns else None

        time.sleep(0.5)

        # 2. Get Theoretical Properties and CID
        prop_res = requests.get(
            f"{base_url}/property/MolecularFormula,MolecularWeight,ExactMass,Charge,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,HeavyAtomCount,TPSA,Complexity,IsotopeAtomCount,CovalentUnitCount/JSON",
            timeout=10
        )

        cid = None
        if prop_res.status_code == 200:
            props_list = prop_res.json().get('PropertyTable', {}).get('Properties', [])
            props = props_list[0] if props_list else {}
            cid = props.get("CID")

            data["theoretical_properties"] = {
                "molecular_formula": props.get("MolecularFormula"),
                "molecular_weight": f"{props.get('MolecularWeight')} g/mol" if props.get('MolecularWeight') else None,
                "exact_mass": f"{props.get('ExactMass')} g/mol" if props.get('ExactMass') else None,
                "formal_charge": props.get("Charge"),
                "hydrogen_bond_donor_count": props.get("HBondDonorCount"),
                "hydrogen_bond_acceptor_count": props.get("HBondAcceptorCount"), 
                "rotatable_bond_count": props.get("RotatableBondCount"),
                "heavy_atom_count": props.get("HeavyAtomCount"),
                "topological_polar_surface_area": f"{props.get('TPSA')} Å²" if props.get('TPSA') else None,
                "isotope_atom_count": props.get("IsotopeAtomCount"),
                "covalently_bonded_unit_count": props.get("CovalentUnitCount")
            }

            time.sleep(0.5)

            # Get Physical Properties & Description (Requires CID)
            if cid:
                # Fetch Description
                data["description"] = get_pubchem_description(cid)
                time.sleep(0.5)
                
                # Fetch Physical Properties
                phy_prop_res = requests.get(
                    f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading=Experimental+Properties",
                    timeout=10
                )

                if phy_prop_res.status_code == 200:
                    try:
                        sections = phy_prop_res.json()['Record']['Section'][0]['Section'][0]['Section']
                        color_form = get_pug_view_val(sections, "Color/Form")
                        
                        data["physical_properties"] = {
                            "physical_state": color_form,               
                            "color": color_form,                  
                            "odor": get_pug_view_val(sections, "Odor"),                    
                            "boiling_point": get_pug_view_val(sections, "Boiling Point"),           
                            "melting_point": get_pug_view_val(sections, "Melting Point"),           
                            "density": get_pug_view_val(sections, "Density"),       
                            "solubility": get_pug_view_val(sections, "Solubility"),
                            "flash_point": get_pug_view_val(sections, "Flash Point"),                 
                            "vapor_pressure": get_pug_view_val(sections, "Vapor Pressure")
                        }
                    except (KeyError, IndexError):
                        print(f"[WARNING] Could not parse physical properties for CID {cid}")

    except Exception as e:
        print(f"[ERROR] Fetching properties for {smiles}: {e}")

    return data