"""
Manufacturer-Specific Data Module
Vendor-specific valve coefficients and performance data
"""

from typing import Dict, Any

class ManufacturerData:
    """Manufacturer-specific valve data and coefficients"""

    def __init__(self):
        self.vendor_data = {
            'Fisher': {
                'multipliers': {'FL': 1.05, 'xT': 1.1, 'Cv': 1.0},
                'series': ['ED', 'HPT', 'WhisperTrim'],
                'features': ['Low noise', 'Anti-cavitation']
            },
            'Emerson': {
                'multipliers': {'FL': 1.0, 'xT': 1.0, 'Cv': 0.9},
                'series': ['Easy-E', 'Pro-E'],
                'features': ['Standard', 'High performance']
            }
        }

    def get_vendor_multipliers(self, vendor: str) -> Dict[str, float]:
        """Get vendor-specific coefficient multipliers"""
        return self.vendor_data.get(vendor, {}).get('multipliers', {'FL': 1.0, 'xT': 1.0, 'Cv': 1.0})
