# Task 3: Data Visualization – Titanic Passengers

**CodeAlpha Data Analytics Internship** | Student: Chandrajeet Chaurasiya | ID: CA/DF1/317087

## Project objective
Turn the cleaned Titanic data into clear, professional charts that explain who survived and why patterns matter.

## Problem statement
Tables of numbers are hard to read. Which visuals best communicate the survival patterns found in Task 2?

## Tools and technologies
Python 3.12/3.13, Matplotlib, Seaborn, Pandas.

## Dataset description
`data/titanic_cleaned.csv`: 891 passengers, produced in Task 2 from a **real public dataset** (seaborn-data repository). It is a copy of Task 2's output so this project runs on its own.

## Methodology
Ten charts, each answering one question, with readable titles, labelled axes and value labels. A log scale is used for the skewed fare data. Insights are generated from the data, not typed by hand.

## Project structure
```
Task_3_Data_Visualization/
├── visualize_data.py
├── requirements.txt
├── README.md
├── data/    titanic_cleaned.csv
└── output/  10 PNG charts + visualization_insights.md
```

## How to run (VS Code terminal, Windows PowerShell)
```powershell
cd Task_3_Data_Visualization
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python visualize_data.py
```

## Charts
| File | Purpose |
|---|---|
| 01_overall_survival | Survived vs not |
| 02_survival_by_sex | Gap between men and women |
| 03_survival_by_class | Effect of class |
| 04_survival_class_sex_heatmap | Class and sex combined |
| 05_age_distribution | Age by outcome |
| 06_survival_by_age_group | Children vs adults |
| 07_fare_by_class_outcome | Fare spread (log scale) |
| 08_survival_by_family_size | Alone vs families |
| 09_survival_by_port | Embarkation port |
| 10_dashboard | One-page summary |

## Key findings (full table in `output/visualization_insights.md`)
- Women 74.2% vs men 18.9% survival.
- 1st class 63.0% vs 3rd class 24.2%.
- Female passengers in 1st/2nd class survived at 96.8% / 92.1%; 3rd-class males at 13.5%.
- Children (0-12) had the highest age-group survival (58.0%); seniors the lowest (22.7%).
- Families of 2-4 survived more (57.9%) than people alone (30.4%) or families of 5+ (16.1%, small group).

## Conclusion
Sex and class explain most of the visible pattern, and the heatmap shows they act together. Charts show associations, not causes.

## Testing status
✅ Syntax check passed; script executed end to end and produced all 10 charts and the insights report (Python 3.12). I visually inspected the dashboard chart. Not run on Python 3.13 or on Windows itself.
