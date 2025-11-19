"""
Athletes Performance Dashboard

A Streamlit application for visualizing the relationship between athlete training volume,
wellness metrics, and competition performance. Coaches can analyze how different factors
affect performance in the days leading up to competitions.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils import aggregate_training_volume, aggregate_metric
from selection_tools import selection_options

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data
def load_data(file_path):
    """
    Load and cache Excel data to avoid re-reading on every interaction.

    This function is cached by Streamlit, so the Excel file is only read once
    per session (or when the file changes). This dramatically improves performance.

    Args:
        file_path (Path): Path to the Excel data file

    Returns:
        tuple: (wellness_df, results_df) - Two dataframes for analysis
    """
    # Define training volume categories as ordered categorical data
    # This ensures proper sorting in visualizations (Low < Moderate < High)
    categories = ['Low', 'Moderate', 'High']
    cat_type = pd.CategoricalDtype(categories=categories, ordered=True)

    # Load all three sheets from the Excel file
    # - 'Wellness and Load': Daily training and wellness metrics for each athlete
    # - 'Results': Competition performance data (ranks, times, dates)
    # - 'Definitions': Metadata describing the metrics
    xls = pd.read_excel(file_path, sheet_name=['Wellness and Load', 'Results', 'Definitions'],
                        dtype={'Sport Specific Training Volume': cat_type})

    # Return the two primary dataframes for analysis
    return xls['Wellness and Load'], xls['Results']


# Construct path to the Excel data file containing wellness, load, and results data
data_file = Path.cwd() / 'data' / 'WellnessLoadandResultsData.xlsx'

# Load data using cached function (10-100x faster on subsequent interactions)
wellness_df, results_df = load_data(data_file)

# =============================================================================
# STREAMLIT APP CONFIGURATION
# =============================================================================

# Configure the page to use wide layout for better visualization of multiple charts
st.set_page_config(layout="wide")

# Display main title and description
st.title("Compare Athlete Performance to Training Volume and Wellness Metrics")
st.write("###### This dashboard is designed to help coaches and athletes visualize the influences "
        "of training and their wellness metrics on their performance for the days leading up to a race")

# =============================================================================
# USER INPUT SELECTION
# =============================================================================

# Render the selection UI and retrieve user choices
# Returns: streamlit object, column objects, selected athlete, travel day option,
#          days prior, result type, selected metrics, and visualization option
(st, col1, col2, athlete, use_travel_day, days_prior, race_result_type, selected_metrics,
 visualization_option) = selection_options(st, wellness_df)

# =============================================================================
# DATA AGGREGATION
# =============================================================================

# Aggregate training volume data for the selected athlete based on user parameters
# This combines wellness data with competition results for the specified time window
aggregated_data = aggregate_training_volume(wellness_df, results_df, athlete, use_travel_day,
                                           days_prior, race_result_type,
                                           st.session_state.heat_1, st.session_state.heat_2)


def adjust_for_date(df):
    """
    Adjust dataframe columns and x-axis title based on the selected result type.

    When viewing by date instead of rank/time, this function swaps the Result and
    Competition Date columns so that dates appear on the x-axis.

    Args:
        df (pd.DataFrame): Dataframe with 'Result' and 'Competition Date' columns

    Returns:
        tuple: (modified dataframe, x-axis title string)
    """
    if race_result_type == 'Date':
        # Switch the date and result columns for date-based x-axis
        df['Result'], df['Competition Date'] = (
            df['Competition Date'], df['Result'])
        x_title = "Competition Date"
    else:
        # Create descriptive x-axis title based on result type and heat selection
        x_title = f"{race_result_type} {'total score' if st.session_state.all_heats else 'Only Heat 1' if st.session_state.heat_1 else 'Only Heat 2'}"
    return df, x_title

# =============================================================================
# DATA VISUALIZATION
# =============================================================================

# Only proceed with visualization if we have aggregated data
if not aggregated_data.empty:
    # Adjust columns based on whether we're viewing by date or rank/time
    aggregated_data, x_title = adjust_for_date(aggregated_data)

    # Sort data by result (rank, time percentage, or date) for consistent visualization
    aggregated_data = aggregated_data.sort_values('Result')

    # Convert Result to categorical to maintain sort order in plots
    aggregated_data['Result'] = pd.Categorical(aggregated_data['Result'],
                                               categories=aggregated_data['Result'].unique(), ordered=True)

    # Define hover template for interactive tooltips
    # Shows different info depending on whether x-axis is Rank or Date
    hovertemplate = 'Date: %{customdata[0]}<br>Days prior included: %{customdata[1]}<extra></extra>' if race_result_type == 'Rank' else \
        'Rank: %{customdata[0]}<br>Days prior included: %{customdata[1]}<extra></extra>'

    # Create two-column layout for displaying charts side by side
    cols = st.columns(2)
    col_index = 0  # Track which column to place the next chart in

    # Create a copy of selected_metrics to avoid modifying the original list
    # This prevents issues when removing items during iteration
    remaining_metrics = selected_metrics.copy()

    # -------------------------------------------------------------------------
    # TRAINING VOLUME VISUALIZATION (Stacked Bar Chart)
    # -------------------------------------------------------------------------
    if "Sport Specific Training Volume" in remaining_metrics:
        """
        Create a stacked bar chart showing training volume distribution.
        Each bar represents a competition result, stacked by Low/Moderate/High training days.
        Colors: Red (High), Orange (Moderate), Yellow (Low)
        """
        fig = go.Figure()

        # Add High intensity training days (bottom of stack, red)
        fig.add_trace(go.Bar(
            x=aggregated_data['Result'],
            y=aggregated_data['High'],
            name='High',
            marker_color='red',
            hovertemplate=hovertemplate,
            customdata=aggregated_data[['Competition Date', 'Days Prior']].values
        ))

        # Add Moderate intensity training days (middle of stack, orange)
        fig.add_trace(go.Bar(
            x=aggregated_data['Result'],
            y=aggregated_data['Moderate'],
            name='Moderate',
            marker_color='orange',
            base=aggregated_data['High'],  # Stack on top of High
            hovertemplate=hovertemplate,
            customdata=aggregated_data[['Competition Date', 'Days Prior']].values
        ))

        # Add Low intensity training days (top of stack, yellow)
        fig.add_trace(go.Bar(
            x=aggregated_data['Result'],
            y=aggregated_data['Low'],
            name='Low',
            marker_color='yellow',
            base=aggregated_data['High'] + aggregated_data['Moderate'],  # Stack on top of High + Moderate
            hovertemplate=hovertemplate,
            customdata=aggregated_data[['Competition Date', 'Days Prior']].values
        ))

        # Configure chart layout
        fig.update_layout(
            title=f"{race_result_type} vs Training Volume for {athlete}",
            xaxis_title=x_title,
            yaxis_title='Number of Training Volume Days',
            barmode='stack'
        )

        # Display chart in current column and move to next column
        cols[col_index].plotly_chart(fig)
        col_index = (col_index + 1) % 2

        # Remove from metrics list to avoid re-plotting
        remaining_metrics.remove("Sport Specific Training Volume")

    # -------------------------------------------------------------------------
    # RESTING HEART RATE VISUALIZATION (Box Plot)
    # -------------------------------------------------------------------------
    if "Resting HR" in remaining_metrics:
        """
        Create a box plot for Resting Heart Rate.
        Box plots show distribution (median, quartiles, outliers) of HR values
        in the days leading up to each competition.
        """
        fig_hr = go.Figure()

        # Aggregate resting HR data for the selected athlete and time window
        resting_hr = aggregate_metric("Resting HR", wellness_df, results_df, athlete,
                                      use_travel_day, days_prior, race_result_type,
                                      st.session_state.heat_1, st.session_state.heat_2)
        resting_hr, x_title = adjust_for_date(resting_hr)

        # Create box plot trace
        fig_hr.add_trace(go.Box(
            x=resting_hr['Result'],
            y=resting_hr["Values"],
            name='Resting HR',
            hovertemplate=hovertemplate,
            customdata=resting_hr[['Competition Date', 'Days Prior']].values
        ))

        # Configure chart layout
        fig_hr.update_layout(
            title=f"{race_result_type} vs Resting HR for {athlete}",
            xaxis_title=x_title,
            yaxis_title='Resting HR (BPM)'
        )

        # Display chart and move to next column
        cols[col_index].plotly_chart(fig_hr)
        col_index = (col_index + 1) % 2
        remaining_metrics.remove("Resting HR")

    # -------------------------------------------------------------------------
    # SLEEP HOURS VISUALIZATION (Box Plot)
    # -------------------------------------------------------------------------
    if "Sleep Hours" in remaining_metrics:
        """
        Create a box plot for Sleep Hours.
        Shows the distribution of sleep duration in the days prior to each competition.
        """
        fig_sleep = go.Figure()

        # Aggregate sleep hours data for the selected athlete and time window
        sleep_hours = aggregate_metric("Sleep Hours", wellness_df, results_df, athlete,
                                       use_travel_day, days_prior, race_result_type,
                                       st.session_state.heat_1, st.session_state.heat_2)
        sleep_hours, x_title = adjust_for_date(sleep_hours)

        # Create box plot trace
        fig_sleep.add_trace(go.Box(
            x=sleep_hours['Result'],
            y=sleep_hours["Values"],
            name='Sleep Hours',
            hovertemplate=hovertemplate,
            customdata=sleep_hours[['Competition Date', 'Days Prior']].values
        ))

        # Configure chart layout
        fig_sleep.update_layout(
            title=f"{race_result_type} vs Sleep Hours for {athlete}",
            xaxis_title=x_title,
            yaxis_title='Sleep (Hrs)'
        )

        # Display chart and move to next column
        cols[col_index].plotly_chart(fig_sleep)
        col_index = (col_index + 1) % 2
        remaining_metrics.remove("Sleep Hours")

    # -------------------------------------------------------------------------
    # REMAINING WELLNESS METRICS VISUALIZATION
    # -------------------------------------------------------------------------
    # Handle remaining metrics: Stress, Soreness, Sleep Quality, Motivation, Fatigue
    # These metrics use a 0-100 subjective scale

    if visualization_option == "combined (if possible)" and len(remaining_metrics) > 0:
        """
        COMBINED VIEW: All remaining metrics on a single chart.
        This works well since all wellness metrics use the same 0-100 scale.
        Allows easy comparison of multiple factors on one graph.
        """
        fig = go.Figure()

        # Add a box plot trace for each remaining metric
        for metric in remaining_metrics:
            metric_data = aggregate_metric(metric, wellness_df, results_df, athlete,
                                           use_travel_day, days_prior, race_result_type,
                                           st.session_state.heat_1, st.session_state.heat_2)
            metric_data, x_title = adjust_for_date(metric_data)

            fig.add_trace(go.Box(
                x=metric_data['Result'],
                y=metric_data["Values"],
                name=metric,
                hovertemplate=hovertemplate,
                customdata=metric_data[['Competition Date', 'Days Prior']].values
            ))

        # Configure combined chart layout
        fig.update_layout(
            title=f"{race_result_type} vs {remaining_metrics} for {athlete}",
            xaxis_title=x_title,
            yaxis_title='Metric Value (0-100 subjective score)'
        )

        cols[col_index].plotly_chart(fig)

    else:
        """
        SEPARATE VIEW: Each metric gets its own chart.
        Provides more detail for individual metrics but uses more screen space.
        """
        for metric in remaining_metrics:
            # Aggregate data for this specific metric
            metric_data = aggregate_metric(metric, wellness_df, results_df, athlete,
                                           use_travel_day, days_prior, race_result_type,
                                           st.session_state.heat_1, st.session_state.heat_2)
            metric_data, x_title = adjust_for_date(metric_data)

            # Create individual box plot for this metric
            fig_metric = go.Figure(go.Box(
                x=metric_data['Result'],
                y=metric_data["Values"],
                name=metric
            ))

            # Configure chart layout
            fig_metric.update_layout(
                title=f"{race_result_type} vs {metric} for {athlete}",
                xaxis_title=x_title,
                yaxis_title='Metric Value (0-100 subjective score)'
            )

            # Display chart in current column and move to next column
            cols[col_index].plotly_chart(fig_metric)
            col_index = (col_index + 1) % 2

# =============================================================================
# FOOTER NOTE
# =============================================================================
st.write("Note: hovering over a value will show the date of the competition and the number of days prior included in the analysis")