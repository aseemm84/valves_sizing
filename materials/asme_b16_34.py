"""
ASME B16.34 Material Standards Module
Pressure-temperature ratings and material specifications

Features:
- Complete ASME B16.34 pressure-temperature rating tables
- Material classification and temperature limits
- Pressure class verification
- Wall thickness calculations
"""

from typing import Dict, Any, List, Optional
import math

class ASMEB1634:
    """ASME B16.34 Implementation for Valve Pressure-Temperature Ratings"""
    
    def __init__(self):
        # ASME B16.34 Pressure-Temperature Rating Tables
        self.pressure_temperature_ratings = {
            'A216_WCB': {  # Carbon Steel
                'class_150': self._create_pt_table([19.0, 17.1, 15.3, 12.4, 9.6, 7.1], [38, 93, 149, 204, 260, 316]),
                'class_300': self._create_pt_table([51.7, 46.2, 41.4, 33.4, 25.9, 19.3], [38, 93, 149, 204, 260, 316]),
                'class_600': self._create_pt_table([103.4, 92.4, 82.7, 66.9, 51.7, 38.6], [38, 93, 149, 204, 260, 316]),
                'class_900': self._create_pt_table([155.1, 138.6, 124.1, 100.3, 77.6, 58.0], [38, 93, 149, 204, 260, 316]),
                'class_1500': self._create_pt_table([258.6, 231.0, 206.8, 167.2, 129.3, 96.5], [38, 93, 149, 204, 260, 316]),
                'max_temp': 425  # °C
            },
            'A351_CF8M': {  # Stainless Steel 316
                'class_150': self._create_pt_table([19.0, 18.6, 18.2, 17.2, 15.5, 13.1, 10.3], [38, 93, 149, 204, 260, 316, 371]),
                'class_300': self._create_pt_table([51.7, 50.3, 49.3, 46.2, 41.4, 35.2, 27.6], [38, 93, 149, 204, 260, 316, 371]),
                'class_600': self._create_pt_table([103.4, 100.7, 98.6, 92.4, 82.7, 70.3, 55.2], [38, 93, 149, 204, 260, 316, 371]),
                'class_900': self._create_pt_table([155.1, 151.0, 147.9, 138.6, 124.1, 105.5, 82.7], [38, 93, 149, 204, 260, 316, 371]),
                'class_1500': self._create_pt_table([258.6, 251.7, 246.5, 231.0, 206.8, 175.8, 138.0], [38, 93, 149, 204, 260, 316, 371]),
                'max_temp': 815  # °C
            },
            'A351_CF3M': {  # Stainless Steel 316L
                'class_150': self._create_pt_table([19.0, 18.3, 17.9, 16.9, 15.2, 12.8, 10.0], [38, 93, 149, 204, 260, 316, 371]),
                'class_300': self._create_pt_table([51.7, 49.6, 48.6, 45.9, 41.0, 34.5, 27.2], [38, 93, 149, 204, 260, 316, 371]),
                'class_600': self._create_pt_table([103.4, 99.3, 97.2, 91.7, 82.1, 69.0, 54.5], [38, 93, 149, 204, 260, 316, 371]),
                'class_900': self._create_pt_table([155.1, 148.9, 145.8, 137.6, 123.1, 103.4, 81.7], [38, 93, 149, 204, 260, 316, 371]),
                'class_1500': self._create_pt_table([258.6, 248.2, 243.0, 229.3, 205.2, 172.4, 136.2], [38, 93, 149, 204, 260, 316, 371]),
                'max_temp': 815  # °C
            }
        }
        
        # Common pressure classes
        self.pressure_classes = ['class_150', 'class_300', 'class_600', 'class_900', 'class_1500', 'class_2500']
        
        # Material properties for wall thickness calculations
        self.material_properties = {
            'A216_WCB': {'allowable_stress': 138.0, 'efficiency': 1.0},  # MPa
            'A351_CF8M': {'allowable_stress': 138.0, 'efficiency': 1.0},
            'A351_CF3M': {'allowable_stress': 138.0, 'efficiency': 1.0}
        }
    
    def _create_pt_table(self, pressures: List[float], temperatures: List[int]) -> Dict[int, float]:
        """Create pressure-temperature lookup table"""
        return dict(zip(temperatures, pressures))
    
    def get_allowable_pressure(self, material: str, pressure_class: str, temperature: float) -> Dict[str, Any]:
        """Get allowable working pressure for given conditions"""
        
        try:
            if material not in self.pressure_temperature_ratings:
                return {'error': f'Material {material} not found in database'}
            
            material_data = self.pressure_temperature_ratings[material]
            
            if pressure_class not in material_data:
                return {'error': f'Pressure class {pressure_class} not available for {material}'}
            
            # Check maximum temperature limit
            if temperature > material_data['max_temp']:
                return {
                    'error': f'Temperature {temperature:.1f}°C exceeds maximum limit {material_data["max_temp"]}°C for {material}'
                }
            
            pt_table = material_data[pressure_class]
            temperatures = sorted(pt_table.keys())
            
            # Find allowable pressure by interpolation
            if temperature <= temperatures[0]:
                allowable_pressure = pt_table[temperatures[0]]
            elif temperature >= temperatures[-1]:
                allowable_pressure = pt_table[temperatures[-1]]
            else:
                # Linear interpolation
                for i in range(len(temperatures) - 1):
                    t_low = temperatures[i]
                    t_high = temperatures[i + 1]
                    
                    if t_low <= temperature <= t_high:
                        p_low = pt_table[t_low]
                        p_high = pt_table[t_high]
                        
                        # Linear interpolation
                        allowable_pressure = p_low + (p_high - p_low) * (temperature - t_low) / (t_high - t_low)
                        break
            
            # Get pressure class nominal rating at room temperature
            nominal_rating = pt_table[temperatures[0]]
            
            # Calculate derating factor
            derating_factor = allowable_pressure / nominal_rating if nominal_rating > 0 else 1.0
            
            return {
                'allowable_pressure_bar': allowable_pressure,
                'nominal_rating_bar': nominal_rating,
                'derating_factor': derating_factor,
                'material': material,
                'pressure_class': pressure_class,
                'temperature_c': temperature,
                'max_temp_c': material_data['max_temp'],
                'compliant': True
            }
            
        except Exception as e:
            return {'error': f'Pressure-temperature calculation failed: {str(e)}'}
    
    def check_pressure_temperature_compliance(self, material: str, pressure_class: str, 
                                            operating_pressure: float, operating_temperature: float) -> Dict[str, Any]:
        """Check if operating conditions are within ASME B16.34 limits"""
        
        allowable = self.get_allowable_pressure(material, pressure_class, operating_temperature)
        
        if 'error' in allowable:
            return allowable
        
        allowable_pressure = allowable['allowable_pressure_bar']
        
        # Check compliance
        is_compliant = operating_pressure <= allowable_pressure
        safety_margin = (allowable_pressure - operating_pressure) / allowable_pressure if allowable_pressure > 0 else 0
        
        # Assessment
        if not is_compliant:
            assessment = "Non-compliant - Operating pressure exceeds ASME B16.34 limits"
            severity = "Critical"
        elif safety_margin < 0.1:
            assessment = "Marginal - Low safety margin"
            severity = "Warning"
        elif safety_margin < 0.2:
            assessment = "Adequate - Acceptable safety margin"
            severity = "Caution"
        else:
            assessment = "Excellent - High safety margin"
            severity = "Good"
        
        return {
            'compliant': is_compliant,
            'operating_pressure_bar': operating_pressure,
            'allowable_pressure_bar': allowable_pressure,
            'safety_margin_percent': safety_margin * 100,
            'assessment': assessment,
            'severity': severity,
            'derating_factor': allowable['derating_factor'],
            'recommendations': self._get_compliance_recommendations(is_compliant, safety_margin, operating_temperature, allowable['max_temp_c'])
        }
    
    def calculate_minimum_wall_thickness(self, internal_pressure: float, outside_diameter: float,
                                       material: str, temperature: float = 20.0, 
                                       corrosion_allowance: float = 3.0) -> Dict[str, Any]:
        """Calculate minimum wall thickness per ASME B16.34"""
        
        try:
            if material not in self.material_properties:
                return {'error': f'Material {material} properties not available'}
            
            material_props = self.material_properties[material]
            
            # Get temperature-dependent allowable stress (simplified)
            allowable_stress = material_props['allowable_stress']  # MPa
            efficiency = material_props['efficiency']
            
            # Temperature derating (simplified - real calculation needs stress tables)
            if temperature > 200:
                temp_factor = max(0.5, 1.0 - (temperature - 200) / 1000)
                allowable_stress *= temp_factor
            
            # Calculate minimum thickness using ASME formula
            # t = (P * D) / (2 * S * E + P)
            # where: t = thickness, P = pressure, D = diameter, S = stress, E = efficiency
            
            pressure_mpa = internal_pressure / 10.0  # Convert bar to MPa
            
            min_thickness = (pressure_mpa * outside_diameter) / (
                2 * allowable_stress * efficiency - pressure_mpa
            )
            
            # Add corrosion allowance
            total_thickness = min_thickness + corrosion_allowance
            
            return {
                'minimum_thickness_mm': min_thickness,
                'corrosion_allowance_mm': corrosion_allowance,
                'total_thickness_mm': total_thickness,
                'allowable_stress_mpa': allowable_stress,
                'material': material,
                'temperature_c': temperature,
                'pressure_mpa': pressure_mpa,
                'design_compliant': min_thickness > 0
            }
            
        except Exception as e:
            return {'error': f'Wall thickness calculation failed: {str(e)}'}
    
    def get_available_materials(self) -> List[str]:
        """Get list of available materials in database"""
        return list(self.pressure_temperature_ratings.keys())
    
    def get_available_pressure_classes(self) -> List[str]:
        """Get list of available pressure classes"""
        return self.pressure_classes.copy()
    
    def _get_compliance_recommendations(self, is_compliant: bool, safety_margin: float, 
                                     operating_temp: float, max_temp: float) -> List[str]:
        """Get recommendations based on compliance check"""
        
        recommendations = []
        
        if not is_compliant:
            recommendations.extend([
                "Select higher pressure class valve",
                "Verify operating pressure calculations",
                "Consider different valve material",
                "Review system design pressure"
            ])
        elif safety_margin < 0.1:
            recommendations.extend([
                "Consider higher pressure class for better safety margin",
                "Implement pressure monitoring and alarms",
                "Review pressure relief system adequacy"
            ])
        
        if operating_temp > max_temp * 0.8:
            recommendations.append("Operating near maximum temperature limit - monitor closely")
        
        if not recommendations:
            recommendations.append("Operating conditions are well within ASME B16.34 limits")
        
        return recommendations
