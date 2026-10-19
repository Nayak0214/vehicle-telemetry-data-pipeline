-- Valid versus quarantined rows
-- Each rejected row counts once, even when it has multiple validation errors.
SELECT 'Valid' AS record_status, COUNT(*) AS record_count
FROM vehicle_telemetry.silver_telemetry
UNION ALL
SELECT 'Quarantined' AS record_status, COUNT(*) AS record_count
FROM vehicle_telemetry.quarantine_telemetry;
