def show_onboarding_form():
    if 'form_page' not in st.session_state:
        st.session_state.form_page = 1

    def next_page():
        st.session_state.form_page += 1

    def prev_page():
        st.session_state.form_page -= 1

    def finish_form():
        # Collect data from current session state
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
        
        # Debug: Print the data to see what's being collected
        st.write("Debug - Collected data:", data)
        
        save_profile_to_firestore(username, data)
        summary = rag.build_profile_summary(data)
        rag.store_profile_embedding(username, summary)
        
        st.session_state.initial_data_filled = True
        st.rerun()

    st.title("Tell us about your grocery habits")

    if st.session_state.form_page == 1:
        st.subheader("1. Household Information")
        
        # Initialize session state values if they don't exist
        if "household_size" not in st.session_state:
            st.session_state.household_size = 1
        if "has_kids" not in st.session_state:
            st.session_state.has_kids = "No"
        if "has_elderly" not in st.session_state:
            st.session_state.has_elderly = "No"
        if "has_pets" not in st.session_state:
            st.session_state.has_pets = "No"
            
        st.number_input("How many people live in your household?", 
                       min_value=1, step=1, key="household_size")
        st.selectbox("Are there children or infants?", 
                    ["Yes", "No"], key="has_kids")
        st.selectbox("Are there elderly members?", 
                    ["Yes", "No"], key="has_elderly")
        st.selectbox("Do you have pets?", 
                    ["Yes", "No"], key="has_pets")

        st.button("Next", on_click=next_page, key="form1_next")

    elif st.session_state.form_page == 2:
        st.subheader("2. Dietary Habits")
        
        # Initialize session state values if they don't exist
        if "milk_freq" not in st.session_state:
            st.session_state.milk_freq = "Never"
        if "milk_qty" not in st.session_state:
            st.session_state.milk_qty = 0.0
        if "rice_qty" not in st.session_state:
            st.session_state.rice_qty = 0.0
        if "oil_qty" not in st.session_state:
            st.session_state.oil_qty = 0.0
        if "eggs_per_week" not in st.session_state:
            st.session_state.eggs_per_week = 0
        if "bread_freq" not in st.session_state:
            st.session_state.bread_freq = "Never"
            
        st.selectbox("How often do you drink milk?", 
                    ["Daily", "Few times a week", "Rarely", "Never"], key="milk_freq")
        st.number_input("How much milk do you consume per day? (in liters)", 
                       min_value=0.0, step=0.1, key="milk_qty")
        st.number_input("How much rice do you consume per day? (in kg)", 
                       min_value=0.0, step=0.1, key="rice_qty")
        st.number_input("How much cooking oil per month? (in liters)", 
                       min_value=0.0, step=0.1, key="oil_qty")
        st.number_input("How many eggs per week?", 
                       min_value=0, step=1, key="eggs_per_week")
        st.selectbox("How often do you eat bread?", 
                    ["Daily", "Weekly", "Occasionally", "Never"], key="bread_freq")

        col1, col2 = st.columns(2)
        with col1:
            st.button("Previous", on_click=prev_page, key="form2_prev")
        with col2:
            st.button("Next", on_click=next_page, key="form2_next")

    elif st.session_state.form_page == 3:
        st.subheader("3. Shopping Behavior")
        
        # Initialize session state values if they don't exist
        if "shopping_freq" not in st.session_state:
            st.session_state.shopping_freq = "Monthly"
        if "shopping_day" not in st.session_state:
            st.session_state.shopping_day = "Monday"
        if "shopping_mode" not in st.session_state:
            st.session_state.shopping_mode = "In-store"
        if "delivery_pref" not in st.session_state:
            st.session_state.delivery_pref = "Scheduled"
            
        st.selectbox("How often do you go shopping?", 
                    ["Daily", "Weekly", "Bi-weekly", "Monthly"], key="shopping_freq")
        st.selectbox("What day of the week do you usually shop?", 
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 
                    key="shopping_day")
        st.selectbox("Preferred mode of shopping", 
                    ["Online", "In-store"], key="shopping_mode")
        st.selectbox("Delivery preference", 
                    ["Scheduled", "Instant"], key="delivery_pref")

        col1, col2 = st.columns(2)
        with col1:
            st.button("Previous", on_click=prev_page, key="form3_prev")
        with col2:
            st.button("Finish", on_click=finish_form, key="form3_finish")