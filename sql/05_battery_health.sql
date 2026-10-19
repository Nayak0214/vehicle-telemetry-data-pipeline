-- Ten vehicles with the most low-battery readings
-- Use this independent dataset for the battery ranking. IDs are categorical labels.
SELECT
    CAST(vehicle_id AS STRING) AS vehicle_id,
    low_battery_events,
    avg_battery_voltage,
    health_score
FROM vehicle_telemetry.gold_vehicle_health
ORDER BY low_battery_events DESC, vehicle_id ASC
LIMIT 10;
