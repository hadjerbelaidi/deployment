from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
from api.predictor import CICIDSPredictor
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Initialisation du prédicteur
try:
    predictor = CICIDSPredictor()
    logger.info("✅ Système de prédiction opérationnel")
except Exception as e:
    logger.error(f"❌ Échec de l'initialisation: {e}")
    predictor = None

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
        'model_loaded': predictor is not None
    })

@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    if predictor is None:
        return jsonify({'error': 'Modèle non chargé'}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        df = pd.read_csv(file)
        
        # --- NETTOYAGE DES DONNÉES AVANT SCALING ---
        # On supprime les colonnes de texte que le scaler ne peut pas traiter
        cols_to_drop = ['Label', 'label', 'Flow ID', 'Source IP', 'Destination IP', 'Timestamp']
        df_cleaned = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

        # Vérification du nombre de colonnes (doit correspondre à l'entraînement, ex: 78)
        # Si ton modèle attend 78 colonnes, df_cleaned doit en avoir 78.
        
        results = predictor.predict(df_cleaned)
        return jsonify({'predictions': results})
    
    except Exception as e:
        logger.error(f"Erreur prédiction batch: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'model_architecture': 'MLP (TensorFlow)',
        'accuracy': 99.36,
        'dataset': 'CICIDS2017'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
