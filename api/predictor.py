import tensorflow as tf
import numpy as np
import joblib
import os

class CICIDSPredictor:
    def __init__(self):
        # On remonte d'un niveau (..) depuis le dossier 'api' pour trouver 'models'
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, 'models', 'mlp_model_subset.h5')
        scaler_path = os.path.join(base_path, 'models', 'scaler.pkl')
        
        try:
            # Vérification de l'existence avant chargement pour éviter le crash 500
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Fichier modèle introuvable à : {model_path}")
            
            self.model = tf.keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            print("✅ Modèle et Scaler chargés avec succès !")
        except Exception as e:
            print(f"❌ Erreur de chargement : {str(e)}")
            raise e

    def predict(self, data):
        # Utilisation du scaler sur les données
        data_scaled = self.scaler.transform(data)
        # Prédiction binaire
        predictions = self.model.predict(data_scaled)
        # On retourne 1 si probabilité > 0.5, sinon 0
        return (predictions > 0.5).astype(int).flatten().tolist()
