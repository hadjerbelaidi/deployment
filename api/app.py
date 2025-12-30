from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import pandas as pd
import os
import tensorflow as tf
import joblib
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend') 
CORS(app)

# --- CHARGEMENT DIRECT DU MODÈLE ET DU SCALER ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'mlp_model_subset.h5')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'scaler.pkl')

model = None
scaler = None

try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("✅ Modèle chargé avec succès")
    if os.path.exists(SCALER_PATH):
        scaler = joblib.load(SCALER_PATH)
        logger.info("✅ Scaler chargé avec succès")
except Exception as e:
    logger.error(f"❌ Erreur chargement fichiers ML: {e}")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None
    })

@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    if model is None:
        return jsonify({'error': 'Modèle non chargé sur le serveur'}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        df = pd.read_csv(file)
        
        # --- NETTOYAGE AUTOMATIQUE ---
        # 1. On retire la colonne Label si elle est présente
        if 'Label' in df.columns:
            df = df.drop(columns=['Label'])
        elif 'label' in df.columns:
            df = df.drop(columns=['label'])

        # 2. On s'assure d'avoir exactement 78 colonnes
        # Si ton modèle a été entraîné sur 78 features, il en faut 78 ici.
        if df.shape[1] != 78:
            return jsonify({'error': f'Le modèle attend 78 colonnes, reçu {df.shape[1]}'}), 400

        # 3. Application du scaler (INDISPENSABLE pour un MLP)
        # On transforme les données brutes du CSV en données normalisées
        X_scaled = scaler.transform(df)
        
        # 4. Prédiction
        predictions = model.predict(X_scaled)
        
        # 5. Conversion des probabilités (0.0 à 1.0) en classes (0 ou 1)
        results = (predictions > 0.5).astype(int).flatten().tolist()
        
        return jsonify({'predictions': results})
    
    except Exception as e:
        logger.error(f"❌ Erreur pendant le traitement: {str(e)}")
        return jsonify({'error': f"Erreur serveur: {str(e)}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'model_architecture': 'MLP (128-64-32)',
        'accuracy': 99.36,
        'dataset': 'CICIDS2017',
        'cloud_platform': 'Render (PaaS)'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
