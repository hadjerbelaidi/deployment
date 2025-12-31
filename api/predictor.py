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
        if self.model is None:
            model_path = os.path.join(self.base_path, 'models', 'mlp_model_subset.h5')
            scaler_path = os.path.join(self.base_path, 'models', 'scaler.pkl')
            self.model = tf.keras.models.load_model(model_path, compile=False)
            self.scaler = joblib.load(scaler_path)

    def predict(self, data):
        self._load_resources()
        
        # --- LOGIQUE DE DÉTECTION DU SCALING ---
        # Si la valeur max est > 10, ce sont des données BRUTES (ex: Port 80)
        # Si la valeur max est < 10, ce sont des données DÉJÀ SCALÉES (ex: -0.45)
        valeur_max = np.abs(data.values).max()
        
        if valeur_max > 10:
            print(f"DEBUG: Données brutes détectées (max={valeur_max}). Application du scaler.")
            data_final = self.scaler.transform(data)
        else:
            print(f"DEBUG: Données déjà normalisées (max={valeur_max}). On saute le scaler.")
            data_final = data.values

        predictions = self.model.predict(data_final, verbose=0)
        
        # Log des probabilités brutes pour voir ce que l'IA pense vraiment
        probs = predictions.flatten().tolist()
        print(f"DEBUG - Probabilités brutes : {probs}")
        
        # Utilise 0.5 comme seuil car ton modèle a été entraîné proprement
        return (predictions > 0.5).astype(int).flatten().tolist()
