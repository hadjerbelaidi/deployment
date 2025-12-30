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

# --- CONFIGURATION DES CHEMINS (MODIFIÉE) ---
# On remonte d'un niveau pour sortir de 'api' puis on entre dans 'models'
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'mlp_model_subset.h5')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.pkl')

model = None
scaler = None

# Chargement au démarrage
try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info(f"✅ Modèle chargé depuis : {MODEL_PATH}")
    else:
        logger.error(f"❌ Modèle introuvable à : {MODEL_PATH}")

    if os.path.exists(SCALER_PATH):
        scaler = joblib.load(SCALER_PATH)
        logger.info(f"✅ Scaler chargé depuis : {SCALER_PATH}")
    else:
        logger.error(f"❌ Scaler introuvable à : {SCALER_PATH}")
except Exception as e:
    logger.error(f"❌ Erreur critique chargement ML: {e}")

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
        'scaler_loaded': scaler is not None,
        'paths_checked': {'model': MODEL_PATH, 'scaler': SCALER_PATH}
    })

@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    if model is None or scaler is None:
        return jsonify({'error': 'Modèle ou Scaler non chargé sur le serveur'}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        df = pd.read_csv(file)
        
        # Nettoyage rapide (enlever les colonnes de texte)
        cols_to_drop = ['Label', 'label', 'Flow ID', 'Source IP', 'Destination IP', 'Timestamp']
        for col in cols_to_drop:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Vérification des colonnes (doit être 78)
        if df.shape[1] != 78:
            return jsonify({'error': f'Le modèle attend 78 colonnes, reçu {df.shape[1]}. Vérifiez votre CSV.'}), 400

        # Prétraitement et Prédiction
        X_scaled = scaler.transform(df)
        predictions = model.predict(X_scaled)
        
        # Conversion 0/1
        results = (predictions > 0.5).astype(int).flatten().tolist()
        
        return jsonify({'predictions': results})
    
    except Exception as e:
        logger.error(f"❌ Erreur prédiction: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
