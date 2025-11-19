# Athletes Performance Dashboard

A comprehensive Streamlit-based data visualization tool designed to help coaches and athletes understand the relationship between training volume, wellness metrics, and competitive performance.

## Overview

This dashboard enables coaches to visualize how training load and wellness indicators affect athlete performance in the days leading up to competitions. By analyzing historical data, coaches can identify optimal training patterns and wellness conditions that correlate with peak performance.

## Features

- **Multi-Athlete Analysis**: Compare performance metrics across different athletes
- **Training Volume Tracking**: Visualize sport-specific training volume categorized as Low, Moderate, or High intensity
- **Wellness Metrics**: Track key indicators including:
  - Resting Heart Rate (HR)
  - Sleep Hours
  - Sleep Quality
  - Stress levels
  - Soreness
  - Motivation
  - Fatigue
- **Performance Analysis**: View results by:
  - Race rank
  - Percentage time away from winner
  - Competition date
- **Heat Selection**: Analyze results from individual heats or combined performance
- **Flexible Time Windows**: Choose analysis periods based on:
  - Fixed number of days prior to competition
  - Last travel day to competition date
- **Interactive Visualizations**:
  - Stacked bar charts for training volume
  - Box plots for wellness metrics
  - Combined or separate graph views
  - Hover tooltips with detailed information

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd athletes_dashboard
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit dashboard:
```bash
streamlit run dashboard.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

## Data Format

The application expects an Excel file (`WellnessLoadandResultsData.xlsx`) with three sheets:

1. **Wellness and Load**: Daily training and wellness data
   - Athlete ID
   - Date
   - Sport Specific Training Volume (Low/Moderate/High)
   - Resting HR
   - Sleep Hours
   - Wellness metrics (0-100 scale)
   - Travel Hours

2. **Results**: Competition performance data
   - Athlete ID
   - Competition Date
   - Rank (Heat 1, Heat 2)
   - Times (Heat 1, Heat 2)
   - Best times

3. **Definitions**: Metadata and definitions for metrics

## Project Structure

```
athletes_dashboard/
├── dashboard.py           # Main Streamlit application
├── utils.py              # Data aggregation and processing functions
├── selection_tools.py    # UI components for user selections
├── requirements.txt      # Python dependencies
├── exploration.ipynb     # Jupyter notebook for data exploration
├── data/
│   └── WellnessLoadandResultsData.xlsx  # Sample data file
└── README.md
```

## How It Works

1. **Select an Athlete**: Choose from the list of athletes in your dataset
2. **Choose Performance Metric**: Select how to view results (Rank, Time %, or Date)
3. **Select Heats**: Include results from Heat 1, Heat 2, or both
4. **Define Time Window**: Set the number of days prior to competition or use travel day as starting point
5. **Pick Metrics**: Select which wellness and training metrics to visualize
6. **Visualization Options**: View metrics combined or in separate graphs

The dashboard will generate interactive charts showing relationships between training/wellness data and competition performance.

## Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **OpenPyXL**: Excel file processing
- **NumPy**: Numerical computing

## Use Cases

- Pre-competition analysis to identify optimal training loads
- Post-competition review to understand performance factors
- Long-term trend analysis for athlete development
- Comparing different training approaches across competitions
- Identifying relationships between wellness metrics and performance

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Future Enhancements

- Support for CSV data import
- Statistical correlation analysis
- Predictive modeling for performance outcomes
- Export functionality for charts and reports
- Multi-athlete comparison views
- Custom metric definitions
