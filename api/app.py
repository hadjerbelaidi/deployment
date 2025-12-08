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

app = Flask(__name__, static_folder='frontend')
CORS(app)

# Initialiser le prédicteur
try:
    predictor = CICIDSPredictor(
        model_path='models/mlp_model_subset.h5',
        scaler_path='models/scaler.pkl'
    )
    logger.info("✅ Modèle chargé avec succès")
except Exception as e:
    logger.error(f"❌ Erreur chargement modèle: {e}")
    predictor = None

@app.route('/')
def index():
    """Servir la page d'accueil"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Servir les fichiers statiques"""
    return send_from_directory('frontend', path)

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
    """Prédire si une connexion est une attaque"""
    if predictor is None:
        return jsonify({'error': 'Modèle non chargé'}), 500
    
    try:
        data = request.get_json()
        
        if 'features' not in data:
            return jsonify({'error': 'Clé "features" manquante'}), 400
        
        features = data['features']
        
        # Prédiction
        result = predictor.predict_single(features)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Erreur prédiction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    """Prédire plusieurs connexions depuis un CSV"""
    if predictor is None:
        return jsonify({'error': 'Modèle non chargé'}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Format invalide. Utilisez CSV'}), 400
        
        # Lire le CSV
        df = pd.read_csv(file)
        
        # Prédiction
        results = predictor.predict_batch(df)
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Erreur prédiction batch: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtenir les statistiques du modèle"""
    return jsonify({
        'model_architecture': 'MLP (Multi-Layer Perceptron)',
        'layers': [128, 64, 32, 1],
        'activation': 'ReLU + Sigmoid',
        'accuracy': 99.36,
        'dataset': 'CICIDS2017',
        'training_method': 'Progressive Chunk Training',
        'attack_types': [
            'DDoS', 'PortScan', 'BotNet', 
            'Web Attack', 'Brute Force SSH/FTP'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)