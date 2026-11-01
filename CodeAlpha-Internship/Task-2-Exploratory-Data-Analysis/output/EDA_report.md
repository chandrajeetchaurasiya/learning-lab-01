# EDA Report: Titanic Passenger Dataset

Source: real public dataset (seaborn-data repository). Every number below is computed by `eda_analysis.py`.

## 1. Questions we want to answer
1. Did survival differ between men and women?
2. Did passenger class (1st/2nd/3rd) affect survival?
3. Did survivors pay different fares than non-survivors?
4. Did survivors differ in age from non-survivors?
5. Which columns have data-quality problems?

## 2. Dataset structure
- Rows: **891**, columns: **15**

|             | dtype   |   non_null |   missing |   missing_% |   unique |
|:------------|:--------|-----------:|----------:|------------:|---------:|
| survived    | int64   |        891 |         0 |         0   |        2 |
| pclass      | int64   |        891 |         0 |         0   |        3 |
| sex         | str     |        891 |         0 |         0   |        2 |
| age         | float64 |        714 |       177 |        19.9 |       88 |
| sibsp       | int64   |        891 |         0 |         0   |        7 |
| parch       | int64   |        891 |         0 |         0   |        7 |
| fare        | float64 |        891 |         0 |         0   |      248 |
| embarked    | str     |        889 |         2 |         0.2 |        3 |
| class       | str     |        891 |         0 |         0   |        3 |
| who         | str     |        891 |         0 |         0   |        3 |
| adult_male  | bool    |        891 |         0 |         0   |        2 |
| deck        | str     |        203 |       688 |        77.2 |        7 |
| embark_town | str     |        889 |         2 |         0.2 |        3 |
| alive       | str     |        891 |         0 |         0   |        2 |
| alone       | bool    |        891 |         0 |         0   |        2 |

## 3. Data quality checks
- **Exact duplicate rows:** 107. The dataset has no passenger ID, so identical rows (e.g. two 3rd-class men, same age and fare) can be different real people. **Decision: duplicates are reported but NOT deleted.** Deleting them could remove real passengers.
- **Missing `age`:** 177 (19.9%)
- **Missing `deck`:** 688 (77.2%) - too many to fill with guesses
- **Missing `embarked`/`embark_town`:** 2 each
- **Fare = 0:** 15 rows (kept; may be crew/free tickets but this is not stated in the data)
- **Fare outliers (IQR rule, > 65.63):** 116 rows. These are real expensive tickets, so they are flagged, not removed.

## 4. Cleaning steps applied
- `age`: filled missing values with the **median age of the same class and sex** (flag column `age_was_missing` keeps track of which were filled).
- `embark_town`/`embarked`: filled 2 missing values with the most common value (**Southampton**).
- `deck`: missing values labelled `Unknown` (not guessed).
- Added new columns: `family_size` (sibsp + parch + 1), `age_group`, `fare_outlier`.
- Dropped `alive` (same information as `survived`) and `class` (same information as `pclass`).
- Cleaned dataset saved: `data/titanic_cleaned.csv` (891 rows, 17 columns). Remaining missing values: 0.

## 5. Statistical summaries
### Numeric columns (cleaned data)
|       |    age |   fare |   sibsp |   parch |   family_size |
|:------|-------:|-------:|--------:|--------:|--------------:|
| count | 891    | 891    |  891    |  891    |        891    |
| mean  |  29.11 |  32.2  |    0.52 |    0.38 |          1.9  |
| std   |  13.3  |  49.69 |    1.1  |    0.81 |          1.61 |
| min   |   0.42 |   0    |    0    |    0    |          1    |
| 25%   |  21.5  |   7.91 |    0    |    0    |          1    |
| 50%   |  26    |  14.45 |    0    |    0    |          1    |
| 75%   |  36    |  31    |    1    |    0    |          2    |
| max   |  80    | 512.33 |    8    |    6    |         11    |

Skewness of `fare` = 4.79, skewness of `age` = 0.53. A skewness well above 0 means a long right tail (a few very high values).

**Overall survival rate: 38.4%** (342 of 891 passengers).

