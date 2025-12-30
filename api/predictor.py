import tensorflow as tf
import numpy as np
import joblib
import os
import logging

logger = logging.getLogger(__name__)

class CICIDSPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _load_resources(self):
        """Charge le modèle uniquement s'il n'est pas déjà en mémoire"""
        if self.model is None:
            print("🚀 Chargement des ressources ML en mémoire...")
            model_path = os.path.join(self.base_path, 'models', 'mlp_model_subset.h5')
            scaler_path = os.path.join(self.base_path, 'models', 'scaler.pkl')
            
            # Charger le modèle avec des options d'économie de mémoire
            self.model = tf.keras.models.load_model(model_path, compile=False)
            self.scaler = joblib.load(scaler_path)
            print("✅ Ressources ML chargées !")
            
    def predict(self, data):
        # --- CETTE PARTIE DOIT ÊTRE INDENTÉE ---
        self._load_resources()
        
        # 1. Normalisation
        data_scaled = self.scaler.transform(data)
        
        # 2. Prédiction (Probabilités brutes)
        predictions = self.model.predict(data_scaled, verbose=0)
        
        # --- LOGS DE DEBUG (Visibles dans Render) ---
        # On affiche les probabilités pour chaque ligne du CSV
        probs = predictions.flatten().tolist()
        print(f"DEBUG - Probabilités brutes détectées : {probs}")
        
        # 3. Seuil de décision (Ajusté à 0.7 pour plus de précision)
        # Retourne 1 (Attack) si probabilité > 0.7, sinon 0 (Normal)
        return (predictions > 0.7).astype(int).flatten().tolist()
