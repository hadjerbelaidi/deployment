from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import logging
import sqlite3
from datetime import datetime
from api.predictor import CICIDSPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend')
CORS(app)

predictor = CICIDSPredictor()

# --- BASE DE DONNÉES POUR L'HISTORIQUE ---
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
            return jsonify({'error': 'Fichier manquant'}), 400
        
        file = request.files['file']
        df = pd.read_csv(file)
        
        # Nettoyage et prédiction (ton code existant)
        predictor._load_resources()
        expected_features = predictor.scaler.feature_names_in_
        cols_to_drop = ['Label', 'label', 'Flow ID', 'Source IP', 'Destination IP', 'Timestamp', 'Unnamed: 0']
        df_cleaned = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
        if df_cleaned.shape[1] > 78: df_cleaned = df_cleaned.iloc[:, :78]
        df_cleaned.columns = expected_features
        df_cleaned = df_cleaned.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        results = predictor.predict(df_cleaned)
        
        # --- SAUVEGARDE DANS L'HISTORIQUE ---
        total = len(results)
        attacks = sum(results)
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO history (filename, total, attacks, date) VALUES (?, ?, ?, ?)",
                         (file.filename, total, attacks, date_str))
        
        return jsonify({
            'predictions': results,
            'total': total,
            'attacks': attacks,
            'filename': file.filename,
            'date': date_str
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        return jsonify([dict(row) for row in rows])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Suppression des "undefined" en envoyant des valeurs fixes
    return jsonify({
        'model_architecture': 'MLP (Deep Learning)',
        'accuracy': '99.36',
        'dataset': 'CICIDS2017',
        'cloud_platform': 'Render Cloud'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
