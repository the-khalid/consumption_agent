# prophet_stock_predictor.py

from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta

def generate_consumption_df(start_date: str, days: int, daily_consumption: float, packet_size: float):
    """
    Create a dataframe showing cumulative stock depletion over time.
    Each entry represents 1 day and the number of packets consumed.
    """
    date_list = [datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i) for i in range(days)]
    daily_packet_consumption = daily_consumption / packet_size

    df = pd.DataFrame({
        "ds": date_list,
        "y": [-daily_packet_consumption for _ in date_list]  # Prophet models cumulative sum, so we use negative
    })
    return df

def train_prophet_model(df: pd.DataFrame):
    """
    Train a Prophet model using the cumulative consumption data.
    """
    df_cumulative = df.copy()
    df_cumulative['y'] = df_cumulative['y'].cumsum()

    model = Prophet()
    model.fit(df_cumulative)
    return model

def predict_depletion(model, periods: int):
    """
    Forecast future stock depletion for the next `periods` days.
    """
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def suggest_restock_dates(forecast_df: pd.DataFrame, threshold: float = -0.1):
    """
    Identify dates when stock is expected to fall below a critical threshold.
    """
    depletion_dates = forecast_df[forecast_df['yhat'] <= threshold]['ds']
    return depletion_dates.tolist()

# Example usage (to test independently)
if __name__ == "__main__":
    df = generate_consumption_df(start_date="2025-06-01", days=10, daily_consumption=500, packet_size=1000)
    model = train_prophet_model(df)
    forecast = predict_depletion(model, periods=7)
    print(suggest_restock_dates(forecast))
