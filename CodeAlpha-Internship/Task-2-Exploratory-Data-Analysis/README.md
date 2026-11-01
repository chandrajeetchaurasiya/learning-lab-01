# Task 2: Exploratory Data Analysis – Titanic Passengers

**CodeAlpha Data Analytics Internship** | Student: Chandrajeet Chaurasiya | ID: CA/DF1/317087

## Project objective
Explore a real dataset, check its quality, clean it, test hypotheses and report evidence-based insights.

## Problem statement
Which passenger characteristics are associated with survival on the Titanic, and what data problems must be handled before analysis?

## Tools and technologies
Python 3.12/3.13, Pandas, NumPy, SciPy (statistical tests), Matplotlib, Seaborn, Tabulate.

## Dataset description
**Real public dataset**: Titanic passengers (891 rows, 15 columns) from the `seaborn-data` GitHub repository (https://github.com/mwaskom/seaborn-data). Saved as `data/titanic_original.csv`; downloaded automatically if missing. This is *not* generated data. Columns include survived, pclass, sex, age, sibsp, parch, fare, embarked, deck, embark_town, alone.

> Note: this is not the scraped Books data from Task 1 (that scraper could not be run live where this was built). Tasks 2 and 3 share the same Titanic dataset for consistency.

## Methodology
1. Ask questions (sex, class, fare, age, data quality).
2. Inspect structure, types, missing values, duplicates, outliers.
3. Clean: impute age by class+sex median (with a flag column), fill 2 embarkation values, label unknown decks, add family_size / age_group.
4. Statistical summaries and survival tables.
5. Hypothesis tests: chi-square (sex, class), Mann-Whitney (fare), Welch t-test (age).
6. Spearman correlations and four diagnostic charts.

## Project structure
```
Task_2_Exploratory_Data_Analysis/
├── eda_analysis.py
├── requirements.txt
├── README.md
├── data/    titanic_original.csv, titanic_cleaned.csv
└── output/  EDA_report.md, summary CSVs, 4 PNG charts
```

## How to run (VS Code terminal, Windows PowerShell)
```powershell
cd Task_2_Exploratory_Data_Analysis
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python eda_analysis.py
```

## Results (all computed by the script; full detail in `output/EDA_report.md`)
- Overall survival 38.4% (342 of 891).
- Women 74.2% vs men 18.9% (chi-square p ≈ 1e-58).
- 1st class 63.0%, 2nd 47.3%, 3rd 24.2% (p ≈ 5e-23).
- Median fare: survivors 26.00 vs non-survivors 10.50 (p ≈ 5e-22).
- Age: means 28.3 vs 30.6, p = 0.041, a statistically significant but small difference.
- Data issues: 688 missing decks, 177 missing ages, 107 exact-duplicate rows, 116 high-fare outliers.

## Key decisions
- **Duplicates were reported, not deleted.** There is no passenger ID, so identical rows may be different people.
- Outliers were flagged, not removed (they are real expensive tickets).

## Conclusion
Sex and passenger class have the strongest association with survival; age is weak. Associations do not prove causes, and the age-based results are affected by 177 estimated ages.

## Testing status
✅ Syntax check passed and the script was executed end to end; all outputs listed above were generated (Python 3.12, pandas 3.0, seaborn 0.13). Not run on Python 3.13 or on Windows itself; the code uses `pathlib` so paths should work on Windows.
