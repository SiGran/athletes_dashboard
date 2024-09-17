
import pandas as pd

# Aggregate training volume data
def aggregate_training_volume(wellness_df, results_df, athlete, use_travel_day, days_prior, race_result_type, heat_1, heat_2):
    training_data = []
    for _, row in results_df[results_df['Athlete'] == athlete].iterrows():
        competition_date = row['Date']
        try:
            travel_day = wellness_df[(wellness_df['Athlete'] == athlete) & (wellness_df['Travel Hours'] > 0) & (wellness_df['Date'] < competition_date)].sort_values('Date').iloc[-1]
        except IndexError:
            continue

        if use_travel_day:
            start_date = travel_day['Date']
        else:
            start_date = competition_date - pd.Timedelta(days=days_prior)

        training_days = wellness_df[(wellness_df['Athlete'] == athlete) & (wellness_df['Date'] >= start_date) & (wellness_df['Date'] <= competition_date)]
        volume_counts = training_days['Sport Specific Training Volume'].value_counts()
        volume_counts['Athlete'] = athlete
        volume_counts['Competition Date'] = competition_date
        volume_counts['Days Prior'] = (competition_date - start_date).days

        if heat_1 and heat_2: # both heats
            select_race_results(race_result_type, row, volume_counts)
        elif heat_1:
            select_race_results(race_result_type, row, volume_counts, heat = " Heat 1")
        elif heat_2:
            select_race_results(race_result_type, row, volume_counts, heat = " Heat 2")
        else:
            print(f"Something is going wrong with heat selection {heat_1} and {heat_2}")

        training_data.append(volume_counts)

    return pd.DataFrame(training_data).fillna(0)


def select_race_results(race_result_type, row, volume_counts, heat = ""):
    rank_row = f'Rank: Athlete{heat}'
    time_row = f'Time: Athlete{heat}'
    time_best_row = f"Time: Best{heat}"
    if heat != "":
        rank_row = f"Split {rank_row}"
        time_row = f"Split {time_row}"

    volume_counts['Result'] = row[rank_row]
    if race_result_type == 'Percentage Time Away from Winner':
        volume_counts['Result'] = (row[time_row] - row[time_best_row]) / row[
            time_best_row] * 100
    return volume_counts


def aggregate_metric(metric, wellness_df, results_df, athlete, use_travel_day,
                     days_prior, race_result_type, heat_1, heat_2):
    """ Similar to aggregate_training_volume but for a single metric and with
    purpose to creat a boxplot
    """
    metric_data = []
    for _, row in results_df[results_df['Athlete'] == athlete].iterrows():
        competition_date = row['Date']
        try:
            travel_day = wellness_df[(wellness_df['Athlete'] == athlete) & (wellness_df['Travel Hours'] > 0) & (wellness_df['Date'] < competition_date)].sort_values('Date').iloc[-1]
        except IndexError:
            continue

        if use_travel_day:
            start_date = travel_day['Date']
        else:
            start_date = competition_date - pd.Timedelta(days=days_prior)

        metric_days = wellness_df[(wellness_df['Athlete'] == athlete) &
                                  (wellness_df['Date'] >= start_date) &
                                  (wellness_df['Date'] <= competition_date)]

        if metric == "Resting HR": # Delete 0 values
            metric_days = metric_days[metric_days[metric] > 0]
        values = metric_days[metric].tolist()
        for value in values:
            metric_counts = pd.Series()
            metric_counts["Values"] = value
            metric_counts['Athlete'] = athlete
            metric_counts['Competition Date'] = competition_date
            metric_counts['Days Prior'] = (competition_date - start_date).days

            if heat_1 and heat_2: # both heats
                select_race_results(race_result_type, row, metric_counts)
            elif heat_1:
                select_race_results(race_result_type, row, metric_counts, heat = " Heat 1")
            elif heat_2:
                select_race_results(race_result_type, row, metric_counts, heat = " Heat 2")
            else:
                print(f"Something is going wrong with heat selection {heat_1} and {heat_2}")

            metric_data.append(metric_counts)

    return pd.DataFrame(metric_data)
