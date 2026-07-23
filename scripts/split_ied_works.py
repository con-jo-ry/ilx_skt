# This script takes the original ied_works.csv and separates gretil from dsbc

import pandas as pd

# 1. Load the main CSV file
try:
    df = pd.read_csv('ied_works.csv')
except FileNotFoundError:
    print("Error: Could not find 'ied_works.csv' in the current directory.")
    exit()

# Ensure the column is treated as a string and handle potential NaN/empty values safely
link_col = df['GRETIL/DSBC Link'].fillna('').astype(str)

# 2. Filter rows based on the starting URL prefix
gretil_mask = link_col.str.startswith('http://gretil.sub.uni-goettingen.de/')
dsbc_mask = link_col.str.startswith('http://www.dsbcproject.org/')

gretil_df = df[gretil_mask]
dsbc_df = df[dsbc_mask]

# 3. Save to separate files
gretil_df.to_csv('gretil.csv', index=False)
dsbc_df.to_csv('dsbc.csv', index=False)

print(f"Split complete! Saved {len(gretil_df)} rows to gretil.csv and {len(dsbc_df)} rows to dsbc.csv.")
