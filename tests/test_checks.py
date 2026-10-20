"""Original CI smoke tests for the synthetic GM-style telemetry project."""
from telemetry_ci.checks import event_flags, reconciles, validation_errors


SAMPLE = {
    "vehicle_id": "V001",
    "timestamp": "2026-10-19T12:00:00Z",
    "engine_temp_c": 93.0,
    "battery_voltage_v": 12.4,
    "speed_kmh": 48.0,
}


def test_valid_reading_is_accepted():
    assert validation_errors(SAMPLE) == []


def test_missing_vehicle_identifier_is_quarantined():
    assert "missing vehicle_id" in validation_errors({**SAMPLE, "vehicle_id": ""})


def test_missing_timestamp_is_quarantined():
    assert "missing timestamp" in validation_errors({**SAMPLE, "timestamp": None})


def test_missing_engine_temperature_is_quarantined():
    assert "missing engine_temp_c" in validation_errors({**SAMPLE, "engine_temp_c": None})


def test_out_of_bounds_battery_reading_is_quarantined():
    assert "invalid battery_voltage_v" in validation_errors({**SAMPLE, "battery_voltage_v": -1})


def test_negative_speed_is_quarantined():
    assert "invalid speed_kmh" in validation_errors({**SAMPLE, "speed_kmh": -20})


def test_alert_thresholds_are_strict():
    assert event_flags({**SAMPLE, "engine_temp_c": 105, "battery_voltage_v": 11.8}) == {
        "high_temperature": False,
        "low_battery": False,
    }
    assert event_flags({**SAMPLE, "engine_temp_c": 106, "battery_voltage_v": 11.7}) == {
        "high_temperature": True,
        "low_battery": True,
    }


def test_telemetry_record_counts_reconcile():
    assert reconciles(100_000, 99_587, 413)
    assert not reconciles(100_000, 99_587, 412)


def test_negative_counts_fail_reconciliation():
    assert not reconciles(100, -1, 101)


def test_validation_does_not_mutate_source_reading():
    original = dict(SAMPLE)
    validation_errors(SAMPLE)
    assert SAMPLE == original
