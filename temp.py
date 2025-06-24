from prophet_stock_predictor import simulate_stock_data, train_prophet_model, forecast_and_suggest_restock
from inventory_data import INVENTORY_DATA

def should_suggest_product(product_name, user_data):
    today = datetime.today()
    
    packet_size_liters = INVENTORY_DATA[product_name]["packet_size_liters"]
    daily_consumption_liters = user_data[f"{product_name}_consumption_ml"] / 1000.0

    df = simulate_stock_data(start_date=today - timedelta(days=30),
                             daily_consumption=daily_consumption_liters,
                             packet_size=packet_size_liters)

    model = train_prophet_model(df)
    forecast_df = forecast_and_suggest_restock(model, threshold=0.1)

    # Check if today's forecasted stock < threshold
    today_forecast = forecast_df[forecast_df["ds"] == pd.to_datetime(today.date())]
    if not today_forecast.empty and today_forecast.iloc[0]["yhat"] <= 0.1:
        return True
    return False
