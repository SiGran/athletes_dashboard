"""
Utility Functions for Athletes Dashboard

This module provides data aggregation functions that combine wellness/training data
with competition results to enable performance analysis.
"""

import pandas as pd

# =============================================================================
# TRAINING VOLUME AGGREGATION
# =============================================================================

def aggregate_training_volume(wellness_df, results_df, athlete, use_travel_day, days_prior,
                              race_result_type, heat_1, heat_2):
    """
    Aggregate training volume data for visualization.

    This function calculates the number of Low, Moderate, and High training volume days
    in the period leading up to each competition for a specific athlete.

    Args:
        wellness_df (pd.DataFrame): Daily wellness and training data
        results_df (pd.DataFrame): Competition results data
        athlete (str): Name/ID of the athlete to analyze
        use_travel_day (bool): If True, use last travel day as start date; else use days_prior
        days_prior (int): Number of days before competition to include (if not using travel day)
        race_result_type (str): How to display results - 'Rank', 'Percentage Time Away from Winner', or 'Date'
        heat_1 (bool): Include Heat 1 results
        heat_2 (bool): Include Heat 2 results

    Returns:
        pd.DataFrame: Aggregated training volume data with columns:
                     - High, Moderate, Low (count of days at each intensity)
                     - Athlete, Competition Date, Days Prior, Result
    """
    training_data = []

    # Process each competition for the selected athlete
    for _, row in results_df[results_df['Athlete'] == athlete].iterrows():
        competition_date = row['Date']

        # Find the most recent travel day before this competition
        try:
            travel_day = wellness_df[
                (wellness_df['Athlete'] == athlete) &
                (wellness_df['Travel Hours'] > 0) &
                (wellness_df['Date'] < competition_date)
            ].sort_values('Date').iloc[-1]
        except IndexError:
            # Skip this competition if no travel day found
            continue

        # Determine the analysis window start date
        if use_travel_day:
            start_date = travel_day['Date']  # Use last travel day as start
        else:
            start_date = competition_date - pd.Timedelta(days=days_prior)  # Use fixed days_prior

        # Extract all training days in the analysis window
        training_days = wellness_df[
            (wellness_df['Athlete'] == athlete) &
            (wellness_df['Date'] >= start_date) &
            (wellness_df['Date'] <= competition_date)
        ]

        # Count the number of Low, Moderate, and High training volume days
        volume_counts = training_days['Sport Specific Training Volume'].value_counts()

        # Add metadata to the counts
        volume_counts['Athlete'] = athlete
        volume_counts['Competition Date'] = competition_date
        volume_counts['Days Prior'] = (competition_date - start_date).days

        # Add competition results based on heat selection
        if heat_1 and heat_2:  # Both heats combined
            select_race_results(race_result_type, row, volume_counts)
        elif heat_1:  # Only Heat 1
            select_race_results(race_result_type, row, volume_counts, heat=" Heat 1")
        elif heat_2:  # Only Heat 2
            select_race_results(race_result_type, row, volume_counts, heat=" Heat 2")
        else:
            print(f"Something is going wrong with heat selection {heat_1} and {heat_2}")

        training_data.append(volume_counts)

    # Convert to DataFrame and fill missing volume categories with 0
    return pd.DataFrame(training_data).fillna(0)


# =============================================================================
# RACE RESULTS SELECTION HELPER
# =============================================================================

def select_race_results(race_result_type, row, volume_counts, heat=""):
    """
    Extract the appropriate race result based on heat selection and result type.

    This helper function determines which column to read from the results data
    based on whether we're analyzing combined heats or individual heats, and
    whether we want rank or percentage time away from winner.

    Args:
        race_result_type (str): Type of result - 'Rank', 'Percentage Time Away from Winner', or 'Date'
        row (pd.Series): Single row from results_df containing competition data
        volume_counts (pd.Series): Series to update with the result value
        heat (str): Heat identifier - "" for combined, " Heat 1", or " Heat 2"

    Returns:
        pd.Series: Updated volume_counts with 'Result' field populated
    """
    # Construct column names based on heat selection
    rank_row = f'Rank: Athlete{heat}'
    time_row = f'Time: Athlete{heat}'
    time_best_row = f"Time: Best{heat}"

    # For individual heats, column names have "Split" prefix
    if heat != "":
        rank_row = f"Split {rank_row}"
        time_row = f"Split {time_row}"

    # Default to rank as the result
    volume_counts['Result'] = row[rank_row]

    # If percentage time is requested, calculate it
    if race_result_type == 'Percentage Time Away from Winner':
        # Calculate how much slower athlete was compared to winner (as percentage)
        volume_counts['Result'] = ((row[time_row] - row[time_best_row]) / row[time_best_row]) * 100

    return volume_counts


