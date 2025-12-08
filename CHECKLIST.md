# ✅ Checklist de Déploiement

Utilise cette checklist pour t'assurer que tout est en place avant le déploiement.

## 📁 Structure des fichiers

```
intrusion-detection-api/
├── [ ] api/
│   ├── [ ] __init__.py
│   ├── [ ] app.py
│   └── [ ] predictor.py
├── [ ] models/
│   ├── [ ] mlp_model_subset.h5 (ton modèle)
│   └── [ ] scaler.pkl (ton scaler)
├── [ ] frontend/
│   ├── [ ] index.html
│   ├── [ ] style.css
│   └── [ ] script.js
├── [ ] requirements.txt
├── [ ] Procfile
├── [ ] runtime.txt
├── [ ] .gitignore
└── [ ] README.md
```

## 🔧 Fichiers de configuration

### requirements.txt
```
[ ] Flask==3.0.0
[ ] flask-cors==4.0.0
[ ] tensorflow-cpu==2.15.0
[ ] numpy==1.24.3
[ ] pandas==2.1.4
[ ] scikit-learn==1.3.2
[ ] gunicorn==21.2.0
```

### Procfile
```
[ ] Contient: web: gunicorn api.app:app --timeout 120 --workers 1 --bind 0.0.0.0:$PORT
```

### runtime.txt
```
[ ] Contient: python-3.11.0
```

## 🧪 Tests locaux

Avant de déployer, exécute ces tests :

```bash
# Test 1: Vérifier la structure
[ ] python test_local.py

# Test 2: Générer des données de test
[ ] python generate_test_data.py

# Test 3: Tester l'import du modèle
[ ] python -c "from api.predictor import CICIDSPredictor; print('✅ OK')"

# Test 4: Vérifier Flask
[ ] python -c "from api.app import app; print('✅ OK')"
```

## 📦 Installation des dépendances

```bash
# Installer les dépendances
[ ] pip install -r requirements.txt

# Vérifier que tout est installé
[ ] pip list | grep Flask
[ ] pip list | grep tensorflow
[ ] pip list | grep gunicorn
```

## 🔐 Git et GitHub

### Initialisation Git
```bash
[ ] git init
[ ] git config --global user.name "Ton Nom"
[ ] git config --global user.email "ton_email@example.com"
```

### Création du repository GitHub
```
[ ] Compte GitHub créé
[ ] Repository "intrusion-detection-api" créé
[ ] Repository configuré en "Public"
```

### Premier commit
```bash
[ ] git add .
[ ] git commit -m "Initial commit: Intrusion Detection System"
[ ] git remote add origin https://github.com/TON_USERNAME/intrusion-detection-api.git
[ ] git branch -M main
[ ] git push -u origin main
```

### Vérifications GitHub
```
[ ] Tous les fichiers sont visibles sur GitHub
[ ] Le dossier models/ contient les 2 fichiers (.h5 et .pkl)
[ ] Le dossier api/ contient les 3 fichiers Python
[ ] Le dossier frontend/ contient les 3 fichiers web
[ ] Les fichiers de config sont à la racine
```

## 🚀 Déploiement Render

### Création du compte
```
[ ] Compte Render créé avec GitHub
[ ] Email vérifié
```

### Configuration du service
```
[ ] New Web Service créé
[ ] Repository GitHub connecté
[ ] Branch: main
[ ] Environment: Python 3
[ ] Build Command: pip install -r requirements.txt
[ ] Start Command: (laisser vide - Procfile utilisé)
[ ] Plan: Free sélectionné
```

### Déploiement
```
[ ] Déploiement lancé
[ ] Build réussi (pas d'erreurs)
[ ] Deploy réussi
[ ] Service "Live" (vert)
[ ] URL obtenue
```

## 🧪 Tests post-déploiement

### Test 1: Interface Web
```
[ ] Visiter: https://TON_URL.onrender.com
[ ] L'interface s'affiche correctement
[ ] Pas d'erreurs dans la console navigateur (F12)
[ ] Le statut est "✅ Système opérationnel"
```

### Test 2: API Health
```bash
[ ] curl https://TON_URL.onrender.com/api/health
[ ] Réponse: {"status": "healthy", "model_loaded": true}
```

### Test 3: Prédiction unique
```
[ ] Aller sur l'onglet "Prédiction Unique"
[ ] Cliquer "Charger un exemple"
[ ] Cliquer "Analyser"
[ ] Résultat affiché (ATTACK ou NORMAL)
```

### Test 4: Prédiction batch
```
[ ] Générer des données de test: python generate_test_data.py
[ ] Uploader test_data_sample.csv dans l'interface
[ ] Résultats affichés correctement
```

### Test 5: Statistiques
```
[ ] Aller sur l'onglet "Statistiques"
[ ] Les statistiques du modèle s'affichent
[ ] Accuracy: 99.36% visible
```

## 📊 Vérifications finales

### Performance
```
[ ] Temps de réponse < 5 secondes pour prédiction unique
[ ] Temps de réponse < 30 secondes pour CSV (100 lignes)
[ ] Pas d'erreurs "Out of Memory"
```

### Logs Render
```
[ ] Pas d'erreurs dans les logs
[ ] Modèle chargé avec succès
[ ] Application démarrée correctement
```

### Accessibilité
```
[ ] L'URL est accessible depuis n'importe quel appareil
[ ] L'interface est responsive (mobile/tablette/desktop)
[ ] Pas d'erreurs CORS
```

## 📝 Documentation

```
[ ] README.md à jour avec l'URL du déploiement
[ ] Captures d'écran prises pour le rapport
[ ] Tests documentés avec résultats
```

## 🎯 Prêt pour la présentation

```
[ ] URL du système notée et testée
[ ] Données de test préparées
[ ] Démonstration répétée et fonctionnelle
[ ] Questions potentielles préparées
```

## 🔄 Mises à jour futures

Si tu dois modifier le code :

```bash
# 1. Modifier les fichiers localement
# 2. Tester localement
[ ] python test_local.py

# 3. Commit et push
[ ] git add .
[ ] git commit -m "Description des changements"
[ ] git push origin main

# 4. Render redéploiera automatiquement !
```

## 📞 Support

En cas de problème :
1. Consulter les logs sur Render Dashboard
2. Vérifier cette checklist
3. Relire GUIDE_DEPLOIEMENT.md
4. Chercher l'erreur spécifique sur Google

## 🎉 Succès !

Une fois tous les points cochés, ton système est :
- ✅ Déployé
- ✅ Fonctionnel
- ✅ Accessible en ligne
- ✅ Prêt pour la démonstration

**Félicitations ! 🚀**