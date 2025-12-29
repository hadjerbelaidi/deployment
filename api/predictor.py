import tensorflow as tf
import numpy as np
import joblib
import os

class CICIDSPredictor:
    def __init__(self):
        # Définition des chemins vers les fichiers dans le dossier 'models'
        base_path = os.path.dirname(os.path.dirname(__file__))
        model_path = os.path.join(base_path, 'models', 'mlp_model_subset.h5')
        scaler_path = os.path.join(base_path, 'models', 'scaler.pkl')
        
        print(f"Tentative de chargement du modèle depuis : {model_path}")
        
        try:
            # Chargement du modèle Keras (.h5)
            self.model = tf.keras.models.load_model(model_path)
            print("✅ Modèle MLP chargé avec succès !")
            
            # Chargement du Scaler (.pkl)
            self.scaler = joblib.load(scaler_path)
            print("✅ Scaler chargé avec succès !")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement : {str(e)}")
            raise e

    def predict(self, data):
        """
        Prend des données brutes, les normalise et retourne la prédiction.
        data: doit être un array numpy ou un DataFrame
        """
        # 1. Normalisation des données
        data_scaled = self.scaler.transform(data)
        
        # 2. Prédiction par le modèle MLP
        predictions = self.model.predict(data_scaled)
        
        # 3. Récupération de l'index de la classe avec la plus haute probabilité
        # (0 pour Normal, 1, 2, 3... pour les types d'attaques CICIDS)
        result = np.argmax(predictions, axis=1)
        
        return result.tolist()
