# Dashboard SQL datasets

Run these queries after Bronze, Silver, and Gold complete, using the same current catalog as the notebooks. All table names are qualified with the `vehicle_telemetry` schema.

| Query | Result | Suggested visual |
|---|---|---|
| [01_top_temperature_vehicles.sql](01_top_temperature_vehicles.sql) | Ten vehicles with the most high-temperature readings | Bar chart: `vehicle_id` versus `overheating_events` |
| [02_fleet_overview.sql](02_fleet_overview.sql) | One row of fleet totals and mean vehicle score | KPI cards for vehicles, valid readings, event totals, and health score |
| [03_data_quality.sql](03_data_quality.sql) | Valid and quarantined row counts | Bar chart: `record_status` versus `record_count` |
| [04_validation_rate.sql](04_validation_rate.sql) | Percentage of Bronze rows accepted into Silver | Numeric KPI with a percent suffix |
| [05_battery_health.sql](05_battery_health.sql) | Ten vehicles with the most low-battery readings | Bar chart: `vehicle_id` versus `low_battery_events` |

## Metric and chart conventions

- Event totals count flagged **readings**, not distinct incidents. A reading can count toward both high-temperature and low-battery totals.
- `avg_health_score` is the unweighted mean of the rounded per-vehicle scores in Gold. It is not a reading-weighted fleet score.
- `validation_pass_rate` is already on a **0–100 scale**, rounded to three decimal places. Add a percent suffix without multiplying by 100 again. It returns `NULL` when Bronze is empty.
- Both ranking queries sort by descending event count, then ascending vehicle ID to resolve ties. Use each query as its own dataset. Treat vehicle IDs as categories and explicitly configure descending event-count sorting in the chart; SQL row order alone may not determine chart order.
- The battery query casts vehicle IDs to strings for categorical display. Generated IDs all have four digits, so its string tie-break order matches numeric order for this dataset.
- The saved battery screenshot displays the same vehicle selection as the temperature screenshot. Use query 05 to produce an independent battery ranking; the screenshot is not verification of that ranking.
- KPI abbreviations such as `99.59K` and `21.7K` are dashboard formatting, not the exact values returned by SQL. An empty Gold table produces `COUNT(*) = 0` and `NULL` sums/averages.

These files supply datasets. Dashboard layout, formatting, and dataset bindings must be configured in Databricks; no dashboard configuration export is included.
