from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from analysis import load_and_validate_data, add_analytics_features

ROOT = Path(__file__).parent
df, validation = load_and_validate_data(ROOT / "data" / "Palo Alto Networks.csv")
df = add_analytics_features(df)
out = ROOT / "outputs"
out.mkdir(exist_ok=True)

print("DATA VALIDATION")
for key, value in validation.items():
    print(f"{key}: {value}")

print("\nENGAGEMENT SUMMARY")
print(df["EngagementIndex"].describe().round(2))
print("\nBURNOUT RISK COUNTS")
print(df["BurnoutRisk"].value_counts())
print("\nENGAGEMENT BY DEPARTMENT")
print(df.groupby("Department")["EngagementIndex"].agg(["count", "mean"]).round(2))
print("\nATTRITION CONTEXT")
print(df.groupby("Attrition")["EngagementIndex"].agg(["count", "mean"]).round(2))

df.to_csv(out / "employee_analytics_enriched.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 5))
df.groupby("Department")["EngagementIndex"].mean().sort_values().plot(kind="bar", ax=ax)
ax.set_title("Average Engagement Index by Department")
ax.set_ylabel("Engagement Index (0–100)")
ax.set_xlabel("Department")
fig.tight_layout()
fig.savefig(out / "engagement_by_department.png", dpi=160)
print(f"\nOutputs saved in: {out}")
