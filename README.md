# ChemGist-NLP
Final Project for CCS 249: NLP

## Overview
This project automates the processing of chemical compounds using SMILES notation. It generates InChIKeys, fetches properties and descriptions from PubChem, and stores the data in a database.

## Prerequisites
- Python 3.8 or higher
- Internet connection (for API calls to PubChem)

## Installation
1. Clone or download this repository.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Data Preparation
1. Place your dataset CSV file in the `data/` directory.
2. The CSV file should contain a column named `SMILES` with the SMILES strings of the chemical compounds.
3. Rename or ensure the file is named `raw_dataset.csv`.

## Running the Code
1. Ensure the dataset is in place as described above.
2. Run the main script:
   ```
   python main.py
   ```
3. The script will initialize the database, process each SMILES string, fetch data from PubChem, and save the results to the database.
4. Progress will be displayed with a progress bar.

## Output
- The processed data is saved to a database (initialized automatically).
- Check the console output for progress and any notices.

## Troubleshooting
- If the dataset file is missing, the script will notify you and wait for the file.
- Ensure all dependencies are installed correctly.
- For RDKit issues, make sure it's compatible with your Python version.
