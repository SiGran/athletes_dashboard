import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from utils import aggregate_training_volume, aggregate_metric
from selection_tools import selection_options

# Load the data
data_file = Path.cwd() / 'data' / 'WellnessLoadandResultsData.xlsx'
categories = ['Low', 'Moderate', 'High']
cat_type = pd.CategoricalDtype(categories=categories, ordered=True)
xls = pd.read_excel(data_file, sheet_name=['Wellness and Load', 'Results', 'Definitions'], dtype={'Sport Specific Training Volume': cat_type})

wellness_df = xls['Wellness and Load']
results_df = xls['Results']

# Streamlit app
st.set_page_config(layout="wide")  # Set the page configuration to wide layout
st.title("Athlete's Performance Dependence on Wellness and Training")

(st, col1, col2, athlete, use_travel_day, days_prior, race_result_type, selected_metrics,
 visualization_option) = selection_options(st, wellness_df)

aggregated_data = aggregate_training_volume(wellness_df, results_df, athlete, use_travel_day, days_prior, race_result_type, st.session_state.heat_1, st.session_state.heat_2)


def adjust_for_date(df):
    if race_result_type == 'Date':
        # Switch the date and result columns
        df['Result'], df['Competition Date'] = (
            df['Competition Date'], df['Result'])
        x_title = "Competition Date"
    else:
        x_title = f"{race_result_type} {'total score' if st.session_state.all_heats else 'Only Heat 1' if st.session_state.heat_1 else 'Only Heat 2'}"
    return df, x_title

# Visualize the data
if not aggregated_data.empty:
    aggregated_data, x_title = adjust_for_date(aggregated_data)

    aggregated_data = aggregated_data.sort_values('Result')
    aggregated_data['Result'] = pd.Categorical(aggregated_data['Result'],
                                               categories=aggregated_data['Result'].unique(), ordered=True)
    hovertemplate = 'Date: %{customdata[0]}<br>Days prior included: %{customdata[1]}<extra></extra>' if race_result_type == 'Rank' else \
        'Rank: %{customdata[0]}<br>Days prior included: %{customdata[1]}<extra></extra>'

    cols = st.columns(2)
    col_index = 0

    if "Sport Specific Training Volume" in selected_metrics:  # Create bar plot
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=aggregated_data['Result'],
            y=aggregated_data['High'],
            name='High',
            marker_color='red',
            hovertemplate=hovertemplate,
            customdata=aggregated_data[['Competition Date', 'Days Prior']].values
        ))
        fig.add_trace(go.Bar(
            x=aggregated_data['Result'],
            y=aggregated_data['Moderate'],
            name='Moderate',
            marker_color='orange',
            base=aggregated_data['High'],
            hovertemplate=hovertemplate,
            customdata=aggregated_data[['Competition Date', 'Days Prior']].values
        ))
        fig.add_trace(go.Bar(
            x=aggregated_data['Result'],
            y=aggregated_data['Low'],
            name='Low',
            marker_color='yellow',
            base=aggregated_data['High'] + aggregated_data['Moderate'],
            hovertemplate=hovertemplate,
            customdata=aggregated_data[['Competition Date', 'Days Prior']].values
        ))

        fig.update_layout(
            title=f"{race_result_type} vs Training Volume for {athlete}",
            xaxis_title=x_title,
            yaxis_title='Number of Training Volume Days',
            barmode='stack'
        )

        cols[col_index].plotly_chart(fig)
        col_index = (col_index + 1) % 2
        selected_metrics.remove("Sport Specific Training Volume")

    if "Resting HR" in selected_metrics:  # Create a separate graph for Resting HR
        fig_hr = go.Figure()
        resting_hr = aggregate_metric("Resting HR", wellness_df, results_df, athlete,
                                      use_travel_day, days_prior, race_result_type,
                                      st.session_state.heat_1, st.session_state.heat_2)
        resting_hr, x_title = adjust_for_date(resting_hr)
        fig_hr.add_trace(go.Box(
            x=resting_hr['Result'],
            y=resting_hr["Values"],
            name='Resting HR',
            hovertemplate=hovertemplate,
            customdata=resting_hr[['Competition Date', 'Days Prior']].values
        ))
        fig_hr.update_layout(
            title=f"{race_result_type} vs Resting HR for {athlete}",
            xaxis_title=x_title,
            yaxis_title='Resting HR (BPM)'
        )
        cols[col_index].plotly_chart(fig_hr)
        col_index = (col_index + 1) % 2
        selected_metrics.remove("Resting HR")

    if "Sleep Hours" in selected_metrics:  # Create a separate graph for Sleep Hours
        fig_sleep = go.Figure()
        sleep_hours = aggregate_metric("Sleep Hours", wellness_df, results_df, athlete,
                                       use_travel_day, days_prior, race_result_type,
                                       st.session_state.heat_1, st.session_state.heat_2)
        sleep_hours, x_title = adjust_for_date(sleep_hours)
        fig_sleep.add_trace(go.Box(
            x=sleep_hours['Result'],
            y=sleep_hours["Values"],
            name='Sleep Hours',
            hovertemplate=hovertemplate,
            customdata=sleep_hours[['Competition Date', 'Days Prior']].values
        ))
        fig_sleep.update_layout(
            title=f"{race_result_type} vs Sleep Hours for {athlete}",
            xaxis_title=x_title,
            yaxis_title='Sleep (Hrs)'
        )
        cols[col_index].plotly_chart(fig_sleep)
        col_index = (col_index + 1) % 2
        selected_metrics.remove("Sleep Hours")

    # Create a single graph for the remaining metrics
    if visualization_option == "In one graph (if possible)" and len(selected_metrics) > 0:
        fig = go.Figure()
        for metric in selected_metrics:
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
        fig.update_layout(
            title=f"{race_result_type} vs {selected_metrics} for {athlete}",
            xaxis_title=x_title,
            yaxis_title='Metric Value (0-100 subjective score)'
        )
        cols[col_index].plotly_chart(fig)
    else:
        for metric in selected_metrics:
            metric_data = aggregate_metric(metric, wellness_df, results_df, athlete,
                                           use_travel_day, days_prior, race_result_type,
                                           st.session_state.heat_1, st.session_state.heat_2)
            metric_data, x_title = adjust_for_date(metric_data)
            fig_metric = go.Figure(go.Box(
                x=metric_data['Result'],
                y=metric_data["Values"],
                name=metric
            ))
            fig_metric.update_layout(
                title=f"{race_result_type} vs {metric} for {athlete}",
                xaxis_title=x_title,
                yaxis_title='Metric Value (0-100 subjective score)'
            )
            cols[col_index].plotly_chart(fig_metric)
            col_index = (col_index + 1) % 2


