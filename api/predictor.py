import tensorflow as tf
import numpy as np
import joblib
import os

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
        self._load_resources()
        # Normalisation
        data_scaled = self.scaler.transform(data)
        # Prédiction sans logs pour économiser du CPU/RAM
        predictions = self.model.predict(data_scaled, verbose=0)
        return (predictions < 0.5).astype(int).flatten().tolist()

