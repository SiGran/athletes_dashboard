
def selection_options(st, wellness_df):
    # Create two columns
    col1, col2 = st.columns(2)
    # User inputs in a 2x2 grid layout
    with col1:
        # Extract and sort athlete names numerically
        athlete_names = sorted(wellness_df['Athlete'].unique(),
                               key=lambda x: int(x.split()[-1]))

        # User input for selecting athlete
        athlete = st.selectbox("Select Athlete", athlete_names)
        use_travel_day = st.checkbox("Use last day of travel prior to competition")
        if not use_travel_day:
            days_prior = st.number_input("Days Prior to Competition", min_value=1,
                                         max_value=30, value=7)
        else:
            days_prior = 0

        # Visualization options
        visualization_option = st.selectbox("Visualization options",
                                            ["In one graph (if possible)",
                                             "Separate graphs"])
    with col2:
        # Initialize session state for checkboxes
        if 'all_heats' not in st.session_state:
            st.session_state.all_heats = True
        if 'heat_1' not in st.session_state:
            st.session_state.heat_1 = True
        if 'heat_2' not in st.session_state:
            st.session_state.heat_2 = True

        # Checkbox logic
        st.write("Race results to include")
        checkbox_col1, checkbox_col2, checkbox_col3 = st.columns(3)
        with checkbox_col1:
            st.session_state.all_heats = st.checkbox("All",
                                                     value=st.session_state.all_heats)
        with checkbox_col2:
            st.session_state.heat_1 = st.checkbox("Heat 1",
                                                  value=st.session_state.heat_1)
        with checkbox_col3:
            st.session_state.heat_2 = st.checkbox("Heat 2",
                                                  value=st.session_state.heat_2)

        # Logic to handle checkbox behavior
        if not st.session_state.heat_1 or not st.session_state.heat_2:
            st.session_state.all_heats = False

        if st.session_state.heat_1 and st.session_state.heat_2:
            st.session_state.all_heats = True

        if st.session_state.all_heats:
            st.session_state.heat_1 = True
            st.session_state.heat_2 = True

        race_result_type = st.selectbox("Show Performance By",
                                        ["Rank", "Percentage Time Away from Winner",
                                         "Date"])

        # Select multiple metrics with a dropdown
        metrics_options = wellness_df.columns.difference(
            ['Athlete', 'Date', 'Travel Hours', 'Gender']).tolist()
        selected_metrics = st.multiselect("Select Comparison Metrics", metrics_options,
                                          default=['Sport Specific Training Volume'])

    return st, col1, col2, athlete, use_travel_day, days_prior, race_result_type, selected_metrics, visualization_option
