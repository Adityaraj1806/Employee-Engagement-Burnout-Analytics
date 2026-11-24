from pathlib import Path
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "Attrition", "BusinessTravel", "Department", "DistanceFromHome",
    "EnvironmentSatisfaction", "JobInvolvement", "JobLevel", "JobRole",
    "JobSatisfaction", "OverTime", "RelationshipSatisfaction",
    "WorkLifeBalance", "YearsAtCompany", "YearsSinceLastPromotion",
]

ENGAGEMENT_COLUMNS = [
    "JobInvolvement", "JobSatisfaction",
    "EnvironmentSatisfaction", "RelationshipSatisfaction",
]

def load_and_validate_data(source):
    """Load CSV and validate the columns required by the dashboard."""
    df = pd.read_csv(source)
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError("Dataset is missing required columns: " + ", ".join(missing_cols))

    validation = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "required_columns_present": True,
    }

    for col in ENGAGEMENT_COLUMNS + ["WorkLifeBalance"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        invalid = ~df[col].between(1, 4)
        if invalid.any():
            raise ValueError(f"{col} contains values outside the expected 1–4 scale.")

    if not set(df["OverTime"].dropna().unique()).issubset({"Yes", "No"}):
        raise ValueError("OverTime must contain only Yes/No values.")
    return df, validation

def add_analytics_features(df):
    """Add transparent, rule-based employee experience indicators."""
    result = df.copy()

    normalized = result[ENGAGEMENT_COLUMNS].apply(lambda s: (s - 1) / 3 * 100)
    result["EngagementIndex"] = normalized.mean(axis=1).round(2)

    overtime = result["OverTime"].eq("Yes")
    low_wlb = result["WorkLifeBalance"].le(2)
    result["BurnoutRisk"] = np.select(
        [overtime & low_wlb, overtime | low_wlb],
        ["High", "Medium"],
        default="Low",
    )

    frequent_travel = result["BusinessTravel"].eq("Travel_Frequently")
    long_commute = result["DistanceFromHome"].ge(15)
    result["WorkloadStressIndicator"] = (
        overtime.astype(int) + frequent_travel.astype(int) + long_commute.astype(int)
    )

    dispersion = normalized.std(axis=1, ddof=0)
    result["SatisfactionStabilityScore"] = (100 - dispersion).clip(0, 100).round(2)
    result["WorkLifeBalanceIndex"] = ((result["WorkLifeBalance"] - 1) / 3 * 100).round(2)
    return result

def summarize_metrics(df):
    if df.empty:
        return {"engagement": 0, "wlb": 0, "high_risk_pct": 0}
    return {
        "engagement": float(df["EngagementIndex"].mean()),
        "wlb": float(df["WorkLifeBalance"].mean()),
        "high_risk_pct": float((df["BurnoutRisk"] == "High").mean() * 100),
    }