### Survival rate (%) by `sex`
| sex    |   passengers |   survivors |   survival_rate |
|:-------|-------------:|------------:|----------------:|
| female |          314 |         233 |            74.2 |
| male   |          577 |         109 |            18.9 |

### Survival rate (%) by `pclass`
|   pclass |   passengers |   survivors |   survival_rate |
|---------:|-------------:|------------:|----------------:|
|        1 |          216 |         136 |            63   |
|        2 |          184 |          87 |            47.3 |
|        3 |          491 |         119 |            24.2 |

### Survival rate (%) by `embark_town`
| embark_town   |   passengers |   survivors |   survival_rate |
|:--------------|-------------:|------------:|----------------:|
| Cherbourg     |          168 |          93 |            55.4 |
| Queenstown    |           77 |          30 |            39   |
| Southampton   |          646 |         219 |            33.9 |

### Survival rate (%) by `age_group`
| age_group           |   passengers |   survivors |   survival_rate |
|:--------------------|-------------:|------------:|----------------:|
| Child (0-12)        |           69 |          40 |            58   |
| Teen (13-18)        |           70 |          30 |            42.9 |
| Young adult (19-35) |          514 |         184 |            35.8 |
| Adult (36-60)       |          216 |          83 |            38.4 |
| Senior (60+)        |           22 |           5 |            22.7 |

### Survival rate (%) by `family_size`
|   family_size |   passengers |   survivors |   survival_rate |
|--------------:|-------------:|------------:|----------------:|
|             1 |          537 |         163 |            30.4 |
|             2 |          161 |          89 |            55.3 |
|             3 |          102 |          59 |            57.8 |
|             4 |           29 |          21 |            72.4 |
|             5 |           15 |           3 |            20   |
|             6 |           22 |           3 |            13.6 |
|             7 |           12 |           4 |            33.3 |
|             8 |            6 |           0 |             0   |
|            11 |            7 |           0 |             0   |

## 6. Hypothesis tests (significance level 0.05)
| hypothesis                                                                | test           |   p_value | conclusion             |
|:--------------------------------------------------------------------------|:---------------|----------:|:-----------------------|
| H1: survival depends on sex                                               | Chi-square     |  1.2e-58  | Significant difference |
| H2: survival depends on class                                             | Chi-square     |  4.55e-23 | Significant difference |
| H3: fares differ between survivors and non-survivors                      | Mann-Whitney U |  4.55e-22 | Significant difference |
| H4: mean age differs between survivors and non-survivors (real ages only) | Welch t-test   |  0.0412   | Significant difference |

Mean age of survivors = 28.3 vs non-survivors = 30.6 (real ages only, n = 714). Median fare of survivors = 26.00 vs non-survivors = 10.50.

*Note: a significant p-value shows an association in this data. It does not prove one factor caused another.*

## 7. Correlation with survival (Spearman)
|             |   correlation_with_survived |
|:------------|----------------------------:|
| pclass      |                       -0.34 |
| fare        |                        0.32 |
| family_size |                        0.17 |
| parch       |                        0.14 |
| sibsp       |                        0.09 |
| age         |                       -0.04 |

## 8. Charts generated
`eda_missing_values.png`, `eda_distributions.png`, `eda_correlation.png`, `eda_fare_outliers.png` (in `output/`).

## 9. Key findings (generated from the data)
1. Overall survival was 38.4%.
2. Women survived at 74.2% versus 18.9% for men (chi-square p = 1.20e-58).
3. Survival fell with class: 1st 63.0%, 2nd 47.3%, 3rd 24.2% (chi-square p = 4.55e-23).
4. Survivors paid a higher median fare (26.00 vs 10.50); Mann-Whitney p = 4.55e-22.
5. Age: survivor mean 28.3 vs non-survivor mean 30.6; Welch t-test p = 0.041 (significant at 0.05), but the gap is only 2.3 years, so age is a weak factor compared with sex and class.
6. Data issues: 688 missing decks, 177 missing ages, 107 duplicate-looking rows, 116 high-fare outliers.

## 10. Limitations
- Imputed ages are estimates; H4 therefore uses real ages only.
- Class, sex and fare are related to each other, so these tests look at one factor at a time.
- This is an observational historical dataset: associations, not causes.