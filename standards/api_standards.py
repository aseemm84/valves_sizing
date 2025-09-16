"""
API Standards Module
Implementation of API 6D and related pipeline valve standards

Features:
- API 6D pipeline valve requirements
- Fire-safe certification tracking
- Double block and bleed requirements
- Fugitive emission standards
"""

from typing import Dict, Any, List

class APIStandards:
    """API Standards Implementation for Pipeline Valves"""
    
    def __init__(self):
        self.api_6d_requirements = {
            'fire_safe': {
                'test_standard': 'API 607',
                'temperature': 750,  # °C
                'duration': 30,      # minutes
                'leakage_limit': 5.0 # L/min per inch of diameter
            },
            'fugitive_emissions': {
                'standard': 'ISO 15848-1',
                'classes': {
                    'A': {'leakage_limit': 10, 'duration': '3 months'},
                    'B': {'leakage_limit': 100, 'duration': '1 month'},
                    'C': {'leakage_limit': 500, 'duration': 'Type test only'}
                }
            },
            'double_block_bleed': {
                'upstream_seal': True,
                'downstream_seal': True,
                'body_drain': True,
                'pressure_rating': 'Full pipeline pressure'
            }
        }
    
    def check_api_6d_compliance(self, valve_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check API 6D compliance requirements"""
        
        compliance = {
            'fire_safe': valve_config.get('fire_safe_required', False),
            'fugitive_emissions': valve_config.get('fugitive_emissions', 'Standard'),
            'double_block_bleed': valve_config.get('double_block_bleed', False),
            'full_port': valve_config.get('full_port', False)
        }
        
        requirements_met = []
        requirements_missing = []
        
        if compliance['fire_safe']:
            requirements_met.append("Fire-safe certification per API 607")
        
        if compliance['fugitive_emissions'] != 'Standard':
            requirements_met.append(f"Low emission class {compliance['fugitive_emissions']}")
        
        if compliance['double_block_bleed']:
            requirements_met.append("Double block and bleed capability")
        
        if compliance['full_port']:
            requirements_met.append("Full port design for pigging")
        
        return {
            'compliance_level': 'API 6D Compliant' if requirements_met else 'Standard',
            'requirements_met': requirements_met,
            'requirements_missing': requirements_missing,
            'certification_needed': self._get_certification_requirements(compliance)
        }
    
    def _get_certification_requirements(self, compliance: Dict[str, Any]) -> List[str]:
        """Get required certifications"""
        certifications = []
        
        if compliance['fire_safe']:
            certifications.append("API 607 Fire Test Certification")
        
        if compliance['fugitive_emissions'] != 'Standard':
            certifications.append(f"ISO 15848-1 Class {compliance['fugitive_emissions']} Certification")
        
        return certifications
