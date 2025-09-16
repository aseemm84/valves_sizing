"""
Application Settings and Configuration
"""

class AppSettings:
    """Application configuration settings"""

    # Calculation settings
    CALCULATION_SETTINGS = {
        'reynolds_max_iterations': 10,
        'reynolds_tolerance': 0.001,
        'cavitation_safety_margin': 1.2,
        'noise_limit_dba': 85.0,
        'min_valve_opening_percent': 10.0,
        'max_valve_opening_percent': 90.0,
        'recommended_min_opening': 20.0,
        'recommended_max_opening': 80.0
    }

    # Validation settings
    VALIDATION_LIMITS = {
        'min_pressure_ratio': 0.05,
        'max_pressure_ratio': 0.98,
        'min_temperature_c': -273.0,
        'max_temperature_c': 2000.0,
        'min_flow_rate': 0.001,
        'max_flow_rate': 1000000.0,
        'min_density': 0.1,
        'max_density': 10000.0
    }

    # Display settings
    DISPLAY_SETTINGS = {
        'decimal_places_cv': 2,
        'decimal_places_pressure': 2,
        'decimal_places_flow': 1,
        'decimal_places_temperature': 1,
        'chart_height': 400,
        'chart_width': 600
    }
