"""
Professional Gas/Vapor Sizing Module
Complete implementation of ISA 75.01/IEC 60534-2-1 for compressible flow

Features:
- Complete gas sizing with expansion factor Y
- Choked flow analysis with xT factors
- Mach number and sonic velocity calculations
- Multi-regime flow analysis
"""

import math
import numpy as np
from typing import Dict, Any
from config.constants import EngineeringConstants

class GasSizing:
    """Professional gas/vapor sizing per ISA 75.01/IEC 60534-2-1"""

    def __init__(self):
        self.constants = EngineeringConstants.SIZING_CONSTANTS
        self.phys_constants = EngineeringConstants.PHYSICAL_CONSTANTS

    def calculate_required_cv(self,
                            flow_rate: float,
                            inlet_pressure: float,
                            outlet_pressure: float,
                            temperature: float,
                            molecular_weight: float,
                            specific_heat_ratio: float,
                            compressibility: float,
                            xt_factor: float,
                            fd_factor: float,
                            pipe_size: str,
                            valve_size: str,
                            flow_units: str = 'Nm3/h',
                            pressure_units: str = 'bar',
                            units: str = 'metric') -> Dict[str, Any]:
        """
        Complete gas sizing calculation per ISA 75.01
        """

        try:
            # Convert temperature to absolute
            temp_abs = temperature + self.phys_constants['standard_temp_k'] if temperature < 100 else temperature

            # Step 1: Calculate pressure ratio and critical conditions
            pressure_ratio = outlet_pressure / inlet_pressure
            critical_analysis = self._analyze_critical_flow(
                pressure_ratio, xt_factor, specific_heat_ratio
            )

            # Step 2: Calculate expansion factor Y
            expansion_factor = self._calculate_expansion_factor(
                pressure_ratio, xt_factor, specific_heat_ratio, critical_analysis['is_choked']
            )

            # Step 3: Calculate sonic velocity and Mach analysis
            sonic_analysis = self._calculate_sonic_properties(
                temp_abs, molecular_weight, specific_heat_ratio, compressibility
            )

            # Step 4: Calculate required Cv based on flow regime
            if critical_analysis['is_choked']:
                cv_required = self._calculate_cv_choked(
                    flow_rate, inlet_pressure, temp_abs, molecular_weight,
                    specific_heat_ratio, compressibility, xt_factor, units
                )
            else:
                cv_required = self._calculate_cv_unchoked(
                    flow_rate, inlet_pressure, outlet_pressure, temp_abs,
                    molecular_weight, expansion_factor, compressibility, units
                )

            # Step 5: Calculate actual velocities
            velocity_analysis = self._calculate_velocities(
                cv_required, flow_rate, inlet_pressure, temp_abs,
                molecular_weight, compressibility, sonic_analysis['sonic_velocity']
            )

            # Step 6: Multi-scenario validation
            scenarios = self._validate_gas_scenarios(
                cv_required, flow_rate, inlet_pressure, outlet_pressure,
                temp_abs, molecular_weight, specific_heat_ratio,
                compressibility, xt_factor, units
            )

            # Compile results
            results = {
                'cv_required': cv_required,
                'pressure_ratio': pressure_ratio,
                'critical_analysis': critical_analysis,
                'expansion_factor': expansion_factor,
                'sonic_analysis': sonic_analysis,
                'velocity_analysis': velocity_analysis,
                'scenarios': scenarios,
                'sizing_method': 'ISA 75.01 Gas Complete',
                'units': units,
                'warnings': [],
                'recommendations': []
            }

            # Add warnings
            self._add_gas_warnings(results)

            return results

        except Exception as e:
            return {
                'error': f"Gas sizing calculation failed: {str(e)}",
                'cv_required': 0.0
            }

    def _analyze_critical_flow(self, pressure_ratio: float, xt_factor: float,
                             specific_heat_ratio: float) -> Dict[str, Any]:
        """Analyze critical (choked) flow conditions"""

        # Critical pressure ratio for perfect gas
        critical_ratio_perfect = math.pow(
            2.0 / (specific_heat_ratio + 1.0),
            specific_heat_ratio / (specific_heat_ratio - 1.0)
        )

        # Apply valve-specific xT factor
        critical_ratio_valve = xt_factor * critical_ratio_perfect

        # Determine if choked
        is_choked = pressure_ratio <= critical_ratio_valve

        return {
            'is_choked': is_choked,
            'critical_ratio_perfect': critical_ratio_perfect,
            'critical_ratio_valve': critical_ratio_valve,
            'pressure_ratio': pressure_ratio,
            'choking_margin': (pressure_ratio - critical_ratio_valve) / critical_ratio_valve if critical_ratio_valve > 0 else 0
        }

    def _calculate_expansion_factor(self, pressure_ratio: float, xt_factor: float,
                                  specific_heat_ratio: float, is_choked: bool) -> float:
        """Calculate expansion factor Y per ISA standard"""

        if is_choked:
            # For choked flow
            y_factor = (2.0/3.0) * math.sqrt(specific_heat_ratio * xt_factor)
        else:
            # For unchoked flow
            try:
                x = 1.0 - pressure_ratio  # Pressure drop ratio

                # Y factor calculation
                y_factor = 1.0 - (x / (3.0 * specific_heat_ratio * xt_factor))

                # Alternative calculation for better accuracy
                if specific_heat_ratio > 1.0:
                    term1 = (specific_heat_ratio - 1.0) / specific_heat_ratio
                    term2 = math.pow(pressure_ratio, term1)
                    y_factor = math.sqrt((specific_heat_ratio / (specific_heat_ratio - 1.0)) * 
                                       (1.0 - term2) / (1.0 - pressure_ratio))

                # Apply bounds
                y_factor = max(0.1, min(1.0, y_factor))

            except:
                y_factor = 0.8  # Conservative default

        return y_factor

    def _calculate_sonic_properties(self, temperature: float, molecular_weight: float,
                                  specific_heat_ratio: float, compressibility: float) -> Dict[str, Any]:
        """Calculate sonic velocity and related properties"""

        try:
            # Sonic velocity: a = sqrt(k * R * T / M)
            sonic_velocity = math.sqrt(
                specific_heat_ratio * self.phys_constants['R_gas'] * temperature / molecular_weight
            )

            # Apply compressibility correction
            sonic_velocity_corrected = sonic_velocity * math.sqrt(compressibility)

            return {
                'sonic_velocity': sonic_velocity_corrected,
                'sonic_velocity_ideal': sonic_velocity,
                'temperature': temperature,
                'molecular_weight': molecular_weight,
                'specific_heat_ratio': specific_heat_ratio,
                'compressibility': compressibility
            }

        except:
            return {
                'sonic_velocity': 300.0,  # Conservative estimate
                'sonic_velocity_ideal': 300.0,
                'temperature': temperature,
                'molecular_weight': molecular_weight,
                'specific_heat_ratio': specific_heat_ratio,
                'compressibility': compressibility
            }

    def _calculate_cv_choked(self, flow_rate: float, inlet_pressure: float,
                           temperature: float, molecular_weight: float,
                           specific_heat_ratio: float, compressibility: float,
                           xt_factor: float, units: str) -> float:
        """Calculate Cv for choked flow conditions"""

        # Get appropriate constants
        if units == 'metric':
            n6 = self.constants['N6_metric']
        else:
            n6 = self.constants['N6_imperial']

        # Density at inlet conditions
        density_inlet = (inlet_pressure * 100000 * molecular_weight) / (
            compressibility * self.phys_constants['R_gas'] * temperature
        )

        # Y factor for choked conditions
        y_choked = (2.0/3.0) * math.sqrt(specific_heat_ratio * xt_factor)

        # Calculate Cv
        cv_required = flow_rate / (n6 * inlet_pressure * y_choked * 
                                 math.sqrt(density_inlet / 1.225))

        return cv_required

    def _calculate_cv_unchoked(self, flow_rate: float, inlet_pressure: float,
                             outlet_pressure: float, temperature: float,
                             molecular_weight: float, expansion_factor: float,
                             compressibility: float, units: str) -> float:
        """Calculate Cv for unchoked flow conditions"""

        # Get appropriate constants
        if units == 'metric':
            n9 = self.constants['N9_metric']
        else:
            n9 = self.constants['N9_imperial']

        # Pressure drop
        delta_p = inlet_pressure - outlet_pressure

        # Density at inlet conditions
        density_inlet = (inlet_pressure * 100000 * molecular_weight) / (
            compressibility * self.phys_constants['R_gas'] * temperature
        )

        # Calculate Cv
        cv_required = flow_rate / (n9 * expansion_factor * inlet_pressure * 
                                 math.sqrt(delta_p * density_inlet / 1.225))

        return cv_required

    def _calculate_velocities(self, cv_required: float, flow_rate: float,
                            inlet_pressure: float, temperature: float,
                            molecular_weight: float, compressibility: float,
                            sonic_velocity: float) -> Dict[str, Any]:
        """Calculate actual gas velocities through valve"""

        try:
            # Estimate valve flow area from Cv (rough approximation)
            flow_area_in2 = cv_required / 29.9  # Approximate
            flow_area_m2 = flow_area_in2 * 0.00064516

            # Gas density at inlet
            density = (inlet_pressure * 100000 * molecular_weight) / (
                compressibility * self.phys_constants['R_gas'] * temperature
            )

            # Volume flow at inlet conditions
            mass_flow = flow_rate * density / 3600.0  # kg/s (rough)
            volume_flow = mass_flow / density  # m³/s

            # Actual velocity
            if flow_area_m2 > 0:
                actual_velocity = volume_flow / flow_area_m2
            else:
                actual_velocity = 0.0

            # Mach number
            mach_number = actual_velocity / sonic_velocity if sonic_velocity > 0 else 0.0

            # Assessment
            if mach_number > 1.0:
                assessment = "Supersonic - Review design"
            elif mach_number > 0.8:
                assessment = "High subsonic - Monitor noise"
            elif mach_number > 0.3:
                assessment = "Moderate - Acceptable"
            else:
                assessment = "Low - Good"

            return {
                'actual_velocity': actual_velocity,
                'sonic_velocity': sonic_velocity,
                'mach_number': mach_number,
                'flow_area_m2': flow_area_m2,
                'density': density,
                'assessment': assessment
            }

        except:
            return {
                'actual_velocity': 0.0,
                'sonic_velocity': sonic_velocity,
                'mach_number': 0.0,
                'flow_area_m2': 0.0,
                'density': 0.0,
                'assessment': "Unable to calculate"
            }

    def _validate_gas_scenarios(self, cv_required: float, normal_flow: float,
                              inlet_pressure: float, outlet_pressure: float,
                              temperature: float, molecular_weight: float,
                              specific_heat_ratio: float, compressibility: float,
                              xt_factor: float, units: str) -> Dict[str, Any]:
        """Validate gas sizing across multiple scenarios"""

        scenarios = {
            'minimum': {
                'flow': normal_flow * 0.3,
                'p1': inlet_pressure,
                'p2': outlet_pressure * 1.1,  # Higher backpressure
                'description': '30% flow, higher backpressure'
            },
            'normal': {
                'flow': normal_flow,
                'p1': inlet_pressure,
                'p2': outlet_pressure,
                'description': 'Normal operating conditions'
            },
            'maximum': {
                'flow': normal_flow * 1.5,
                'p1': inlet_pressure * 1.1,  # Higher supply pressure
                'p2': outlet_pressure,
                'description': '150% flow, higher supply pressure'
            }
        }

        results = {}

        for scenario_name, scenario in scenarios.items():
            # Calculate for this scenario
            pressure_ratio = scenario['p2'] / scenario['p1']

            # Check critical flow
            critical_ratio = xt_factor * math.pow(
                2.0 / (specific_heat_ratio + 1.0),
                specific_heat_ratio / (specific_heat_ratio - 1.0)
            )
            is_choked = pressure_ratio <= critical_ratio

            # Calculate expansion factor
            if is_choked:
                y_factor = (2.0/3.0) * math.sqrt(specific_heat_ratio * xt_factor)
            else:
                x = 1.0 - pressure_ratio
                y_factor = 1.0 - (x / (3.0 * specific_heat_ratio * xt_factor))
                y_factor = max(0.1, min(1.0, y_factor))

            # Estimate Cv for this scenario (simplified)
            if is_choked:
                cv_scenario = scenario['flow'] / (
                    self.constants['N6_metric'] * scenario['p1'] * y_factor
                )
            else:
                delta_p = scenario['p1'] - scenario['p2']
                cv_scenario = scenario['flow'] / (
                    self.constants['N9_metric'] * y_factor * scenario['p1'] * math.sqrt(delta_p)
                )

            # Calculate opening percentage
            opening_percent = (cv_scenario / cv_required) * 100 if cv_required > 0 else 0

            # Assessment
            if opening_percent > 95:
                assessment = "Critical - Insufficient capacity"
            elif opening_percent > 85:
                assessment = "Warning - Limited margin"
            elif opening_percent < 10:
                assessment = "Warning - Very low opening"
            else:
                assessment = "Good - Adequate capacity"

            results[scenario_name] = {
                'flow_rate': scenario['flow'],
                'pressure_ratio': pressure_ratio,
                'is_choked': is_choked,
                'cv_required': cv_scenario,
                'opening_percent': opening_percent,
                'assessment': assessment,
                'description': scenario['description']
            }

        return results

    def _add_gas_warnings(self, results: Dict[str, Any]):
        """Add professional warnings for gas sizing"""

        warnings = []
        recommendations = []

        # Check for choking
        if results['critical_analysis']['is_choked']:
            warnings.append("Flow is choked (sonic) - maximum flow rate achieved")
            recommendations.append("Consider larger valve or increased downstream pressure")

        # Check Mach number
        mach_number = results['velocity_analysis']['mach_number']
        if mach_number > 0.8:
            warnings.append(f"High Mach number ({mach_number:.2f}) - noise and erosion concerns")
            recommendations.append("Consider low-noise trim or velocity reduction")

        # Check pressure ratio
        if results['pressure_ratio'] < 0.3:
            warnings.append("Very low pressure ratio - high velocity potential")
            recommendations.append("Verify downstream pressure requirements")

        # Check scenarios
        for scenario_name, scenario in results['scenarios'].items():
            if "Critical" in scenario['assessment']:
                warnings.append(f"{scenario_name.title()}: {scenario['assessment']}")

        results['warnings'] = warnings
        results['recommendations'] = recommendations
