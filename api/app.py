from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import sqlite3
import logging
from datetime import datetime
from api.predictor import CICIDSPredictor

# Configuration
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='../frontend')
CORS(app)

predictor = CICIDSPredictor()
DB_PATH = 'history.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS history 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         filename TEXT, total INTEGER, attacks INTEGER, date TEXT)''')
init_db()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier'}), 400
        
        file = request.files['file']
        df = pd.read_csv(file)
        
        # Préparation des données pour le modèle
        predictor._load_resources()
        expected_features = predictor.scaler.feature_names_in_
        cols_to_drop = ['Label', 'label', 'Flow ID', 'Source IP', 'Destination IP', 'Timestamp', 'Unnamed: 0']
        df_cleaned = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
        
        if df_cleaned.shape[1] > 78: df_cleaned = df_cleaned.iloc[:, :78]
        df_cleaned.columns = expected_features
        df_cleaned = df_cleaned.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # Prédiction (retourne une liste de 0 et 1)
        results = predictor.predict(df_cleaned)
        
        total = len(results)
        attacks_count = int(sum(results)) # Somme des '1'
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Sauvegarde en base de données
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO history (filename, total, attacks, date) VALUES (?, ?, ?, ?)",
                         (file.filename, total, attacks_count, date_str))
        
        return jsonify({
            'predictions': results, # On envoie la liste pour le tableau détaillé
            'total': total,
            'attacks': attacks_count,
            'filename': file.filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT 10")
        return jsonify([dict(row) for row in cursor.fetchall()])

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': predictor.model is not None})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
