"""
Input Validation Module
Comprehensive validation for all process inputs

Features:
- Process parameter validation against industry limits
- Fluid property range checking
- Engineering reasonableness checks
- Safety and regulatory compliance validation
"""

from typing import Dict, Any, List
from config.constants import EngineeringConstants
from config.settings import AppSettings

class ValidationHelper:
    """Professional input validation for control valve sizing"""

    def __init__(self):
        self.limits = AppSettings.VALIDATION_LIMITS
        self.constants = EngineeringConstants.PHYSICAL_CONSTANTS

    def validate_process_data(self, process_data: Dict[str, Any]) -> List[str]:
        """
        Comprehensive validation of process data

        Returns:
            List of validation error messages
        """

        errors = []

        # Basic pressure validation
        errors.extend(self._validate_pressures(process_data))

        # Temperature validation  
        errors.extend(self._validate_temperature(process_data))

        # Flow rate validation
        errors.extend(self._validate_flow_rates(process_data))

        # Fluid property validation
        errors.extend(self._validate_fluid_properties(process_data))

        # Engineering reasonableness checks
        errors.extend(self._validate_engineering_limits(process_data))

        # Safety and regulatory checks
        errors.extend(self._validate_safety_requirements(process_data))

        return errors

    def _validate_pressures(self, data: Dict[str, Any]) -> List[str]:
        """Validate pressure inputs"""
        errors = []

        p1 = data.get('p1', 0)
        p2 = data.get('p2', 0)

        # Basic pressure checks
        if p1 <= 0:
            errors.append("Inlet pressure must be positive")

        if p2 <= 0:
            errors.append("Outlet pressure must be positive")

        if p1 <= p2:
            errors.append("Inlet pressure must be greater than outlet pressure")

        # Pressure ratio checks
        if p1 > 0 and p2 > 0:
            pressure_ratio = p2 / p1
            if pressure_ratio < self.limits['min_pressure_ratio']:
                errors.append(f"Very low pressure ratio ({pressure_ratio:.3f}) - check for errors")
            elif pressure_ratio > self.limits['max_pressure_ratio']:
                errors.append(f"Very high pressure ratio ({pressure_ratio:.3f}) - limited valve authority")

        # Reasonable pressure limits
        max_reasonable_pressure = 500.0  # bar or equivalent
        if p1 > max_reasonable_pressure:
            errors.append(f"Inlet pressure ({p1:.1f}) exceeds typical industrial range")

        return errors

    def _validate_temperature(self, data: Dict[str, Any]) -> List[str]:
        """Validate temperature inputs"""
        errors = []

        temperature = data.get('temperature', 25)

        if temperature < self.limits['min_temperature_c']:
            errors.append(f"Temperature ({temperature:.1f}°C) below absolute minimum")
        elif temperature > self.limits['max_temperature_c']:
            errors.append(f"Temperature ({temperature:.1f}°C) above reasonable maximum")

        # Fluid-specific temperature checks
        fluid_type = data.get('fluid_type', 'Liquid')
        if fluid_type == 'Liquid':
            if temperature < -50:
                errors.append("Very low temperature for liquid service - check phase conditions")
            elif temperature > 400:
                errors.append("High temperature for liquid service - verify fluid properties")

        return errors

    def _validate_flow_rates(self, data: Dict[str, Any]) -> List[str]:
        """Validate flow rate inputs"""
        errors = []

        normal_flow = data.get('normal_flow', 0)
        min_flow = data.get('min_flow', 0)
        max_flow = data.get('max_flow', 0)

        # Basic flow checks
        if normal_flow <= 0:
            errors.append("Normal flow rate must be positive")

        if min_flow <= 0:
            errors.append("Minimum flow rate must be positive")

        if max_flow <= normal_flow:
            errors.append("Maximum flow must be greater than normal flow")

        if min_flow >= normal_flow:
            errors.append("Minimum flow must be less than normal flow")

        # Turndown ratio check
        if min_flow > 0 and max_flow > 0:
            turndown_ratio = max_flow / min_flow
            if turndown_ratio > 100:
                errors.append(f"Very high turndown ratio ({turndown_ratio:.1f}:1) - verify requirements")
            elif turndown_ratio < 2:
                errors.append(f"Low turndown ratio ({turndown_ratio:.1f}:1) - limited control range")

        return errors

    def _validate_fluid_properties(self, data: Dict[str, Any]) -> List[str]:
        """Validate fluid property inputs"""
        errors = []

        fluid_type = data.get('fluid_type', 'Liquid')

        if fluid_type == 'Liquid':
            errors.extend(self._validate_liquid_properties(data))
        else:
            errors.extend(self._validate_gas_properties(data))

        return errors

    def _validate_liquid_properties(self, data: Dict[str, Any]) -> List[str]:
        """Validate liquid-specific properties"""
        errors = []

        density = data.get('density', 0)
        viscosity = data.get('viscosity', 0)
        vapor_pressure = data.get('vapor_pressure', 0)
        p1 = data.get('p1', 0)
        p2 = data.get('p2', 0)

        # Density checks
        if density < self.limits['min_density']:
            errors.append(f"Density ({density:.1f}) too low for liquid")
        elif density > self.limits['max_density']:
            errors.append(f"Density ({density:.1f}) unreasonably high")

        # Viscosity checks
        if viscosity <= 0:
            errors.append("Viscosity must be positive")
        elif viscosity > 1000:
            errors.append(f"Very high viscosity ({viscosity:.1f} cSt) - verify Reynolds correction")

        # Vapor pressure checks
        if vapor_pressure < 0:
            errors.append("Vapor pressure cannot be negative")
        elif vapor_pressure >= p1:
            errors.append("Vapor pressure exceeds inlet pressure - flashing will occur")
        elif vapor_pressure >= p2:
            errors.append("Vapor pressure exceeds outlet pressure - cavitation likely")

        return errors

    def _validate_gas_properties(self, data: Dict[str, Any]) -> List[str]:
        """Validate gas-specific properties"""
        errors = []

        molecular_weight = data.get('molecular_weight', 0)
        specific_heat_ratio = data.get('specific_heat_ratio', 1.4)
        compressibility = data.get('compressibility', 1.0)

        # Molecular weight checks
        if molecular_weight <= 0:
            errors.append("Molecular weight must be positive")
        elif molecular_weight > 200:
            errors.append(f"Very high molecular weight ({molecular_weight:.1f}) - verify gas properties")

        # Specific heat ratio checks
        if specific_heat_ratio < 1.0:
            errors.append("Specific heat ratio must be ≥ 1.0")
        elif specific_heat_ratio > 2.0:
            errors.append(f"Specific heat ratio ({specific_heat_ratio:.2f}) outside typical range")

        # Compressibility checks
        if compressibility <= 0:
            errors.append("Compressibility factor must be positive")
        elif compressibility > 2.0:
            errors.append(f"High compressibility factor ({compressibility:.2f}) - verify conditions")

        return errors

    def _validate_engineering_limits(self, data: Dict[str, Any]) -> List[str]:
        """Validate against engineering best practices"""
        errors = []

        p1 = data.get('p1', 0)
        p2 = data.get('p2', 0)
        normal_flow = data.get('normal_flow', 0)

        # Pressure drop reasonableness
        if p1 > 0 and p2 > 0:
            delta_p = p1 - p2
            delta_p_percent = (delta_p / p1) * 100

            if delta_p_percent > 90:
                errors.append(f"Very high pressure drop ({delta_p_percent:.0f}%) - review system design")
            elif delta_p_percent < 5:
                errors.append(f"Very low pressure drop ({delta_p_percent:.0f}%) - poor valve authority expected")

        return errors

    def _validate_safety_requirements(self, data: Dict[str, Any]) -> List[str]:
        """Validate safety and regulatory requirements"""
        errors = []

        criticality = data.get('criticality', 'Non-Critical')
        h2s_present = data.get('h2s_present', False)
        h2s_partial_pressure = data.get('h2s_partial_pressure', 0)

        # H2S service validation
        if h2s_present:
            if h2s_partial_pressure <= 0:
                errors.append("H2S partial pressure must be specified for sour service")
            elif h2s_partial_pressure > 0.05:  # 0.05 bar threshold for NACE
                errors.append(f"High H2S partial pressure ({h2s_partial_pressure:.3f} bar) - NACE MR0175 applies")

        # Critical service validation
        if criticality in ['Critical', 'Safety Critical']:
            expansion_factor = data.get('expansion_factor', 0)
            if expansion_factor < 10:
                errors.append("Critical services should include adequate safety margins")

        return errors

    def validate_valve_selection(self, valve_config: Dict[str, Any]) -> List[str]:
        """Validate valve selection parameters"""
        errors = []

        # Valve coefficient validation
        fl_factor = valve_config.get('fl_factor', 0.9)
        xt_factor = valve_config.get('xt_factor', 0.7)
        fd_factor = valve_config.get('fd_factor', 1.0)

        if not 0.1 <= fl_factor <= 1.0:
            errors.append(f"FL factor ({fl_factor:.2f}) outside valid range (0.1-1.0)")

        if not 0.1 <= xt_factor <= 1.0:
            errors.append(f"xT factor ({xt_factor:.2f}) outside valid range (0.1-1.0)")

        if not 0.1 <= fd_factor <= 2.0:
            errors.append(f"Fd factor ({fd_factor:.2f}) outside typical range (0.1-2.0)")

        return errors
