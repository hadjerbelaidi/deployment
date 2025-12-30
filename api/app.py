from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import logging
from api.predictor import CICIDSPredictor

# Configuration du logging pour voir les erreurs dans les logs Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Initialisation du prédicteur (charge le modèle et le scaler)
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
        # 1. Vérifier si un fichier est présent dans la requête
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier n\'a été envoyé.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide.'}), 400

        # 2. Charger le CSV en mémoire avec Pandas
        df = pd.read_csv(file)
        logger.info(f"Fichier reçu. Colonnes détectées : {df.shape[1]}")

        # 3. NETTOYAGE AUTOMATIQUE DES DONNÉES
        # On retire les colonnes non-numériques ou labels qui causent l'erreur 500
        cols_to_drop = [
            'Label', 'label', ' Label', 'Label ', 
            'Source IP', 'Destination IP', 'Timestamp', 'Flow ID', 'Unnamed: 0'
        ]
        
        # Supprime les colonnes de la liste si elles existent dans le CSV
        df_cleaned = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

        # 4. FORCER LE FORMAT (78 colonnes attendues par ton MLP)
        # Si après nettoyage il reste plus de 78 colonnes, on ne garde que les 78 premières
        if df_cleaned.shape[1] > 78:
            logger.warning(f"Trop de colonnes ({df_cleaned.shape[1]}). Troncature à 78.")
            df_cleaned = df_cleaned.iloc[:, :78]
        
        if df_cleaned.shape[1] < 78:
            return jsonify({
                'error': f'Le modèle attend 78 colonnes numériques, mais le fichier en contient {df_cleaned.shape[1]}.'
            }), 400

        # 5. EXECUTER LA PRÉDICTION
        # Le prédicteur va appliquer le scaler.pkl automatiquement
        results = predictor.predict(df_cleaned)
        
        logger.info("Prédiction réussie !")
        return jsonify({'predictions': results})
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse : {str(e)}")
        # On renvoie l'erreur réelle pour t'aider à débugger
        return jsonify({'error': f"Erreur interne : {str(e)}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retourne les métriques pour le tableau de bord"""
    return jsonify({
        'model_type': 'Multi-Layer Perceptron (MLP)',
        'framework': 'TensorFlow/Keras',
        'dataset': 'CICIDS2017',
        'accuracy_reported': '99.36%'
    })

if __name__ == '__main__':
    # Utilisation du port défini par Render ou 10000 par défaut
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
