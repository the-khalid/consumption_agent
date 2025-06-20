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
        
        with st.form("household_form"):
            household_size = st.number_input("How many people live in your household?", 
                                           min_value=1, step=1, 
                                           value=st.session_state.get("household_size", 1))
            has_kids = st.selectbox("Are there children or infants?", 
                                  ["Yes", "No"], 
                                  index=0 if st.session_state.get("has_kids", "No") == "Yes" else 1)
            has_elderly = st.selectbox("Are there elderly members?", 
                                     ["Yes", "No"],
                                     index=0 if st.session_state.get("has_elderly", "No") == "Yes" else 1)
            has_pets = st.selectbox("Do you have pets?", 
                                  ["Yes", "No"],
                                  index=0 if st.session_state.get("has_pets", "No") == "Yes" else 1)

            submitted = st.form_submit_button("Next")
            if submitted:
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
                next_clicked = st.form_submit_button("Next")
            
            if prev_clicked:
                prev_page()
                st.rerun()
            elif next_clicked:
                st.session_state.milk_freq = milk_freq
                st.session_state.milk_qty = milk_qty
                st.session_state.rice_qty = rice_qty
                st.session_state.oil_qty = oil_qty
                st.session_state.eggs_per_week = eggs_per_week
                st.session_state.bread_freq = bread_freq
                next_page()
                st.rerun()

    elif st.session_state.form_page == 3:
        st.subheader("3. Shopping Behavior")
        
        with st.form("shopping_form"):
            shopping_freq_options = ["Daily", "Weekly", "Bi-weekly", "Monthly"]
            current_shopping_freq = st.session_state.get("shopping_freq", "Monthly")
            shopping_freq = st.selectbox("How often do you go shopping?", 
                                       shopping_freq_options,
                                       index=shopping_freq_options.index(current_shopping_freq) if current_shopping_freq in shopping_freq_options else 3)
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            current_day = st.session_state.get("shopping_day", "Monday")
            shopping_day = st.selectbox("What day of the week do you usually shop?", 
                                      days,
                                      index=days.index(current_day) if current_day in days else 0)
            
            mode_options = ["Online", "In-store"]
            current_mode = st.session_state.get("shopping_mode", "In-store")
            shopping_mode = st.selectbox("Preferred mode of shopping", 
                                       mode_options,
                                       index=mode_options.index(current_mode) if current_mode in mode_options else 1)
            
            delivery_options = ["Scheduled", "Instant"]
            current_delivery = st.session_state.get("delivery_pref", "Scheduled")
            delivery_pref = st.selectbox("Delivery preference", 
                                       delivery_options,
                                       index=delivery_options.index(current_delivery) if current_delivery in delivery_options else 0)

            col1, col2 = st.columns(2)
            with col1:
                prev_clicked = st.form_submit_button("Previous")
            with col2:
                finish_clicked = st.form_submit_button("Finish")
            
            if prev_clicked:
                prev_page()
                st.rerun()
            elif finish_clicked:
                # Save current form data to session state
                st.session_state.shopping_freq = shopping_freq
                st.session_state.shopping_day = shopping_day
                st.session_state.shopping_mode = shopping_mode
                st.session_state.delivery_pref = delivery_pref
                
                # Collect all data
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
                
                # Debug output
                st.write("Debug - Final collected data:", data)
                
                save_profile_to_firestore(username, data)
                summary = rag.build_profile_summary(data)
                rag.store_profile_embedding(username, summary)
                
                st.session_state.initial_data_filled = True
                st.rerun()
