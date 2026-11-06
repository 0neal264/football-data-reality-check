# Football Data Intelligence Pipeline

A football data analytics project focused on data quality, event processing and performance analysis using real-world football data.

The project demonstrates how raw football event data can be transformed into structured datasets, validated through automated checks, analysed using Python and presented through an interactive Streamlit dashboard.

## Project Overview

Football data is only useful when it is reliable, structured and interpreted correctly.

This project explores a simple data pipeline that takes raw football event data and turns it into meaningful performance insights.

Using StatsBomb Open Data, I built a pipeline that:

- Loads and processes raw football event data.
- Flattens nested JSON structures into a structured Pandas DataFrame.
- Performs data-quality checks to identify potential issues.
- Profiles missing values, event distributions and coordinate completeness.
- Calculates team performance statistics.
- Generates visualisations and an interactive dashboard.

## Dataset

**Source:** [StatsBomb Open Data](https://github.com/statsbomb/open-data)

**Match:** Real Madrid vs Liverpool  
**Competition:** UEFA Champions League  
**Season:** 2017/18  
**Date:** 26 May 2018  
**Final score:** Real Madrid 3–1 Liverpool  
**Match ID:** 18245  
**Events analysed:** 3,497

The project uses the 2018 Champions League final available in the selected StatsBomb open-data season folder. It does not represent a complete season of matches.

StatsBomb event data records actions such as passes, shots, carries, pressures and other match events. It is event-level data, not continuous player-tracking data.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data processing and analysis |
| NumPy | Numerical operations |
| Pytest | Automated testing |
| Matplotlib | Data visualisation |
| Plotly | Interactive charts |
| Streamlit | Interactive dashboard |
| Git & GitHub | Version control and project management |

## Project Structure

```text
football-data-reality-check/
│
├── data/
│   └── raw/
│       └── statsbomb/
│
├── outputs/
│   ├── profiling/
│   ├── statsbomb_validation_report.csv
│   └── football_team_statistics.csv
│
├── src/
│   └── data_quality/
│       ├── statsbomb.py
│       ├── statsbomb_checks.py
│       ├── rules.py
│       ├── reporting.py
│       ├── profiling.py
│       ├── completeness.py
│       ├── football.py
│       ├── football_analytics.py
│       └── visualisations.py
│
├── tests/
│
├── app.py
├── run_analysis.py
├── run_statsbomb_validation.py
├── run_data_profiling.py
├── run_football_analytics.py
├── create_visualisations.py
├── requirements.txt
└── README.md
```

## Data Pipeline

### 1. Data ingestion and processing

Raw StatsBomb JSON event data is loaded and transformed into a structured Pandas DataFrame.

Nested fields are extracted, including:

- Event type
- Team and player
- Match timing
- Pitch coordinates
- Pass information
- Shot outcomes and expected goals (xG)
- Possession information

### 2. Data-quality validation

The pipeline includes checks for:

- Missing event IDs
- Duplicate event IDs
- Missing event types
- Invalid pitch coordinates
- Missing or invalid shot xG values
- Missing shot outcomes

The validation report records potential issues identified by these checks.

### 3. Data profiling

The profiling stage examines:

- Missing values across columns
- Event-type distribution
- Coordinate completeness
- Team activity
- Event-specific field completeness

Event-specific completeness is particularly useful because not every field applies to every event. For example, shot xG should be evaluated for shots rather than all match events.

### 4. Football performance analytics

The project calculates team-level statistics, including:

- Passes attempted
- Passes completed
- Pass accuracy
- Shots
- Goals
- Total expected goals (xG)
- Number of possession sequences

### 5. Visualisation and dashboard

The results are presented through visualisations and an interactive Streamlit dashboard.

The dashboard brings together match statistics, team comparisons, event distributions and data-quality findings.

## Initial Findings

The analysis of the selected match produced the following results:

| Metric | Liverpool | Real Madrid |
|---|---:|---:|
| Passes attempted | 360 | 673 |
| Passes completed | 266 | 596 |
| Pass accuracy | 73.89% | 88.56% |
| Shots | 14 | 14 |
| Goals | 1 | 3 |
| Total xG | 1.427 | 1.677 |
| Possession sequences | 74 | 90 |

Some observations:

- Both teams recorded 14 shots.
- Real Madrid recorded a higher pass accuracy.
- Real Madrid scored three goals compared with Liverpool's one.
- The teams had relatively close total xG values despite the difference in goals scored.

These findings illustrate how event data can be used to compare team performance beyond the final score.

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/0neal264/football-data-reality-check.git
cd football-data-reality-check
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run automated tests

```bash
python -m pytest tests/ -v
```

### 5. Run the analysis scripts

```bash
python run_statsbomb_validation.py
python run_data_profiling.py
python run_football_analytics.py
python create_visualisations.py
```

### 6. Launch the dashboard

```bash
streamlit run app.py
```

## Testing

Automated tests are implemented using Pytest to verify data-processing, validation and football analytics functionality.

Run the test suite with:

```bash
python -m pytest tests/ -v
```

## Limitations and Future Improvements

The current implementation focuses on one Champions League match. This provides a practical foundation for developing and testing the pipeline, but does not support broad conclusions about team performance across a full season.

Potential future improvements include:

- Expanding the pipeline to multiple matches and competitions.
- Developing player-level performance analysis.
- Exploring passing networks and possession patterns.
- Adding more advanced football metrics.
- Improving the dashboard with additional interactive filters.
- Incorporating tracking data when an appropriate source is available.

## Author

**O'Neal Okutu**

BSc Data Science student at the IT University of Copenhagen.

Interested in football analytics, data engineering, data quality and turning complex datasets into useful insights.

[GitHub](https://github.com/0neal264)