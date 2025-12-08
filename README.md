# 🛡️ Système de Détection d'Intrusion - CICIDS2017

Système professionnel de détection d'attaques réseau utilisant le Deep Learning (MLP) déployé sur Render.

## 📊 Caractéristiques

- **Modèle**: MLP (Multi-Layer Perceptron) avec 4 couches
- **Architecture**: 128 → 64 → 32 → 1 neurones
- **Précision**: 99.36%
- **Dataset**: CICIDS2017 (3.47 Go)
- **Types d'attaques**: DDoS, PortScan, BotNet, Web Attack, Brute Force SSH/FTP

## 🚀 Déploiement sur Render

### Étape 1: Préparer ton projet localement

1. **Créer la structure de dossiers:**
```bash
mkdir intrusion-detection-api
cd intrusion-detection-api
```

2. **Créer tous les dossiers nécessaires:**
```bash
mkdir api models frontend
```

3. **Copier tous les fichiers:**
   - `api/app.py` → Code API Flask
   - `api/predictor.py` → Logique de prédiction
   - `api/__init__.py` → Fichier vide
   - `models/mlp_model_subset.h5` → TON MODÈLE
   - `models/scaler.pkl` → TON SCALER
   - `frontend/index.html` → Interface web
   - `frontend/style.css` → Design
   - `frontend/script.js` → Logique JS
   - `requirements.txt` → Dépendances
   - `Procfile` → Config Render
   - `runtime.txt` → Version Python
   - `README.md` → Ce fichier

### Étape 2: Créer un dépôt GitHub

1. **Initialiser Git:**
```bash
git init
git add .
git commit -m "Initial commit: Intrusion Detection System"
```

2. **Créer un compte GitHub** (si tu n'en as pas):
   - Aller sur https://github.com
   - Créer un compte gratuit

3. **Créer un nouveau repository:**
   - Cliquer sur "New repository"
   - Nom: `intrusion-detection-api`
   - Visibilité: Public
   - Ne pas initialiser avec README

4. **Pousser ton code:**
```bash
git remote add origin https://github.com/TON_USERNAME/intrusion-detection-api.git
git branch -M main
git push -u origin main
```

### Étape 3: Déployer sur Render

1. **Créer un compte Render:**
   - Aller sur https://render.com
   - S'inscrire avec GitHub (gratuit, pas de carte bancaire)

2. **Créer un nouveau Web Service:**
   - Cliquer sur "New +" → "Web Service"
   - Connecter ton repository GitHub
   - Sélectionner `intrusion-detection-api`

3. **Configuration:**
   - **Name**: `intrusion-detection-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: Laisser vide (Procfile utilisé)
   - **Plan**: Sélectionner "Free"

4. **Variables d'environnement (optionnel):**
   - Aucune nécessaire pour le moment

5. **Cliquer sur "Create Web Service"**

6. **Attendre le déploiement** (5-10 minutes)

### Étape 4: Accéder à ton application

Une fois déployé, Render te donnera une URL comme:
```
https://intrusion-detection-api.onrender.com
```

Ton système est maintenant en ligne ! 🎉

## 📡 API Endpoints

### Health Check
```bash
GET /api/health
```

### Prédiction unique
```bash
POST /api/predict
Content-Type: application/json

{
  "features": [0.5, 1.2, 3.4, ..., 78 valeurs]
}
```

### Prédiction batch (CSV)
```bash
POST /api/predict_batch
Content-Type: multipart/form-data

file: fichier.csv
```

### Statistiques
```bash
GET /api/stats
```

## 🧪 Tester l'API

### Avec curl:
```bash
# Health check
curl https://TON_URL.onrender.com/api/health

# Prédiction
curl -X POST https://TON_URL.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.2, 3.4, ..., 78 valeurs]}'
```

### Avec Python:
```python
import requests

url = "https://TON_URL.onrender.com/api/predict"
data = {"features": [1.2, 3.4, ...]}  # 78 valeurs

response = requests.post(url, json=data)
print(response.json())
```

## 🎨 Interface Web

Accéder à l'interface web à l'adresse racine:
```
https://TON_URL.onrender.com
```

Fonctionnalités:
- ✅ Prédiction unique avec JSON
- ✅ Analyse de fichier CSV
- ✅ Statistiques du modèle
- ✅ Interface moderne et responsive

## ⚠️ Notes importantes

### Limitation du plan gratuit Render:
- **RAM**: 512 MB (suffisant pour ton modèle MLP)
- **Inactivité**: Le service s'endort après 15 min d'inactivité
- **Réveil**: 30-60 secondes au premier accès après endormissement
- **Heures**: 750h gratuites/mois (largement suffisant)

### Optimisations possibles:
1. **Réduire la taille du modèle** (déjà fait, 200 KB)
2. **Utiliser un worker léger** (déjà fait, gunicorn avec 1 worker)
3. **Limiter les prédictions batch** (limite à 100 lignes affichées)

## 🔧 Dépannage

### Problème: "Application failed to start"
- Vérifier que `mlp_model_subset.h5` et `scaler.pkl` sont bien dans `models/`
- Vérifier les logs sur Render Dashboard

### Problème: "Out of memory"
- Réduire le nombre de workers dans Procfile (déjà à 1)
- Limiter la taille des fichiers CSV uploadés

### Problème: "Slow response"
- Normal au premier accès (réveil du service)
- Considérer un plan payant si besoin de réactivité constante

## 📈 Améliorations futures

- [ ] Ajouter une authentification
- [ ] Stocker l'historique des prédictions
- [ ] Ajouter des graphiques de visualisation
- [ ] Supporter plus de formats (Excel, JSON)
- [ ] Ajouter un système de cache

## 👨‍💻 Auteur

Système développé dans le cadre d'un projet de détection d'intrusion par Deep Learning.

## 📄 Licence

MIT License - Utilisation libre pour projets académiques et commerciaux.