# Natural gas storage nowcast: results (analyze data)

Last EIA week in the data: **2026-11-20**. Every forecast was made using only information available before that week's release (walk-forward). The model was chosen on 2018-2021; the headline is scored on 2022 onward, 255 weeks the model choices never saw.

## Headline

- Best model: **Ridge regression**, average miss **13.1 Bcf** a week, vs **31.0 Bcf** for the 5-year average (58% smaller).
- Beat the 5-year average in **73%** of weeks.
- Called the direction of the surprise vs the 5-year average correctly in **86%** of weeks.
- The 80% range contained the real number **80%** of the time.

## All methods, 2022 onward, 255 weeks the model choices never saw

| model                     |   MAE (Bcf) |   RMSE (Bcf) |   bias (Bcf) |   beats 5-yr avg (% of weeks) |   surprise direction right (%) |   80% range covered (%) |
|:--------------------------|------------:|-------------:|-------------:|------------------------------:|-------------------------------:|------------------------:|
| Weather-adjusted 5-yr avg |        18.4 |         24   |         -1.6 |                          62.7 |                           79.5 |                    74.9 |
| Ridge regression          |        13.1 |         17   |         -4.1 |                          72.5 |                           86.4 |                    79.6 |
| Gradient boosting         |        16.2 |         21.5 |         -2.5 |                          68.6 |                           81.8 |                    73.3 |
| 5-year average            |        31   |         45.2 |         -0   |                           0   |                          nan   |                    76.9 |
| Same week last year       |        39.9 |         59.4 |         -0.3 |                          38.8 |                           53.2 |                    78   |
| Last week's change        |        35.1 |         53.3 |         -0   |                          45.9 |                           64.5 |                    76.1 |

## All methods, 2018 onward

| model                     |   MAE (Bcf) |   RMSE (Bcf) |   bias (Bcf) |   beats 5-yr avg (% of weeks) |   surprise direction right (%) |   80% range covered (%) |
|:--------------------------|------------:|-------------:|-------------:|------------------------------:|-------------------------------:|------------------------:|
| Weather-adjusted 5-yr avg |        20.3 |         26.1 |         -2.7 |                          57.5 |                           74.6 |                    74.9 |
| Ridge regression          |        14.5 |         18.4 |         -5.2 |                          69.6 |                           85.2 |                    78.1 |
| Gradient boosting         |        17.8 |         24.2 |         -2.2 |                          65.5 |                           80.4 |                    76   |
| 5-year average            |        30   |         44.1 |         -0.6 |                           0   |                          nan   |                    77.9 |
| Same week last year       |        39.6 |         58   |         -0.3 |                          37.5 |                           51.5 |                    75.8 |
| Last week's change        |        34.7 |         51.9 |         -0.4 |                          42.9 |                           63.8 |                    76.7 |

## Nowcast for weeks EIA hasn't released yet

- Week ending **Fri Nov 27, 2026**: **-12 Bcf** (80% range -24 to +12); 5-year average -34 (5 of 7 days use forecast weather, so less certain). EIA releases it Thu Dec 03.

## Model vs analyst consensus

Not compared yet. Fill in data/consensus.csv with the survey numbers reported in the news each Wednesday to add this.

## Data checks

- unexplained change: 7

Details in quality.csv.
