# Natural gas storage nowcast: results (analyze data)

Last EIA week in the data: **2026-11-13**. Every forecast was made using only information available before that week's release (walk-forward). The model was chosen on 2018-2021; the headline is scored on 2022 onward, 254 weeks the model choices never saw.

## Headline

- Best model: **Ridge regression**, average miss **13.0 Bcf** a week, vs **31.2 Bcf** for the 5-year average (58% smaller).
- Beat the 5-year average in **73%** of weeks.
- Called the direction of the surprise vs the 5-year average correctly in **86%** of weeks.
- The 80% range contained the real number **80%** of the time.

## All methods, 2022 onward, 254 weeks the model choices never saw

| model                     |   MAE (Bcf) |   RMSE (Bcf) |   bias (Bcf) |   beats 5-yr avg (% of weeks) |   surprise direction right (%) |   80% range covered (%) |
|:--------------------------|------------:|-------------:|-------------:|------------------------------:|-------------------------------:|------------------------:|
| Weather-adjusted 5-yr avg |        18.4 |         24   |         -1.7 |                          63   |                           79.5 |                    75.2 |
| Ridge regression          |        13   |         17   |         -4.2 |                          72.8 |                           86.4 |                    79.9 |
| Gradient boosting         |        16.2 |         21.5 |         -2.6 |                          68.9 |                           81.8 |                    73.2 |
| 5-year average            |        31.2 |         45.3 |         -0   |                           0   |                          nan   |                    76.8 |
| Same week last year       |        40   |         59.5 |         -0.3 |                          39   |                           53.2 |                    78   |
| Last week's change        |        35   |         53.3 |         -0.2 |                          46.1 |                           64.5 |                    76   |

## All methods, 2018 onward

| model                     |   MAE (Bcf) |   RMSE (Bcf) |   bias (Bcf) |   beats 5-yr avg (% of weeks) |   surprise direction right (%) |   80% range covered (%) |
|:--------------------------|------------:|-------------:|-------------:|------------------------------:|-------------------------------:|------------------------:|
| Weather-adjusted 5-yr avg |        20.3 |         26.1 |         -2.7 |                          57.7 |                           74.6 |                    75.1 |
| Ridge regression          |        14.4 |         18.4 |         -5.2 |                          69.8 |                           85.2 |                    78.3 |
| Gradient boosting         |        17.8 |         24.2 |         -2.2 |                          65.7 |                           80.4 |                    76   |
| 5-year average            |        30   |         44.2 |         -0.6 |                           0   |                          nan   |                    77.8 |
| Same week last year       |        39.6 |         58.1 |         -0.3 |                          37.6 |                           51.5 |                    75.7 |
| Last week's change        |        34.7 |         52   |         -0.5 |                          43   |                           63.8 |                    76.7 |

## Nowcast for weeks EIA hasn't released yet

- Week ending **Fri Nov 20, 2026**: **-5 Bcf** (80% range -14 to +19); 5-year average -24 (7 of 7 days use forecast weather, so less certain). EIA releases it Thu Nov 26.

## Model vs analyst consensus

Not compared yet. Fill in data/consensus.csv with the survey numbers reported in the news each Wednesday to add this.

## Data checks

- unexplained change: 7

Details in quality.csv.
