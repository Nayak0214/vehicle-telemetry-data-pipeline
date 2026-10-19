-- Ten vehicles with the most high-temperature readings
-- Counts are flagged readings, not distinct failure incidents.
SELECT
    vehicle_id,
    total_readings,
    overheating_events,
    low_battery_events,
    avg_engine_temp,
    health_score,
    risk_category
FROM vehicle_telemetry.gold_vehicle_health
ORDER BY overheating_events DESC, vehicle_id ASC
LIMIT 10;