# =============================================================================
# INDIVIDUAL METRIC AGGREGATION
# =============================================================================

def aggregate_metric(metric, wellness_df, results_df, athlete, use_travel_day,
                     days_prior, race_result_type, heat_1, heat_2):
    """
    Aggregate a single wellness metric for box plot visualization.

    Similar to aggregate_training_volume, but returns individual metric values
    (not counts) for each day in the analysis window. This allows box plots to
    show the distribution of metric values leading up to each competition.

    Args:
        metric (str): Name of the wellness metric to aggregate (e.g., 'Resting HR', 'Sleep Hours')
        wellness_df (pd.DataFrame): Daily wellness and training data
        results_df (pd.DataFrame): Competition results data
        athlete (str): Name/ID of the athlete to analyze
        use_travel_day (bool): If True, use last travel day as start date; else use days_prior
        days_prior (int): Number of days before competition to include (if not using travel day)
        race_result_type (str): How to display results - 'Rank', 'Percentage Time Away from Winner', or 'Date'
        heat_1 (bool): Include Heat 1 results
        heat_2 (bool): Include Heat 2 results

    Returns:
        pd.DataFrame: Long-format data with columns:
                     - Values (individual metric readings)
                     - Athlete, Competition Date, Days Prior, Result
    """
    metric_data = []

    # Process each competition for the selected athlete
    for _, row in results_df[results_df['Athlete'] == athlete].iterrows():
        competition_date = row['Date']

        # Find the most recent travel day before this competition
        try:
            travel_day = wellness_df[
                (wellness_df['Athlete'] == athlete) &
                (wellness_df['Travel Hours'] > 0) &
                (wellness_df['Date'] < competition_date)
            ].sort_values('Date').iloc[-1]
        except IndexError:
            # Skip this competition if no travel day found
            continue

        # Determine the analysis window start date
        if use_travel_day:
            start_date = travel_day['Date']  # Use last travel day as start
        else:
            start_date = competition_date - pd.Timedelta(days=days_prior)  # Use fixed days_prior

        # Extract all days with the specified metric in the analysis window
        metric_days = wellness_df[
            (wellness_df['Athlete'] == athlete) &
            (wellness_df['Date'] >= start_date) &
            (wellness_df['Date'] <= competition_date)
        ]

        # Special handling for Resting HR: filter out 0 values (missing/invalid readings)
        if metric == "Resting HR":
            metric_days = metric_days[metric_days[metric] > 0]

        # Get all individual metric values for this time window
        values = metric_days[metric].tolist()

        # Create a separate row for each metric value (enables box plot visualization)
        for value in values:
            metric_counts = pd.Series()
            metric_counts["Values"] = value
            metric_counts['Athlete'] = athlete
            metric_counts['Competition Date'] = competition_date
            metric_counts['Days Prior'] = (competition_date - start_date).days

            # Add competition results based on heat selection
            if heat_1 and heat_2:  # Both heats combined
                select_race_results(race_result_type, row, metric_counts)
            elif heat_1:  # Only Heat 1
                select_race_results(race_result_type, row, metric_counts, heat=" Heat 1")
            elif heat_2:  # Only Heat 2
                select_race_results(race_result_type, row, metric_counts, heat=" Heat 2")
            else:
                print(f"Something is going wrong with heat selection {heat_1} and {heat_2}")

            metric_data.append(metric_counts)

    # Convert to DataFrame (long format for box plots)
    return pd.DataFrame(metric_data)
