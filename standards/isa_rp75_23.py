"""
ISA RP75.23 Cavitation Analysis Module
Complete implementation of five-level sigma methodology with scaling

Features:
- Incipient, constant, damage, choking, and manufacturer limit analysis
- Pressure Scale Effect (PSE) and Size Scale Effect (SSE) corrections
- Professional recommendations and mitigation strategies
"""

import math
from typing import Dict, Any, Optional
from config.constants import EngineeringConstants

class ISAStandardRP7523:
    """ISA RP75.23 Cavitation Analysis Implementation"""

    def __init__(self):
        self.cavitation_limits = EngineeringConstants.CAVITATION_LIMITS

    def analyze_cavitation(self,
                         inlet_pressure: float,
                         outlet_pressure: float,
                         vapor_pressure: float,
                         fl_factor: float,
                         valve_size: float,
                         valve_type: str = 'globe',
                         reference_size: float = 100.0,
                         reference_pressure_diff: float = 100.0,
                         sigma_reference: Optional[Dict[str, float]] = None,
                         units: str = 'metric') -> Dict[str, Any]:
        """
        Complete ISA RP75.23 cavitation analysis with scaling
        """

        try:
            # Basic parameters
            delta_p = inlet_pressure - outlet_pressure
            pressure_diff = inlet_pressure - vapor_pressure

            # Service cavitation index
            sigma_service = pressure_diff / delta_p if delta_p > 0 else float('inf')

            # Use provided or default sigma values
            if sigma_reference is None:
                sigma_reference = self.cavitation_limits.copy()

            # Apply scaling corrections
            scaled_sigmas = {}
            scaling_analysis = {}

            for level, sigma_ref in sigma_reference.items():
                # Pressure Scale Effect (PSE)
                pse = self._calculate_pressure_scale_effect(
                    pressure_diff, reference_pressure_diff, level, valve_type
                )

                # Size Scale Effect (SSE)
                sse = self._calculate_size_scale_effect(
                    valve_size, reference_size, level, valve_type
                )

                # Apply scaling: σ_scaled = (σ_ref * SSE - 1) * PSE + 1
                sigma_scaled = (sigma_ref * sse - 1.0) * pse + 1.0
                scaled_sigmas[level] = sigma_scaled

                scaling_analysis[level] = {
                    'sigma_reference': sigma_ref,
                    'pse': pse,
                    'sse': sse,
                    'sigma_scaled': sigma_scaled
                }

            # Determine cavitation level and severity
            cavitation_assessment = self._assess_cavitation_level(
                sigma_service, scaled_sigmas, fl_factor
            )

            # Calculate allowable pressure drops
            allowable_drops = self._calculate_allowable_pressure_drops(
                pressure_diff, scaled_sigmas
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                cavitation_assessment, sigma_service, scaled_sigmas, valve_type
            )

            return {
                'sigma_service': sigma_service,
                'sigma_fl_corrected': sigma_service * fl_factor,
                'pressure_parameters': {
                    'inlet_pressure': inlet_pressure,
                    'outlet_pressure': outlet_pressure,
                    'vapor_pressure': vapor_pressure,
                    'delta_p': delta_p,
                    'pressure_diff': pressure_diff
                },
                'sigma_reference': sigma_reference,
                'scaled_sigmas': scaled_sigmas,
                'scaling_analysis': scaling_analysis,
                'cavitation_assessment': cavitation_assessment,
                'allowable_drops': allowable_drops,
                'fl_factor': fl_factor,
                'recommendations': recommendations,
                'compliance': 'ISA RP75.23-1995 (R2024)',
                'units': units
            }

        except Exception as e:
            return {
                'error': f"ISA RP75.23 analysis failed: {str(e)}",
                'sigma_service': 0.0
            }

    def _calculate_pressure_scale_effect(self, actual_pressure_diff: float,
                                       reference_pressure_diff: float,
                                       cavitation_level: str,
                                       valve_type: str) -> float:
        """Calculate Pressure Scale Effect per ISA RP75.23"""

        # Scaling exponents based on cavitation level and valve type
        exponents = {
            'globe': {
                'incipient': 0.10, 'constant': 0.15, 'damage': 0.20,
                'choking': 0.25, 'manufacturer': 0.15
            },
            'ball': {
                'incipient': 0.15, 'constant': 0.20, 'damage': 0.25,
                'choking': 0.30, 'manufacturer': 0.20
            },
            'butterfly': {
                'incipient': 0.20, 'constant': 0.25, 'damage': 0.30,
                'choking': 0.35, 'manufacturer': 0.25
            }
        }

        valve_key = 'globe'  # Default
        if 'ball' in valve_type.lower():
            valve_key = 'ball'
        elif 'butterfly' in valve_type.lower():
            valve_key = 'butterfly'

        exponent = exponents[valve_key].get(cavitation_level, 0.15)

        try:
            if reference_pressure_diff > 0:
                pse = math.pow(actual_pressure_diff / reference_pressure_diff, exponent)
            else:
                pse = 1.0

            # Apply reasonable bounds
            return max(0.5, min(2.0, pse))

        except:
            return 1.0

    def _calculate_size_scale_effect(self, actual_size: float, reference_size: float,
                                   cavitation_level: str, valve_type: str) -> float:
        """Calculate Size Scale Effect per ISA RP75.23"""

        # Size scaling exponents
        exponents = {
            'globe': {
                'incipient': 0.05, 'constant': 0.08, 'damage': 0.12,
                'choking': 0.15, 'manufacturer': 0.08
            },
            'ball': {
                'incipient': 0.08, 'constant': 0.12, 'damage': 0.15,
                'choking': 0.20, 'manufacturer': 0.12
            },
            'butterfly': {
                'incipient': 0.10, 'constant': 0.15, 'damage': 0.20,
                'choking': 0.25, 'manufacturer': 0.15
            }
        }

        valve_key = 'globe'  # Default
        if 'ball' in valve_type.lower():
            valve_key = 'ball'
        elif 'butterfly' in valve_type.lower():
            valve_key = 'butterfly'

        exponent = exponents[valve_key].get(cavitation_level, 0.08)

        try:
            if reference_size > 0:
                sse = math.pow(actual_size / reference_size, exponent)
            else:
                sse = 1.0

            # Apply reasonable bounds
            return max(0.7, min(1.5, sse))

        except:
            return 1.0

    def _assess_cavitation_level(self, sigma_service: float, scaled_sigmas: Dict[str, float],
                               fl_factor: float) -> Dict[str, Any]:
        """Assess cavitation level and severity"""

        # Apply FL factor correction
        sigma_corrected = sigma_service * fl_factor

        # Determine current cavitation level
        current_level = "None"
        severity_factor = 0.0

        # Check against each level (most severe to least)
        level_order = ['choking', 'damage', 'constant', 'incipient', 'manufacturer']

        for level in level_order:
            if level in scaled_sigmas:
                if sigma_corrected <= scaled_sigmas[level]:
                    current_level = level
                    severity_factor = scaled_sigmas[level] / sigma_corrected if sigma_corrected > 0 else float('inf')
                    break

        # Risk assessment
        risk_levels = {
            'choking': {'level': 'Critical', 'description': 'Severe cavitation with flow limitation'},
            'damage': {'level': 'High', 'description': 'Cavitation-induced damage potential'},
            'constant': {'level': 'Moderate', 'description': 'Steady cavitation - monitor for wear'},
            'incipient': {'level': 'Low', 'description': 'Beginning of cavitation - generally acceptable'},
            'manufacturer': {'level': 'Caution', 'description': 'Above manufacturer recommended limit'},
            'None': {'level': 'None', 'description': 'No cavitation detected'}
        }

        risk_info = risk_levels.get(current_level, risk_levels['None'])

        # Calculate margins to each limit
        margin_analysis = {}
        for level, sigma_limit in scaled_sigmas.items():
            margin = sigma_corrected - sigma_limit
            margin_analysis[level] = {
                'margin': margin,
                'percentage': (margin / sigma_limit * 100) if sigma_limit > 0 else 0,
                'status': 'Safe' if margin > 0 else 'Violated'
            }

        return {
            'current_level': current_level,
            'risk_level': risk_info['level'],
            'risk_description': risk_info['description'],
            'severity_factor': severity_factor,
            'sigma_corrected': sigma_corrected,
            'margin_analysis': margin_analysis,
            'is_cavitating': current_level != "None"
        }

    def _calculate_allowable_pressure_drops(self, pressure_diff: float,
                                          scaled_sigmas: Dict[str, float]) -> Dict[str, float]:
        """Calculate allowable pressure drops for each cavitation level"""

        allowable_drops = {}

        for level, sigma_limit in scaled_sigmas.items():
            if sigma_limit > 0:
                # From σ = (P1-Pv)/ΔP, therefore ΔP = (P1-Pv)/σ
                allowable_drop = pressure_diff / sigma_limit
                allowable_drops[level] = allowable_drop
            else:
                allowable_drops[level] = 0.0

        return allowable_drops

    def _generate_recommendations(self, cavitation_assessment: Dict[str, Any],
                                sigma_service: float, scaled_sigmas: Dict[str, float],
                                valve_type: str) -> Dict[str, Any]:
        """Generate professional recommendations"""

        current_level = cavitation_assessment['current_level']
        risk_level = cavitation_assessment['risk_level']

        recommendations = []
        actions = []
        alternatives = []

        if risk_level == "Critical":
            recommendations.extend([
                "Immediate design review required",
                "Flow is severely limited by cavitation"
            ])
            actions.extend([
                "Consider multi-stage pressure reduction",
                "Evaluate anti-cavitation trim designs",
                "Increase downstream pressure if possible",
                "Consider multiple valves in parallel"
            ])
            alternatives.extend([
                "Multi-stage trim (cage with multiple restriction stages)",
                "Series valve arrangement",
                "Different valve technology (rotary vs linear)",
                "Process condition modifications"
            ])

        elif risk_level == "High":
            recommendations.extend([
                "Design modification recommended",
                "High potential for trim damage"
            ])
            actions.extend([
                "Consider cavitation-resistant materials (Stellite, ceramics)",
                "Evaluate low-recovery valve designs",
                "Implement vibration monitoring",
                "Plan for frequent inspection"
            ])
            alternatives.extend([
                "Hardened trim materials",
                "Low FL valve design",
                "Staged pressure reduction"
            ])

        elif risk_level == "Moderate":
            recommendations.extend([
                "Monitor operation closely",
                "Acceptable with proper materials"
            ])
            actions.extend([
                "Establish regular inspection schedule",
                "Monitor noise and vibration levels",
                "Consider material upgrades for critical service"
            ])

        elif risk_level == "Low":
            recommendations.extend([
                "Acceptable operation",
                "Minimal cavitation effects expected"
            ])
            actions.extend([
                "Standard maintenance procedures",
                "Periodic performance monitoring"
            ])
        else:
            recommendations.append("Excellent - No cavitation concerns")
            actions.append("Standard operation and maintenance")

        # Add margin-based recommendations
        manufacturer_margin = cavitation_assessment['margin_analysis'].get('manufacturer', {})
        if manufacturer_margin.get('percentage', 100) < 20:
            recommendations.append("Operating close to manufacturer limits")
            actions.append("Verify manufacturer acceptance for this application")

        return {
            'primary_recommendations': recommendations,
            'required_actions': actions,
            'design_alternatives': alternatives,
            'monitoring_requirements': self._define_monitoring_requirements(risk_level)
        }

    def _define_monitoring_requirements(self, risk_level: str) -> Dict[str, Any]:
        """Define monitoring requirements based on risk level"""

        monitoring = {
            'Critical': {
                'frequency': 'Continuous or weekly',
                'parameters': ['Noise', 'Vibration', 'Pressure drop', 'Visual inspection', 'Performance'],
                'special': 'Consider online monitoring system'
            },
            'High': {
                'frequency': 'Monthly',
                'parameters': ['Noise', 'Vibration', 'Performance trends'],
                'special': 'Document all operational changes'
            },
            'Moderate': {
                'frequency': 'Quarterly',
                'parameters': ['Visual inspection', 'Performance verification'],
                'special': 'Monitor for gradual degradation'
            },
            'Low': {
                'frequency': 'Semi-annually',
                'parameters': ['Standard maintenance inspection'],
                'special': 'Standard documentation'
            },
            'None': {
                'frequency': 'Annual',
                'parameters': ['Routine maintenance'],
                'special': 'Standard operation'
            }
        }

        return monitoring.get(risk_level, monitoring['None'])
