"""
Task 2: Exploratory Data Analysis (EDA) - Titanic passenger dataset
CodeAlpha Data Analytics Internship | Student ID: CA/DF1/317087

Dataset: Titanic passengers (891 rows), a real public dataset distributed with the
seaborn-data repository: https://github.com/mwaskom/seaborn-data
Saved locally as data/titanic_original.csv (downloaded automatically if missing).

Run (PowerShell):  python eda_analysis.py
Everything written to the report is computed from the data by this script.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # save charts to files, no pop-up windows
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"
ORIGINAL_CSV = DATA_DIR / "titanic_original.csv"
CLEAN_CSV = DATA_DIR / "titanic_cleaned.csv"
URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"

sns.set_theme(style="whitegrid")
report = []  # lines of the Markdown report


def add(text=""):
    report.append(text)


def table(df):
    """Convert a DataFrame to a Markdown table."""
    return df.to_markdown() if hasattr(df, "to_markdown") else df.to_string()


# ---------------------------------------------------------------- 1. LOAD
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
if not ORIGINAL_CSV.exists():
    print("Downloading dataset...")
    pd.read_csv(URL).to_csv(ORIGINAL_CSV, index=False)
raw = pd.read_csv(ORIGINAL_CSV)
df = raw.copy()

add("# EDA Report: Titanic Passenger Dataset")
add()
add("Source: real public dataset (seaborn-data repository). Every number below is computed by `eda_analysis.py`.")
add()
add("## 1. Questions we want to answer")
add("1. Did survival differ between men and women?")
add("2. Did passenger class (1st/2nd/3rd) affect survival?")
add("3. Did survivors pay different fares than non-survivors?")
add("4. Did survivors differ in age from non-survivors?")
add("5. Which columns have data-quality problems?")
add()

# ---------------------------------------------------------------- 2. STRUCTURE
add("## 2. Dataset structure")
add(f"- Rows: **{raw.shape[0]}**, columns: **{raw.shape[1]}**")
add()
info = pd.DataFrame({"dtype": raw.dtypes.astype(str), "non_null": raw.notna().sum(),
                     "missing": raw.isna().sum(), "missing_%": (raw.isna().mean() * 100).round(1),
                     "unique": raw.nunique()})
info.to_csv(OUTPUT_DIR / "column_overview.csv")
add(table(info))
add()

# ---------------------------------------------------------------- 3. DATA QUALITY
add("## 3. Data quality checks")
n_dup = int(raw.duplicated().sum())
add(f"- **Exact duplicate rows:** {n_dup}. The dataset has no passenger ID, so identical rows "
    "(e.g. two 3rd-class men, same age and fare) can be different real people. "
    "**Decision: duplicates are reported but NOT deleted.** Deleting them could remove real passengers.")
add(f"- **Missing `age`:** {int(raw['age'].isna().sum())} ({raw['age'].isna().mean() * 100:.1f}%)")
add(f"- **Missing `deck`:** {int(raw['deck'].isna().sum())} ({raw['deck'].isna().mean() * 100:.1f}%) - too many to fill with guesses")
add(f"- **Missing `embarked`/`embark_town`:** {int(raw['embarked'].isna().sum())} each")
zero_fare = int((raw["fare"] == 0).sum())
add(f"- **Fare = 0:** {zero_fare} rows (kept; may be crew/free tickets but this is not stated in the data)")
q1, q3 = raw["fare"].quantile([0.25, 0.75])
iqr = q3 - q1
fare_upper = q3 + 1.5 * iqr
n_fare_out = int((raw["fare"] > fare_upper).sum())
add(f"- **Fare outliers (IQR rule, > {fare_upper:.2f}):** {n_fare_out} rows. These are real expensive tickets, so they are flagged, not removed.")
add()

# ---------------------------------------------------------------- 4. CLEANING
add("## 4. Cleaning steps applied")
df["age_was_missing"] = df["age"].isna()
age_median = df.groupby(["pclass", "sex"])["age"].transform("median")
df["age"] = df["age"].fillna(age_median)
add("- `age`: filled missing values with the **median age of the same class and sex** (flag column `age_was_missing` keeps track of which were filled).")
mode_town = df["embark_town"].mode()[0]
df["embark_town"] = df["embark_town"].fillna(mode_town)
df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])
add(f"- `embark_town`/`embarked`: filled {int(raw['embarked'].isna().sum())} missing values with the most common value (**{mode_town}**).")
df["deck"] = df["deck"].astype(object).fillna("Unknown")
add("- `deck`: missing values labelled `Unknown` (not guessed).")
df["family_size"] = df["sibsp"] + df["parch"] + 1
df["age_group"] = pd.cut(df["age"], bins=[0, 12, 18, 35, 60, 120],
                         labels=["Child (0-12)", "Teen (13-18)", "Young adult (19-35)", "Adult (36-60)", "Senior (60+)"])
df["fare_outlier"] = df["fare"] > fare_upper
add("- Added new columns: `family_size` (sibsp + parch + 1), `age_group`, `fare_outlier`.")
df = df.drop(columns=["alive", "class"])
add("- Dropped `alive` (same information as `survived`) and `class` (same information as `pclass`).")
df.to_csv(CLEAN_CSV, index=False)
add(f"- Cleaned dataset saved: `data/titanic_cleaned.csv` ({df.shape[0]} rows, {df.shape[1]} columns). Remaining missing values: {int(df.isna().sum().sum())}.")
add()

# ---------------------------------------------------------------- 5. STATISTICS
add("## 5. Statistical summaries")
num_summary = df[["age", "fare", "sibsp", "parch", "family_size"]].describe().round(2)
num_summary.to_csv(OUTPUT_DIR / "numeric_summary.csv")
add("### Numeric columns (cleaned data)")
add(table(num_summary))
add()
add(f"Skewness of `fare` = {df['fare'].skew():.2f}, skewness of `age` = {df['age'].skew():.2f}. "
    "A skewness well above 0 means a long right tail (a few very high values).")
add()

overall = df["survived"].mean() * 100
add(f"**Overall survival rate: {overall:.1f}%** ({int(df['survived'].sum())} of {len(df)} passengers).")
add()
surv_tables = {}
for col in ["sex", "pclass", "embark_town", "age_group", "family_size"]:
    t = df.groupby(col, observed=True)["survived"].agg(passengers="count", survivors="sum", survival_rate="mean")
    t["survival_rate"] = (t["survival_rate"] * 100).round(1)
    surv_tables[col] = t
    t.to_csv(OUTPUT_DIR / f"survival_by_{col}.csv")
    add(f"### Survival rate (%) by `{col}`")
    add(table(t))
    add()

# ---------------------------------------------------------------- 6. HYPOTHESIS TESTS
add("## 6. Hypothesis tests (significance level 0.05)")
tests = []

# H1: sex vs survival (chi-square)
ct = pd.crosstab(df["sex"], df["survived"])
chi2, p, _, _ = stats.chi2_contingency(ct)
tests.append(("H1: survival depends on sex", "Chi-square", p))
# H2: class vs survival (chi-square)
ct2 = pd.crosstab(df["pclass"], df["survived"])
chi2b, p2, _, _ = stats.chi2_contingency(ct2)
tests.append(("H2: survival depends on class", "Chi-square", p2))
# H3: fare survivors vs non-survivors (Mann-Whitney, fare is skewed)
f_surv = df.loc[df["survived"] == 1, "fare"]
f_dead = df.loc[df["survived"] == 0, "fare"]
u3, p3 = stats.mannwhitneyu(f_surv, f_dead)
tests.append(("H3: fares differ between survivors and non-survivors", "Mann-Whitney U", p3))
# H4: age, using ONLY passengers with a real (not imputed) age
real_age = df[~df["age_was_missing"]]
a_surv = real_age.loc[real_age["survived"] == 1, "age"]
a_dead = real_age.loc[real_age["survived"] == 0, "age"]
t4, p4 = stats.ttest_ind(a_surv, a_dead, equal_var=False)
tests.append(("H4: mean age differs between survivors and non-survivors (real ages only)", "Welch t-test", p4))

test_df = pd.DataFrame(tests, columns=["hypothesis", "test", "p_value"])
test_df["conclusion"] = np.where(test_df["p_value"] < 0.05, "Significant difference", "No significant difference")
test_df["p_value"] = test_df["p_value"].apply(lambda x: f"{x:.2e}")
test_df.to_csv(OUTPUT_DIR / "hypothesis_tests.csv", index=False)
add(table(test_df.set_index("hypothesis")))
add()
add(f"Mean age of survivors = {a_surv.mean():.1f} vs non-survivors = {a_dead.mean():.1f} (real ages only, n = {len(real_age)}). "
    f"Median fare of survivors = {f_surv.median():.2f} vs non-survivors = {f_dead.median():.2f}.")
add()
add("*Note: a significant p-value shows an association in this data. It does not prove one factor caused another.*")
add()

# ---------------------------------------------------------------- 7. CORRELATION
corr = df[["survived", "pclass", "age", "fare", "sibsp", "parch", "family_size"]].corr(method="spearman").round(2)
corr.to_csv(OUTPUT_DIR / "correlation_spearman.csv")
pairs = corr["survived"].drop("survived").sort_values(key=abs, ascending=False)
add("## 7. Correlation with survival (Spearman)")
add(table(pairs.to_frame("correlation_with_survived")))
add()

# ---------------------------------------------------------------- 8. CHARTS
fig, ax = plt.subplots(figsize=(8, 4.5))
miss = raw.isna().mean().mul(100).sort_values(ascending=False)
miss = miss[miss > 0]
sns.barplot(x=miss.values, y=miss.index, ax=ax, color="#d9534f")
ax.set_title("Missing Values per Column (original data)")
ax.set_xlabel("% missing")
for i, v in enumerate(miss.values):
    ax.text(v + 0.5, i, f"{v:.1f}%", va="center")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "eda_missing_values.png", dpi=150)
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
sns.histplot(df["age"], bins=30, kde=True, ax=axes[0], color="#4c72b0")
axes[0].set_title("Age Distribution (cleaned)")
sns.histplot(df["fare"], bins=40, ax=axes[1], color="#55a868")
axes[1].set_title("Fare Distribution (right-skewed)")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "eda_distributions.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 5.5))
sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax)
ax.set_title("Spearman Correlation Matrix")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "eda_correlation.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 4.5))
sns.boxplot(data=df, x="pclass", y="fare", ax=ax, color="#8172b2")
ax.set_title("Fare by Class (outliers visible as dots)")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "eda_fare_outliers.png", dpi=150)
plt.close(fig)

add("## 8. Charts generated")
add("`eda_missing_values.png`, `eda_distributions.png`, `eda_correlation.png`, `eda_fare_outliers.png` (in `output/`).")
add()

# ---------------------------------------------------------------- 9. FINDINGS (computed)
sex_t, cls_t = surv_tables["sex"], surv_tables["pclass"]
add("## 9. Key findings (generated from the data)")
add(f"1. Overall survival was {overall:.1f}%.")
add(f"2. Women survived at {sex_t.loc['female', 'survival_rate']}% versus {sex_t.loc['male', 'survival_rate']}% for men "
    f"(chi-square p = {p:.2e}).")
add(f"3. Survival fell with class: 1st {cls_t.loc[1, 'survival_rate']}%, 2nd {cls_t.loc[2, 'survival_rate']}%, "
    f"3rd {cls_t.loc[3, 'survival_rate']}% (chi-square p = {p2:.2e}).")
add(f"4. Survivors paid a higher median fare ({f_surv.median():.2f} vs {f_dead.median():.2f}); Mann-Whitney p = {p3:.2e}.")
add(f"5. Age: survivor mean {a_surv.mean():.1f} vs non-survivor mean {a_dead.mean():.1f}; Welch t-test p = {p4:.3f} "
    f"({'significant' if p4 < 0.05 else 'not significant'} at 0.05), but the gap is only "
    f"{abs(a_dead.mean() - a_surv.mean()):.1f} years, so age is a weak factor compared with sex and class.")
add(f"6. Data issues: {int(raw['deck'].isna().sum())} missing decks, {int(raw['age'].isna().sum())} missing ages, "
    f"{n_dup} duplicate-looking rows, {n_fare_out} high-fare outliers.")
add()
add("## 10. Limitations")
add("- Imputed ages are estimates; H4 therefore uses real ages only.")
add("- Class, sex and fare are related to each other, so these tests look at one factor at a time.")
add("- This is an observational historical dataset: associations, not causes.")

(OUTPUT_DIR / "EDA_report.md").write_text("\n".join(report), encoding="utf-8")
print("EDA finished.")
print(f"  Cleaned data : {CLEAN_CSV}")
print(f"  Report       : {OUTPUT_DIR / 'EDA_report.md'}")
