import sqlite3
import pandas as pd

conn = sqlite3.connect('data/chemical_dataset.db')
query = "SELECT * FROM chemical_knowledge_base"
df = pd.read_sql_query(query,conn)

df.to_csv('data/ChemGist-CHON.csv', index = False)

conn.close()