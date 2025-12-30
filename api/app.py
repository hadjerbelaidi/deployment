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
        # 1. Vérifier la présence du fichier
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide.'}), 400
        
        # 2. Charger le CSV
        df = pd.read_csv(file)
        logger.info(f"📁 Fichier reçu - Dimensions initiales: {df.shape}")

        # 3. Récupérer les noms exacts attendus par le Scaler
        # C'est ici que l'on récupère les noms avec/sans espaces du fit original
        expected_features = predictor.scaler.feature_names_in_
        
        # 4. Nettoyage initial des colonnes de texte/labels
        # On retire les colonnes inutiles pour ne garder que les features
        cols_to_drop = [
            'Label', 'label', 'Flow ID', 'Source IP', 
            'Destination IP', 'Timestamp', 'Unnamed: 0'
        ]
        df_cleaned = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

        # 5. Gestion des colonnes et Renommage forcé
        # Si après retrait des labels on a trop de colonnes, on tronque à 78
        if df_cleaned.shape[1] > 78:
            df_cleaned = df_cleaned.iloc[:, :78]

        # Si on a bien 78 colonnes, on leur donne les noms exacts du scaler
        # Cela règle l'erreur "Feature names unseen at fit time"
        if df_cleaned.shape[1] == len(expected_features):
            df_cleaned.columns = expected_features
            logger.info("✅ Colonnes renommées pour correspondre au Scaler")
        else:
            return jsonify({
                'error': f'Le modèle attend {len(expected_features)} colonnes, reçu {df_cleaned.shape[1]} après nettoyage.'
            }), 400

        # 6. Conversion numérique et gestion des NaN
        df_cleaned = df_cleaned.apply(pd.to_numeric, errors='coerce').fillna(0)

        # 7. PRÉDICTION
        # Envoie les données au predictor qui fera le transform() et le predict()
        results = predictor.predict(df_cleaned)
        
        logger.info(f"✅ Prédiction réussie ! {len(results)} lignes analysées")
        
        return jsonify({
            'predictions': results,
            'total': len(results),
            'attacks': sum(results),
            'normal': len(results) - sum(results)
        })
    
    except Exception as e:
        logger.error(f"❌ Erreur Serveur : {str(e)}")
        # On retourne l'erreur détaillée pour le débug
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retourne les métriques du modèle"""
    return jsonify({
        'model_architecture': 'MLP (Multi-Layer Perceptron)',
        'accuracy': 99.36,
        'dataset': 'CICIDS2017',
        'cloud_platform': 'Render'
    })
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    # On désactive le debug pour éviter les doubles chargements de modèle
    app.run(host='0.0.0.0', port=port, debug=False)

