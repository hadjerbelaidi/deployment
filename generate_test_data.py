"""
Script pour générer des données de test CSV pour le système
Exécuter: python generate_test_data.py
"""

import numpy as np
import pandas as pd
import pickle

print("🔧 Génération de données de test pour CICIDS2017\n")

# Charger le scaler pour connaître les features
try:
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    
    n_features = scaler.n_features_in_
    print(f"✅ Nombre de features: {n_features}")
    
except FileNotFoundError:
    print("❌ Fichier scaler.pkl non trouvé dans models/")
    print("Utilisation de 78 features par défaut")
    n_features = 78

# Générer des données de test
print(f"\n📊 Génération de 100 connexions de test...\n")

# Créer des noms de colonnes génériques
feature_names = [f'feature_{i}' for i in range(n_features)]

# Générer 50 connexions "normales" et 50 "attaques"
np.random.seed(42)

# Connexions normales (valeurs plus basses)
normal_data = np.random.rand(50, n_features) * 50

# Connexions attaques (valeurs plus élevées et variables)
attack_data = np.random.rand(50, n_features) * 150 + 50

# Combiner les données
all_data = np.vstack([normal_data, attack_data])

# Créer les labels (0 = normal, 1 = attaque)
labels = np.array([0] * 50 + [1] * 50)

# Mélanger les données
indices = np.random.permutation(100)
all_data = all_data[indices]
labels = labels[indices]

# Créer le DataFrame
df = pd.DataFrame(all_data, columns=feature_names)
df['Label'] = labels

# Sauvegarder les fichiers de test

# 1. Fichier complet avec labels (pour tester l'accuracy)
df.to_csv('test_data_with_labels.csv', index=False)
print(f"✅ Créé: test_data_with_labels.csv")
print(f"   - {len(df)} lignes")
print(f"   - {len(df.columns)} colonnes (incluant Label)")
print(f"   - Attaques: {labels.sum()} ({labels.sum()/len(labels)*100:.1f}%)")
print(f"   - Normales: {len(labels) - labels.sum()} ({(len(labels) - labels.sum())/len(labels)*100:.1f}%)")

# 2. Fichier sans labels (pour prédiction pure)
df_no_labels = df.drop('Label', axis=1)
df_no_labels.to_csv('test_data_no_labels.csv', index=False)
print(f"\n✅ Créé: test_data_no_labels.csv")
print(f"   - {len(df_no_labels)} lignes")
print(f"   - {len(df_no_labels.columns)} colonnes (sans Label)")

# 3. Petit échantillon (10 lignes) pour tests rapides
df_sample = df.head(10)
df_sample.to_csv('test_data_sample.csv', index=False)
print(f"\n✅ Créé: test_data_sample.csv")
print(f"   - {len(df_sample)} lignes")
print(f"   - Parfait pour tests rapides")

# 4. Fichier JSON pour test API unique
import json

single_test = {
    "features": all_data[0].tolist()
}

with open('test_single_prediction.json', 'w') as f:
    json.dump(single_test, f, indent=2)

print(f"\n✅ Créé: test_single_prediction.json")
print(f"   - 1 connexion pour test API")
print(f"   - Label réel: {'ATTAQUE' if labels[indices[0]] == 1 else 'NORMAL'}")

# Afficher un aperçu
print("\n" + "="*60)
print("📋 Aperçu des premières lignes:")
print("="*60)
print(df.head())

print("\n" + "="*60)
print("✅ Fichiers de test générés avec succès !")
print("="*60)
print("\n📝 Utilisation:")
print("   1. test_data_with_labels.csv → Upload dans l'interface web")
print("   2. test_data_no_labels.csv → Test sans connaître les vraies réponses")
print("   3. test_data_sample.csv → Tests rapides (10 lignes)")
print("   4. test_single_prediction.json → Test de l'API /predict")

print("\n🧪 Pour tester localement:")
print("   python -c \"import pandas as pd; print(pd.read_csv('test_data_sample.csv'))\"")

print("\n🌐 Pour tester l'API (après déploiement):")
print("   curl -X POST https://TON_URL.onrender.com/api/predict_batch \\")
print("     -F 'file=@test_data_sample.csv'")

print("\n" + "="*60 + "\n")