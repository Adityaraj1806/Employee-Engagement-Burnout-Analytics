
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

from pathlib import Path

from analysis import (
    add_analytics_features,
    load_and_validate_data,
    summarize_metrics,
)

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Employee Experience Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. PROFESSIONAL DASHBOARD CSS
# =====================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

[data-testid="stMetric"] {
    background-color: var(--secondary-background-color) !important;
    border: 1px solid rgba(128,128,128,0.3);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: var(--text-color) !important;
    opacity: 0.9;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: var(--text-color) !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,0.2);
}

.hero {
    background: linear-gradient(
        115deg,
        #102a43,
        #145374,
        #1b7a78
    );
    padding: 28px;
    border-radius: 16px;
    margin-bottom: 20px;
    color: white;
}

.hero h1 {
    color: white !important;
    font-size: 30px;
}

.hero p {
    color: #e7f4f4 !important;
    font-size: 15px;
}

.section-note {
    opacity: 0.75;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. DATA LOADING
# =====================================================

DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "Palo Alto Networks.csv"
)


@st.cache_data
def get_data(uploaded_file=None):

    if uploaded_file is not None:
        return load_and_validate_data(uploaded_file)

    return load_and_validate_data(DATA_PATH)


try:

    with st.spinner("Loading employee dataset..."):

        uploaded = None

        with st.sidebar:

            st.title("📊 Control Panel")

            uploaded = st.file_uploader(
                "Upload Employee CSV",
                type=["csv"]
            )

        raw_df, validation = get_data(uploaded)

except Exception as e:

    st.error(f"Dataset loading error: {e}")
    st.stop()


# =====================================================
# 4. FEATURE ENGINEERING
# =====================================================

df = add_analytics_features(raw_df)


# =====================================================
# 5. SIDEBAR FILTERS
# =====================================================

with st.sidebar:

    st.success(
        f"Loaded {len(raw_df):,} employee records"
    )

    st.divider()

    st.subheader("Dashboard Filters")

    departments = sorted(
        raw_df["Department"].dropna().unique()
    )

    roles = sorted(
        raw_df["JobRole"].dropna().unique()
    )

    selected_departments = st.multiselect(
        "Department",
        departments,
        default=departments
    )

    selected_roles = st.multiselect(
        "Job Role",
        roles,
        default=roles
    )

    overtime_filter = st.selectbox(
        "Overtime",
        ["All", "Yes", "No"]
    )

    engagement_range = st.slider(
        "Engagement Threshold",
        0,
        100,
        (0, 100)
    )

    tenure_range = st.slider(
        "Years At Company",
        int(df["YearsAtCompany"].min()),
        int(df["YearsAtCompany"].max()),
        (
            int(df["YearsAtCompany"].min()),
            int(df["YearsAtCompany"].max())
        )
    )

    st.divider()

    st.caption(
        "Filters apply to all dashboard modules."
    )


# =====================================================
# 6. FILTER DATA
# =====================================================

filtered = df[
    (df["Department"].isin(selected_departments))
    & (df["JobRole"].isin(selected_roles))
    & (df["EngagementIndex"].between(
        engagement_range[0],
        engagement_range[1]
    ))
    & (df["YearsAtCompany"].between(
        tenure_range[0],
        tenure_range[1]
    ))
].copy()

if overtime_filter != "All":

    filtered = filtered[
        filtered["OverTime"] == overtime_filter
    ]

if filtered.empty:

    st.warning(
        "No employees match the selected filters."
    )

    st.stop()


# =====================================================
# 7. DASHBOARD HEADER
# =====================================================

st.markdown("""
<div class="hero">

<h1>
Employee Engagement & Burnout Risk Analytics
</h1>

<p>
Preventive Employee Experience Diagnostics |
HR Analytics Case Study
</p>

</div>
""", unsafe_allow_html=True)


st.caption(
    "Identify engagement gaps and workload-related warning "
    "signals before they become larger workforce concerns."
)


# =====================================================
# 8. NAVIGATION TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([

    "📈 Engagement Overview",

    "🔥 Burnout Risk",

    "🧭 Role & Career Analysis",

    "🛠 Manager Action Panel",

    "📚 Data & Methodology"

])


# =====================================================
# TAB 1: ENGAGEMENT OVERVIEW
# =====================================================

