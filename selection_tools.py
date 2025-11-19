"""
Selection Tools for Athletes Dashboard

This module provides UI components for user input selection in the Streamlit dashboard.
It handles athlete selection, result type selection, heat selection, time window configuration,
and visualization options.
"""

# =============================================================================
# MAIN SELECTION OPTIONS UI
# =============================================================================

def selection_options(st, wellness_df):
    """
    Render the user input selection interface for the dashboard.

    Creates a two-column layout with:
    - Left: Instructions for using the dashboard
    - Right: Selection widgets (athlete, result type, heats, metrics, etc.)

    Args:
        st: Streamlit module/object
        wellness_df (pd.DataFrame): Wellness data used to extract athlete names

    Returns:
        tuple: (st, col1, col2, athlete, use_travel_day, days_prior,
                race_result_type, selected_metrics, visualization_option)
            - st: Streamlit object
            - col1, col2: Column objects for layout
            - athlete (str): Selected athlete name
            - use_travel_day (bool): Whether to use travel day as start date
            - days_prior (int): Number of days prior to competition
            - race_result_type (str): Result display type
            - selected_metrics (list): Selected wellness metrics to visualize
            - visualization_option (str): Combined or separate graphs
    """
    # -------------------------------------------------------------------------
    # TOP SECTION: Instructions and Basic Selection
    # -------------------------------------------------------------------------

    # Create two columns for instructions and athlete/result selection
    col1, col2 = st.columns(2)

    # Left column: User instructions
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

    # Right column: Selection widgets
    with col2:
        # -----
        # 1) ATHLETE SELECTION
        # -----
        # Extract athlete names from wellness data and sort numerically
        # (assumes names like "Athlete 1", "Athlete 2", etc.)
        athlete_names = sorted(wellness_df['Athlete'].unique(),
                               key=lambda x: int(x.split()[-1]))
        athlete = st.selectbox("1) Select Athlete", athlete_names)

        # -----
        # 2) RESULT TYPE SELECTION
        # -----
        # Choose how to display competition results on x-axis:
        # - Rank: Position in race (1st, 2nd, etc.)
        # - Percentage Time Away from Winner: How much slower than winner
        # - Date: Competition date
        race_result_type = st.selectbox("2) Show Performance By",
                                        ["Rank", "Percentage Time Away from Winner",
                                         "Date"])

        # -----
        # 3) HEAT SELECTION
        # -----
        # Initialize session state for heat checkboxes
        # Session state persists across reruns to maintain user selections
        if 'all_heats' not in st.session_state:
            st.session_state.all_heats = True
        if 'heat_1' not in st.session_state:
            st.session_state.heat_1 = True
        if 'heat_2' not in st.session_state:
            st.session_state.heat_2 = True

        # Create three-column layout for heat checkboxes
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

        # Implement checkbox interdependency logic:
        # - If either Heat 1 or Heat 2 is unchecked, uncheck "All"
        if not st.session_state.heat_1 or not st.session_state.heat_2:
            st.session_state.all_heats = False

        # - If both Heat 1 and Heat 2 are checked, check "All"
        if st.session_state.heat_1 and st.session_state.heat_2:
            st.session_state.all_heats = True

        # - If "All" is checked, ensure both Heat 1 and Heat 2 are checked
        if st.session_state.all_heats:
            st.session_state.heat_1 = True
            st.session_state.heat_2 = True

    # Add vertical spacing between sections using custom CSS
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

    # -------------------------------------------------------------------------
    # BOTTOM SECTION: Time Window, Metrics, and Visualization Options
    # -------------------------------------------------------------------------

    # Create two columns for detailed options and instructions
    col3, col4 = st.columns(2)

    # Left column: Configuration options
    with col3:
        # -----
        # 4) TIME WINDOW SELECTION
        # -----
        # Define analysis period: either from last travel day or fixed days prior
        use_travel_day = st.checkbox(
                "4) Use last day of travel prior to competition")

        if not use_travel_day:
            # If not using travel day, ask for specific number of days
            days_prior = st.number_input("4) Days Prior to Competition",
                                             min_value=1,
                                             max_value=30, value=7)
        else:
            # If using travel day, set days_prior to 0 (not used)
            days_prior = 0

        # -----
        # 5) METRICS SELECTION
        # -----
        # Select which wellness/training metrics to visualize
        # Exclude non-metric columns (Athlete, Date, Travel Hours, Gender)
        metrics_options = wellness_df.columns.difference(
            ['Athlete', 'Date', 'Travel Hours', 'Gender']).tolist()

        selected_metrics = st.multiselect("5. Select Comparison Metrics", metrics_options,
                                          default=['Sport Specific Training Volume'])

        # -----
        # 6) VISUALIZATION OPTIONS
        # -----
        # Choose whether to combine compatible metrics or show separately
        visualization_option = st.selectbox("6. Visualization options",
                                            ["combined (if possible)",
                                             "Separate graphs"])

    # Right column: Additional instructions
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

    # -------------------------------------------------------------------------
    # RETURN VALUES
    # -------------------------------------------------------------------------
    # Return all necessary components and user selections for the main dashboard
    return st, col1, col2, athlete, use_travel_day, days_prior, race_result_type, selected_metrics, visualization_option
