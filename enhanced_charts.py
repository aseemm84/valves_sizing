"""
Enhanced Charts and Analysis Module
Professional engineering charts for valve sizing analysis

Features:
- Valve characteristic curves with operating points
- Cavitation analysis charts (ISA RP75.23)
- Valve opening analysis at various flow conditions
- Noise calculation analysis (IEC 60534-8-3)
- Reynolds number analysis
- Pressure drop analysis
- Safety factor breakdown
- Complete service conditions overview
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import streamlit as st

class EnhancedChartsGenerator:
    """Professional charts generator for valve sizing analysis"""
    
    def __init__(self):
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light_blue': '#add8e6',
            'light_green': '#90ee90',
            'light_red': '#ffcccb'
        }
    
    def create_valve_characteristic_curve(self, valve_data: Dict[str, Any], 
                                        sizing_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive valve characteristic curve"""
        
        characteristic = valve_data.get('flow_characteristic', 'Equal Percentage')
        max_cv = valve_data.get('max_cv', 100)
        cv_required = sizing_data.get('cv_required', 50)
        
        # Generate opening range
        openings = np.linspace(0, 100, 101)
        
        # Calculate flow characteristics
        if characteristic == 'Equal Percentage':
            # Exponential curve: Cv = Cv_max * R^((L-100)/100) where R is rangeability
            rangeability = valve_data.get('rangeability', 50)
            cv_values = max_cv * np.power(rangeability, (openings - 100) / 100)
        elif characteristic == 'Linear':
            cv_values = (openings / 100) * max_cv
        elif characteristic == 'Quick Opening':
            cv_values = max_cv * np.sqrt(openings / 100)
        else:  # Modified characteristics
            cv_values = max_cv * (openings / 100) ** 1.5
        
        # Create main plot
        fig = go.Figure()
        
        # Add characteristic curve
        fig.add_trace(go.Scatter(
            x=openings,
            y=cv_values,
            mode='lines',
            name=f'{characteristic} Characteristic',
            line=dict(color=self.colors['primary'], width=3),
            hovertemplate='Opening: %{x:.1f}%<br>Cv: %{y:.1f}<extra></extra>'
        ))
        
        # Add operating point
        if cv_required > 0 and max_cv > 0:
            operating_opening = (cv_required / max_cv) * 100
            fig.add_trace(go.Scatter(
                x=[operating_opening],
                y=[cv_required],
                mode='markers',
                name='Normal Operating Point',
                marker=dict(color=self.colors['warning'], size=15, symbol='diamond'),
                hovertemplate=f'Normal Operation<br>Opening: {operating_opening:.1f}%<br>Cv: {cv_required:.1f}<extra></extra>'
            ))
        
        # Add operating range bands
        fig.add_hrect(y0=0, y1=max_cv*0.1, fillcolor=self.colors['light_red'], 
                      opacity=0.2, annotation_text="Poor Control Range", 
                      annotation_position="bottom right")
        
        fig.add_hrect(y0=max_cv*0.1, y1=max_cv*0.8, fillcolor=self.colors['light_green'], 
                      opacity=0.2, annotation_text="Good Control Range", 
                      annotation_position="top left")
        
        fig.add_hrect(y0=max_cv*0.8, y1=max_cv, fillcolor=self.colors['light_red'], 
                      opacity=0.2, annotation_text="Limited Control", 
                      annotation_position="top right")
        
        # Add recommended range lines
        fig.add_hline(y=max_cv*0.2, line_dash="dash", line_color="orange",
                      annotation_text="Min Recommended (20%)")
        fig.add_hline(y=max_cv*0.8, line_dash="dash", line_color="orange",
                      annotation_text="Max Recommended (80%)")
        
        fig.update_layout(
            title='Valve Flow Characteristic Curve with Operating Analysis',
            xaxis_title='Valve Opening (%)',
            yaxis_title='Flow Coefficient (Cv)',
            height=500,
            showlegend=True,
            hovermode='closest'
        )
        
        return fig
    
    def create_cavitation_analysis_chart(self, cavitation_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive ISA RP75.23 cavitation analysis chart"""
        
        sigma_service = cavitation_data.get('sigma_service', 0)
        scaled_sigmas = cavitation_data.get('scaled_sigmas', {})
        
        # Default sigma limits if not provided
        if not scaled_sigmas:
            scaled_sigmas = {
                'incipient': 3.5,
                'constant': 2.5,
                'damage': 1.8,
                'choking': 1.2,
                'manufacturer': 2.0
            }
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=('Cavitation Sigma Analysis', 'Risk Assessment'),
            vertical_spacing=0.1
        )
        
        # Top plot: Sigma levels
        levels = ['Choking', 'Damage', 'Constant', 'Incipient', 'Manufacturer']
        sigma_values = [scaled_sigmas.get(level.lower(), 0) for level in levels]
        colors = ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c', '#1f77b4']
        
        for level, sigma_val, color in zip(levels, sigma_values, colors):
            fig.add_trace(go.Bar(
                x=[sigma_val],
                y=[level],
                orientation='h',
                marker_color=color,
                name=f'{level} Limit (σ = {sigma_val:.1f})',
                opacity=0.8,
                hovertemplate=f'{level} Limit<br>Sigma: {sigma_val:.1f}<extra></extra>'
            ), row=1, col=1)
        
        # Add service operating point
        fig.add_vline(
            x=sigma_service,
            line=dict(color='red', width=4, dash='dash'),
            annotation_text=f'Service σ = {sigma_service:.1f}',
            annotation_position="top",
            row=1, col=1
        )
        
        # Bottom plot: Risk assessment gauge
        risk_level = cavitation_data.get('risk_level', 'Unknown')
        risk_colors = {
            'None': 'green',
            'Low': 'lightgreen', 
            'Moderate': 'yellow',
            'High': 'orange',
            'Critical': 'red'
        }
        
        risk_values = {
            'None': 0,
            'Low': 1,
            'Moderate': 2, 
            'High': 3,
            'Critical': 4
        }
        
        current_risk_value = risk_values.get(risk_level, 2)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=current_risk_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Cavitation Risk Level"},
            delta={'reference': 2},
            gauge={
                'axis': {'range': [None, 4]},
                'bar': {'color': risk_colors.get(risk_level, 'yellow')},
                'steps': [
                    {'range': [0, 1], 'color': "lightgreen"},
                    {'range': [1, 2], 'color': "yellow"},
                    {'range': [2, 3], 'color': "orange"},
                    {'range': [3, 4], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': current_risk_value
                }
            }
        ), row=2, col=1)
        
        fig.update_layout(
            title='ISA RP75.23 Cavitation Analysis with Risk Assessment',
            height=700,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Sigma (σ) Value", row=1, col=1)
        fig.update_yaxes(title_text="Cavitation Level", row=1, col=1)
        
        return fig
    
    def create_valve_opening_vs_flow_chart(self, process_data: Dict[str, Any], 
                                         valve_data: Dict[str, Any],
                                         sizing_data: Dict[str, Any]) -> go.Figure:
        """Create valve opening vs flow rate analysis"""
        
        normal_flow = process_data.get('normal_flow', 100)
        min_flow = process_data.get('min_flow', 30)
        max_flow = process_data.get('max_flow', 125)
        max_cv = valve_data.get('max_cv', 100)
        cv_required = sizing_data.get('cv_required', 50)
        characteristic = valve_data.get('flow_characteristic', 'Equal Percentage')
        
        # Generate flow range
        flows = np.linspace(min_flow, max_flow, 50)
        
        # Calculate required Cv for each flow (simplified linear relationship)
        cv_values = (flows / normal_flow) * cv_required
        
        # Calculate valve openings based on characteristic
        if characteristic == 'Equal Percentage':
            rangeability = valve_data.get('rangeability', 50)
            # Inverse of equal percentage: Opening = 100 + 100*log(Cv/Cv_max)/log(R)
            openings = []
            for cv in cv_values:
                if cv > 0 and cv <= max_cv:
                    opening = 100 + 100 * np.log(cv/max_cv) / np.log(rangeability)
                    openings.append(max(0, min(100, opening)))
                else:
                    openings.append(0 if cv <= 0 else 100)
            openings = np.array(openings)
        elif characteristic == 'Linear':
            openings = (cv_values / max_cv) * 100
        else:  # Quick Opening
            openings = ((cv_values / max_cv) ** 2) * 100
        
        fig = go.Figure()
        
        # Main curve
        fig.add_trace(go.Scatter(
            x=flows,
            y=openings,
            mode='lines+markers',
            name='Valve Opening Profile',
            line=dict(color=self.colors['primary'], width=3),
            marker=dict(size=4),
            hovertemplate='Flow: %{x:.1f}<br>Opening: %{y:.1f}%<extra></extra>'
        ))
        
        # Add operating points
        operating_points = [
            (min_flow, "Minimum Flow"),
            (normal_flow, "Normal Flow"),
            (max_flow, "Maximum Flow")
        ]
        
        for flow, label in operating_points:
            cv_point = (flow / normal_flow) * cv_required
            if characteristic == 'Equal Percentage':
                opening_point = 100 + 100 * np.log(cv_point/max_cv) / np.log(valve_data.get('rangeability', 50))
                opening_point = max(0, min(100, opening_point))
            elif characteristic == 'Linear':
                opening_point = (cv_point / max_cv) * 100
            else:
                opening_point = ((cv_point / max_cv) ** 2) * 100
            
            fig.add_trace(go.Scatter(
                x=[flow],
                y=[opening_point],
                mode='markers',
                name=label,
                marker=dict(size=12, symbol='diamond'),
                hovertemplate=f'{label}<br>Flow: {flow:.1f}<br>Opening: {opening_point:.1f}%<extra></extra>'
            ))
        
        # Add control range bands
        fig.add_hrect(y0=0, y1=10, fillcolor=self.colors['light_red'], opacity=0.3,
                      annotation_text="Poor Control", annotation_position="bottom left")
        fig.add_hrect(y0=10, y1=20, fillcolor="yellow", opacity=0.3,
                      annotation_text="Marginal Control", annotation_position="middle left")
        fig.add_hrect(y0=20, y1=80, fillcolor=self.colors['light_green'], opacity=0.3,
                      annotation_text="Good Control Range", annotation_position="top left")
        fig.add_hrect(y0=80, y1=90, fillcolor="yellow", opacity=0.3,
                      annotation_text="Marginal Control", annotation_position="middle right")
        fig.add_hrect(y0=90, y1=100, fillcolor=self.colors['light_red'], opacity=0.3,
                      annotation_text="Poor Control", annotation_position="top right")
        
        fig.update_layout(
            title='Valve Opening vs Flow Rate Analysis',
            xaxis_title=f'Flow Rate ({process_data.get("flow_units", "m³/h")})',
            yaxis_title='Valve Opening (%)',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_noise_analysis_chart(self, noise_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive noise analysis chart"""
        
        spl_1m = noise_data.get('spl_1m', 70)
        lw_total = noise_data.get('lw_total', 80)
        
        # Calculate noise at various distances
        distances = np.logspace(0, 2, 50)  # 1m to 100m
        spl_values = [spl_1m - 10 * np.log10(d) for d in distances]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Noise vs Distance', 'Frequency Analysis', 
                          'Regulatory Compliance', 'Noise Sources'),
            specs=[[{"secondary_y": False}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Top left: Noise vs distance
        fig.add_trace(go.Scatter(
            x=distances,
            y=spl_values,
            mode='lines',
            name='Sound Pressure Level',
            line=dict(color=self.colors['primary'], width=3),
            hovertemplate='Distance: %{x:.1f}m<br>SPL: %{y:.1f} dBA<extra></extra>'
        ), row=1, col=1)
        
        # Add regulatory limits
        fig.add_hline(y=85, line_dash="dash", line_color="orange",
                      annotation_text="OSHA Limit (85 dBA)", row=1, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="red",
                      annotation_text="Industrial Limit (80 dBA)", row=1, col=1)
        
        # Top right: Frequency analysis (simplified)
        frequencies = ['125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz', '8 kHz']
        # Simplified frequency spectrum (would be calculated from actual analysis)
        spl_octave = [spl_1m-10, spl_1m-5, spl_1m, spl_1m-3, spl_1m-8, spl_1m-15, spl_1m-20]
        
        fig.add_trace(go.Bar(
            x=frequencies,
            y=spl_octave,
            name='Octave Band Levels',
            marker_color=self.colors['secondary'],
            hovertemplate='Frequency: %{x}<br>SPL: %{y:.1f} dBA<extra></extra>'
        ), row=1, col=2)
        
        # Bottom left: Regulatory compliance
        standards = ['OSHA\n(85 dBA)', 'EU Directive\n(87 dBA)', 'Industrial\n(80 dBA)']
        limits = [85, 87, 80]
        compliance = ['Pass' if spl_1m < limit else 'Fail' for limit in limits]
        colors_compliance = ['green' if c == 'Pass' else 'red' for c in compliance]
        
        fig.add_trace(go.Bar(
            x=standards,
            y=[spl_1m] * 3,
            name='Current Level',
            marker_color=colors_compliance,
            hovertemplate='Standard: %{x}<br>Current: %{y:.1f} dBA<br>Status: %{text}<extra></extra>',
            text=compliance
        ), row=2, col=1)
        
        # Add limit lines
        for i, limit in enumerate(limits):
            fig.add_hline(y=limit, line_dash="dash", line_color="black", row=2, col=1)
        
        # Bottom right: Noise sources (pie chart)
        noise_sources = ['Turbulence', 'Cavitation', 'Mechanical', 'Flow Separation']
        # Simplified breakdown (would be from actual analysis)
        source_values = [40, 30, 15, 15] if noise_data.get('is_cavitating', False) else [60, 5, 20, 15]
        
        fig.add_trace(go.Pie(
            labels=noise_sources,
            values=source_values,
            name="Noise Sources",
            hovertemplate='Source: %{label}<br>Contribution: %{percent}<extra></extra>'
        ), row=2, col=2)
        
        fig.update_layout(
            title='Comprehensive Noise Analysis (IEC 60534-8-3)',
            height=800,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Distance (m)", type="log", row=1, col=1)
        fig.update_yaxes(title_text="Sound Pressure Level (dBA)", row=1, col=1)
        fig.update_xaxes(title_text="Frequency", row=1, col=2)
        fig.update_yaxes(title_text="SPL (dBA)", row=1, col=2)
        fig.update_xaxes(title_text="Standard", row=2, col=1)
        fig.update_yaxes(title_text="SPL (dBA)", row=2, col=1)
        
        return fig
    
    def create_pressure_drop_analysis_chart(self, process_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive pressure drop analysis"""
        
        p1 = process_data.get('p1', 10)
        p2 = process_data.get('p2', 2)
        delta_p = p1 - p2
        
        # Create system pressure profile
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('System Pressure Profile', 'Pressure Drop Distribution',
                          'Valve Authority Analysis', 'Pressure Ratio Effects'),
            specs=[[{"colspan": 2}, None],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Top: System pressure profile
        positions = np.linspace(0, 100, 100)
        pressures = []
        
        for pos in positions:
            if pos < 20:  # Upstream piping
                pressure = p1 - (p1 - p1*0.98) * (pos/20)
            elif pos < 30:  # Valve inlet approach
                pressure = p1*0.98 - (p1*0.98 - p1*0.95) * ((pos-20)/10)
            elif pos < 70:  # Valve pressure drop
                pressure = p1*0.95 - (p1*0.95 - p2*1.05) * ((pos-30)/40)
            elif pos < 80:  # Valve outlet
                pressure = p2*1.05 - (p2*1.05 - p2) * ((pos-70)/10)
            else:  # Downstream piping
                pressure = p2 - (p2 - p2*0.98) * ((pos-80)/20)
            
            pressures.append(pressure)
        
        fig.add_trace(go.Scatter(
            x=positions,
            y=pressures,
            mode='lines',
            name='System Pressure Profile',
            line=dict(color=self.colors['primary'], width=4),
            fill='tonexty',
            hovertemplate='Position: %{x:.0f}%<br>Pressure: %{y:.2f} bar<extra></extra>'
        ), row=1, col=1)
        
        # Add zone markers
        zones = [
            (0, 20, 'Upstream Piping'),
            (20, 30, 'Valve Approach'),
            (30, 70, 'Valve Pressure Drop'),
            (70, 80, 'Valve Recovery'),
            (80, 100, 'Downstream Piping')
        ]
        
        colors_zones = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightgray']
        for i, (start, end, label) in enumerate(zones):
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=colors_zones[i],
                opacity=0.3,
                annotation_text=label,
                annotation_position="top",
                row=1, col=1
            )
        
        # Bottom left: Pressure drop distribution
        components = ['Valve', 'Upstream Piping', 'Downstream Piping', 'Fittings']
        dp_values = [delta_p*0.8, delta_p*0.05, delta_p*0.05, delta_p*0.1]
        
        fig.add_trace(go.Pie(
            labels=components,
            values=dp_values,
            name="Pressure Drop Distribution",
            hovertemplate='Component: %{label}<br>ΔP: %{value:.2f} bar<br>%{percent}<extra></extra>'
        ), row=2, col=1)
        
        # Bottom right: Pressure ratio effects
        ratios = ['Pressure\nRatio', 'Valve\nAuthority', 'Recovery\nFactor']
        pressure_ratio = p2/p1 if p1 > 0 else 0
        valve_authority = delta_p/p1 if p1 > 0 else 0
        recovery_factor = 0.8  # Simplified
        
        ratio_values = [pressure_ratio, valve_authority, recovery_factor]
        
        fig.add_trace(go.Bar(
            x=ratios,
            y=ratio_values,
            name='System Ratios',
            marker_color=[self.colors['primary'], self.colors['secondary'], self.colors['success']],
            hovertemplate='Parameter: %{x}<br>Value: %{y:.3f}<extra></extra>'
        ), row=2, col=2)
        
        fig.update_layout(
            title='Comprehensive Pressure Drop Analysis',
            height=700,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="System Position (%)", row=1, col=1)
        fig.update_yaxes(title_text="Pressure (bar)", row=1, col=1)
        fig.update_yaxes(title_text="Ratio Value", row=2, col=2)
        
        return fig
    
    def create_reynolds_analysis_chart(self, sizing_data: Dict[str, Any]) -> go.Figure:
        """Create Reynolds number analysis chart"""
        
        reynolds_analysis = sizing_data.get('reynolds_analysis', {})
        reynolds_number = reynolds_analysis.get('reynolds_number', 50000)
        fr_factor = reynolds_analysis.get('fr_factor', 1.0)
        
        # Reynolds number ranges
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Reynolds Number Flow Regimes', 'Correction Factor Analysis'),
            row_heights=[0.3, 0.7]
        )
        
        # Top: Flow regime visualization
        regimes = [
            (0, 2300, 'Laminar', 'lightcoral'),
            (2300, 4000, 'Transition', 'lightyellow'), 
            (4000, 40000, 'Turbulent', 'lightgreen'),
            (40000, 1000000, 'Fully Turbulent', 'lightblue')
        ]
        
        for start, end, regime, color in regimes:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=color, opacity=0.5,
                annotation_text=regime,
                annotation_position="top",
                row=1, col=1
            )
        
        # Add current Reynolds number
        fig.add_vline(
            x=reynolds_number,
            line=dict(color='red', width=4),
            annotation_text=f'Re = {reynolds_number:.0f}',
            row=1, col=1
        )
        
        # Bottom: Fr factor vs Reynolds number curve
        re_range = np.logspace(1, 6, 1000)
        fr_values = []
        
        for re in re_range:
            if re <= 56:  # Laminar
                fr = 0.019 * (re ** 0.67)
            elif re >= 40000:  # Turbulent
                fr = 1.0
            else:  # Transition
                # Linear interpolation in log space
                re_log = np.log10(re)
                re_low_log = np.log10(56)
                re_high_log = np.log10(40000)
                
                interpolation_factor = (re_log - re_low_log) / (re_high_log - re_low_log)
                fr_laminar = 0.019 * (56 ** 0.67)
                fr = fr_laminar + interpolation_factor * (1.0 - fr_laminar)
            
            fr_values.append(min(1.0, max(0.01, fr)))
        
        fig.add_trace(go.Scatter(
            x=re_range,
            y=fr_values,
            mode='lines',
            name='Fr Factor Curve',
            line=dict(color=self.colors['primary'], width=3),
            hovertemplate='Reynolds: %{x:.0f}<br>Fr Factor: %{y:.3f}<extra></extra>'
        ), row=2, col=1)
        
        # Add current operating point
        fig.add_trace(go.Scatter(
            x=[reynolds_number],
            y=[fr_factor],
            mode='markers',
            name='Operating Point',
            marker=dict(color='red', size=15, symbol='diamond'),
            hovertemplate=f'Current Operation<br>Re: {reynolds_number:.0f}<br>Fr: {fr_factor:.3f}<extra></extra>'
        ), row=2, col=1)
        
        fig.update_layout(
            title='Reynolds Number Analysis and Correction Factors',
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Reynolds Number", type="log", row=1, col=1)
        fig.update_xaxes(title_text="Reynolds Number", type="log", row=2, col=1)
        fig.update_yaxes(title_text="Fr Correction Factor", row=2, col=1)
        
        return fig
    
    def create_safety_factor_analysis_chart(self, process_data: Dict[str, Any]) -> go.Figure:
        """Create safety factor breakdown analysis"""
        
        safety_factor = process_data.get('safety_factor', 1.2)
        criticality = process_data.get('criticality', 'Important')
        service_type = process_data.get('service_type', 'Clean Service')
        
        # Break down safety factor components
        base_factors = {
            'Non-Critical': 1.1,
            'Important': 1.2,
            'Critical': 1.3,
            'Safety Critical': 1.5
        }
        
        service_multipliers = {
            'Clean Service': 0.0,
            'Dirty Service': 0.1,
            'Corrosive Service': 0.2,
            'Erosive Service': 0.25,
            'High Temperature': 0.15,
            'Cryogenic': 0.2
        }
        
        base_factor = base_factors.get(criticality, 1.2)
        service_addition = service_multipliers.get(service_type, 0.0)
        h2s_addition = 0.1 if process_data.get('h2s_present', False) else 0.0
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Safety Factor Breakdown', 'Comparison with Standards'),
            specs=[[{"type": "waterfall"}, {"type": "bar"}]]
        )
        
        # Left: Waterfall chart showing factor buildup
        fig.add_trace(go.Waterfall(
            name="Safety Factor Components",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=["Base Factor", "Service Type", "H2S Service", "Expansion", "Total"],
            textposition="outside",
            text=[f"{base_factor:.1f}", f"+{service_addition:.1f}", 
                  f"+{h2s_addition:.1f}", "+0.0", f"{safety_factor:.1f}"],
            y=[base_factor, service_addition, h2s_addition, 0.0, safety_factor],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            hovertemplate='Component: %{x}<br>Value: %{y:.2f}<extra></extra>'
        ), row=1, col=1)
        
        # Right: Comparison with industry standards
        standards = ['ANSI/ISA\n(1.1-1.3)', 'API 14C\n(1.2-1.5)', 'IEC 61511\n(1.3-2.0)', f'Current\n({safety_factor:.1f})']
        standard_ranges = [[1.1, 1.3], [1.2, 1.5], [1.3, 2.0], [safety_factor, safety_factor]]
        
        # Add range bars
        for i, (std, (low, high)) in enumerate(zip(standards, standard_ranges)):
            fig.add_trace(go.Bar(
                x=[std],
                y=[high - low],
                base=[low],
                name=f'{std} Range',
                marker_color=self.colors['primary'] if i < 3 else self.colors['warning'],
                opacity=0.7,
                hovertemplate=f'Standard: {std}<br>Range: {low:.1f} - {high:.1f}<extra></extra>'
            ), row=1, col=2)
        
        fig.update_layout(
            title='Safety Factor Analysis and Standards Comparison',
            height=500,
            showlegend=False
        )
        
        fig.update_yaxes(title_text="Safety Factor", row=1, col=1)
        fig.update_yaxes(title_text="Safety Factor", row=1, col=2)
        
        return fig
    
    def create_service_conditions_overview_chart(self, process_data: Dict[str, Any],
                                               sizing_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive service conditions overview"""
        
        # Normalize parameters to 0-10 scale for radar chart
        temp_norm = min(10, max(0, process_data.get('temperature', 25) / 50))
        pressure_norm = min(10, max(0, process_data.get('p1', 10) / 20))
        flow_norm = min(10, max(0, process_data.get('normal_flow', 100) / 200))
        
        criticality_map = {'Non-Critical': 2, 'Important': 5, 'Critical': 8, 'Safety Critical': 10}
        criticality_norm = criticality_map.get(process_data.get('criticality', 'Important'), 5)
        
        safety_norm = min(10, max(0, process_data.get('safety_factor', 1.2) * 5))
        
        # Add sizing-related parameters
        cv_norm = min(10, max(0, sizing_data.get('cv_required', 50) / 100))
        
        # Create radar chart
        fig = go.Figure()
        
        parameters = ['Temperature', 'Pressure', 'Flow Rate', 'Criticality', 'Safety Factor', 'Cv Required']
        values = [temp_norm, pressure_norm, flow_norm, criticality_norm, safety_norm, cv_norm]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=parameters,
            fill='toself',
            name='Service Conditions',
            line=dict(color=self.colors['primary'], width=2),
            fillcolor=self.colors['primary'],
            opacity=0.6,
            hovertemplate='Parameter: %{theta}<br>Normalized Value: %{r:.1f}<extra></extra>'
        ))
        
        # Add ideal/target range
        ideal_values = [5, 5, 5, 5, 6, 5]  # Target normalized values
        fig.add_trace(go.Scatterpolar(
            r=ideal_values,
            theta=parameters,
            fill='toself',
            name='Target Range',
            line=dict(color=self.colors['success'], width=2, dash='dash'),
            fillcolor=self.colors['success'],
            opacity=0.2
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickvals=[0, 2, 4, 6, 8, 10],
                    ticktext=['Very Low', 'Low', 'Moderate', 'Normal', 'High', 'Very High']
                )
            ),
            title="Service Conditions Overview - Normalized Assessment",
            height=600,
            showlegend=True
        )
        
        return fig