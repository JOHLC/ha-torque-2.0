"""Comprehensive test for all sensor types to verify raw value passthrough."""
from __future__ import annotations

import pytest

from custom_components.torque.sensor import TorqueSensor


class TestComprehensiveRawValuePassthrough:
    """Test that ALL sensor types pass through raw values without manipulation."""

    @pytest.mark.parametrize("name,unit,pid,description", [
        # Temperature sensors - various units
        ("Coolant Temperature", "°F", 5, "Should preserve Fahrenheit"),
        ("Air Intake Temperature", "°C", 15, "Should preserve Celsius"), 
        ("Oil Temperature", "K", 23, "Should preserve Kelvin"),
        ("Exhaust Gas Temperature", "°R", 51, "Should preserve Rankine"),
        
        # Speed sensors - various units  
        ("Vehicle Speed", "mph", 13, "Should preserve miles per hour"),
        ("Vehicle Speed", "km/h", 13, "Should preserve kilometers per hour"),
        ("Vehicle Speed", "m/s", 13, "Should preserve meters per second"),
        ("Vehicle Speed", "knots", 13, "Should preserve knots"),
        
        # Pressure sensors - various units
        ("Intake Manifold Pressure", "kPa", 11, "Should preserve kilopascals"),
        ("Fuel Pressure", "psi", 10, "Should preserve pounds per square inch"),
        ("Barometric Pressure", "bar", 51, "Should preserve bar"),
        ("Tire Pressure", "mmHg", 33, "Should preserve millimeters of mercury"),
        
        # RPM sensors
        ("Engine RPM", "rpm", 12, "Should preserve RPM"),
        ("Engine RPM", "rev/min", 12, "Should preserve rev/min"),
        
        # Voltage sensors - various units
        ("Battery Voltage", "V", 14, "Should preserve volts"),
        ("Sensor Voltage", "mV", 22, "Should preserve millivolts"),
        
        # Flow sensors - various units
        ("Mass Air Flow", "g/s", 16, "Should preserve grams per second"),
        ("Fuel Flow Rate", "L/h", 94, "Should preserve liters per hour"),
        ("Fuel Flow Rate", "gal/min", 95, "Should preserve gallons per minute"),
        
        # Distance sensors
        ("Trip Distance", "miles", 161, "Should preserve miles"),
        ("Trip Distance", "km", 162, "Should preserve kilometers"),
        
        # Torque sensors
        ("Engine Torque", "Nm", 98, "Should preserve Newton-meters"),
        ("Engine Torque", "lb-ft", 99, "Should preserve pound-feet"),
        
        # Efficiency sensors
        ("Fuel Economy", "mpg", 85, "Should preserve miles per gallon"),
        ("Fuel Economy", "L/100km", 86, "Should preserve liters per 100km"),
        
        # Percentage sensors
        ("Engine Load", "%", 4, "Should preserve percentage"),
        ("Throttle Position", "%", 17, "Should preserve percentage"),
        
        # Angle sensors
        ("Timing Advance", "°", 14, "Should preserve degrees"),
        ("Timing Advance", "rad", 15, "Should preserve radians"),
        
        # Unknown/Custom units
        ("Custom Sensor", "custom_unit", 200, "Should preserve custom units"),
        ("Another Sensor", "xyz", 201, "Should preserve unknown units"),
    ])
    def test_sensor_raw_unit_passthrough(self, name, unit, pid, description):
        """Test that all sensor types preserve their raw units without conversion."""
        sensor = TorqueSensor(name, unit, pid, "TestCar", {})
        
        # The unit should be passed through exactly as received from Torque
        assert sensor._attr_native_unit_of_measurement == unit, \
            f"{name}: Expected unit '{unit}', got '{sensor._attr_native_unit_of_measurement}'. {description}"

    def test_all_sensor_types_accept_all_numeric_values(self):
        """Test that all sensor types accept all numeric values without filtering."""
        sensor_types = [
            ("Vehicle Speed", "mph", 13),
            ("Coolant Temperature", "°F", 5), 
            ("Engine RPM", "rpm", 12),
            ("Intake Pressure", "kPa", 11),
            ("Battery Voltage", "V", 14),
            ("Engine Load", "%", 4),
            ("Fuel Flow", "L/h", 94),
            ("Trip Distance", "miles", 161),
            ("Engine Torque", "Nm", 98),
            ("Timing Advance", "°", 14),
        ]
        
        test_values = [0.0, 0.1, 1.0, 50.5, 100.0, 999.9, -5.0]
        
        for name, unit, pid in sensor_types:
            sensor = TorqueSensor(name, unit, pid, "TestCar", {})
            
            # All numeric values should be accepted (no filtering/debouncing)
            for test_val in test_values:
                assert sensor._is_value_valid(test_val) is True, \
                    f"{name} sensor rejected value {test_val} when it should accept all numeric values"

    def test_database_efficiency_preserved_for_all_types(self):
        """Test that database efficiency mechanisms work for all sensor types."""
        sensor_types_with_expected_thresholds = [
            ("Vehicle Speed", "mph", 13, 1.0),  # Speed threshold
            ("Coolant Temperature", "°F", 5, 0.5),  # Temperature threshold
            ("Engine RPM", "rpm", 12, 50.0),  # RPM threshold
            ("Battery Voltage", "V", 14, 0.1),  # Voltage threshold
            ("Intake Pressure", "kPa", 11, 1.0),  # Pressure threshold
            ("Unknown Sensor", "xyz", 99, 0.1),  # Default threshold
        ]
        
        for name, unit, pid, expected_threshold in sensor_types_with_expected_thresholds:
            sensor = TorqueSensor(name, unit, pid, "TestCar", {})
            
            # Verify the correct significance threshold is used
            actual_threshold = sensor._get_significant_change_threshold()
            assert actual_threshold == expected_threshold, \
                f"{name} has wrong significance threshold: expected {expected_threshold}, got {actual_threshold}"

    def test_no_device_class_manipulation(self):
        """Test that device class is not set to avoid HA manipulation."""
        sensor_types = [
            ("Vehicle Speed", "mph", 13),
            ("Coolant Temperature", "°F", 5), 
            ("Engine RPM", "rpm", 12),
            ("Battery Voltage", "V", 14),
        ]
        
        for name, unit, pid in sensor_types:
            sensor = TorqueSensor(name, unit, pid, "TestCar", {})
            
            # Device class should be None to avoid HA's automatic unit conversion
            assert sensor._attr_device_class is None, \
                f"{name} has device_class set to {sensor._attr_device_class}, should be None"