"""
Engineering Constants and Standards Values
All constants per ISA 75.01, IEC 60534-2-1, and related standards
"""

class EngineeringConstants:
    """Engineering constants for valve sizing calculations"""

    # ISA 75.01 / IEC 60534-2-1 Constants
    SIZING_CONSTANTS = {
        # Metric units (m³/h, bar, kg/m³)
        'N1_metric': 0.0865,    # Liquid sizing constant
        'N2_metric': 0.00214,   # Reynolds number constant  
        'N4_metric': 7600.0,    # Reynolds number constant
        'N6_metric': 0.0373,    # Gas sizing constant (choked)
        'N7_metric': 0.00241,   # Gas sizing constant (mass flow)
        'N8_metric': 0.00214,   # Gas sizing constant
        'N9_metric': 0.0948,    # Gas sizing constant (unchoked)

        # Imperial units (GPM, psi, lb/ft³)
        'N1_imperial': 1.0,     # Liquid sizing constant
        'N2_imperial': 0.00214, # Reynolds number constant
        'N4_imperial': 7600.0,  # Reynolds number constant
        'N6_imperial': 63.3,    # Gas sizing constant (choked)
        'N7_imperial': 1.0,     # Gas sizing constant (mass flow)
        'N8_imperial': 0.00214, # Gas sizing constant
        'N9_imperial': 1360.0   # Gas sizing constant (unchoked)
    }

    # Physical constants
    PHYSICAL_CONSTANTS = {
        'R_gas': 8314.0,           # Universal gas constant (J/kmol·K)
        'standard_temp_k': 273.15, # Standard temperature (K)
        'standard_pressure_bar': 1.01325, # Standard pressure (bar)
        'standard_pressure_psi': 14.696,  # Standard pressure (psi)
        'water_density_kg_m3': 1000.0,    # Water density at STP (kg/m³)
        'water_density_lb_ft3': 62.4,     # Water density at STP (lb/ft³)
        'air_molecular_weight': 28.97,    # Air molecular weight (kg/kmol)
        'gravity_ms2': 9.80665             # Standard gravity (m/s²)
    }

    # Conversion factors
    CONVERSIONS = {
        'bar_to_psi': 14.5038,
        'psi_to_bar': 0.068948,
        'celsius_to_kelvin': 273.15,
        'fahrenheit_to_celsius': lambda f: (f - 32) * 5/9,
        'celsius_to_fahrenheit': lambda c: c * 9/5 + 32,
        'm3h_to_gpm': 4.40287,
        'gpm_to_m3h': 0.227125,
        'kg_m3_to_lb_ft3': 0.062428,
        'lb_ft3_to_kg_m3': 16.0185
    }

    # Standard pipe data (NPS vs ID)
    PIPE_DATA = {
        '1/2"': {'id_mm': 15.8, 'id_in': 0.622},
        '3/4"': {'id_mm': 20.9, 'id_in': 0.824},
        '1"': {'id_mm': 26.6, 'id_in': 1.049},
        '1.5"': {'id_mm': 40.9, 'id_in': 1.610},
        '2"': {'id_mm': 52.5, 'id_in': 2.067},
        '3"': {'id_mm': 77.9, 'id_in': 3.068},
        '4"': {'id_mm': 102.3, 'id_in': 4.026},
        '6"': {'id_mm': 154.1, 'id_in': 6.065},
        '8"': {'id_mm': 202.7, 'id_in': 7.981},
        '10"': {'id_mm': 254.5, 'id_in': 10.020},
        '12"': {'id_mm': 303.2, 'id_in': 11.938}
    }

    # Reynolds number flow regime boundaries
    REYNOLDS_LIMITS = {
        'laminar_upper': 56,      # Upper limit for laminar flow
        'transition_lower': 56,   # Lower limit for transitional flow
        'transition_upper': 40000, # Upper limit for transitional flow
        'turbulent_lower': 40000  # Lower limit for turbulent flow
    }

    # Cavitation sigma limits (typical values)
    CAVITATION_LIMITS = {
        'incipient': 15.0,    # Incipient cavitation sigma
        'constant': 8.0,      # Constant cavitation sigma
        'damage': 4.0,        # Damage potential sigma
        'choking': 2.0,       # Choking cavitation sigma
        'manufacturer': 6.0   # Typical manufacturer limit
    }
