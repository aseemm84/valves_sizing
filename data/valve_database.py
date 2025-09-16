"""
Comprehensive Valve Database
Travel-dependent coefficients and manufacturer data
"""

from typing import Dict, Any, List
import numpy as np

class ValveDatabase:
    """Comprehensive valve database with manufacturer data"""

    def __init__(self):
        self.valve_types = {
            'Globe Valve': {
                'Single Seat': {
                    'FL': 0.9, 'xT': 0.75, 'Fd': 1.0,
                    'max_cv_per_inch2': 25, 'rangeability': 50
                },
                'Cage Guided': {
                    'FL': 0.95, 'xT': 0.8, 'Fd': 1.0,
                    'max_cv_per_inch2': 30, 'rangeability': 100
                }
            },
            'Ball Valve (Segmented)': {
                'V-Notch': {
                    'FL': 0.6, 'xT': 0.15, 'Fd': 1.0,
                    'max_cv_per_inch2': 35, 'rangeability': 100
                }
            },
            'Butterfly Valve': {
                'High Performance': {
                    'FL': 0.5, 'xT': 0.3, 'Fd': 0.8,
                    'max_cv_per_inch2': 80, 'rangeability': 50
                }
            }
        }

    def get_valve_data(self, valve_type: str, valve_style: str, valve_size: str) -> Dict[str, Any]:
        """Get valve data for specified type and style"""

        data = self.valve_types.get(valve_type, {}).get(valve_style, {})

        if data:
            # Calculate max Cv based on size
            size_inches = float(valve_size.replace('"', '').replace('in', ''))
            max_cv = data['max_cv_per_inch2'] * size_inches ** 2

            return {
                'FL': data['FL'],
                'xT': data['xT'], 
                'Fd': data['Fd'],
                'max_cv': max_cv,
                'rangeability': data['rangeability']
            }

        return {'FL': 0.8, 'xT': 0.6, 'Fd': 1.0, 'max_cv': 100, 'rangeability': 50}

    def get_valve_series(self, vendor: str, valve_type: str) -> List[str]:
        """Get available valve series for vendor and type"""
        return ['Standard', 'High Performance', 'Low Noise']
