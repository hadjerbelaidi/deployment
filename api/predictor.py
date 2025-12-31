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
        self._load_resources()
        
        # Vérification intelligente : 
        # Si la valeur maximale est très petite (ex < 10), 
        # c'est que les données sont déjà scalées.
        if data.values.max() < 10:
            print("INFO: Données déjà scalées détectées. Saut du transform.")
            data_final = data.values
        else:
            print("INFO: Données brutes détectées. Application du Scaler.")
            data_final = self.scaler.transform(data)
        
        # Prédiction
        predictions = self.model.predict(data_final, verbose=0)
        
        probs = predictions.flatten().tolist()
        print(f"DEBUG - Probabilités brutes détectées : {probs}")
        
        # On remet le seuil à 0.5 pour voir si ça bouge
        return (predictions > 0.5).astype(int).flatten().tolist()
