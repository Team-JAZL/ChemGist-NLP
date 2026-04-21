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

def get_chembl_description(inchikey):
    """
    Fetches basic drug/molecule information from ChEMBL using their REST API.
    """
    if not inchikey:
        return None
        
    # Query ChEMBL by exact InChIKey match
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule.json?molecule_structures__standard_inchi_key={inchikey}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            molecules = response.json().get("molecules", [])
            
            if molecules:
                mol = molecules[0] # Grab the first match
                
                pref_name = mol.get("pref_name") or "Unnamed Compound"
                mol_type = mol.get("molecule_type") or "Unknown Type"
                max_phase = mol.get("max_phase")
                
                # Format this structured data into a readable summary string
                name = pref_name or "This compound"
                type_ = mol_type.lower() if mol_type else "molecule"

                if max_phase and str(max_phase) not in ["0", "None"]:
                    desc = f"{name} is a {type_} listed in the ChEMBL database and has reached clinical trial phase {max_phase}."
                else:
                    desc = f"{name} is a {type_} listed in the ChEMBL database but has not progressed to an approved clinical phase."
                    
                return desc
                
    except Exception as e:
        print(f"[WARNING] Could not fetch ChEMBL data for {inchikey}: {e}")
        
    return None

def get_wikipedia_description(search_term):
    """Fetches the introductory paragraph by searching Wikipedia (handles inexact names better)."""
    if not search_term:
        return None
        
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",        
        "gsrsearch": search_term,     
        "gsrlimit": 1,                
        "prop": "extracts",
        "exintro": True,              
        "explaintext": True           
    }
    
    # NEW: Create a nametag for your script (Change the email to your actual email!)
    headers = {
        "User-Agent": "MyChemicalDatabaseFetcher/1.0 (escrupulo.asherah@gmail.com) Python-requests"
    }
    
    try:
        # Pass the headers into the request
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            pages = response.json().get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                if page_id != "-1":
                    return page_info.get("extract")
                    
    except Exception as e:
        print(f"[WARNING] Could not fetch Wikipedia data for {search_term}: {e}")
        
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