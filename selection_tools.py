
def selection_options(st, wellness_df):
    # Create two columns
    col1, col2 = st.columns(2)
    # User inputs in a 2x2 grid layout
    with col1:
        st.write("### Instructions for selecting athletes and results")
        st.write("###### 1) Select an athlete. "
                 "\n Athlete number to look at"
                 "\n ###### 2) Select result metric."
                    "\n Can choose between result of race (rank), "
                    "\n percentage time away from winner, "
                    "\n or date."
                 "\n ###### 3) Select which of the two heats to include."
                 "\n Selecting 'All' automatically selects 'Heat 1' and 'Heat 2'."
                 "\n Selecting only Heat 1 should enable races without results from Heat 2.")

    with col2:
        # Extract and sort athlete names numerically
        athlete_names = sorted(wellness_df['Athlete'].unique(),
                               key=lambda x: int(x.split()[-1]))
        athlete = st.selectbox("1) Select Athlete", athlete_names)

        race_result_type = st.selectbox("2) Show Performance By",
                                        ["Rank", "Percentage Time Away from Winner",
                                         "Date"])

        # Initialize session state for checkboxes
        if 'all_heats' not in st.session_state:
            st.session_state.all_heats = True
        if 'heat_1' not in st.session_state:
            st.session_state.heat_1 = True
        if 'heat_2' not in st.session_state:
            st.session_state.heat_2 = True

        # Checkbox logic
        st.write("3) Race results to include")
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

    st.markdown(
            """
            <style>
            .spacer {
                margin-top: 20px;
                margin-bottom: 20px;
            }
            </style>
            <div class="spacer"></div>
            """,
            unsafe_allow_html=True
        )

    col3, col4 = st.columns(2)
    with col3:
        use_travel_day = st.checkbox(
                "4) Use last day of travel prior to competition")
        if not use_travel_day:
            days_prior = st.number_input("4) Days Prior to Competition",
                                             min_value=1,
                                             max_value=30, value=7)
        else:
            days_prior = 0
        # Select multiple metrics with a dropdown
        metrics_options = wellness_df.columns.difference(
            ['Athlete', 'Date', 'Travel Hours', 'Gender']).tolist()
        selected_metrics = st.multiselect("5. Select Comparison Metrics", metrics_options,
                                          default=['Sport Specific Training Volume'])

        # Visualization options
        visualization_option = st.selectbox("6. Visualization options",
                                            ["combined (if possible)",
                                             "Separate graphs"])

    with col4:
        st.write("#### Instructions for Wellness metrics and graph options")
        st.write("###### 4) Days prior to competition to include in the analysis"
                "\n  choose the number of days or checkmark the box to select from last "
                 "day of travel till competition for each competition day"
                "\n ###### 5) Select which metrics you want visualize:"
                 "\n Sport Specific Training Volume, Resting HR, Sleep, Stress, "
                 "Soreness, Sleep Quality, Motivation, and Fatigue "
                "\n ###### 6) Select if you want to visualize the data in one graph or separate graphs"
                "\n combined will only combine the metrics with scores from 0 to 100:"
                 "\n  Stress, Soreness, Sleep Quality, Motivation, and Fatigue")


    return st, col1, col2, athlete, use_travel_day, days_prior, race_result_type, selected_metrics, visualization_option
