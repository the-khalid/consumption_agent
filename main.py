import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import rag

# def get_ollama_embedding(text):
#     url = "http://localhost:11434/api/embeddings"
#     payload = {
#         "model": "mxbai-embed-large",
#         "prompt": text
#     }

#     response = requests.post(url, json=payload)
#     response.raise_for_status()
#     return response.json()["embedding"]

# Initialize Firebase
if 'firebase_initialized' not in st.session_state:
    cred = credentials.Certificate("consumption-agent-firebase-adminsdk-fbsvc-10a26adf1a.json")
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

if 'firebase_db' not in st.session_state:
    st.session_state.firebase_db = firestore.client()

db = firestore.client()

from datetime import datetime, timedelta

def save_profile_to_firebase(uid, data):
    # Save profile data
    db.collection("users").document(uid).collection("profile").document("main").set(data)

    # Optionally initialize consumption history with current day (if new user)
    today = datetime.today()
    default_consumption = {
        "milk": data.get("milk_qty", 0.0),
        "rice": data.get("rice_qty", 0.0) / 30,  # assuming monthly amount spread over days
        "oil": data.get("oil_qty", 0.0) / 30,
        "eggs": data.get("eggs_per_week", 0) / 7,
        "bread": 2 if data.get("bread_freq") != "Never" else 0
    }

    for product, qty in default_consumption.items():
        db.collection("users").document(uid).collection("consumption").document(product).set({
            today.strftime("%Y-%m-%d"): qty
        }, merge=True)


from datetime import datetime
def generate_daily_suggestion():
    today = datetime.today().strftime("%A, %B %d")
    prompt = f"""
    You are a smart grocery ordering Agentic AI system which prompts the user with your suggestions on buying groceries so that his kitchen is just stocked up enough.
    Today is {today}. Based on the user's grocery preferences, household size, and habits, suggest exactly ONE product to buy today.
    Be specific and concise. Do not list more than one product. Just give the product name and its suggested quantity.
    """
    rag_chain = rag.set_rag_chain()
    result = rag_chain.run(prompt)
    return result
# def signup(email, password):
#     try:
#         user = auth.create_user(email=email, password=password)
#         st.success("User created successfully!")
#         return user
#     except Exception as e:
#         st.error(f"Error: {e}")

# def signin(email, password):
#     # mock for now
#     st.session_state.logged_in = True
#     st.session_state.user_email = email
#     st.rerun()

# def show_login():
#     st.title("Login / Signup")

#     # choice = st.radio("Choose action", ["Login", "Sign up"], key="auth_action_choice")

#     email = st.text_input("Email", key="login_email_input")
#     password = st.text_input("Password", type="password", key="login_password_input")

#     if choice == "Sign up":
#         if st.button("Sign up", key="signup_button"):
#             signup(email, password)

#     if choice == "Login":
#         if st.button("Login", key="login_button"):
#             signin(email, password)

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
        st.subheader("1. Household Information")
        st.number_input("How many people live in your household?", min_value=1, step=1, key="household_size")
        st.selectbox("Are there children or infants?", ["Yes", "No"], key="has_kids")
        st.selectbox("Are there elderly members?", ["Yes", "No"], key="has_elderly")
        st.selectbox("Do you have pets?", ["Yes", "No"], key="has_pets")

        st.button("Next", on_click=next_page, key="form1_next")

    elif st.session_state.form_page == 2:
        st.subheader("2. Dietary Habits")
        st.selectbox("How often do you drink milk?", ["Daily", "Few times a week", "Rarely", "Never"], key="milk_freq")
        st.number_input("How much milk do you consume per day? (in liters)", min_value=0.0, step=0.1, key="milk_qty")
        st.number_input("How much rice do you consume per day? (in kg)", min_value=0.0, step=0.1, key="rice_qty")
        st.number_input("How much cooking oil per month? (in liters)", min_value=0.0, step=0.1, key="oil_qty")
        st.number_input("How many eggs per week?", min_value=0, step=1, key="eggs_per_week")
        st.selectbox("How often do you eat bread?", ["Daily", "Weekly", "Occasionally", "Never"], key="bread_freq")

        col1, col2 = st.columns(2)
        with col1:
            st.button("Previous", on_click=prev_page, key="form2_prev")
        with col2:
            st.button("Next", on_click=next_page, key="form2_next")

    elif st.session_state.form_page == 3:
        st.subheader("3. Shopping Behavior")
        st.selectbox("How often do you go shopping?", ["Daily", "Weekly", "Bi-weekly", "Monthly"], key="shopping_freq")
        st.selectbox("What day of the week do you usually shop?", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="shopping_day")
        st.selectbox("Preferred mode of shopping", ["Online", "In-store"], key="shopping_mode")
        st.selectbox("Delivery preference", ["Scheduled", "Instant"], key="delivery_pref")

        col1, col2 = st.columns(2)
        with col1:
            st.button("Previous", on_click=prev_page, key="form3_prev")
        with col2:
            if st.button("Finish", key="form3_finish"):
                username = st.session_state.username
                data = {
                    "household_size": st.session_state.get("household_size", 0),
                    "has_kids": st.session_state.get("has_kids", "No"),
                    "has_elderly": st.session_state.get("has_elderly", "No"),
                    "has_pets": st.session_state.get("has_pets", "No"),

                    "milk_freq": st.session_state.get("milk_freq", "Never"),
                    "milk_qty": st.session_state.get("milk_qty", 0.0),
                    "rice_qty": st.session_state.get("rice_qty", 0.0),
                    "oil_qty": st.session_state.get("oil_qty", 0.0),
                    "eggs_per_week": st.session_state.get("eggs_per_week", 0),
                    "bread_freq": st.session_state.get("bread_freq", "Never"),

                    "shopping_freq": st.session_state.get("shopping_freq", "Monthly"),
                    "shopping_day": st.session_state.get("shopping_day", "Monday"),
                    "shopping_mode": st.session_state.get("shopping_mode", "In-store"),
                    "delivery_pref": st.session_state.get("delivery_pref", "Scheduled"),
                }

                save_profile_to_firestore(st.session_state.username , data)

                summary = rag.build_profile_summary(data)
                rag.store_profile_embedding(st.session_state.username, summary)

                st.session_state.initial_data_filled = True
                st.rerun()


def show_landing():
    st.title("Welcome to Smart Grocery Agent!")
    st.write(f"Logged in as: {st.session_state.username}")
    suggestion = generate_daily_suggestion()
    st.markdown(f"### 📅 {datetime.today().strftime('%A, %d %B %Y')}")
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


# Session default values
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'initial_data_filled' not in st.session_state:
    st.session_state.initial_data_filled = False

# App flow control
if st.session_state.logged_in:
    if not st.session_state.initial_data_filled:
        show_onboarding_form()
    else:
        show_landing()
else:
    simple_login()

