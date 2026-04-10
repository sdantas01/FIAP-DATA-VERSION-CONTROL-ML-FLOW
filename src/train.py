import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
df = pd.read_csv('data/processed/features_v1.csv')
X, y = df.drop('churn', axis=1), df['churn']
model = RandomForestClassifier().fit(X, y)
with open('models/experiments/model_v1.pkl', 'wb') as f: pickle.dump(model, f)
print('✅ Dev C: Modelo treinado.')