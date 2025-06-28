import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
# import rag
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_core.messages.human import HumanMessage

# ------------------- Initialize Firebase -------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("consumption-agent-firebase-adminsdk-fbsvc-a17c98de69.json")
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

# def run_prophet_prediction(uid, product, inventory_units):
#     doc = db.collection("users").document(uid).collection("consumption").document(product).get()
#     if not doc.exists:
#         return None
#     data = doc.to_dict()
#     if len(data) < 2:
#         return None

#     df = pd.DataFrame({
#         "ds": pd.to_datetime(list(data.keys())),
#         "y": list(data.values())
#     }).sort_values("ds")

#     model = Prophet(daily_seasonality=True)
#     model.fit(df)

#     daily_rate = df["y"].mean()
#     packet_size = inventory_units.get(product, 1.0)
#     days_to_depletion = int(packet_size / daily_rate)

#     predicted_runout = df["ds"].max() + timedelta(days=days_to_depletion)
#     return {
#         "product": product,
#         "reorder_date": (predicted_runout - timedelta(days=1)).date(),
#         "daily_rate": round(daily_rate, 2)
#     }

# def predict_all_products(uid):
#     return {
#         p: pred for p in inventory_units
#         if (pred := run_prophet_prediction(uid, p, inventory_units))
#     }

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
# def generate_daily_suggestion(start_date, current_date):
#     prompt = f"""
#     You are a smart grocery ordering Agentic AI system ...
#     """
#     rag_chain = rag.set_rag_chain()
#     return rag_chain.run(prompt)

import json
def parseInput(input_text):
    """
    Parse input text in format 'product/units/weekly_usage' into list of JSON objects
    
    Args:
        input_text (str): Multi-line string with format:
                         product/units/weekly_usage
                         Example: "milk/litres/7\nrice/gms/2100"
    
    Returns:
        list: List of dictionaries with keys: name, unit, weekly_usage
              Example: [{"name": "milk", "unit": "litres", "weekly_usage": "7"}]
    """
    json_objects = []
    lines = input_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line:
            parts = line.split('/')
            if len(parts) == 3:
                product, units, weekly_usage = parts
                json_obj = {
                    "name": product.strip(),
                    "unit": units.strip(),
                    "weekly_usage": weekly_usage.strip()
                }
                json_objects.append(json_obj)
    
    return json_objects

# def parseInput(data):
#     prompt = f"""
#     You are an Intelligent Data Conversion ASsistant. Convert the following data into valid JSON format.
#     Each input line is corresponds to a product and it will be following this syntax:
#     milk/litres/7
#     which means the product is "milk" and it's weekly usage is '7' and the units of consumption is "litres".
#     For each product entry, create a JSON object with exactly these fields:
#     - "name": the product name
#     - "unit": the unit measurement
#     - "weekly_usage": the weekly usage amount

#     Input data:
#     {data}

#     Output format:
#     {{
#         "milk": {{ "amount": 0.2, "unit": "liters/day" }},
#         "rice": {{ "amount": 0.3, "unit": "kg/day" }},
#         "oil": {{ "amount": 1, "unit": "liters/month" }}
#     }}
#     Give only the JSON file, nothing else.
#     """
    
#     chat = ChatOllama(model='gemma:2b')
#     response = chat.invoke([HumanMessage(content=prompt)])
#     print(f'response: {response}')
#     parsed_json = json.loads(response.content)
#     print(parsed_json)
#     return parsed_json

from langchain.schema import Document
from langchain_community.embeddings import OllamaEmbeddings
import os
from langchain.vectorstores import FAISS
def store_profile_embedding(user_id: str, profile_data: str):
    """
    Stores or updates a user's profile summary in a LangChain FAISS index.
    - user_id: unique identifier
    - summary_text: full profile summary text
    """
    summary_text = f"""
    User is a {profile_data['age']} years old {profile_data['gender']}, weighs {profile_data['weight']}, follows {profile_data['diet_type']} specific diet, and is allergic to {profile_data['allergies']}.
    User's financial consition is {profile_data['fc']}.
    """

    doc = Document(page_content=summary_text, metadata={"user_id": user_id})

    embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
    index_dir = "faiss_index"
    if os.path.isdir(index_dir) and os.path.exists(os.path.join(index_dir, "index.faiss")):
        faiss_index = FAISS.load_local(index_dir, embedding_model, allow_dangerous_deserialization=True)
        faiss_index.add_documents([doc])
    else:
        faiss_index = FAISS.from_documents([doc], embedding_model)

    faiss_index.save_local(index_dir)

