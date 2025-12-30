class CICIDSPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _load_resources(self):
        if self.model is None:
            model_path = os.path.join(self.base_path, 'models', 'mlp_model_subset.h5')
            scaler_path = os.path.join(self.base_path, 'models', 'scaler.pkl')
            self.model = tf.keras.models.load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            print("✅ Ressources chargées à la demande")

    def predict(self, data):
        self._load_resources() # Charge seulement si nécessaire
        data_scaled = self.scaler.transform(data)
        predictions = self.model.predict(data_scaled, verbose=0)
        return (predictions > 0.5).astype(int).flatten().tolist()# Package API pour le système de détection d'intrusion
