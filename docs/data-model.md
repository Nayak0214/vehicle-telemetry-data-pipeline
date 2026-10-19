# Data model and validation rules

All four tables use Delta format in the `vehicle_telemetry` schema of the current catalog. Each notebook overwrites its output tables for the current batch.

## Bronze and Silver

**Grain:** one generated sensor reading per vehicle per minute. The generated batch has 100 vehicles and 1,000 readings per vehicle before validation. No primary key or uniqueness constraint is enforced.

| Column | Meaning |
|---|---|
| `vehicle_id` | Integer identifier, generated from 1001 through 1100 |
| `timestamp` | Reading time; one-minute steps from `2026-10-01 00:00:00` |
| `engine_temp` | Engine temperature in °C, rounded to one decimal |
| `battery_voltage` | Auxiliary battery voltage in V, rounded to two decimals |
| `speed` | Speed in km/h, rounded to one decimal |
| `ingestion_timestamp` | Spark timestamp added when writing Bronze |

The timestamp literal has no explicit timezone; interpretation follows the Spark session timezone. Silver retains the Bronze columns and ingestion timestamp for rows that pass all checks.

## Silver validation and Quarantine

| Field | Accepted values | Rejection reason |
|---|---|---|
| `engine_temp` | Non-null, from −40 through 150 °C inclusive | `Invalid temperature` |
| `battery_voltage` | Non-null, greater than 0 and at most 16 V | `Invalid battery voltage` |
| `speed` | Non-null, from 0 through 200 km/h inclusive | `Invalid speed` |
| `vehicle_id`, `timestamp` | Both non-null | `Missing vehicle ID or timestamp` |

Quarantine retains all Bronze columns and adds `validation_errors`, a string joining applicable reasons with ` | `. Passing rows have an empty error string before that column is dropped from Silver. Each rejected row is stored once, even if it fails several rules.

For generated IDs 0–99,999, missing temperature is injected when `id % 499 == 0`, negative speed when `id % 997 == 0`, and zero voltage when `id % 887 == 0`. These rules affect 201, 101, and 113 rows respectively. Only ID 0 overlaps, yielding **413 unique rejected rows** and **99,587 valid rows**. This arithmetic describes the generator, not a recorded Spark execution.

## Gold

**Grain:** one row per vehicle represented in Silver.

| Column | Definition |
|---|---|
| `vehicle_id` | Grouping key |
| `total_readings` | Number of valid readings for the vehicle |
| `avg_engine_temp` | Mean engine temperature, rounded to two decimals |
| `max_engine_temp` | Maximum engine temperature |
| `avg_battery_voltage` | Mean voltage, rounded to two decimals |
| `avg_speed` | Mean speed, rounded to two decimals |
| `overheating_events` | Count of valid readings with `engine_temp > 105` |
| `low_battery_events` | Count of valid readings with `battery_voltage < 11.8` |
| `overheating_rate` | Mean of the 0/1 temperature flag, from 0 to 1 |
| `low_battery_rate` | Mean of the 0/1 battery flag, from 0 to 1 |
| `health_score` | `round(max(0, 100 - 60 × overheating_rate - 40 × low_battery_rate), 1)` |
| `risk_category` | `High` for rounded score <70; `Moderate` for <85; otherwise `Low` |

The temperature and battery flags exist in an intermediate DataFrame; they are not persisted in Silver. Validity limits and event thresholds serve different purposes: a reading can pass Silver validation and still trigger a Gold event flag.

## Existing reconciliation assertions

- After Silver writes: saved Bronze count equals saved Silver plus saved Quarantine count.
- After Gold writes: saved Gold has exactly 100 rows, and summed `total_readings` equals the loaded Silver count.

These checks assume the supplied 100-vehicle demonstration and sequential execution. They check row counts rather than record-level equality, uniqueness, or event-count reconciliation.
