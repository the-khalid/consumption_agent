# main.py (updated with Prophet-based prediction and batch runner)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
import rag

# ------------------- Initialize Firebase -------------------
if 'firebase_initialized' not in st.session_state:
    cred = credentials.Certificate("consumption-agent-firebase-adminsdk-fbsvc-58b80d61e2.json")
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()

# ------------------- Inventory & Prophet Logic -------------------
inventory_units = {
    "milk": 1.0,    # 1 L packets
    "rice": 5.0,    # 5 kg bags
    "oil": 1.0,     # 1 L bottles
    "eggs": 12,     # 1 dozen
    "bread": 1      # 1 loaf
}

def run_prophet_prediction(uid, product, inventory_dict):
    doc = db.collection("users").document(uid).collection("consumption").document(product).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    if len(data) < 2:
        return None

    df = pd.DataFrame({
        "ds": pd.to_datetime(list(data.keys())),
        "y": list(data.values())
    }).sort_values("ds")

    model = Prophet(daily_seasonality=True)
    model.fit(df)

    daily_rate = df["y"].mean()
    packet_size = inventory_dict.get(product, 1.0)
    days_to_depletion = int(packet_size / daily_rate)

    predicted_runout = df["ds"].max() + timedelta(days=days_to_depletion)
    return {
        "product": product,
        "reorder_date": (predicted_runout - timedelta(days=1)).date(),
        "daily_rate": round(daily_rate, 2)
    }

def predict_all_products(uid):
    return {
        p: pred for p in inventory_units
        if (pred := run_prophet_prediction(uid, p, inventory_units))
    }

# ------------------- Profile Save -------------------
def save_profile_to_firestore(uid, data):
    db.collection("users").document(uid).collection("profile").document("main").set(data)
    today = datetime.today()
    daily_defaults = {
        "milk": data.get("milk_qty", 0.0),
        "rice": data.get("rice_qty", 0.0) / 30,
        "oil": data.get("oil_qty", 0.0) / 30,
        "eggs": data.get("eggs_per_week", 0) / 7,
        "bread": 1 if data.get("bread_freq") != "Never" else 0
    }
    for prod, qty in daily_defaults.items():
        db.collection("users").document(uid).collection("consumption").document(prod).set({
            today.strftime("%Y-%m-%d"): qty
        }, merge=True)

# ------------------- Generate Suggestion -------------------
def generate_daily_suggestion(start_date, current_date):
    prompt = f"""
    You are a smart grocery ordering Agentic AI system ...
    """
    rag_chain = rag.set_rag_chain()
    return rag_chain.run(prompt)

# ------------------- Login & Onboarding -------------------
def simple_login():
    st.title("Enter Your Username")
    u = st.text_input("Username")
    if st.button("Continue") and u:
        st.session_state.logged_in = True
        st.session_state.username = u
        st.rerun()

def show_onboarding_form():
    # … (same as your existing form code)
    pass

# ------------------- Dashboard -------------------
def show_landing():
    st.title("Smart Grocery Agent")
    st.write(f"User: {st.session_state.username}")
    st.markdown(f"### 📅 {st.session_state.current_day.strftime('%A, %d %B %Y')}")

    preds = predict_all_products(st.session_state.username)
    st.subheader("🔁 Reorder Predictions")
    if preds:
        for prod, d in preds.items():
            st.markdown(f"**{prod.title()}**: order on `{d['reorder_date']}` (daily avg: {d['daily_rate']})")
    else:
        st.info("Not enough data to predict consumption yet.")

    suggestion = generate_daily_suggestion(st.session_state.start_day, st.session_state.current_day)
    st.markdown(f"🛒 **Today's Suggestion:** {suggestion}")

    col1, col2 = st.columns(2)
    if col1.button("Ordered"):
        st.success("Thanks! We'll use this feedback.")
    if col2.button("Discard"):
        st.info("Got it — skipping next time.")

# ------------------- App Entry -------------------
if 'start_day' not in st.session_state:
    st.session_state.start_day = datetime.today()
if 'current_day' not in st.session_state:
    st.session_state.current_day = datetime.today()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'initial_data_filled' not in st.session_state:
    st.session_state.initial_data_filled = False

if st.session_state.logged_in:
    if not st.session_state.initial_data_filled:
        show_onboarding_form()
    else:
        show_landing()
else:
    simple_login()
