# Football Data Intelligence Pipeline

A football data analytics project focused on data quality, event processing, performance analysis and unsupervised anomaly detection using real-world football data.

The project demonstrates how raw football event data can be transformed into structured datasets, validated through automated checks, analysed using Python and machine learning, and presented through visualisations and an interactive Streamlit dashboard.

## Project Overview

Football data is only useful when it is reliable, structured and interpreted correctly.

Using StatsBomb Open Data, this project explores a data pipeline that transforms raw football event data into structured datasets and meaningful insights.

The project:

- Loads and processes raw football event data.
- Flattens nested JSON structures into a structured Pandas DataFrame.
- Performs rule-based data-quality checks to identify potential issues.
- Profiles missing values, event distributions and coordinate completeness.
- Calculates team performance statistics.
- Uses Isolation Forest to identify statistically unusual football events.
- Compares rule-based validation with unsupervised anomaly detection.
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
| Scikit-learn | Unsupervised machine learning and anomaly detection |
| Pytest | Automated testing |
| Matplotlib | Data visualisation |
| Plotly | Interactive charts |
| Streamlit | Interactive dashboard |
| Jupyter Notebook | Exploratory analysis and machine learning |
| Git & GitHub | Version control and project management |

## Project Structure

```text
football-data-reality-check/
│
├── data/
│   └── raw/
│       └── statsbomb/
│
├── notebooks/
│   └── football_anomaly_detection.ipynb
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

### 1. Data Ingestion and Processing

Raw StatsBomb JSON event data is loaded and transformed into a structured Pandas DataFrame.

Nested fields are extracted, including:

- Event type
- Team and player
- Match timing
- Pitch coordinates
- Pass information
- Shot outcomes and expected goals (xG)
- Possession information

### 2. Data Quality Validation

The pipeline includes checks for:

- Missing event IDs
- Duplicate event IDs
- Missing event types
- Invalid pitch coordinates
- Missing or invalid shot xG values
- Missing shot outcomes

The validation report records potential issues identified by these checks.

### 3. Data Profiling

The profiling stage examines:

- Missing values across columns
- Event-type distribution
- Coordinate completeness
- Team activity
- Event-specific field completeness

Event-specific completeness is particularly important because not every field applies to every event.

For example, shot xG should be evaluated for shots rather than all match events. A missing xG value for a pass is expected and should not automatically be classified as a data-quality issue.

### 4. Football Performance Analytics

The project calculates team-level statistics, including:

- Passes attempted
- Passes completed
- Pass accuracy
- Shots
- Goals
- Total expected goals (xG)
- Number of possession sequences

### 5. Unsupervised Anomaly Detection

To extend the data-quality analysis, an unsupervised machine-learning approach was implemented using **Isolation Forest**.

The objective was to investigate whether machine learning could identify unusual football events that traditional rule-based validation might overlook.

#### Feature Engineering

The analysis focused on 1,033 pass events from the selected match.

Six numerical features were used:

| Feature | Description |
|---|---|
| x | Starting horizontal pitch coordinate |
| y | Starting vertical pitch coordinate |
| delta_x | Horizontal displacement of the pass |
| delta_y | Vertical displacement of the pass |
| pass_length | Recorded pass length |
| duration | Recorded pass duration |

Additional feature engineering was performed to calculate pass displacement and independently calculate the distance between the starting and ending coordinates.

The calculated distance was compared with the recorded pass length to investigate internal consistency.

#### Model Implementation

An Isolation Forest model was trained using:

- **Algorithm:** Isolation Forest
- **Number of estimators:** 200
- **Contamination:** 0.05
- **Random state:** 42

The contamination parameter was set to 5%, meaning the model was configured to identify approximately 5% of observations as potential anomalies.

The model identified 52 potentially anomalous passes out of 1,033.

These observations were investigated further using anomaly scores and visualisations.

#### Results

The following table compares the average characteristics of normal and flagged passes.

| Metric | Normal passes (981) | Flagged passes (52) |
|---|---:|---:|
| Average pass length | 18.89 m | 59.19 m |
| Average duration | 1.38 s | 3.58 s |

The flagged passes had substantially greater average pass lengths and durations.

This suggests that the model identified unusual combinations of passing characteristics within the selected match.

However, an unusual pass is not necessarily an incorrect pass. A long goalkeeper pass, for example, may be unusual compared with the majority of passes but still represent a completely valid football action.

#### Rule-Based Validation vs Machine Learning

The anomaly detection results were compared with two existing rule-based checks:

1. Pitch-coordinate boundaries.
2. Consistency between recorded pass length and calculated distance.

None of the 52 Isolation Forest flagged passes violated these two checks.

A controlled experiment was also conducted by introducing three artificial abnormalities into copies of an ordinary pass:

| Artificial anomaly | Rule-based validation | Isolation Forest |
|---|---|---|
| Impossible pitch coordinate | Detected | Not detected |
| Unusual pass duration | Not detected | Detected |
| Extreme pass length | Detected | Detected |

This experiment illustrates how the two approaches can complement one another.

Rule-based validation is effective at identifying predefined constraints, while Isolation Forest can identify unusual statistical patterns that are not explicitly covered by those rules.

The controlled experiment is illustrative rather than a comprehensive performance evaluation. It uses only three deliberately extreme examples.

### 6. Visualisation and Dashboard

The project includes visualisations and an interactive Streamlit dashboard.

The dashboard brings together:

- Match statistics
- Team comparisons
- Event distributions
- Data-quality findings

The anomaly detection notebook also includes a football pitch visualisation showing normal and flagged passes, together with the trajectories of the ten most unusual passes.

## Initial Football Analytics Findings

The analysis of the selected match produced the following team-level results:

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

### 1. Clone the Repository

```bash
git clone https://github.com/0neal264/football-data-reality-check.git

cd football-data-reality-check
```

### 2. Create a Virtual Environment

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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For the anomaly detection notebook, ensure the environment includes:

```bash
pip install scikit-learn jupyter
```

### 4. Run Automated Tests

```bash
python -m pytest tests/ -v
```

### 5. Run the Analysis Scripts

```bash
python run_statsbomb_validation.py

python run_data_profiling.py

python run_football_analytics.py

python create_visualisations.py
```

### 6. Run the Anomaly Detection Notebook

Start Jupyter:

```bash
jupyter notebook
```

Open:

```text
notebooks/football_anomaly_detection.ipynb
```

Run the notebook cells in order.

### 7. Launch the Dashboard

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

The anomaly detection analysis also has limitations:

- The model was trained on one match and may not generalise to other matches or competitions.
- The contamination parameter influences how many observations are flagged.
- Isolation Forest identifies unusual patterns, not confirmed data errors.
- The controlled anomaly experiment used only three deliberately extreme examples.
- The selected features do not capture every aspect of football context or tactical behaviour.
- The flagged events require further investigation before they can be classified as genuine data-quality problems.

Potential future improvements include:

- Expanding the pipeline to multiple matches and competitions.
- Evaluating anomaly detection across different matches.
- Testing a wider range of controlled anomalies.
- Investigating flagged events using football context and domain knowledge.
- Developing player-level performance analysis.
- Exploring passing networks and possession patterns.
- Adding more advanced football metrics.
- Improving the dashboard with additional interactive filters.
- Incorporating tracking data when an appropriate source is available.

## Author

**O'Neal Okutu**

BSc Data Science student at the IT University of Copenhagen.

Interested in football analytics, data engineering, machine learning and turning complex datasets into useful insights.

[GitHub](https://github.com/0neal264)