# ------------------- Login & Onboarding -------------------
def simple_login():
    st.title("Enter Your Username")
    u = st.text_input("Username")
    if st.button("Continue") and u:
        st.session_state.logged_in = True
        st.session_state.username = u
        st.rerun()

def show_onboarding_form():
    if 'form_page' not in st.session_state:
        st.session_state.form_page = 1

    def next_page():
        st.session_state.form_page += 1

    def prev_page():
        st.session_state.form_page -= 1

    st.title("Tell us about your grocery habits")

    if st.session_state.form_page == 1:
        st.subheader("1. Personal & Household Information")
        
        with st.form("household_form"):
            # Personal Information
            age = st.number_input("What is your age?", 
                                min_value=1, max_value=120, step=1, 
                                value=st.session_state.get("age", 22))
            
            gender_options = ["Male", "Female"]
            current_gender = st.session_state.get("gender", "Male")
            gender = st.selectbox("Gender?", 
                                  gender_options,
                                  index=gender_options.index(current_gender) if current_gender in gender_options else 0)
            
            weight = st.number_input("What is your weight? (in kg)", 
                                   min_value=1.0, max_value=300.0, step=0.5, 
                                   value=st.session_state.get("weight", 55.0))
            
            diet_options = ["High-protein", "Keto", "No", "Vegan"]
            current_diet = st.session_state.get("diet_type", "High-protein")
            diet_type = st.selectbox("Do you follow any diet?", 
                                   diet_options,
                                   index=diet_options.index(current_diet) if current_diet in diet_options else 0)
            
            allergy_options = ["None", "Lactose", "Seafood", "Soy"]
            current_allergy = st.session_state.get("allergies", "None")
            allergies = st.selectbox("Do you have any allergies?", 
                                   allergy_options,
                                   index=allergy_options.index(current_allergy) if current_allergy in allergy_options else 0)

            pet_options = ["No", "Cat", "Dog"]
            current_pets = st.session_state.get("has_pets", "No")
            has_pets = st.selectbox("Do you have any pets?", 
                                  pet_options,
                                  index=pet_options.index(current_pets) if current_pets in pet_options else 0)
            
            fc_options = ["Normal", "So Good", "Not so Good"]
            current_fc = st.session_state.get("fc", "Normal")
            fc = st.selectbox("How's your financial condition?", 
                                  fc_options,
                                  index=fc_options.index(current_fc) if current_fc in fc_options else 0)
            

            submitted = st.form_submit_button("Next")
            if submitted:
                st.session_state.age = age
                st.session_state.gender = gender
                st.session_state.weight = weight
                st.session_state.diet_type = diet_type
                st.session_state.allergies = allergies
                st.session_state.has_pets = has_pets
                st.session_state.fc = fc
                next_page()
                st.rerun()

    elif st.session_state.form_page == 2:
        st.subheader("2. Food Habits")
        # Food Habits
        with st.form("dietary_form"):
            habit_text = st.text_area("Enter your food habits (e.g., 'I drink 200ml milk and eat 300g rice daily')")
            col1, col2 = st.columns(2)
            with col1:
                prev_clicked = st.form_submit_button("Previous")
            with col2:
                finish_clicked = st.form_submit_button("Finish")
            
            if prev_clicked:
                prev_page()
                st.rerun()
            elif finish_clicked:
                username = st.session_state.username
                if not habit_text.strip():
                    st.warning("Please enter your food habits first")
                else:
                    with st.spinner("Taking in the data.."):
                        items_list = parseInput(habit_text)
                        jsonfile = {
                            "user_id": st.session_state.username,
                            "store": "Walmart",
                            "last_updated": st.session_state.current_day.strftime('%A, %d %B %Y'),
                            "items": items_list
                        }
                        with open("products.json", "w") as file:
                            json.dump(jsonfile, file)

                data = {    
                    "age": st.session_state.get("age", 22),
                    "weight": st.session_state.get("weight", 55.0),
                    "gender": st.session_state.get("gender", "Male"),
                    "diet_type": st.session_state.get("diet_type", "High-protein"),
                    "allergies": st.session_state.get("allergies", "None"),
                    "has_pets": st.session_state.get("has_pets", "No"),
                    "fc": st.session_state.get("fc", "Normal"),
                }
                
                # Debug output
                st.write("Debug - Final collected data:", data)
                
                save_profile_to_firestore(username, data)
                # summary = rag.build_profile_summary(data)
                store_profile_embedding(username, data)
                
                st.session_state.initial_data_filled = True
                st.rerun()

# ------------------- Dashboard -------------------
def show_landing():
    st.title("Smart Grocery Agent")
    st.write(f"User: {st.session_state.username}")
    st.markdown(f"### 📅 {st.session_state.current_day.strftime('%A, %d %B %Y')}")

    

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
