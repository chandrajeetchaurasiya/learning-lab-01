"""
Task 3: Data Visualization - Titanic passengers
CodeAlpha Data Analytics Internship | Student ID: CA/DF1/317087

Input : data/titanic_cleaned.csv  (cleaned in Task 2 from a real public dataset,
        seaborn-data repository; 891 passengers)
Output: charts (PNG) and visualization_insights.md in output/

Run (PowerShell):  python visualize_data.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # save to files instead of opening windows
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "titanic_cleaned.csv"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.0)
COLORS = {0: "#d9534f", 1: "#5cb85c"}  # red = did not survive, green = survived
LABELS = {0: "Did not survive", 1: "Survived"}

if not DATA_FILE.exists():
    raise SystemExit(f"Missing {DATA_FILE}. Run Task 2 first or copy titanic_cleaned.csv here.")
df = pd.read_csv(DATA_FILE)
df["Outcome"] = df["survived"].map(LABELS)
df["age_group"] = pd.Categorical(
    df["age_group"],
    categories=["Child (0-12)", "Teen (13-18)", "Young adult (19-35)", "Adult (36-60)", "Senior (60+)"],
    ordered=True)
df["Class"] = df["pclass"].map({1: "1st", 2: "2nd", 3: "3rd"})
df["Sex"] = df["sex"].str.capitalize()


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / name, dpi=150)
    plt.close(fig)
    print("Saved", name)


def label_bars(ax, fmt="{:.1f}%"):
    for bar in ax.patches:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 1, fmt.format(h), ha="center", fontsize=9)


# 01 Overall outcome ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(5.5, 4.5))
counts = df["Outcome"].value_counts().reindex(["Did not survive", "Survived"])
ax.bar(counts.index, counts.values, color=[COLORS[0], COLORS[1]])
for i, v in enumerate(counts.values):
    ax.text(i, v + 8, f"{v} ({v / len(df) * 100:.1f}%)", ha="center")
ax.set_title("Overall Survival on the Titanic")
ax.set_ylabel("Passengers")
save(fig, "01_overall_survival.png")

# 02 Survival rate by sex ---------------------------------------------------
rate_sex = df.groupby("Sex")["survived"].mean().mul(100)
fig, ax = plt.subplots(figsize=(5.5, 4.5))
sns.barplot(x=rate_sex.index, y=rate_sex.values, hue=rate_sex.index, palette=["#e377c2", "#1f77b4"], legend=False, ax=ax)
ax.set_title("Survival Rate by Sex")
ax.set_ylabel("Survival rate (%)")
ax.set_xlabel("")
ax.set_ylim(0, 100)
label_bars(ax)
save(fig, "02_survival_by_sex.png")

# 03 Survival rate by class --------------------------------------------------
rate_cls = df.groupby("Class")["survived"].mean().mul(100)
fig, ax = plt.subplots(figsize=(5.5, 4.5))
sns.barplot(x=rate_cls.index, y=rate_cls.values, hue=rate_cls.index, palette="Blues_r", legend=False, ax=ax)
ax.set_title("Survival Rate by Passenger Class")
ax.set_ylabel("Survival rate (%)")
ax.set_xlabel("Class")
ax.set_ylim(0, 100)
label_bars(ax)
save(fig, "03_survival_by_class.png")

# 04 Class x Sex heatmap -----------------------------------------------------
pivot = df.pivot_table(index="Sex", columns="Class", values="survived", aggfunc="mean").mul(100)
fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn", vmin=0, vmax=100,
            cbar_kws={"label": "Survival rate (%)"}, ax=ax)
ax.set_title("Survival Rate (%) by Class and Sex")
save(fig, "04_survival_class_sex_heatmap.png")

# 05 Age distribution by outcome ---------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.histplot(data=df, x="age", hue="Outcome", bins=30, kde=True, multiple="layer",
             palette={"Did not survive": COLORS[0], "Survived": COLORS[1]}, alpha=0.45, ax=ax)
ax.set_title("Age Distribution by Survival Outcome")
ax.set_xlabel("Age (years; some missing ages were estimated in Task 2)")
save(fig, "05_age_distribution.png")

# 06 Survival rate by age group -----------------------------------------------
rate_age = df.groupby("age_group", observed=True)["survived"].mean().mul(100)
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.barplot(x=rate_age.index.astype(str), y=rate_age.values, hue=rate_age.index.astype(str),
            palette="viridis", legend=False, ax=ax)
ax.set_title("Survival Rate by Age Group")
ax.set_ylabel("Survival rate (%)")
ax.set_xlabel("")
ax.set_ylim(0, 100)
label_bars(ax)
plt.setp(ax.get_xticklabels(), rotation=15)
save(fig, "06_survival_by_age_group.png")

# 07 Fare by class and outcome (boxplot) ----------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.8))
sns.boxplot(data=df, x="Class", y="fare", hue="Outcome", order=["1st", "2nd", "3rd"],
            palette={"Did not survive": COLORS[0], "Survived": COLORS[1]}, ax=ax)
ax.set_yscale("log")  # fares are heavily skewed; log scale keeps boxes readable
ax.set_title("Ticket Fare by Class and Outcome (log scale)")
ax.set_ylabel("Fare (log scale; zero fares not shown)")
save(fig, "07_fare_by_class_outcome.png")

# 08 Family size ----------------------------------------------------------------
fam = df.groupby("family_size")["survived"].agg(["mean", "count"])
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(fam.index.astype(str), fam["mean"] * 100, color="#4c72b0")
for i, (rate, n) in enumerate(zip(fam["mean"] * 100, fam["count"])):
    ax.text(i, rate + 1.5, f"n={n}", ha="center", fontsize=8)
ax.set_title("Survival Rate by Family Size (n = number of passengers)")
ax.set_xlabel("Family size (including the passenger)")
ax.set_ylabel("Survival rate (%)")
ax.set_ylim(0, 100)
save(fig, "08_survival_by_family_size.png")

# 09 Embarkation port -----------------------------------------------------------
port = df.groupby("embark_town")["survived"].mean().mul(100).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6, 4.5))
sns.barplot(x=port.index, y=port.values, hue=port.index, palette="Set2", legend=False, ax=ax)
ax.set_title("Survival Rate by Port of Embarkation")
ax.set_ylabel("Survival rate (%)")
ax.set_xlabel("")
ax.set_ylim(0, 100)
label_bars(ax)
save(fig, "09_survival_by_port.png")

# 10 Dashboard --------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
sns.barplot(x=rate_sex.index, y=rate_sex.values, hue=rate_sex.index, palette=["#e377c2", "#1f77b4"],
            legend=False, ax=axes[0, 0])
axes[0, 0].set(title="Survival Rate by Sex", ylabel="%", xlabel="", ylim=(0, 100))
sns.barplot(x=rate_cls.index, y=rate_cls.values, hue=rate_cls.index, palette="Blues_r", legend=False, ax=axes[0, 1])
axes[0, 1].set(title="Survival Rate by Class", ylabel="%", xlabel="", ylim=(0, 100))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn", vmin=0, vmax=100, cbar=False, ax=axes[1, 0])
axes[1, 0].set_title("Survival Rate (%) by Class and Sex")
sns.barplot(x=rate_age.index.astype(str), y=rate_age.values, hue=rate_age.index.astype(str),
            palette="viridis", legend=False, ax=axes[1, 1])
axes[1, 1].set(title="Survival Rate by Age Group", ylabel="%", xlabel="", ylim=(0, 100))
plt.setp(axes[1, 1].get_xticklabels(), rotation=20, fontsize=8)
for a in (axes[0, 0], axes[0, 1], axes[1, 1]):
    label_bars(a)
fig.suptitle("Titanic Survival Dashboard", fontsize=16, fontweight="bold")
save(fig, "10_dashboard.png")

# ------------------------------------------------------------------ insights report
cls_sex = pivot.round(1)
best_age = rate_age.idxmax()
worst_age = rate_age.idxmin()
big_fam = df[df["family_size"] >= 5]
small_fam = df[df["family_size"].between(2, 4)]
alone = df[df["family_size"] == 1]

lines = [
    "# Visualization Insights Report",
    "",
    "Data: Titanic passengers (real public dataset, 891 rows), cleaned in Task 2. All numbers are computed by `visualize_data.py`.",
    "",
    "| Chart | What it shows | Insight (computed from data) |",
    "|---|---|---|",
    f"| 01_overall_survival | Survived vs not | {df['survived'].sum()} of {len(df)} passengers survived ({df['survived'].mean() * 100:.1f}%). |",
    f"| 02_survival_by_sex | Survival rate by sex | Women {rate_sex['Female']:.1f}% vs men {rate_sex['Male']:.1f}%. |",
    f"| 03_survival_by_class | Survival rate by class | 1st {rate_cls['1st']:.1f}%, 2nd {rate_cls['2nd']:.1f}%, 3rd {rate_cls['3rd']:.1f}%. |",
    f"| 04_class_sex_heatmap | Class and sex together | Females: 1st {cls_sex.loc['Female', '1st']}%, 2nd {cls_sex.loc['Female', '2nd']}%, 3rd {cls_sex.loc['Female', '3rd']}%. "
    f"Males: 1st {cls_sex.loc['Male', '1st']}%, 2nd {cls_sex.loc['Male', '2nd']}%, 3rd {cls_sex.loc['Male', '3rd']}%. |",
    f"| 05_age_distribution | Age histogram by outcome | Median age: survivors {df[df.survived == 1]['age'].median():.1f}, non-survivors {df[df.survived == 0]['age'].median():.1f}. Both groups are concentrated in the 20s-30s. |",
    f"| 06_survival_by_age_group | Survival by age band | Highest: {best_age} ({rate_age[best_age]:.1f}%). Lowest: {worst_age} ({rate_age[worst_age]:.1f}%). |",
    f"| 07_fare_by_class_outcome | Fare spread (log scale) | Median fare of survivors {df[df.survived == 1]['fare'].median():.2f} vs non-survivors {df[df.survived == 0]['fare'].median():.2f}. |",
    f"| 08_survival_by_family_size | Survival by family size | Alone: {alone['survived'].mean() * 100:.1f}% (n={len(alone)}). Family of 2-4: {small_fam['survived'].mean() * 100:.1f}% (n={len(small_fam)}). Family of 5+: {big_fam['survived'].mean() * 100:.1f}% (n={len(big_fam)}). |",
    f"| 09_survival_by_port | Survival by port | " + ", ".join(f"{k} {v:.1f}%" for k, v in port.items()) + ". |",
    "| 10_dashboard | Four key charts together | One-page summary for presentations. |",
    "",
    "## Reading the charts carefully",
    "- Sex and class together tell a clearer story than either alone (see the heatmap).",
    "- Port of embarkation is likely linked to class mix, so it should not be read as a direct cause.",
    "- Family-size groups above 4 are small; treat those percentages with caution (counts are printed on chart 08).",
    f"- {int(df['age_was_missing'].sum())} ages were estimated in Task 2, which slightly affects charts 05 and 06.",
    "- These charts show associations in historical data, not proof of cause.",
]
(OUTPUT_DIR / "visualization_insights.md").write_text("\n".join(lines), encoding="utf-8")
print("Saved visualization_insights.md\nDone.")
