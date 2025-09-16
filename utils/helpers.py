"""
Helper Utilities Module
Safety factors, plotting helpers, and general utilities
"""

import math
from typing import Dict, Any

class SafetyFactorCalculator:
    """Calculate safety factors based on service conditions"""

    def __init__(self):
        self.base_factors = {
            'Non-Critical': 1.1,
            'Important': 1.2,
            'Critical': 1.3,
            'Safety Critical': 1.5
        }

        self.service_multipliers = {
            'Clean Service': 1.0,
            'Dirty Service': 1.1,
            'Corrosive Service': 1.2,
            'High Temperature': 1.15,
            'Cryogenic': 1.2,
            'Erosive Service': 1.25
        }

    def calculate_safety_factor(self,
                              criticality: str,
                              service_type: str,
                              control_mode: str,
                              expansion_factor: float = 0.0,
                              h2s_service: bool = False) -> float:
        """Calculate recommended safety factor"""

        # Base factor
        base = self.base_factors.get(criticality, 1.2)

        # Service multiplier
        service_mult = self.service_multipliers.get(service_type, 1.0)

        # Control mode adjustment
        if control_mode == 'Emergency Shutdown':
            control_mult = 1.3
        elif control_mode == 'On-Off':
            control_mult = 0.95
        else:
            control_mult = 1.0

        # H2S service adjustment
        h2s_mult = 1.1 if h2s_service else 1.0

        # Expansion factor
        exp_mult = 1.0 + (expansion_factor / 100.0)

        # Total factor
        total = base * service_mult * control_mult * h2s_mult * exp_mult

        return max(1.05, min(2.0, round(total, 1)))
