import tensorflow as tf
import numpy as np
import joblib
import os

class CICIDSPredictor:
    def __init__(self):
        # On définit les chemins en interne
        base_path = os.path.dirname(os.path.dirname(__file__))
        model_path = os.path.join(base_path, 'models', 'mlp_model_subset.h5')
        scaler_path = os.path.join(base_path, 'models', 'scaler.pkl')
        
        try:
            self.model = tf.keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            print("✅ Modèle et Scaler chargés avec succès !")
        except Exception as e:
            print(f"❌ Erreur interne predictor: {str(e)}")
            raise e

    def predict(self, data):
        data_scaled = self.scaler.transform(data)
        predictions = self.model.predict(data_scaled)
        return np.argmax(predictions, axis=1).tolist()
