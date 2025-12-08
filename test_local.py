"""
Script de test local pour vérifier que tout fonctionne avant le déploiement
Exécuter: python test_local.py
"""

import sys
import os

print("🧪 Test du système de détection d'intrusion\n")
print("=" * 60)

# Test 1: Vérifier la structure des dossiers
print("\n1️⃣ Vérification de la structure des dossiers...")

required_dirs = ['api', 'models', 'frontend']
missing_dirs = []

for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"   ✅ Dossier '{dir_name}/' trouvé")
    else:
        print(f"   ❌ Dossier '{dir_name}/' MANQUANT")
        missing_dirs.append(dir_name)

if missing_dirs:
    print(f"\n⚠️ ERREUR: Dossiers manquants: {missing_dirs}")
    print("Créer ces dossiers avant de continuer.")
    sys.exit(1)

# Test 2: Vérifier les fichiers requis
print("\n2️⃣ Vérification des fichiers requis...")

required_files = {
    'api/__init__.py': 'Package API',
    'api/app.py': 'API Flask principale',
    'api/predictor.py': 'Logique de prédiction',
    'models/mlp_model_subset.h5': 'Modèle MLP',
    'models/scaler.pkl': 'Scaler StandardScaler',
    'frontend/index.html': 'Interface web',
    'frontend/style.css': 'Styles CSS',
    'frontend/script.js': 'Logique JavaScript',
    'requirements.txt': 'Dépendances Python',
    'Procfile': 'Configuration Render',
    'runtime.txt': 'Version Python'
}

missing_files = []

for filepath, description in required_files.items():
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        size_kb = size / 1024
        print(f"   ✅ {filepath} ({size_kb:.1f} KB) - {description}")
    else:
        print(f"   ❌ {filepath} MANQUANT - {description}")
        missing_files.append(filepath)

if missing_files:
    print(f"\n⚠️ ERREUR: Fichiers manquants: {len(missing_files)}")
    for f in missing_files:
        print(f"   - {f}")
    sys.exit(1)

# Test 3: Vérifier les dépendances Python
print("\n3️⃣ Vérification des dépendances Python...")

dependencies = {
    'flask': 'Flask',
    'flask_cors': 'Flask-CORS',
    'tensorflow': 'TensorFlow',
    'numpy': 'NumPy',
    'pandas': 'Pandas',
    'sklearn': 'Scikit-learn'
}

missing_deps = []

for module, name in dependencies.items():
    try:
        __import__(module)
        print(f"   ✅ {name} installé")
    except ImportError:
        print(f"   ❌ {name} NON INSTALLÉ")
        missing_deps.append(name)

if missing_deps:
    print(f"\n⚠️ Dépendances manquantes: {missing_deps}")
    print("Installer avec: pip install -r requirements.txt")
    sys.exit(1)

# Test 4: Tester le chargement du modèle
print("\n4️⃣ Test de chargement du modèle...")

try:
    from api.predictor import CICIDSPredictor
    
    predictor = CICIDSPredictor(
        model_path='models/mlp_model_subset.h5',
        scaler_path='models/scaler.pkl'
    )
    print("   ✅ Modèle chargé avec succès")
    print(f"   ✅ Nombre de features attendues: {predictor.scaler.n_features_in_}")
    
    # Test de prédiction
    print("\n5️⃣ Test de prédiction...")
    import numpy as np
    
    # Créer des features de test (78 valeurs aléatoires)
    test_features = np.random.rand(78).tolist()
    
    result = predictor.predict_single(test_features)
    
    if 'error' in result:
        print(f"   ❌ Erreur de prédiction: {result['error']}")
        sys.exit(1)
    else:
        print(f"   ✅ Prédiction réussie")
        print(f"   📊 Résultat: {result['prediction']}")
        print(f"   📊 Confiance: {result['confidence']}%")
        
except Exception as e:
    print(f"   ❌ Erreur lors du test: {e}")
    sys.exit(1)

# Test 6: Vérifier les fichiers de configuration
print("\n6️⃣ Vérification des fichiers de configuration...")

# Vérifier Procfile
with open('Procfile', 'r') as f:
    procfile_content = f.read().strip()
    if 'web:' in procfile_content and 'gunicorn' in procfile_content:
        print("   ✅ Procfile valide")
    else:
        print("   ❌ Procfile invalide")
        sys.exit(1)

# Vérifier runtime.txt
with open('runtime.txt', 'r') as f:
    runtime_content = f.read().strip()
    if 'python-' in runtime_content:
        print(f"   ✅ runtime.txt valide: {runtime_content}")
    else:
        print("   ❌ runtime.txt invalide")
        sys.exit(1)

# Vérifier requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = f.read()
    required_packages = ['Flask', 'tensorflow', 'numpy', 'pandas', 'gunicorn']
    all_present = all(pkg.lower() in requirements.lower() for pkg in required_packages)
    
    if all_present:
        print("   ✅ requirements.txt valide")
    else:
        print("   ❌ requirements.txt incomplet")
        sys.exit(1)

# Résumé final
print("\n" + "=" * 60)
print("✅ TOUS LES TESTS SONT PASSÉS !")
print("=" * 60)
print("\n🚀 Ton projet est prêt pour le déploiement sur Render !")
print("\n📋 Prochaines étapes:")
print("   1. Initialiser Git: git init")
print("   2. Ajouter les fichiers: git add .")
print("   3. Commit: git commit -m 'Initial commit'")
print("   4. Créer un repo GitHub")
print("   5. Pousser le code: git push origin main")
print("   6. Déployer sur Render")
print("\n📚 Consulter GUIDE_DEPLOIEMENT.md pour les détails\n")