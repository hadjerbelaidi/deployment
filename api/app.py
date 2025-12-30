from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import logging
from api.predictor import CICIDSPredictor

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Initialisation du prédicteur
try:
    predictor = CICIDSPredictor()
    logger.info("✅ Système de prédiction chargé et prêt.")
except Exception as e:
    logger.error(f"❌ Échec du chargement du prédicteur : {e}")
    predictor = None

@app.route('/')
def index():
    """Sert la page d'accueil frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Sert les fichiers CSS/JS/Images"""
    return send_from_directory(app.static_folder, path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifie si le serveur et le modèle sont en ligne"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor is not None,
        'api_version': '1.0.0'
    })

@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    """Route principale pour l'analyse du fichier CSV"""
    if predictor is None:
        return jsonify({'error': 'Le modèle n\'est pas disponible sur le serveur.'}), 500
    
    try:
        # 1. Vérifier si un fichier est présent
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier n\'a été envoyé.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide.'}), 400
        
        # 2. Charger le CSV
        df = pd.read_csv(file)
        logger.info(f"📁 Fichier reçu - Shape: {df.shape}")
        
        # 3. NETTOYER LES NOMS DE COLONNES (enlever les espaces)
        df.columns = df.columns.str.strip()
        logger.info(f"🧹 Colonnes nettoyées: {list(df.columns[:5])}...")
        
        # 4. Supprimer les colonnes non-numériques
        cols_to_drop = [
            'Label', 'label', 'Source IP', 'Destination IP', 
            'Timestamp', 'Flow ID', 'Unnamed: 0'
        ]
        df_cleaned = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
        
        # 5. Convertir tout en numérique (au cas où)
        df_cleaned = df_cleaned.apply(pd.to_numeric, errors='coerce')
        
        # 6. Remplir les valeurs manquantes avec 0
        df_cleaned = df_cleaned.fillna(0)
        
        logger.info(f"✅ Données nettoyées - Shape: {df_cleaned.shape}")
        
        # 7. Vérifier le nombre de colonnes (78 attendues)
        if df_cleaned.shape[1] > 78:
            logger.warning(f"⚠️ Trop de colonnes ({df_cleaned.shape[1]}). Troncature à 78.")
            df_cleaned = df_cleaned.iloc[:, :78]
        
        if df_cleaned.shape[1] < 78:
            return jsonify({
                'error': f'Le modèle attend 78 colonnes numériques, mais le fichier en contient {df_cleaned.shape[1]} après nettoyage.'
            }), 400
        
        # 8. PRÉDICTION
        results = predictor.predict(df_cleaned)
        
        logger.info(f"✅ Prédiction réussie ! {len(results)} lignes analysées")
        
        return jsonify({
            'predictions': results,
            'total': len(results),
            'attacks': sum(results),
            'normal': len(results) - sum(results)
        })
    
    except Exception as e:
        logger.error(f"❌ Erreur : {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f"Erreur : {str(e)}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retourne les métriques"""
    return jsonify({
        'model_architecture': 'MLP (Multi-Layer Perceptron)',
        'accuracy': 99.36,
        'dataset': 'CICIDS2017',
        'cloud_platform': 'Render'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
