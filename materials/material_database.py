"""
Material Database Module
Comprehensive material properties and selection database

Features:
- Material property database for common valve materials
- Temperature-dependent properties
- Corrosion resistance data
- Material selection guidance
"""

from typing import Dict, Any, List, Optional

class MaterialDatabase:
    """Comprehensive material database for valve applications"""
    
    def __init__(self):
        self.materials = {
            'A216_WCB': {
                'name': 'Carbon Steel (WCB)',
                'category': 'Carbon Steel',
                'composition': {'C': 0.30, 'Mn': 1.0, 'Si': 0.60, 'P': 0.035, 'S': 0.035},
                'mechanical_properties': {
                    'yield_strength_mpa': 248,
                    'tensile_strength_mpa': 485,
                    'elongation_percent': 22,
                    'hardness_bhn_max': 187
                },
                'temperature_limits': {
                    'min_temp_c': -29,
                    'max_temp_c': 425
                },
                'corrosion_resistance': 'Poor',
                'sour_service': 'Limited',
                'applications': ['General service', 'Water', 'Steam', 'Oil'],
                'cost_factor': 1.0
            },
            'A351_CF8M': {
                'name': 'Stainless Steel 316 (CF8M)',
                'category': 'Stainless Steel',
                'composition': {'C': 0.08, 'Cr': 19.0, 'Ni': 10.0, 'Mo': 2.5},
                'mechanical_properties': {
                    'yield_strength_mpa': 205,
                    'tensile_strength_mpa': 515,
                    'elongation_percent': 40,
                    'hardness_bhn_max': 217
                },
                'temperature_limits': {
                    'min_temp_c': -196,
                    'max_temp_c': 815
                },
                'corrosion_resistance': 'Excellent',
                'sour_service': 'Suitable',
                'applications': ['Chemical processing', 'Marine', 'Food grade', 'Pharmaceuticals'],
                'cost_factor': 3.5
            },
            'A351_CF3M': {
                'name': 'Stainless Steel 316L (CF3M)',
                'category': 'Stainless Steel',
                'composition': {'C': 0.03, 'Cr': 19.0, 'Ni': 12.0, 'Mo': 2.5},
                'mechanical_properties': {
                    'yield_strength_mpa': 170,
                    'tensile_strength_mpa': 485,
                    'elongation_percent': 45,
                    'hardness_bhn_max': 217
                },
                'temperature_limits': {
                    'min_temp_c': -196,
                    'max_temp_c': 815
                },
                'corrosion_resistance': 'Excellent',
                'sour_service': 'Suitable',
                'applications': ['Low carbon applications', 'Welded constructions', 'Cryogenic'],
                'cost_factor': 4.0
            },
            'A890_4A': {
                'name': 'Duplex Stainless Steel (2205)',
                'category': 'Duplex Stainless',
                'composition': {'C': 0.03, 'Cr': 22.0, 'Ni': 5.5, 'Mo': 3.0, 'N': 0.17},
                'mechanical_properties': {
                    'yield_strength_mpa': 450,
                    'tensile_strength_mpa': 655,
                    'elongation_percent': 25,
                    'hardness_bhn_max': 293
                },
                'temperature_limits': {
                    'min_temp_c': -50,
                    'max_temp_c': 315
                },
                'corrosion_resistance': 'Excellent',
                'sour_service': 'Excellent',
                'applications': ['Oil & gas', 'Chemical processing', 'Marine', 'High strength'],
                'cost_factor': 5.0
            },
            'Inconel_625': {
                'name': 'Inconel 625',
                'category': 'Nickel Alloy',
                'composition': {'Ni': 58.0, 'Cr': 21.5, 'Mo': 9.0, 'Nb': 3.6},
                'mechanical_properties': {
                    'yield_strength_mpa': 415,
                    'tensile_strength_mpa': 825,
                    'elongation_percent': 30,
                    'hardness_bhn_max': 269
                },
                'temperature_limits': {
                    'min_temp_c': -196,
                    'max_temp_c': 980
                },
                'corrosion_resistance': 'Excellent',
                'sour_service': 'Excellent',
                'applications': ['Severe service', 'High temperature', 'Highly corrosive'],
                'cost_factor': 15.0
            }
        }
        
        self.selection_criteria = {
            'temperature': {
                'cryogenic': {'min': -196, 'max': -50, 'materials': ['A351_CF8M', 'A351_CF3M']},
                'low': {'min': -50, 'max': 100, 'materials': ['A216_WCB', 'A351_CF8M', 'A351_CF3M', 'A890_4A']},
                'moderate': {'min': 100, 'max': 400, 'materials': ['A216_WCB', 'A351_CF8M', 'A351_CF3M']},
                'high': {'min': 400, 'max': 800, 'materials': ['A351_CF8M', 'A351_CF3M', 'Inconel_625']},
                'very_high': {'min': 800, 'max': 1000, 'materials': ['Inconel_625']}
            },
            'service_type': {
                'clean_water': ['A216_WCB', 'A351_CF8M'],
                'seawater': ['A351_CF8M', 'A351_CF3M', 'A890_4A'],
                'acids': ['A351_CF8M', 'A351_CF3M', 'Inconel_625'],
                'caustic': ['A351_CF8M', 'A351_CF3M'],
                'hydrocarbons': ['A216_WCB', 'A351_CF8M', 'A890_4A'],
                'sour_gas': ['A351_CF8M', 'A890_4A', 'Inconel_625']
            }
        }
    
    def get_material_properties(self, material_code: str) -> Dict[str, Any]:
        """Get complete material properties"""
        return self.materials.get(material_code, {})
    
    def recommend_materials(self, temperature_c: float, service_type: str, 
                          pressure_bar: float = 0, sour_service: bool = False,
                          budget_factor: float = 1.0) -> Dict[str, Any]:
        """Recommend suitable materials based on service conditions"""
        
        suitable_materials = []
        
        # Temperature screening
        temp_suitable = []
        for material_code, properties in self.materials.items():
            temp_limits = properties['temperature_limits']
            if temp_limits['min_temp_c'] <= temperature_c <= temp_limits['max_temp_c']:
                temp_suitable.append(material_code)
        
        # Service type screening
        service_suitable = self.selection_criteria['service_type'].get(service_type, list(self.materials.keys()))
        
        # Combine temperature and service requirements
        basic_suitable = list(set(temp_suitable) & set(service_suitable))
        
        # Sour service screening
        if sour_service:
            sour_suitable = [code for code in basic_suitable 
                           if self.materials[code]['sour_service'] in ['Suitable', 'Excellent']]
        else:
            sour_suitable = basic_suitable
        
        # Budget screening
        budget_suitable = []
        for material_code in sour_suitable:
            cost_factor = self.materials[material_code]['cost_factor']
            if cost_factor <= budget_factor * 5.0:  # Allow 5x budget factor
                budget_suitable.append(material_code)
        
        # Rank materials
        ranked_materials = []
        for material_code in budget_suitable:
            material = self.materials[material_code]
            
            # Calculate suitability score
            score = self._calculate_suitability_score(
                material, temperature_c, service_type, sour_service, budget_factor
            )
            
            ranked_materials.append({
                'material_code': material_code,
                'material_name': material['name'],
                'category': material['category'],
                'suitability_score': score,
                'cost_factor': material['cost_factor'],
                'corrosion_resistance': material['corrosion_resistance'],
                'sour_service_rating': material['sour_service'],
                'temperature_margin_c': min(
                    temperature_c - material['temperature_limits']['min_temp_c'],
                    material['temperature_limits']['max_temp_c'] - temperature_c
                ),
                'applications': material['applications']
            })
        
        # Sort by suitability score
        ranked_materials.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return {
            'recommended_materials': ranked_materials,
            'selection_criteria': {
                'temperature_c': temperature_c,
                'service_type': service_type,
                'sour_service': sour_service,
                'budget_factor': budget_factor
            },
            'selection_notes': self._get_selection_notes(service_type, sour_service, temperature_c)
        }
    
    def compare_materials(self, material_codes: List[str]) -> Dict[str, Any]:
        """Compare multiple materials side by side"""
        
        comparison = {}
        
        for code in material_codes:
            if code in self.materials:
                material = self.materials[code]
                comparison[code] = {
                    'name': material['name'],
                    'category': material['category'],
                    'yield_strength': material['mechanical_properties']['yield_strength_mpa'],
                    'tensile_strength': material['mechanical_properties']['tensile_strength_mpa'],
                    'min_temp': material['temperature_limits']['min_temp_c'],
                    'max_temp': material['temperature_limits']['max_temp_c'],
                    'corrosion_resistance': material['corrosion_resistance'],
                    'sour_service': material['sour_service'],
                    'cost_factor': material['cost_factor'],
                    'applications': material['applications']
                }
        
        return comparison
    
    def _calculate_suitability_score(self, material: Dict[str, Any], temperature_c: float,
                                   service_type: str, sour_service: bool, budget_factor: float) -> float:
        """Calculate material suitability score (0-100)"""
        
        score = 50  # Base score
        
        # Temperature suitability (0-20 points)
        temp_limits = material['temperature_limits']
        temp_range = temp_limits['max_temp_c'] - temp_limits['min_temp_c']
        temp_margin = min(
            temperature_c - temp_limits['min_temp_c'],
            temp_limits['max_temp_c'] - temperature_c
        )
        temp_score = min(20, (temp_margin / temp_range) * 20) if temp_range > 0 else 10
        score += temp_score
        
        # Corrosion resistance (0-20 points)
        corr_scores = {'Poor': 5, 'Fair': 10, 'Good': 15, 'Excellent': 20}
        score += corr_scores.get(material['corrosion_resistance'], 10)
        
        # Sour service (0-15 points if required)
        if sour_service:
            sour_scores = {'Not suitable': 0, 'Limited': 5, 'Suitable': 10, 'Excellent': 15}
            score += sour_scores.get(material['sour_service'], 0)
        
        # Cost factor (0-15 points, higher score for lower cost)
        cost_score = max(0, 15 - (material['cost_factor'] - 1) * 2)
        score += cost_score
        
        return min(100, max(0, score))
    
    def _get_selection_notes(self, service_type: str, sour_service: bool, temperature_c: float) -> List[str]:
        """Get material selection notes and recommendations"""
        
        notes = []
        
        if sour_service:
            notes.append("NACE MR0175 compliance required for sour service")
            notes.append("Hardness testing mandatory for all pressure-containing parts")
        
        if temperature_c > 400:
            notes.append("High temperature service - consider thermal expansion effects")
            notes.append("Special welding procedures may be required")
        
        if temperature_c < 0:
            notes.append("Low temperature service - verify impact toughness requirements")
        
        if service_type in ['seawater', 'acids']:
            notes.append("Corrosion allowance should be considered in design")
            notes.append("Regular inspection schedule recommended")
        
        notes.append("Final material selection must consider all service conditions")
        notes.append("Consult material manufacturer for specific application guidance")
        
        return notes
    
    def get_available_materials(self) -> List[Dict[str, str]]:
        """Get list of all available materials"""
        
        materials_list = []
        for code, properties in self.materials.items():
            materials_list.append({
                'code': code,
                'name': properties['name'],
                'category': properties['category'],
                'cost_factor': properties['cost_factor']
            })
        
        return sorted(materials_list, key=lambda x: x['cost_factor'])
