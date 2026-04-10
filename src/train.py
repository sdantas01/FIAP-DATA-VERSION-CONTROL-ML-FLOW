import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import json
import os
from datetime import datetime

def create_dataset():
    np.random.seed(42)
    X = np.random.randn(1000, 10)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
    df['target'] = y
    return df

def train_model():
    print("📊 Criando dataset...")
    df = create_dataset()
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/train_data.csv', index=False)
    
    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    print("🤖 Treinando modelo...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"✅ Acurácia: {acc:.4f}")
    
    os.makedirs('models', exist_ok=True)
    with open('models/model_v1.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    metrics = {'timestamp': datetime.now().isoformat(), 'accuracy': float(acc)}
    with open('models/metrics_v1.json', 'w') as f:
        json.dump(metrics, f, indent=2)

if __name__ == '__main__':
    train_model()
