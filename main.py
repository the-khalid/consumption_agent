import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import rag
from datetime import datetime, timedelta

# Initialize Firebase
if 'firebase_initialized' not in st.session_state:
    cred = credentials.Certificate("consumption-agent-firebase-adminsdk-fbsvc-58b80d61e2.json")
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

if 'firebase_db' not in st.session_state:
    st.session_state.firebase_db = firestore.client()

db = firestore.client()

def save_profile_to_firestore(uid, data):
    db.collection("users").document(uid).collection("profile").document("main").set(data)

    today = datetime.today()
    default_consumption = {
        "milk": data.get("milk_qty", 0.0),
        "rice": data.get("rice_qty", 0.0) / 30,
        "oil": data.get("oil_qty", 0.0) / 30,
        "eggs": data.get("eggs_per_week", 0) / 7,
        "bread": 2 if data.get("bread_freq") != "Never" else 0
    }

    for product, qty in default_consumption.items():
        db.collection("users").document(uid).collection("consumption").document(product).set({
            today.strftime("%Y-%m-%d"): qty
        }, merge=True)

def generate_daily_suggestion(start_date, current_date):
    prompt = f"""
    You are a smart grocery ordering Agentic AI system which prompts the user with your suggestions on buying groceries/milk/bread or any such food items so that his kitchen is just stocked up enough.
    Today is {current_date.strftime("%A, %B %d")}, and consider his kitchen has no current stock as of {start_date}. Based on the user's grocery preferences and habits, suggest exactly all the products to buy today so as to stock up his kitchen.
    Be specific, concise and intellegent. Don't give suggestions with arbitary quantities, give in discrete quantity as available in the market, for example, if he consumes 600ml of milk daily, don't suggest 500ml on a daily basis but suggest 1L twice a day keeping general shelf life of that food item and expiry date.
    Just give the product and its suggested quantity. You can order excess quantity if you think its a good idea to stick up the kitchen, only if his financial condition is So Good, and suggest only absolutely essential things when financial condition is not so good.
    """
    rag_chain = rag.set_rag_chain()
    result = rag_chain.run(prompt)
    return result

def simple_login():
    st.title("Enter Your Username to Continue")
    username = st.text_input("Username")

    if st.button("Continue") and username:
        st.session_state.logged_in = True
        st.session_state.username = username
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
            milk_options = ["Daily", "Few times a week", "Rarely", "Never"]
            current_milk = st.session_state.get("milk_freq", "Daily")
            milk_freq = st.selectbox("How often do you drink milk?", 
                                   milk_options,
                                   index=milk_options.index(current_milk) if current_milk in milk_options else 3)
            
            milk_qty = st.number_input("How much milk do you consume per day? (in liters)", 
                                     min_value=0.0, step=0.1, 
                                     value=st.session_state.get("milk_qty", 0.0))
            rice_qty = st.number_input("How much rice do you consume per day? (in kg)", 
                                     min_value=0.0, step=0.1,
                                     value=st.session_state.get("rice_qty", 0.0))
            oil_qty = st.number_input("How much cooking oil per month? (in liters)", 
                                    min_value=0.0, step=0.1,
                                    value=st.session_state.get("oil_qty", 0.0))
            eggs_per_week = st.number_input("How many eggs per week?", 
                                          min_value=0, step=1,
                                          value=st.session_state.get("eggs_per_week", 0))
            
            bread_options = ["Daily", "Weekly", "Occasionally", "Never"]
            current_bread = st.session_state.get("bread_freq", "Never")
            bread_freq = st.selectbox("How often do you eat bread?", 
                                    bread_options,
                                    index=bread_options.index(current_bread) if current_bread in bread_options else 3)

            col1, col2 = st.columns(2)
            with col1:
                prev_clicked = st.form_submit_button("Previous")
            with col2:
                finish_clicked = st.form_submit_button("Finish")
            
            if prev_clicked:
                prev_page()
                st.rerun()
            elif finish_clicked:
                st.session_state.milk_freq = milk_freq
                st.session_state.milk_qty = milk_qty
                st.session_state.rice_qty = rice_qty
                st.session_state.oil_qty = oil_qty
                st.session_state.eggs_per_week = eggs_per_week
                st.session_state.bread_freq = bread_freq
                
                username = st.session_state.username
                data = {    
                    "age": st.session_state.get("age", 22),
                    "weight": st.session_state.get("weight", 55.0),
                    "gender": st.session_state.get("gender", "Male"),
                    "diet_type": st.session_state.get("diet_type", "High-protein"),
                    "allergies": st.session_state.get("allergies", "None"),
                    "has_pets": st.session_state.get("has_pets", "No"),
                    "fc": st.session_state.get("fc", "Normal"),

                    "milk_freq": st.session_state.get("milk_freq", "Never"),
                    "milk_qty": st.session_state.get("milk_qty", 0.0),
                    "rice_qty": st.session_state.get("rice_qty", 0.0),
                    "oil_qty": st.session_state.get("oil_qty", 0.0),
                    "eggs_per_week": st.session_state.get("eggs_per_week", 0),
                    "bread_freq": st.session_state.get("bread_freq", "Never"),
                }
                
                # Debug output
                st.write("Debug - Final collected data:", data)
                
                save_profile_to_firestore(username, data)
                summary = rag.build_profile_summary(data)
                rag.store_profile_embedding(username, summary)
                
                st.session_state.initial_data_filled = True
                st.rerun()

if 'start_day' not in st.session_state:
    st.session_state.start_day = datetime.today()

def show_landing():
    st.title("Welcome to Smart Grocery Agent!")
    st.write(f"Logged in as: {st.session_state.username}")

    if 'current_day' not in st.session_state:
        st.session_state.current_day = datetime.today()

    st.markdown(f"### 📅 {st.session_state.current_day.strftime('%A, %d %B %Y')}")

    suggestion = generate_daily_suggestion(st.session_state.start_day, st.session_state.current_day)
    st.markdown(f"🛒 **Today's Suggestion:** {suggestion}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ordered"):
            st.success("Thanks! We'll learn from this feedback.")
            # TODO: Store feedback

    with col2:
        if st.button("Discard"):
            st.info("Okay, we’ll skip that one next time.")
            # TODO: Store feedback

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'initial_data_filled' not in st.session_state:
    st.session_state.initial_data_filled = False

if st.session_state.logged_in:
    if not st.session_state.initial_data_filled:
        show_onboarding_form()
    else:
        show_landing()
else:
    simple_login()

