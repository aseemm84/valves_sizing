"""
NACE MR0175/ISO 15156 Sour Service Materials Module
Material selection for H2S-containing environments

Features:
- H2S partial pressure calculations
- Material hardness limits for sour service
- Environmental severity classification
- Compliance checking per NACE MR0175/ISO 15156
"""

from typing import Dict, Any, List, Optional
import math

class NACEMR0175:
    """NACE MR0175/ISO 15156 Implementation for Sour Service Materials"""
    
    def __init__(self):
        # NACE MR0175 Environmental limits
        self.environmental_limits = {
            'h2s_threshold_bar': 0.0003,  # 0.05 psia threshold
            'h2s_threshold_psi': 0.05,
            'temperature_limit_c': 177,   # 350°F
            'temperature_limit_f': 350,
            'ph_minimum': 3.5,
            'chloride_limit_ppm': 20000
        }
        
        # Material hardness limits for sour service (HRC)
        self.hardness_limits = {
            'carbon_steel': {
                'base_metal': 22,
                'weld_metal': 22,
                'heat_affected_zone': 22
            },
            'low_alloy_steel': {
                'base_metal': 22,
                'weld_metal': 22,
                'heat_affected_zone': 22
            },
            'martensitic_stainless': {
                'base_metal': 23,
                'weld_metal': 23,
                'heat_affected_zone': 23
            },
            'duplex_stainless': {
                'base_metal': 28,
                'weld_metal': 28,
                'heat_affected_zone': 28
            }
        }
        
        # Acceptable materials for sour service
        self.sour_service_materials = {
            'carbon_steel': {
                'grades': ['A216 WCB', 'A105', 'A350 LF2'],
                'max_hardness': 22,
                'notes': 'Limited to moderate sour service'
            },
            'stainless_steel_316': {
                'grades': ['A351 CF8M', 'A182 F316', 'A479 316'],
                'max_hardness': 28,
                'notes': 'Suitable for most sour service applications'
            },
            'stainless_steel_317': {
                'grades': ['A351 CF8C', 'A182 F317'],
                'max_hardness': 28,
                'notes': 'Enhanced chloride resistance'
            },
            'duplex_stainless': {
                'grades': ['A890 4A', 'A182 F51', 'A182 F55'],
                'max_hardness': 28,
                'notes': 'High strength sour service'
            },
            'nickel_alloys': {
                'grades': ['Inconel 625', 'Hastelloy C-276', 'Incoloy 825'],
                'max_hardness': 35,
                'notes': 'Severe sour service applications'
            }
        }
    
    def calculate_h2s_partial_pressure(self, total_pressure: float, h2s_mole_percent: float,
                                     pressure_units: str = 'bar') -> Dict[str, Any]:
        """Calculate H2S partial pressure from composition"""
        
        try:
            # Calculate H2S partial pressure
            h2s_partial_pressure = total_pressure * (h2s_mole_percent / 100.0)
            
            # Convert to both units
            if pressure_units.lower() == 'bar':
                h2s_partial_bar = h2s_partial_pressure
                h2s_partial_psi = h2s_partial_pressure * 14.5038
            else:  # psi
                h2s_partial_psi = h2s_partial_pressure
                h2s_partial_bar = h2s_partial_pressure / 14.5038
            
            # Check threshold
            exceeds_threshold = h2s_partial_bar > self.environmental_limits['h2s_threshold_bar']
            
            return {
                'h2s_partial_pressure_bar': h2s_partial_bar,
                'h2s_partial_pressure_psi': h2s_partial_psi,
                'total_pressure': total_pressure,
                'h2s_mole_percent': h2s_mole_percent,
                'exceeds_threshold': exceeds_threshold,
                'threshold_bar': self.environmental_limits['h2s_threshold_bar'],
                'threshold_psi': self.environmental_limits['h2s_threshold_psi'],
                'nace_applicable': exceeds_threshold
            }
            
        except Exception as e:
            return {'error': f'H2S partial pressure calculation failed: {str(e)}'}
    
    def assess_environmental_severity(self, h2s_partial_pressure_bar: float, temperature_c: float,
                                    ph: float = 7.0, chloride_ppm: float = 0) -> Dict[str, Any]:
        """Assess environmental severity per NACE MR0175"""
        
        try:
            # Convert to psi for NACE evaluation
            h2s_partial_psi = h2s_partial_pressure_bar * 14.5038
            temperature_f = temperature_c * 9/5 + 32
            
            # Check individual limits
            h2s_severity = self._assess_h2s_severity(h2s_partial_psi)
            temp_severity = self._assess_temperature_severity(temperature_f)
            ph_severity = self._assess_ph_severity(ph)
            chloride_severity = self._assess_chloride_severity(chloride_ppm)
            
            # Overall severity assessment
            severities = [h2s_severity['level'], temp_severity['level'], ph_severity['level'], chloride_severity['level']]
            
            if 'Severe' in severities:
                overall_severity = 'Severe'
                overall_description = 'Severe sour service - Special materials required'
            elif 'Moderate' in severities:
                overall_severity = 'Moderate' 
                overall_description = 'Moderate sour service - Standard NACE materials acceptable'
            elif 'Mild' in severities:
                overall_severity = 'Mild'
                overall_description = 'Mild sour service - Most NACE materials suitable'
            else:
                overall_severity = 'Non-sour'
                overall_description = 'Below NACE threshold - Standard materials acceptable'
            
            return {
                'overall_severity': overall_severity,
                'overall_description': overall_description,
                'h2s_assessment': h2s_severity,
                'temperature_assessment': temp_severity,
                'ph_assessment': ph_severity,
                'chloride_assessment': chloride_severity,
                'nace_applicable': h2s_partial_psi >= self.environmental_limits['h2s_threshold_psi'],
                'special_requirements': self._get_special_requirements(overall_severity)
            }
            
        except Exception as e:
            return {'error': f'Environmental severity assessment failed: {str(e)}'}
    
    def check_material_compliance(self, material_category: str, hardness_hrc: float,
                                environmental_severity: str) -> Dict[str, Any]:
        """Check material compliance with NACE MR0175"""
        
        try:
            if material_category not in self.hardness_limits:
                return {'error': f'Material category {material_category} not recognized'}
            
            limits = self.hardness_limits[material_category]
            max_hardness = limits['base_metal']
            
            # Check hardness compliance
            hardness_compliant = hardness_hrc <= max_hardness
            hardness_margin = max_hardness - hardness_hrc
            
            # Check material suitability for severity level
            suitable_materials = self._get_suitable_materials(environmental_severity)
            material_suitable = material_category in suitable_materials
            
            # Overall compliance
            overall_compliant = hardness_compliant and material_suitable
            
            # Assessment
            if not hardness_compliant:
                assessment = f"Non-compliant - Hardness ({hardness_hrc} HRC) exceeds limit ({max_hardness} HRC)"
                severity = "Critical"
            elif not material_suitable:
                assessment = f"Material not suitable for {environmental_severity.lower()} sour service"
                severity = "Critical"
            elif hardness_margin < 2:
                assessment = "Marginal - Close to hardness limit"
                severity = "Warning"
            else:
                assessment = "Compliant - Suitable for sour service"
                severity = "Good"
            
            return {
                'overall_compliant': overall_compliant,
                'hardness_compliant': hardness_compliant,
                'material_suitable': material_suitable,
                'hardness_hrc': hardness_hrc,
                'max_hardness_hrc': max_hardness,
                'hardness_margin_hrc': hardness_margin,
                'assessment': assessment,
                'severity': severity,
                'recommendations': self._get_material_recommendations(
                    overall_compliant, material_category, environmental_severity
                )
            }
            
        except Exception as e:
            return {'error': f'Material compliance check failed: {str(e)}'}
    
    def get_recommended_materials(self, environmental_severity: str) -> Dict[str, Any]:
        """Get recommended materials for given environmental severity"""
        
        suitable_categories = self._get_suitable_materials(environmental_severity)
        
        recommendations = {}
        for category in suitable_categories:
            if category in self.sour_service_materials:
                recommendations[category] = self.sour_service_materials[category]
        
        return {
            'environmental_severity': environmental_severity,
            'recommended_materials': recommendations,
            'selection_notes': self._get_selection_notes(environmental_severity)
        }
    
    def _assess_h2s_severity(self, h2s_partial_psi: float) -> Dict[str, Any]:
        """Assess H2S partial pressure severity"""
        if h2s_partial_psi < 0.05:
            return {'level': 'Non-sour', 'description': 'Below NACE threshold'}
        elif h2s_partial_psi < 1.0:
            return {'level': 'Mild', 'description': 'Low H2S concentration'}
        elif h2s_partial_psi < 15.0:
            return {'level': 'Moderate', 'description': 'Moderate H2S concentration'}
        else:
            return {'level': 'Severe', 'description': 'High H2S concentration'}
    
    def _assess_temperature_severity(self, temperature_f: float) -> Dict[str, Any]:
        """Assess temperature severity"""
        if temperature_f < 180:
            return {'level': 'Mild', 'description': 'Low temperature'}
        elif temperature_f < 350:
            return {'level': 'Moderate', 'description': 'Moderate temperature'}
        else:
            return {'level': 'Severe', 'description': 'High temperature'}
    
    def _assess_ph_severity(self, ph: float) -> Dict[str, Any]:
        """Assess pH severity"""
        if ph < 3.5:
            return {'level': 'Severe', 'description': 'Very acidic conditions'}
        elif ph < 5.0:
            return {'level': 'Moderate', 'description': 'Acidic conditions'}
        else:
            return {'level': 'Mild', 'description': 'Neutral to basic conditions'}
    
    def _assess_chloride_severity(self, chloride_ppm: float) -> Dict[str, Any]:
        """Assess chloride concentration severity"""
        if chloride_ppm > 20000:
            return {'level': 'Severe', 'description': 'High chloride concentration'}
        elif chloride_ppm > 1000:
            return {'level': 'Moderate', 'description': 'Moderate chloride concentration'}
        else:
            return {'level': 'Mild', 'description': 'Low chloride concentration'}
    
    def _get_suitable_materials(self, environmental_severity: str) -> List[str]:
        """Get suitable material categories for environmental severity"""
        if environmental_severity == 'Severe':
            return ['nickel_alloys', 'duplex_stainless', 'stainless_steel_317']
        elif environmental_severity == 'Moderate':
            return ['duplex_stainless', 'stainless_steel_316', 'stainless_steel_317', 'nickel_alloys']
        elif environmental_severity == 'Mild':
            return ['stainless_steel_316', 'stainless_steel_317', 'duplex_stainless', 'carbon_steel']
        else:
            return ['carbon_steel', 'stainless_steel_316']
    
    def _get_special_requirements(self, environmental_severity: str) -> List[str]:
        """Get special requirements for environmental severity"""
        requirements = []
        
        if environmental_severity == 'Severe':
            requirements.extend([
                "Hardness testing of all pressure-containing parts",
                "Positive Material Identification (PMI) testing",
                "Special welding procedures and qualification",
                "Post-weld heat treatment verification",
                "Enhanced quality control procedures"
            ])
        elif environmental_severity == 'Moderate':
            requirements.extend([
                "Hardness testing recommended",
                "Material certification verification",
                "Qualified welding procedures"
            ])
        elif environmental_severity == 'Mild':
            requirements.append("Standard NACE material requirements")
        
        return requirements
    
    def _get_material_recommendations(self, compliant: bool, material_category: str, 
                                   environmental_severity: str) -> List[str]:
        """Get material selection recommendations"""
        recommendations = []
        
        if not compliant:
            recommendations.extend([
                "Select alternative material with suitable hardness",
                "Review heat treatment procedures",
                "Consider upgrade to higher alloy material"
            ])
        
        if environmental_severity == 'Severe' and material_category in ['carbon_steel', 'low_alloy_steel']:
            recommendations.append("Consider upgrading to stainless steel or nickel alloy")
        
        if not recommendations:
            recommendations.append("Material selection appears suitable for application")
        
        return recommendations
    
    def _get_selection_notes(self, environmental_severity: str) -> List[str]:
        """Get material selection notes"""
        notes = [
            "All materials must meet NACE MR0175/ISO 15156 requirements",
            "Hardness testing required for all pressure-containing parts",
            "Material certificates must be verified"
        ]
        
        if environmental_severity in ['Severe', 'Moderate']:
            notes.extend([
                "Consider corrosion allowance in design",
                "Regular inspection and monitoring recommended",
                "Welding procedures must be qualified for sour service"
            ])
        
        return notes
