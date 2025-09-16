"""
Piping Geometry Factors Module
Implementation of Fp factor calculations per ISA 75.01/IEC 60534-2-1

Features:
- Fp factor calculation for different valve/pipe configurations
- Reducer/expander effects
- Valve installation factor corrections
"""

import math
from typing import Dict, Any
from config.constants import EngineeringConstants

class GeometryFactors:
    """Piping geometry factor calculations"""

    def __init__(self):
        self.pipe_data = EngineeringConstants.PIPE_DATA

    def calculate_fp_factor(self, valve_size: str, pipe_size: str, 
                          valve_style: str, units: str = 'metric') -> float:
        """
        Calculate piping geometry factor Fp per ISA 75.01

        Args:
            valve_size: Valve nominal size
            pipe_size: Pipe nominal size  
            valve_style: Valve style (globe, ball, butterfly)
            units: Unit system

        Returns:
            Fp factor (dimensionless)
        """

        try:
            # Get pipe and valve diameters
            pipe_diameter = self._get_diameter(pipe_size, units)
            valve_diameter = self._get_diameter(valve_size, units)

            # Calculate diameter ratio
            beta = valve_diameter / pipe_diameter if pipe_diameter > 0 else 1.0

            # Base Fp calculation depends on valve type
            if valve_style.lower() in ['globe', 'single seat', 'double seat']:
                fp_factor = self._calculate_fp_globe(beta)
            elif valve_style.lower() in ['ball', 'segmented ball', 'v-notch']:
                fp_factor = self._calculate_fp_ball(beta)
            elif valve_style.lower() in ['butterfly', 'wafer', 'lug']:
                fp_factor = self._calculate_fp_butterfly(beta)
            else:
                fp_factor = self._calculate_fp_globe(beta)  # Default to globe

            return max(0.1, min(1.0, fp_factor))

        except:
            return 1.0  # Default value if calculation fails

    def _get_diameter(self, size: str, units: str) -> float:
        """Get internal diameter for given size"""
        pipe_data = self.pipe_data.get(size, {})
        if units == 'metric':
            return pipe_data.get('id_mm', 80.0)  # Default to 80mm
        else:
            return pipe_data.get('id_in', 3.068)  # Default to 3.068"

    def _calculate_fp_globe(self, beta: float) -> float:
        """Calculate Fp for globe valves"""
        if beta >= 1.0:
            return 1.0
        elif beta >= 0.9:
            # Minimal reduction
            return 1.0 - 0.1 * (1.0 - beta)
        else:
            # Standard reduction formula
            return math.sqrt(1.0 / (1.0 + 0.3 * (1.0 - beta**2)**2))

    def _calculate_fp_ball(self, beta: float) -> float:
        """Calculate Fp for ball valves"""
        if beta >= 1.0:
            return 1.0
        else:
            # Ball valves typically have less geometry effect
            return math.sqrt(1.0 / (1.0 + 0.2 * (1.0 - beta**2)**2))

    def _calculate_fp_butterfly(self, beta: float) -> float:
        """Calculate Fp for butterfly valves"""
        if beta >= 0.95:
            return 1.0
        else:
            # Butterfly valves are very sensitive to pipe size
            return math.sqrt(1.0 / (1.0 + 0.5 * (1.0 - beta**2)**2))

    def calculate_reducer_effects(self, upstream_size: str, valve_size: str,
                                downstream_size: str, units: str = 'metric') -> Dict[str, Any]:
        """
        Calculate effects of upstream/downstream reducers

        Returns:
            Dictionary with reducer analysis
        """

        try:
            d_up = self._get_diameter(upstream_size, units)
            d_valve = self._get_diameter(valve_size, units)
            d_down = self._get_diameter(downstream_size, units)

            # Upstream reducer effect
            beta_up = d_valve / d_up if d_up > 0 else 1.0

            # Downstream expander effect  
            beta_down = d_valve / d_down if d_down > 0 else 1.0

            # Calculate velocity changes
            velocity_ratio_up = (d_up / d_valve)**2 if d_valve > 0 else 1.0
            velocity_ratio_down = (d_valve / d_down)**2 if d_down > 0 else 1.0

            # Pressure loss coefficients (simplified)
            if beta_up < 1.0:  # Contraction
                k_up = 0.5 * (1.0 - beta_up**2)
            else:  # Expansion
                k_up = (1.0 - beta_up**2)**2

            if beta_down > 1.0:  # Expansion
                k_down = (1.0 - 1.0/beta_down**2)**2
            else:  # Contraction (unusual)
                k_down = 0.5 * (1.0 - beta_down**2)

            return {
                'upstream_beta': beta_up,
                'downstream_beta': beta_down,
                'velocity_ratio_upstream': velocity_ratio_up,
                'velocity_ratio_downstream': velocity_ratio_down,
                'loss_coefficient_upstream': k_up,
                'loss_coefficient_downstream': k_down,
                'total_geometry_effect': math.sqrt(1.0 / (1.0 + k_up + k_down))
            }

        except:
            return {
                'upstream_beta': 1.0,
                'downstream_beta': 1.0,
                'velocity_ratio_upstream': 1.0,
                'velocity_ratio_downstream': 1.0,
                'loss_coefficient_upstream': 0.0,
                'loss_coefficient_downstream': 0.0,
                'total_geometry_effect': 1.0
            }
