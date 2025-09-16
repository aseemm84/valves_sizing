"""
Unit Conversion Module
Professional unit conversion for all valve sizing parameters
"""

from typing import Dict, Any, Union
from config.constants import EngineeringConstants

class UnitConverter:
    """Professional unit conversion utilities"""

    def __init__(self):
        self.conversions = EngineeringConstants.CONVERSIONS

    def convert_pressure(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert pressure units"""
        # Convert to bar as intermediate
        if from_unit.lower() == 'psi':
            bar_value = value * self.conversions['psi_to_bar']
        elif from_unit.lower() == 'kpa':
            bar_value = value / 100.0
        elif from_unit.lower() == 'mpa':
            bar_value = value * 10.0
        else:  # assume bar
            bar_value = value

        # Convert from bar to target
        if to_unit.lower() == 'psi':
            return bar_value * self.conversions['bar_to_psi']
        elif to_unit.lower() == 'kpa':
            return bar_value * 100.0
        elif to_unit.lower() == 'mpa':
            return bar_value / 10.0
        else:  # assume bar
            return bar_value

    def convert_flow_rate(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert flow rate units"""
        # Normalize to m³/h
        if from_unit.lower() == 'gpm':
            m3h_value = value / self.conversions['m3h_to_gpm']
        elif from_unit.lower() == 'l/s':
            m3h_value = value * 3.6
        elif from_unit.lower() == 'l/min':
            m3h_value = value * 0.06
        else:  # assume m³/h
            m3h_value = value

        # Convert to target
        if to_unit.lower() == 'gpm':
            return m3h_value * self.conversions['m3h_to_gpm']
        elif to_unit.lower() == 'l/s':
            return m3h_value / 3.6
        elif to_unit.lower() == 'l/min':
            return m3h_value / 0.06
        else:  # assume m³/h
            return m3h_value
