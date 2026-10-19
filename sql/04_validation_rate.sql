-- Percentage of raw rows that pass validation
-- Returns a 0-100 percentage (not a fraction); NULL when Bronze is empty.
SELECT ROUND(
    100.0 *
    (SELECT COUNT(*) FROM vehicle_telemetry.silver_telemetry) /
    NULLIF((SELECT COUNT(*) FROM vehicle_telemetry.bronze_telemetry), 0),
    3
) AS validation_pass_rate;
