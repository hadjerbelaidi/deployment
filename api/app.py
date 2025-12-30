from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import pandas as pd
import os
from api.predictor import CICIDSPredictor
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend') # Ajusté pour pointer vers le dossier frontend à la racine
CORS(app)

# Initialiser le prédicteur sans arguments (la classe gère ses propres chemins)
try:
    predictor = CICIDSPredictor()
    logger.info("✅ Modèle chargé avec succès")
except Exception as e:
    logger.error(f"❌ Erreur chargement modèle: {e}")
    predictor = None

@app.route('/')
def index():
    """Servir la page d'accueil"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Servir les fichiers statiques (css, js, images)"""
    return send_from_directory(app.static_folder, path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifier l'état de l'API"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor is not None,
        'version': '1.0.0'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Prédire si une connexion est une attaque (Données JSON)"""
    if predictor is None:
        return jsonify({'error': 'Modèle non chargé'}), 500
    
    try:
        data = request.get_json()
        if 'features' not in data:
            return jsonify({'error': 'Clé "features" manquante'}), 400
        
        features = data['features']
        # Utilisation de la méthode predict de notre classe
        result = predictor.predict(np.array([features]))
        
        return jsonify({'prediction': result[0]})
    
    except Exception as e:
        logger.error(f"Erreur prédiction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    """Prédire plusieurs connexions depuis un fichier CSV"""
    if predictor is None:
        return jsonify({'error': 'Modèle non chargé'}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.endswith('.csv'):
            return jsonify({'error': 'Format invalide. Utilisez CSV'}), 400
        
        # Lire le CSV
        df = pd.read_csv(file)
        
        # Supposons que le CSV contient uniquement les features nécessaires
        results = predictor.predict(df)
        
        return jsonify({'predictions': results})
    
    except Exception as e:
        logger.error(f"Erreur prédiction batch: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtenir les informations du projet pour le mémoire"""
    return jsonify({
        'model_architecture': 'MLP (Multi-Layer Perceptron)',
        'accuracy': 99.36,
        'dataset': 'CICIDS2017',
        'cloud_platform': 'Render (PaaS)',
        'attack_types': [
            'DDoS', 'PortScan', 'BotNet', 
            'Web Attack', 'Brute Force SSH/FTP'
        ]
    })

if __name__ == '__main__':
    # Render utilise la variable d'environnement PORT
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
