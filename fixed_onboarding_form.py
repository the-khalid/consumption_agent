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
            
            weight = st.number_input("What is your weight? (in kg)", 
                                   min_value=1.0, max_value=300.0, step=0.5, 
                                   value=st.session_state.get("weight", 55.0))
            
            diet_options = ["High-protein", "Keto", "No", "Vegan"]
            current_diet = st.session_state.get("diet_type", "High-protein")
            diet_type = st.selectbox("Do you follow any diet?", 
                                   diet_options,
                                   index=diet_options.index(current_diet) if current_diet in diet_options else 0)
            
            allergy_options = ["No", "Lactose", "Seafood", "Soy"]
            current_allergy = st.session_state.get("allergies", "No")
            allergies = st.selectbox("Do you have any allergies?", 
                                   allergy_options,
                                   index=allergy_options.index(current_allergy) if current_allergy in allergy_options else 0)
            
            # Household Information
            household_size = st.number_input("How many people live in your household?", 
                                           min_value=1, step=1, 
                                           value=st.session_state.get("household_size", 1))
            has_kids = st.selectbox("Are there children or infants?", 
                                  ["Yes", "No"], 
                                  index=0 if st.session_state.get("has_kids", "No") == "Yes" else 1)
            has_elderly = st.selectbox("Are there elderly members?", 
                                     ["Yes", "No"],
                                     index=0 if st.session_state.get("has_elderly", "No") == "Yes" else 1)
            
            pet_options = ["No", "Cat", "Dog"]
            current_pets = st.session_state.get("has_pets", "No")
            has_pets = st.selectbox("Do you have any pets?", 
                                  pet_options,
                                  index=pet_options.index(current_pets) if current_pets in pet_options else 0)

            submitted = st.form_submit_button("Next")
            if submitted:
                st.session_state.age = age
                st.session_state.weight = weight
                st.session_state.diet_type = diet_type
                st.session_state.allergies = allergies
                st.session_state.household_size = household_size
                st.session_state.has_kids = has_kids
                st.session_state.has_elderly = has_elderly
                st.session_state.has_pets = has_pets
                next_page()
                st.rerun()

    elif st.session_state.form_page == 2:
        st.subheader("2. Dietary Habits")
        
        with st.form("dietary_form"):
            milk_options = ["Daily", "Few times a week", "Rarely", "Never"]
            current_milk = st.session_state.get("milk_freq", "Never")
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
                
                # Collect all data
                username = st.session_state.username
                data = {
                    # Personal Information
                    "age": st.session_state.get("age", 22),
                    "weight": st.session_state.get("weight", 55.0),
                    "diet_type": st.session_state.get("diet_type", "High-protein"),
                    "allergies": st.session_state.get("allergies", "No"),
                    
                    # Household Information
                    "household_size": st.session_state.get("household_size", 1),
                    "has_kids": st.session_state.get("has_kids", "No"),
                    "has_elderly": st.session_state.get("has_elderly", "No"),
                    "has_pets": st.session_state.get("has_pets", "No"),

                    # Dietary Habits
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
