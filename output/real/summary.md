# Natural gas storage nowcast: results (analyze data)

Last EIA week in the data: **2026-11-06**. Every forecast was made using only information available before that week's release (walk-forward). The model was chosen on 2018-2021; the headline is scored on 2022 onward, 253 weeks the model choices never saw.

## Headline

- Best model: **Ridge regression**, average miss **13.1 Bcf** a week, vs **31.3 Bcf** for the 5-year average (58% smaller).
- Beat the 5-year average in **73%** of weeks.
- Called the direction of the surprise vs the 5-year average correctly in **86%** of weeks.
- The 80% range contained the real number **80%** of the time.

## All methods, 2022 onward, 253 weeks the model choices never saw

| model                     |   MAE (Bcf) |   RMSE (Bcf) |   bias (Bcf) |   beats 5-yr avg (% of weeks) |   surprise direction right (%) |   80% range covered (%) |
|:--------------------------|------------:|-------------:|-------------:|------------------------------:|-------------------------------:|------------------------:|
| Weather-adjusted 5-yr avg |        18.4 |         24   |         -1.8 |                          63.2 |                           79.9 |                    75.5 |
| Ridge regression          |        13.1 |         17   |         -4.2 |                          72.7 |                           86.3 |                    79.8 |
| Gradient boosting         |        16.1 |         21.4 |         -2.7 |                          69.2 |                           82.2 |                    73.5 |
| 5-year average            |        31.3 |         45.4 |         -0   |                           0   |                          nan   |                    76.7 |
| Same week last year       |        40.1 |         59.6 |         -0.2 |                          39.1 |                           53   |                    77.9 |
| Last week's change        |        35   |         53.4 |         -0.4 |                          46.2 |                           64.8 |                    75.9 |

## All methods, 2018 onward

| model                     |   MAE (Bcf) |   RMSE (Bcf) |   bias (Bcf) |   beats 5-yr avg (% of weeks) |   surprise direction right (%) |   80% range covered (%) |
|:--------------------------|------------:|-------------:|-------------:|------------------------------:|-------------------------------:|------------------------:|
| Weather-adjusted 5-yr avg |        20.2 |         26.1 |         -2.8 |                          57.8 |                           74.8 |                    75.2 |
| Ridge regression          |        14.5 |         18.4 |         -5.2 |                          69.7 |                           85.1 |                    78.2 |
| Gradient boosting         |        17.8 |         24.2 |         -2.3 |                          65.8 |                           80.6 |                    76.1 |
| 5-year average            |        30.1 |         44.2 |         -0.6 |                           0   |                          nan   |                    77.8 |
| Same week last year       |        39.6 |         58.1 |         -0.2 |                          37.7 |                           51.4 |                    75.7 |
| Last week's change        |        34.7 |         52   |         -0.6 |                          43.1 |                           64   |                    76.6 |

## Nowcast for weeks EIA hasn't released yet

- Week ending **Fri Nov 13, 2026**: **+16 Bcf** (80% range +7 to +40); 5-year average +27 (2 of 7 days use forecast weather, so less certain). EIA releases it Thu Nov 19.
- Week ending **Fri Nov 20, 2026**: **+0 Bcf** (80% range -9 to +24); 5-year average -24 (7 of 7 days use forecast weather, so less certain). EIA releases it Thu Nov 26.

## Model vs analyst consensus

Not compared yet. Fill in data/consensus.csv with the survey numbers reported in the news each Wednesday to add this.

## Data checks

- unexplained change: 7

Details in quality.csv.
