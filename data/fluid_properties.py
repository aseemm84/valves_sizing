"""
Fluid Properties Database
Comprehensive fluid property database for automatic property lookup
"""

from typing import Dict, Any

class FluidProperties:
    """Fluid properties database for common industrial fluids"""

    def __init__(self):
        self.liquid_properties = {
            'Water': {
                'density': 998.0,  # kg/m³ at 20°C
                'vapor_pressure': 0.032,  # bar at 25°C
                'viscosity': 1.0,  # cSt at 20°C
                'typical_temp': 25.0,
                'critical_pressure': 221.2,  # bar
                'molecular_weight': 18.015
            },
            'Light Oil': {
                'density': 850.0,
                'vapor_pressure': 0.1,
                'viscosity': 10.0,
                'typical_temp': 40.0,
                'critical_pressure': 25.0,
                'molecular_weight': 150.0
            },
            'Heavy Oil': {
                'density': 950.0,
                'vapor_pressure': 0.01,
                'viscosity': 100.0,
                'typical_temp': 60.0,
                'critical_pressure': 15.0,
                'molecular_weight': 300.0
            }
        }

        self.gas_properties = {
            'Air': {
                'molecular_weight': 28.97,
                'k_ratio': 1.4,
                'z_factor': 1.0,
                'typical_temp': 25.0,
                'critical_pressure': 37.7,  # bar
                'critical_temperature': 132.5  # K
            },
            'Natural Gas': {
                'molecular_weight': 16.04,
                'k_ratio': 1.3,
                'z_factor': 0.95,
                'typical_temp': 25.0,
                'critical_pressure': 46.0,
                'critical_temperature': 190.6
            },
            'Steam': {
                'molecular_weight': 18.015,
                'k_ratio': 1.33,
                'z_factor': 1.0,
                'typical_temp': 150.0,
                'critical_pressure': 221.2,
                'critical_temperature': 647.1
            }
        }

    def get_liquid_properties(self, fluid_name: str) -> Dict[str, Any]:
        """Get liquid properties for specified fluid"""
        return self.liquid_properties.get(fluid_name, {})

    def get_gas_properties(self, fluid_name: str) -> Dict[str, Any]:
        """Get gas properties for specified fluid"""
        return self.gas_properties.get(fluid_name, {})
