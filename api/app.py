from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import logging
from api.predictor import CICIDSPredictor

# Configuration du logging pour surveiller la RAM dans Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# --- INSTANCIATION GLOBALE (SANS CHARGEMENT IMMÉDIAT) ---
# On crée l'objet, mais le modèle .h5 n'est pas encore lu.
predictor = CICIDSPredictor()

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
    """Vérifie l'état de l'API sans forcer le chargement du modèle"""
    return jsonify({
        'status': 'healthy',
        'api_version': '1.0.0',
        'note': 'Le modèle sera chargé lors de la première prédiction pour économiser la RAM.'
    })

@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    """Route principale pour l'analyse du fichier CSV"""
    try:
        # 1. Vérifier la présence du fichier
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide.'}), 400
        
        # 2. Charger le CSV en mémoire
        df = pd.read_csv(file)
        logger.info(f"📁 Fichier reçu - Lignes: {df.shape[0]}, Colonnes: {df.shape[1]}")

        # 3. Récupérer les noms attendus (Déclenche _load_resources si nécessaire)
        # On appelle une méthode pour s'assurer que le scaler est chargé
        predictor._load_resources()
        expected_features = predictor.scaler.feature_names_in_
        
        # 4. Nettoyage des colonnes (Labels, IPs, etc.)
        cols_to_drop = [
            'Label', 'label', 'Flow ID', 'Source IP', 
            'Destination IP', 'Timestamp', 'Unnamed: 0'
        ]
        df_cleaned = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

        # 5. Forcer le format à 78 colonnes
        if df_cleaned.shape[1] > 78:
            df_cleaned = df_cleaned.iloc[:, :78]

        # 6. Renommage pour le Scaler (Évite l'erreur Feature Names Mismatch)
        if df_cleaned.shape[1] == len(expected_features):
            df_cleaned.columns = expected_features
        else:
            return jsonify({
                'error': f'Format invalide. Attendu: {len(expected_features)} colonnes numériques, reçu: {df_cleaned.shape[1]}'
            }), 400

        # 7. Conversion numérique finale
        df_cleaned = df_cleaned.apply(pd.to_numeric, errors='coerce').fillna(0)

        # 8. EXÉCUTION DE LA PRÉDICTION (MLP)
        # L'appel à predict() gère le reste
        results = predictor.predict(df_cleaned)
        
        logger.info(f"✅ Analyse terminée : {sum(results)} attaques détectées.")
        
        return jsonify({
            'predictions': results,
            'total': len(results),
            'attacks': sum(results),
            'normal': len(results) - sum(results)
        })
    
    except Exception as e:
        logger.error(f"❌ Erreur critique : {str(e)}")
        return jsonify({'error': f"Erreur serveur : {str(e)}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'model': 'MLP Classifier',
        'dataset': 'CICIDS2017',
        'status': 'Optimized for Render (Memory Limited)'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    # debug=False est CRUCIAL pour éviter que Flask ne charge le modèle deux fois en RAM
    app.run(host='0.0.0.0', port=port, debug=False)
