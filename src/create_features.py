import pandas as pd
import os
df = pd.read_csv('data/raw/customers_v1.csv')
df['income_per_age'] = df['income'] / df['age']
os.makedirs('data/processed', exist_ok=True)
df.to_csv('data/processed/features_v1.csv', index=False)
print(' Dev B: Features processadas.')