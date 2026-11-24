# Employee Engagement & Burnout Risk Analytics

A Streamlit-based HR analytics case-study project focused on preventive employee-experience diagnostics.

## Project objective

Analyze employee engagement dimensions, work-life balance, overtime, travel, commute, role and career-stage patterns. The dashboard is designed to help HR teams identify group-level areas that may deserve further investigation and supportive intervention.

**Important:** The included CSV has the familiar 1,470-row / 31-column structure of the IBM HR Analytics Employee Attrition dataset. Its provenance should be verified. Do not claim that it is verified internal Palo Alto Networks employee data unless you have an authoritative source confirming that.

## Features

- Engagement Health Overview
- Rule-based Burnout Risk Dashboard
- Role and Career-Stage Analysis
- Manager Action Panel with group-level intervention themes
- Department, role, overtime, engagement and tenure filters
- CSV exports for filtered analytics and HR review segments
- Data validation and methodology notes

## Tech stack

Python, Pandas, NumPy, Plotly and Streamlit.

## Setup on Windows (Anaconda / PowerShell)

1. Extract the ZIP.
2. Open the extracted `Employee_Engagement_Burnout_Analytics` folder in VS Code.
3. Open the VS Code terminal (PowerShell).
4. Create and activate an environment (optional but recommended):

```powershell
conda create -n employee-analytics python=3.11 -y
conda activate employee-analytics
```

5. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

6. Run the dashboard:

```powershell
python -m streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Dataset

The provided file is stored at:

`data/Palo Alto Networks.csv`

You can also upload another compatible CSV from the dashboard sidebar.

## Analytical definitions

### Engagement Index

Four dimensions are normalized from 1–4 to 0–100:

`normalized_score = ((rating - 1) / 3) * 100`

The Engagement Index is the unweighted mean of:
- JobInvolvement
- JobSatisfaction
- EnvironmentSatisfaction
- RelationshipSatisfaction

### Burnout Risk (heuristic)

- High: OverTime = Yes AND WorkLifeBalance <= 2
- Medium: exactly one of those conditions is true
- Low: neither condition is true

This is a screening proxy, not a medical or psychological diagnosis.

### Workload Stress Indicator (0–3)

One point each for:
- Overtime = Yes
- BusinessTravel = Travel_Frequently
- DistanceFromHome >= 15

The commute threshold is a project-defined analytical rule and should be tested for sensitivity.

### Satisfaction Stability Score

100 minus the population standard deviation of the four normalized engagement dimensions. It measures consistency across dimensions, not the level of satisfaction.

## Suggested project structure

```text
Employee_Engagement_Burnout_Analytics/
│
├── app.py
├── analysis.py
├── requirements.txt
├── README.md
└── data/
    └── Palo Alto Networks.csv
```

## Research and ethical limitations

- This is cross-sectional data; it cannot establish causality or prove that burnout causes attrition.
- The data has no direct working-hours measure, medical/health data, employee names, manager IDs or longitudinal engagement history.
- Use results at team/department level where possible. Do not use a heuristic risk score for punitive employment decisions.
- Validate any proposed intervention with employee listening sessions and HR context.
- Confirm the dataset source before attributing it to a specific company.

## Future enhancements

- Add a longitudinal survey data pipeline.
- Add confidence intervals and minimum group-size suppression.
- Validate the risk rules with HR subject-matter experts.
- Add role-specific and department-specific benchmarks.
- Add authentication and role-based access before any real organizational deployment.
