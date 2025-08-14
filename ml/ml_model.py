import os
import joblib
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, "ml", "fraud_detector_xgb.pkl")  # adjust path

model = joblib.load(MODEL_PATH)

def predict_anomaly(transaction_data):
    """
    transaction_data: list or array of features [amount, hour, location, ...]
    Returns: (is_anomalous: bool, score: float, reason: str)
    """
    score = model.decision_function([transaction_data])[0]
    pred = model.predict([transaction_data])[0]  # 1 = anomaly, 0 = normal
    reason = None

    if pred == 1:
        if transaction_data[0] > 5000:  # Example rule
            reason = "High amount outside user range"
        # You can add more reason logic here

    return bool(pred), float(score), reason
