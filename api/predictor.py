import tensorflow as tf
import numpy as np
import joblib
import os

class CICIDSPredictor:
    def __init__(self):
        # Localisation absolue du dossier racine du projet
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, 'models', 'mlp_model_subset.h5')
        scaler_path = os.path.join(base_path, 'models', 'scaler.pkl')
        
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Fichier modèle introuvable à : {model_path}")
            
            # Chargement du modèle et du scaler
            self.model = tf.keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            print("✅ Modèle et Scaler chargés avec succès !")
        except Exception as e:
            print(f"❌ Erreur de chargement predictor: {str(e)}")
            raise e

    def predict(self, data):
        """
        Effectue la normalisation et la prédiction.
        'data' doit être un DataFrame avec les noms de colonnes corrects
        ou un tableau numpy de forme (N, 78).
        """
        try:
            # 1. Normalisation (utilise les noms de colonnes si data est un DataFrame)
            data_scaled = self.scaler.transform(data)
            
            # 2. Prédiction (retourne une probabilité entre 0 et 1)
            predictions = self.model.predict(data_scaled, verbose=0)
            
            # 3. Conversion en classes binaires (Seuil 0.5)
            # On utilise flatten() pour transformer en liste simple [0, 1, 0...]
            return (predictions > 0.5).astype(int).flatten().tolist()
            
        except Exception as e:
            print(f"❌ Erreur lors de la prédiction: {str(e)}")
            raise e
