-- Fleet KPIs from Gold-level vehicle summaries
-- Mean score is unweighted across the rounded per-vehicle Gold scores.
SELECT
    COUNT(*) AS total_vehicles,
    SUM(total_readings) AS valid_readings,
    SUM(overheating_events) AS overheating_events,
    SUM(low_battery_events) AS low_battery_events,
    ROUND(AVG(health_score), 1) AS avg_health_score
FROM vehicle_telemetry.gold_vehicle_health;
