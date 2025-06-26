
import json
from datetime import datetime, timedelta
from typing import Dict

# --- STEP 1: LLM Prompt to Extract Structured Data from Habit Text ---
def extract_consumption_from_habit_text(llm_chain, user_text: str) -> Dict:
    prompt = f"""
    Extract structured grocery consumption data from the following text. 
    Return a JSON with amount and unit (per day/week/month) for each item.

    Input:
    {user_text}

    Output format:
    {{
        "milk": {{ "amount": 0.2, "unit": "liters/day" }},
        "rice": {{ "amount": 0.3, "unit": "kg/day" }},
        "oil": {{ "amount": 1, "unit": "liters/month" }}
    }}
    """
    
    response = llm_chain.run(prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {}

# --- STEP 2: Generate Time Series for Prophet ---
def generate_timeseries(product_info: Dict, start_date: datetime, days: int = 60):
    data = {}
    amount = product_info["amount"]
    unit = product_info["unit"].lower()

    for i in range(days):
        date = (start_date - timedelta(days=i)).strftime("%Y-%m-%d")
        if "day" in unit:
            data[date] = amount
        elif "week" in unit and i % 7 == 0:
            data[date] = amount
        elif "month" in unit and i % 30 == 0:
            data[date] = amount
    return data

# --- STEP 3: Batch Backfill and Store to Firestore ---
def backfill_firestore_from_habit(habit_json: Dict, db, uid: str):
    start_date = datetime.today()
    for product, info in habit_json.items():
        time_series = generate_timeseries(info, start_date)
        doc_ref = db.collection("users").document(uid).collection("consumption").document(product)
        doc_ref.set(time_series, merge=True)

# --- Main Wrapper ---
def parse_habits_and_generate_backfill(user_text: str, rag_chain, db, uid: str):
    habit_json = extract_consumption_from_habit_text(rag_chain, user_text)
    if not habit_json:
        return "⚠️ Could not parse habits. Please rephrase."
    backfill_firestore_from_habit(habit_json, db, uid)
    return f"✅ Consumption data generated for {', '.join(habit_json.keys())} and saved."

# --- Optional Example ---
if __name__ == "__main__":
    from rag import set_rag_chain
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Firebase setup
    cred = credentials.Certificate("consumption-agent-firebase-adminsdk-fbsvc-58b80d61e2.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Sample run
    llm_chain = set_rag_chain()
    text = "I drink 200ml of milk daily and eat 300 grams of rice daily. We use 1L oil per month."
    print(parse_habits_and_generate_backfill(text, llm_chain, db, uid="test_user"))
