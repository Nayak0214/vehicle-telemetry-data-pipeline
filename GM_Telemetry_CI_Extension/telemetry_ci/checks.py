"""Self-contained illustrative validation checks for a telemetry CI demonstration.

These checks mirror *categories* in the Databricks project but do not execute
its PySpark notebooks or assert identical production rule boundaries.
"""
from collections.abc import Mapping


def validation_errors(row: Mapping) -> list[str]:
    """Return human-readable reasons to quarantine one synthetic reading."""
    errors = []
    if not row.get("vehicle_id"):
        errors.append("missing vehicle_id")
    if not row.get("timestamp"):
        errors.append("missing timestamp")
    if row.get("engine_temp_c") is None:
        errors.append("missing engine_temp_c")

    voltage = row.get("battery_voltage_v")
    # Illustrative bounds for this stand-alone exercise, not automotive advice.
    if not isinstance(voltage, (int, float)) or not (0 <= voltage <= 20):
        errors.append("invalid battery_voltage_v")

    speed = row.get("speed_kmh")
    if not isinstance(speed, (int, float)) or not (0 <= speed <= 300):
        errors.append("invalid speed_kmh")
    return errors


def event_flags(row: Mapping) -> dict[str, bool]:
    """Apply the synthetic dashboard's illustrative alert thresholds."""
    temperature = row.get("engine_temp_c")
    voltage = row.get("battery_voltage_v")
    return {
        "high_temperature": temperature is not None and temperature > 105,
        "low_battery": voltage is not None and voltage < 11.8,
    }


def reconciles(raw_count: int, accepted_count: int, rejected_count: int) -> bool:
    """The count of Bronze rows must equal Silver plus Quarantine rows."""
    return (
        all(isinstance(v, int) and v >= 0 for v in (raw_count, accepted_count, rejected_count))
        and raw_count == accepted_count + rejected_count
    )
