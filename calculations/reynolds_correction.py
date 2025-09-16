"""
Reynolds Number Correction Module
Implementation of Fr factor calculations per IEC 60534-2-1

Features:
- Iterative Reynolds number calculation
- Flow regime classification
- Fd factor integration for valve geometry
"""

import math
from typing import Dict, Any
from config.constants import EngineeringConstants

class ReynoldsCorrection:
    """Reynolds number correction calculations per IEC 60534-2-1"""

    def __init__(self):
        self.constants = EngineeringConstants.SIZING_CONSTANTS
        self.limits = EngineeringConstants.REYNOLDS_LIMITS

    def calculate_fr_factor(self,
                          flow_rate: float,
                          cv_initial: float,
                          viscosity: float,
                          fd_factor: float,
                          pipe_diameter: float,
                          specific_gravity: float,
                          delta_p: float,
                          units: str = 'metric',
                          max_iterations: int = 10,
                          tolerance: float = 0.001) -> Dict[str, Any]:
        """
        Calculate Reynolds number correction factor with iterative solution

        Returns:
            Dictionary with complete Reynolds analysis
        """

        try:
            # Get constants
            if units == 'metric':
                n2 = self.constants['N2_metric']
                n4 = self.constants['N4_metric']
            else:
                n2 = self.constants['N2_imperial']
                n4 = self.constants['N4_imperial']

            # Iterative solution
            cv_current = max(cv_initial, 1e-6)  # Prevent division by zero
            reynolds_history = []
            fr_history = []

            for iteration in range(max_iterations):
                # Calculate valve Reynolds number
                # Rev = (N4 * Fd * Q * sqrt(Gf)) / (N2 * D^1.25 * ν * sqrt(Cv))
                try:
                    reynolds_num = (n4 * fd_factor * flow_rate * math.sqrt(specific_gravity)) / (
                        n2 * math.pow(max(pipe_diameter, 1e-3), 1.25) * 
                        max(viscosity, 1e-6) * math.sqrt(cv_current)
                    )
                except:
                    reynolds_num = 100000  # Assume turbulent

                reynolds_history.append(reynolds_num)

                # Calculate Fr factor based on Reynolds number
                fr_factor = self._calculate_fr_from_reynolds(reynolds_num)
                fr_history.append(fr_factor)

                # Calculate new Cv
                cv_new = cv_initial / max(fr_factor, 1e-6)

                # Check convergence
                if iteration > 0:
                    cv_change = abs(cv_new - cv_current) / max(cv_current, 1e-6)
                    if cv_change < tolerance:
                        break

                cv_current = cv_new

            # Final values
            final_reynolds = reynolds_num
            final_fr = fr_factor
            final_cv = cv_current

            # Flow regime classification
            flow_regime = self._classify_flow_regime(final_reynolds)

            # Performance assessment
            correction_factor = final_cv / cv_initial
            is_significant = correction_factor > 1.1

            # Calculate characteristic length and velocity
            char_analysis = self._calculate_characteristic_parameters(
                flow_rate, cv_current, pipe_diameter, specific_gravity, units
            )

            return {
                'reynolds_number': final_reynolds,
                'fr_factor': final_fr,
                'cv_corrected': final_cv,
                'cv_initial': cv_initial,
                'correction_factor': correction_factor,
                'flow_regime': flow_regime,
                'is_significant': is_significant,
                'iterations_used': iteration + 1,
                'converged': iteration < max_iterations - 1,
                'reynolds_history': reynolds_history,
                'fr_history': fr_history,
                'characteristic_analysis': char_analysis,
                'warnings': self._generate_reynolds_warnings(
                    final_reynolds, final_fr, correction_factor, flow_regime
                )
            }

        except Exception as e:
            return {
                'error': f"Reynolds correction failed: {str(e)}",
                'reynolds_number': 100000,
                'fr_factor': 1.0,
                'cv_corrected': cv_initial,
                'cv_initial': cv_initial,
                'correction_factor': 1.0,
                'flow_regime': 'Turbulent (Assumed)',
                'is_significant': False,
                'converged': False
            }

    def _calculate_fr_from_reynolds(self, reynolds_number: float) -> float:
        """Calculate Fr factor from Reynolds number per IEC standard"""

        try:
            if reynolds_number <= self.limits['laminar_upper']:
                # Laminar flow: Fr = 0.019 * Re^0.67
                fr_factor = 0.019 * math.pow(max(reynolds_number, 1.0), 0.67)
                fr_factor = max(0.01, fr_factor)

            elif reynolds_number >= self.limits['turbulent_lower']:
                # Fully turbulent flow: Fr = 1.0
                fr_factor = 1.0

            else:
                # Transitional flow: interpolation
                re_log = math.log10(max(reynolds_number, 1.0))
                re_low_log = math.log10(self.limits['laminar_upper'])
                re_high_log = math.log10(self.limits['turbulent_lower'])

                # Linear interpolation in log space
                if re_high_log > re_low_log:
                    interpolation_factor = (re_log - re_low_log) / (re_high_log - re_low_log)
                else:
                    interpolation_factor = 0.5

                # Fr at laminar boundary
                fr_laminar = 0.019 * math.pow(self.limits['laminar_upper'], 0.67)

                # Interpolate between laminar and turbulent
                fr_factor = fr_laminar + interpolation_factor * (1.0 - fr_laminar)

                # Ensure bounds
                fr_factor = max(fr_laminar, min(1.0, fr_factor))

            return fr_factor

        except:
            return 1.0  # Default to no correction

    def _classify_flow_regime(self, reynolds_number: float) -> str:
        """Classify flow regime based on Reynolds number"""

        if reynolds_number <= self.limits['laminar_upper']:
            return "Laminar"
        elif reynolds_number <= 2300:
            return "Transitional (Low)"
        elif reynolds_number <= 4000:
            return "Transitional (Mixed)"
        elif reynolds_number <= self.limits['turbulent_lower']:
            return "Transitional (High)"
        else:
            return "Turbulent"

    def _calculate_characteristic_parameters(self, flow_rate: float, cv: float,
                                           pipe_diameter: float, specific_gravity: float,
                                           units: str) -> Dict[str, Any]:
        """Calculate characteristic flow parameters"""

        try:
            # Estimate valve flow area from Cv
            valve_area_in2 = cv / 29.9  # Approximate relationship
            valve_area_m2 = valve_area_in2 * 0.00064516

            # Convert flow rate to m³/s
            if units == 'metric':
                volume_flow_m3s = flow_rate / 3600.0
            else:
                volume_flow_m3s = flow_rate * 0.0063  # GPM to m³/s

            # Characteristic velocity
            if valve_area_m2 > 0:
                char_velocity = volume_flow_m3s / valve_area_m2
            else:
                char_velocity = 0.0

            # Hydraulic diameter (approximate)
            hydraulic_diameter = 2.0 * math.sqrt(valve_area_m2 / math.pi)

            return {
                'valve_area_m2': valve_area_m2,
                'characteristic_velocity': char_velocity,
                'hydraulic_diameter': hydraulic_diameter,
                'volume_flow_m3s': volume_flow_m3s
            }

        except:
            return {
                'valve_area_m2': 0.0,
                'characteristic_velocity': 0.0,
                'hydraulic_diameter': 0.0,
                'volume_flow_m3s': 0.0
            }

    def _generate_reynolds_warnings(self, reynolds_number: float, fr_factor: float,
                                  correction_factor: float, flow_regime: str) -> list:
        """Generate warnings based on Reynolds analysis"""

        warnings = []

        # Reynolds number warnings
        if reynolds_number < self.limits['laminar_upper']:
            warnings.append(
                f"Laminar flow (Re = {reynolds_number:.0f}) - Standard equations may not apply"
            )
        elif reynolds_number < 2300:
            warnings.append(
                f"Low Reynolds number ({reynolds_number:.0f}) - Transitional flow effects"
            )

        # Fr factor warnings
        if fr_factor < 0.1:
            warnings.append(
                f"Very low Fr factor ({fr_factor:.3f}) - Review calculation inputs"
            )
        elif fr_factor < 0.5:
            warnings.append(
                f"Low Fr factor ({fr_factor:.3f}) - Significant viscous effects"
            )

        # Correction factor warnings
        if correction_factor > 2.0:
            warnings.append(
                f"Large sizing correction ({correction_factor:.1f}x) - Consider process optimization"
            )
        elif correction_factor > 1.5:
            warnings.append(
                f"Significant sizing correction ({correction_factor:.1f}x) required"
            )

        return warnings
