from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
from firebase_admin import firestore

db = firestore.client()

def fetch_timeseries_from_firestore(user_id, product):
    doc_ref = db.collection("users").document(user_id).collection("consumption").document(product)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    
    raw = doc.to_dict()  # { "2024-06-17": 0.3, ... }
    data = pd.DataFrame([
        {"ds": datetime.strptime(k, "%Y-%m-%d"), "y": v}
        for k, v in raw.items()
    ])
    return data.sort_values("ds")

def run_prophet_prediction(user_id, product, forecast_days=7):
    ts_data = fetch_timeseries_from_firestore(user_id, product)
    
    if ts_data is None or len(ts_data) < 3:
        return None  # Not enough data

    model = Prophet(daily_seasonality=True)
    model.fit(ts_data)

    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)

    # Get today's prediction
    today_str = datetime.today().strftime("%Y-%m-%d")
    today_pred = forecast[forecast['ds'] == datetime.today().normalize()]
    
    if today_pred.empty:
        # fallback: take closest date
        today_pred = forecast.iloc[-forecast_days:]
    
    return today_pred[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(orient="records")



###
st.header("📈 Forecast Today's Need (Prophet)")

product = st.selectbox("Choose a product to forecast", ["milk", "rice", "oil", "eggs", "bread"])

if st.button("Forecast"):
    with st.spinner(f"Running Prophet forecast for {product}..."):
        forecast = run_prophet_prediction(st.session_state.username, product)

        if forecast:
            st.success("Today's Forecast:")
            st.write(forecast)
        else:
            st.warning("Not enough data to forecast. Try backfilling more days.")
###
