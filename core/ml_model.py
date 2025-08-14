import os
import joblib
import pandas as pd

# -------------------
# Load LightGBM model (with preprocessing pipeline inside)
# -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "lightgbm.pkl")
model = joblib.load(MODEL_PATH)

# -------------------
# Prepare raw features for model
# -------------------
def prepare_features(txn):
    """
    Prepare features in the exact raw format as training data before preprocessing.
    The pipeline inside the model will handle encoding & scaling.
    """
    data = {
        'Transaction_Amount': [float(txn.amount)],
        'Account_Balance': [float(txn.user.account.account_balance)],
        'IP_Address_Flag': [txn.ip_flag],
        'Previous_Fraudulent_Activity': [txn.previous_fraudulent_activity],
        'Daily_Transaction_Count': [txn.daily_txn_count],
        'Avg_Transaction_Amount_7d': [txn.avg_txn_amount_7d],
        'Card_Age': [txn.card_age],
        'Transaction_Distance': [txn.txn_distance],
        'Risk_Score': [txn.risk_score],
        'Is_Weekend': [txn.is_weekend],
        'Transaction_Type': [txn.transaction_type],
        'Device_Type': [txn.device_type],
        'Location': [txn.location],
        'Merchant_Category': [txn.merchant_category],
        'Failed_Transaction_Count_7d': [txn.failed_txn_count_7d],
        'Card_Type': [txn.card_type],
        'Authentication_Method': [txn.auth_method],
        'Date': [txn.date.date()],   # Keep as datetime.date
        'Time': [txn.date.time()],    # Keep as datetime.time
        'Month': [txn.date.month],
        'Day': [txn.date.day],
        'Hour': [txn.date.hour]
    }
    return pd.DataFrame(data)

# -------------------
# Prediction function
# -------------------
def predict_anomaly(transaction):
    """
    Predict anomaly using LightGBM model with preprocessing pipeline.
    """
    features_df = prepare_features(transaction)
    pred = int(model.predict(features_df)[0])
    prob = float(model.predict_proba(features_df)[0][1])
    reason = "Unusual transaction pattern detected" if pred == 1 else None
    return bool(pred), prob, reason
