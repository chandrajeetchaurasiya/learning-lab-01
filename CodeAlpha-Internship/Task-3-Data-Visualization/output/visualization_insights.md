# Visualization Insights Report

Data: Titanic passengers (real public dataset, 891 rows), cleaned in Task 2. All numbers are computed by `visualize_data.py`.

| Chart | What it shows | Insight (computed from data) |
|---|---|---|
| 01_overall_survival | Survived vs not | 342 of 891 passengers survived (38.4%). |
| 02_survival_by_sex | Survival rate by sex | Women 74.2% vs men 18.9%. |
| 03_survival_by_class | Survival rate by class | 1st 63.0%, 2nd 47.3%, 3rd 24.2%. |
| 04_class_sex_heatmap | Class and sex together | Females: 1st 96.8%, 2nd 92.1%, 3rd 50.0%. Males: 1st 36.9%, 2nd 15.7%, 3rd 13.5%. |
| 05_age_distribution | Age histogram by outcome | Median age: survivors 27.0, non-survivors 25.0. Both groups are concentrated in the 20s-30s. |
| 06_survival_by_age_group | Survival by age band | Highest: Child (0-12) (58.0%). Lowest: Senior (60+) (22.7%). |
| 07_fare_by_class_outcome | Fare spread (log scale) | Median fare of survivors 26.00 vs non-survivors 10.50. |
| 08_survival_by_family_size | Survival by family size | Alone: 30.4% (n=537). Family of 2-4: 57.9% (n=292). Family of 5+: 16.1% (n=62). |
| 09_survival_by_port | Survival by port | Cherbourg 55.4%, Queenstown 39.0%, Southampton 33.9%. |
| 10_dashboard | Four key charts together | One-page summary for presentations. |

## Reading the charts carefully
- Sex and class together tell a clearer story than either alone (see the heatmap).
- Port of embarkation is likely linked to class mix, so it should not be read as a direct cause.
- Family-size groups above 4 are small; treat those percentages with caution (counts are printed on chart 08).
- 177 ages were estimated in Task 2, which slightly affects charts 05 and 06.
- These charts show associations in historical data, not proof of cause.