with tab1:

    st.header("Engagement Health Overview")

    metrics = summarize_metrics(filtered)

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Employees In View",
            f"{len(filtered):,}"
        )

    with col2:

        st.metric(
            "Average Engagement",
            f"{metrics['engagement']:.1f}/100"
        )

    with col3:

        st.metric(
            "Work-Life Balance",
            f"{metrics['wlb']:.2f}/4"
        )

    with col4:

        st.metric(
            "High Burnout Risk",
            f"{metrics['high_risk_pct']:.1f}%"
        )

    st.divider()

    left, right = st.columns(2)

    with left:

        dimensions = [
            "JobInvolvement",
            "JobSatisfaction",
            "EnvironmentSatisfaction",
            "RelationshipSatisfaction"
        ]

        labels = [
            "Job Involvement",
            "Job Satisfaction",
            "Environment Satisfaction",
            "Relationship Satisfaction"
        ]

        values = [
            filtered[c].mean()
            for c in dimensions
        ]

        fig = px.bar(
            x=labels,
            y=values,
            title="Average Engagement Dimensions",
            labels={
                "x": "Dimension",
                "y": "Average Rating"
            },
            range_y=[0, 4],
            text_auto=".2f"
        )

        fig.update_traces(
            marker_color="#3298dc"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        risk_counts = (
            filtered["BurnoutRisk"]
            .value_counts()
            .reindex(
                ["Low", "Medium", "High"],
                fill_value=0
            )
            .reset_index()
        )

        risk_counts.columns = [
            "Risk Level",
            "Employees"
        ]

        fig = px.pie(
            risk_counts,
            names="Risk Level",
            values="Employees",
            hole=0.5,
            title="Burnout Risk Distribution",
            color="Risk Level",
            color_discrete_map={
                "Low": "#38a169",
                "Medium": "#e6a23c",
                "High": "#d9534f"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    department_data = (
        filtered.groupby("Department")
        ["EngagementIndex"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        department_data,
        x="Department",
        y="EngagementIndex",
        title="Department-wise Engagement",
        color="EngagementIndex",
        color_continuous_scale="Blues",
        range_y=[0, 100]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# TAB 2: BURNOUT RISK
# =====================================================

with tab2:

    st.header("Burnout Risk Analysis")

    st.warning(
        "These are rule-based analytical indicators, "
        "not medical burnout diagnoses."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "High Risk Employees",
            int(
                (filtered["BurnoutRisk"] == "High").sum()
            )
        )

    with col2:

        st.metric(
            "Overtime Employees",
            f"{(filtered['OverTime'] == 'Yes').mean()*100:.1f}%"
        )

    with col3:

        st.metric(
            "Low Work-Life Balance",
            f"{(filtered['WorkLifeBalance'] <= 2).mean()*100:.1f}%"
        )

    st.divider()

    left, right = st.columns(2)

    with left:

        risk_dept = (
            filtered.groupby(
                ["Department", "BurnoutRisk"]
            )
            .size()
            .reset_index(name="Employees")
        )

        fig = px.bar(
            risk_dept,
            x="Department",
            y="Employees",
            color="BurnoutRisk",
            barmode="stack",
            title="Burnout Risk by Department",
            color_discrete_map={
                "Low": "#38a169",
                "Medium": "#e6a23c",
                "High": "#d9534f"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        fig = px.box(
            filtered,
            x="OverTime",
            y="EngagementIndex",
            color="OverTime",
            title="Overtime vs Engagement"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    travel_data = (
        filtered.groupby("BusinessTravel")
        ["EngagementIndex"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        travel_data,
        x="BusinessTravel",
        y="EngagementIndex",
        title="Business Travel vs Engagement"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.scatter(
        filtered,
        x="DistanceFromHome",
        y="EngagementIndex",
        color="OverTime",
        title="Distance From Home vs Engagement",
        hover_data=["Department", "JobRole"]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# TAB 3: ROLE & CAREER ANALYSIS
# =====================================================

with tab3:

    st.header("Role & Career Stage Analysis")

    left, right = st.columns(2)

    with left:

        role_data = (
            filtered.groupby("JobRole")
            ["EngagementIndex"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            role_data,
            x="EngagementIndex",
            y="JobRole",
            orientation="h",
            title="Engagement by Job Role"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        level_data = (
            filtered.groupby("JobLevel")
            ["EngagementIndex"]
            .mean()
            .reset_index()
        )

        fig = px.line(
            level_data,
            x="JobLevel",
            y="EngagementIndex",
            markers=True,
            title="Engagement by Job Level"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    tenure_data = (
        filtered.groupby("YearsAtCompany")
        ["EngagementIndex"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        tenure_data,
        x="YearsAtCompany",
        y="EngagementIndex",
        markers=True,
        title="Tenure vs Engagement"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    promotion_data = (
        filtered.groupby("YearsSinceLastPromotion")
        ["EngagementIndex"]
        .mean()
        .reset_index()
    )

    fig = px.scatter(
        promotion_data,
        x="YearsSinceLastPromotion",
        y="EngagementIndex",
        title="Promotion Gap vs Engagement"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# TAB 4: MANAGER ACTION PANEL
# =====================================================

with tab4:

    st.header("Manager Action Panel")

    priority = (
        filtered.groupby("Department")
        .agg(
            Employees=("EngagementIndex", "size"),

            AverageEngagement=(
                "EngagementIndex",
                "mean"
            ),

            HighRisk=(
                "BurnoutRisk",
                lambda x: (x == "High").sum()
            ),

            OvertimeShare=(
                "OverTime",
                lambda x: (x == "Yes").mean() * 100
            ),

            AverageWLB=(
                "WorkLifeBalance",
                "mean"
            )
        )
        .reset_index()
    )

    priority["HighRiskShare"] = (
        priority["HighRisk"]
        / priority["Employees"]
        * 100
    )

    priority = priority.sort_values(
        "HighRiskShare",
        ascending=False
    )

    st.subheader("Department Priority Analysis")

    st.dataframe(
        priority.style.format({
            "AverageEngagement": "{:.2f}",
            "OvertimeShare": "{:.1f}%",
            "AverageWLB": "{:.2f}",
            "HighRiskShare": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Suggested HR Interventions")

    if (filtered["OverTime"] == "Yes").mean() > 0.25:

        st.warning(
            "Review workload distribution, staffing "
            "and overtime frequency."
        )

    if (filtered["WorkLifeBalance"] <= 2).mean() > 0.20:

        st.warning(
            "Review work-life balance, flexible working "
            "and employee recovery time."
        )

    if filtered["EngagementIndex"].mean() < 60:

        st.warning(
            "Conduct employee feedback sessions to "
            "understand engagement gaps."
        )

    if (
        filtered["YearsSinceLastPromotion"] >= 4
    ).mean() > 0.20:

        st.warning(
            "Review career development opportunities "
            "and promotion pathways."
        )

    review = filtered[
        (filtered["EngagementIndex"] < 50)
        | (filtered["BurnoutRisk"] == "High")
    ].copy()

    review.insert(
        0,
        "Dataset Row Reference",
        review.index + 1
    )

    review_columns = [
        "Dataset Row Reference",
        "Department",
        "JobRole",
        "EngagementIndex",
        "BurnoutRisk",
        "OverTime",
        "WorkLifeBalance",
        "YearsAtCompany"
    ]

    st.subheader("HR Review Records")

    st.dataframe(
        review[review_columns],
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download HR Review CSV",
        review[review_columns].to_csv(index=False),
        file_name="hr_review_records.csv",
        mime="text/csv"
    )


# =====================================================
# TAB 5: DATA & METHODOLOGY
# =====================================================

with tab5:

    st.header("Data Validation & Methodology")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Rows",
            validation["rows"]
        )

    with col2:

        st.metric(
            "Total Columns",
            validation["columns"]
        )

    with col3:

        st.metric(
            "Missing Values",
            validation["missing_cells"]
        )

    with col4:

        st.metric(
            "Duplicate Records",
            validation["duplicate_rows"]
        )

    st.divider()

    st.subheader("Engagement Index")

    st.write("""
    Engagement Index is calculated using four dimensions:

    1. Job Involvement
    2. Job Satisfaction
    3. Environment Satisfaction
    4. Relationship Satisfaction

    Each rating is normalized from 1–4 to 0–100.

    Formula:

    Normalized Score = ((Rating - 1) / 3) × 100

    Engagement Index = Average of all four normalized scores.
    """)

    st.subheader("Burnout Risk Classification")

    st.write("""
    High Risk:
    Overtime = Yes AND WorkLifeBalance <= 2

    Medium Risk:
    Only one of the above conditions is true.

    Low Risk:
    Neither condition is true.
    """)

    st.subheader("Workload Stress Indicator")

    st.write("""
    One point is assigned for each condition:

    - Overtime = Yes
    - BusinessTravel = Travel_Frequently
    - DistanceFromHome >= 15

    Total score ranges from 0 to 3.
    """)

    st.subheader("Research Limitations")

    st.write("""
    - Dataset is cross-sectional.
    - It cannot establish that burnout causes attrition.
    - It does not contain medical or health information.
    - Risk categories are analytical screening indicators,
      not clinical diagnoses.
    - Dataset provenance must be verified before claiming
      that these are actual Palo Alto Networks employee records.
    """)

    st.subheader("Dataset Preview")

    st.dataframe(
        raw_df.head(20),
        use_container_width=True
    )

    st.download_button(
        "Download Filtered Analytics Dataset",
        filtered.to_csv(index=False),
        file_name="employee_analytics.csv",
        mime="text/csv"
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "Employee Engagement & Burnout Risk Analytics | "
    "Preventive HR Diagnostics"
)
