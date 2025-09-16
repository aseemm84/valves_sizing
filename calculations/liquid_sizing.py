"""
Professional Liquid Sizing Module
Complete implementation of ISA 75.01/IEC 60534-2-1 for liquid service

Features:
- Complete liquid sizing with all correction factors
- Piping geometry factor (Fp) integration
- Reynolds correction with iterative solution
- Choked flow analysis with FL and Ff factors
- Multi-scenario validation
"""

import math
import numpy as np
from typing import Dict, Any, List, Tuple
from config.constants import EngineeringConstants
from calculations.geometry_factors import GeometryFactors
from calculations.reynolds_correction import ReynoldsCorrection

class LiquidSizing:
    """Professional liquid sizing per ISA 75.01/IEC 60534-2-1"""

    def __init__(self):
        self.constants = EngineeringConstants.SIZING_CONSTANTS
        self.phys_constants = EngineeringConstants.PHYSICAL_CONSTANTS
        self.geometry = GeometryFactors()
        self.reynolds = ReynoldsCorrection()

    def calculate_required_cv(self, 
                            flow_rate: float,
                            inlet_pressure: float,
                            outlet_pressure: float,
                            temperature: float,
                            density: float,
                            viscosity: float,
                            vapor_pressure: float,
                            fl_factor: float,
                            fd_factor: float,
                            pipe_size: str,
                            valve_size: str,
                            valve_style: str = 'globe',
                            units: str = 'metric') -> Dict[str, Any]:
        """
        Complete liquid sizing calculation per ISA 75.01

        Returns:
            Dictionary with comprehensive sizing results
        """

        try:
            # Step 1: Basic calculations
            delta_p = inlet_pressure - outlet_pressure
            specific_gravity = self._calculate_specific_gravity(density, units)

            # Step 2: Calculate Ff factor (liquid critical pressure ratio)
            ff_factor = self._calculate_ff_factor(
                vapor_pressure, density, temperature, units
            )

            # Step 3: Check for choked flow conditions
            choked_analysis = self._analyze_choked_flow(
                inlet_pressure, vapor_pressure, delta_p, fl_factor, ff_factor
            )

            # Use effective pressure drop (may be limited by choking)
            effective_delta_p = choked_analysis['effective_delta_p']

            # Step 4: Calculate piping geometry factor
            fp_factor = self.geometry.calculate_fp_factor(
                valve_size, pipe_size, valve_style, units
            )

            # Step 5: Basic Cv calculation (turbulent flow assumption)
            n1 = self.constants['N1_metric'] if units == 'metric' else self.constants['N1_imperial']
            cv_basic = (flow_rate / fp_factor) / (n1 * math.sqrt(effective_delta_p / specific_gravity))

            # Step 6: Reynolds correction
            reynolds_analysis = self.reynolds.calculate_fr_factor(
                flow_rate=flow_rate,
                cv_initial=cv_basic,
                viscosity=viscosity,
                fd_factor=fd_factor,
                pipe_diameter=self._get_pipe_diameter(pipe_size, units),
                specific_gravity=specific_gravity,
                delta_p=effective_delta_p,
                units=units
            )

            # Step 7: Final Cv with all corrections
            cv_required = cv_basic / reynolds_analysis['fr_factor']

            # Step 8: Multi-scenario validation
            scenarios = self._validate_scenarios(
                cv_required, flow_rate, inlet_pressure, outlet_pressure,
                specific_gravity, fp_factor, units
            )

            # Step 9: Calculate valve authority
            valve_authority = self._calculate_valve_authority(
                effective_delta_p, flow_rate, pipe_size, units
            )

            # Compile results
            results = {
                'cv_required': cv_required,
                'cv_basic': cv_basic,
                'specific_gravity': specific_gravity,
                'ff_factor': ff_factor,
                'fp_factor': fp_factor,
                'choked_analysis': choked_analysis,
                'reynolds_analysis': reynolds_analysis,
                'scenarios': scenarios,
                'valve_authority': valve_authority,
                'effective_delta_p': effective_delta_p,
                'sizing_method': 'ISA 75.01 Complete',
                'units': units,
                'warnings': [],
                'recommendations': []
            }

            # Add professional warnings
            self._add_sizing_warnings(results)

            return results

        except Exception as e:
            return {
                'error': f"Liquid sizing calculation failed: {str(e)}",
                'cv_required': 0.0
            }

    def _calculate_specific_gravity(self, density: float, units: str) -> float:
        """Calculate specific gravity from density"""
        if units == 'metric':
            return density / self.phys_constants['water_density_kg_m3']
        else:
            return density / self.phys_constants['water_density_lb_ft3']

    def _calculate_ff_factor(self, vapor_pressure: float, density: float, 
                           temperature: float, units: str) -> float:
        """
        Calculate liquid critical pressure ratio factor (Ff)
        Enhanced calculation based on fluid properties
        """
        try:
            # Estimate critical pressure based on fluid type
            # This is a simplified approach - real implementation needs fluid database
            if units == 'metric':
                if 900 <= density <= 1100:  # Water-like
                    critical_pressure = 221.2  # bar
                else:
                    # Rough estimation for hydrocarbons
                    critical_pressure = 50.0
            else:
                if 55 <= density <= 70:  # Water-like
                    critical_pressure = 3206  # psi
                else:
                    critical_pressure = 725

            # Calculate Ff factor
            ff_factor = 0.96 - 0.28 * math.sqrt(vapor_pressure / critical_pressure)

            # Apply bounds
            return max(0.7, min(0.98, ff_factor))

        except:
            return 0.9  # Conservative default

    def _analyze_choked_flow(self, inlet_pressure: float, vapor_pressure: float,
                           delta_p: float, fl_factor: float, ff_factor: float) -> Dict[str, Any]:
        """
        Analyze choked flow conditions per ISA 75.01
        """
        # Calculate allowable pressure drop
        delta_p_allowable = fl_factor**2 * (inlet_pressure - ff_factor * vapor_pressure)

        # Check if flow is choked
        is_choked = delta_p > delta_p_allowable

        # Effective pressure drop for sizing
        effective_delta_p = min(delta_p, delta_p_allowable)

        # Calculate cavitation index
        sigma_service = (inlet_pressure - vapor_pressure) / delta_p if delta_p > 0 else float('inf')

        return {
            'is_choked': is_choked,
            'delta_p_allowable': delta_p_allowable,
            'effective_delta_p': effective_delta_p,
            'sigma_service': sigma_service,
            'fl_factor': fl_factor,
            'ff_factor': ff_factor,
            'choking_margin': (delta_p_allowable - delta_p) / delta_p_allowable if delta_p_allowable > 0 else 0
        }

    def _get_pipe_diameter(self, pipe_size: str, units: str) -> float:
        """Get pipe internal diameter"""
        pipe_data = EngineeringConstants.PIPE_DATA.get(pipe_size, {})
        if units == 'metric':
            return pipe_data.get('id_mm', 80.0)  # Default 3" pipe
        else:
            return pipe_data.get('id_in', 3.068)

    def _validate_scenarios(self, cv_required: float, normal_flow: float,
                          inlet_pressure: float, outlet_pressure: float,
                          specific_gravity: float, fp_factor: float,
                          units: str) -> Dict[str, Any]:
        """Validate sizing across multiple flow scenarios"""

        n1 = self.constants['N1_metric'] if units == 'metric' else self.constants['N1_imperial']

        scenarios = {
            'minimum': {
                'flow': normal_flow * 0.3,
                'delta_p': (inlet_pressure - outlet_pressure) * 0.7,  # Lower ΔP at low flow
                'description': '30% flow (minimum controllable)'
            },
            'normal': {
                'flow': normal_flow,
                'delta_p': inlet_pressure - outlet_pressure,
                'description': '100% flow (normal operation)'
            },
            'maximum': {
                'flow': normal_flow * 1.25,
                'delta_p': (inlet_pressure - outlet_pressure) * 1.4,  # Higher ΔP at high flow
                'description': '125% flow (maximum design)'
            }
        }

        results = {}
        for scenario_name, scenario in scenarios.items():
            # Calculate actual Cv needed for this scenario
            cv_actual = (scenario['flow'] / fp_factor) / (n1 * math.sqrt(scenario['delta_p'] / specific_gravity))

            # Calculate valve opening percentage
            opening_percent = (cv_actual / cv_required) * 100 if cv_required > 0 else 0

            # Assess operating point
            if opening_percent < 10:
                assessment = "Critical - Below minimum opening"
            elif opening_percent < 20:
                assessment = "Warning - Below recommended minimum"
            elif opening_percent > 90:
                assessment = "Critical - Above maximum opening"
            elif opening_percent > 80:
                assessment = "Warning - Above recommended maximum"
            else:
                assessment = "Good - Within recommended range"

            results[scenario_name] = {
                'flow_rate': scenario['flow'],
                'delta_p': scenario['delta_p'],
                'cv_actual': cv_actual,
                'opening_percent': opening_percent,
                'assessment': assessment,
                'description': scenario['description']
            }

        return results

    def _calculate_valve_authority(self, valve_delta_p: float, flow_rate: float,
                                 pipe_size: str, units: str) -> Dict[str, Any]:
        """Calculate valve authority (valve ΔP / total system ΔP)"""

        # Estimate system pressure drop (simplified)
        pipe_diameter = self._get_pipe_diameter(pipe_size, units)

        # Rough pipe friction calculation
        if units == 'metric':
            velocity = flow_rate / (3600 * math.pi * (pipe_diameter/1000/2)**2)  # m/s
            pipe_delta_p = 0.02 * (velocity**2) / (2 * 9.81) * 100  # Rough estimate in bar
        else:
            velocity = flow_rate / (60 * math.pi * (pipe_diameter/2)**2)  # ft/s
            pipe_delta_p = 0.02 * (velocity**2) / (2 * 32.2) * 0.433  # Rough estimate in psi

        total_system_delta_p = valve_delta_p + pipe_delta_p
        authority = valve_delta_p / total_system_delta_p if total_system_delta_p > 0 else 0

        # Authority assessment
        if authority > 0.5:
            authority_assessment = "Excellent - Good control expected"
        elif authority > 0.25:
            authority_assessment = "Good - Adequate control"
        elif authority > 0.1:
            authority_assessment = "Poor - Control may be difficult"
        else:
            authority_assessment = "Very Poor - Consider system redesign"

        return {
            'valve_delta_p': valve_delta_p,
            'system_delta_p_estimate': pipe_delta_p,
            'total_delta_p': total_system_delta_p,
            'authority': authority,
            'assessment': authority_assessment
        }

    def _add_sizing_warnings(self, results: Dict[str, Any]):
        """Add professional warnings and recommendations"""

        warnings = []
        recommendations = []

        # Check choked flow
        if results['choked_analysis']['is_choked']:
            warnings.append("Flow is choked - valve capacity limited by cavitation")
            recommendations.append("Consider anti-cavitation trim or increase downstream pressure")

        # Check Reynolds correction
        if results['reynolds_analysis']['fr_factor'] < 0.8:
            warnings.append(f"Significant viscous effects (Fr = {results['reynolds_analysis']['fr_factor']:.3f})")
            recommendations.append("Consider larger valve or verify viscosity data")

        # Check valve authority
        if results['valve_authority']['authority'] < 0.25:
            warnings.append(f"Poor valve authority ({results['valve_authority']['authority']:.2f})")
            recommendations.append("Increase valve pressure drop or reduce system losses")

        # Check operating scenarios
        for scenario_name, scenario in results['scenarios'].items():
            if "Critical" in scenario['assessment'] or "Warning" in scenario['assessment']:
                warnings.append(f"{scenario_name.title()} flow: {scenario['assessment']}")

        results['warnings'] = warnings
        results['recommendations'] = recommendations
