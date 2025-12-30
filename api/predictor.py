import tensorflow as tf
import numpy as np
import joblib
import os

class CICIDSPredictor:
    def __init__(self):
        # Définition des chemins vers le dossier 'models' à la racine
        base_path = os.path.dirname(os.path.dirname(__file__))
        model_path = os.path.join(base_path, 'models', 'mlp_model_subset.h5')
        scaler_path = os.path.join(base_path, 'models', 'scaler.pkl')
        
        try:
            # Chargement du modèle Keras et du scaler scikit-learn
            self.model = tf.keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            print(f"✅ Modèle et Scaler chargés depuis {base_path}")
        except Exception as e:
            print(f"❌ Erreur critique chargement predictor: {str(e)}")
            raise e

    def predict(self, data):
        """
        Prédit les classes pour les données fournies.
        'data' peut être un tableau NumPy ou un DataFrame Pandas.
        """
        # 1. Normalisation avec le scaler d'entraînement
        data_scaled = self.scaler.transform(data)
        
        # 2. Prédiction (renvoie une probabilité entre 0 et 1)
        predictions = self.model.predict(data_scaled)
        
        # 3. Conversion binaire (MLP Sigmoid)
        # On aplatit le résultat et on transforme en 1 si > 0.5, sinon 0
        binary_results = (predictions > 0.5).astype(int).flatten().tolist()
        
        return binary_results
