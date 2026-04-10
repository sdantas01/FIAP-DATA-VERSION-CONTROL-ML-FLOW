import pandas as pd
import numpy as np
import os
df = pd.DataFrame({'age': np.random.randint(18, 80, 1000), 'income': np.random.randint(20, 150, 1000), 'churn': np.random.choice([0,1], 1000)})
os.makedirs('data/raw', exist_ok=True)
df.to_csv('data/raw/customers_v1.csv', index=False)
print('✅ Dev A: Dados brutos criados.')