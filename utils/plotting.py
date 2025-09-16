"""
Professional Plotting Utilities
Charts and visualizations for valve sizing analysis
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, Any

class PlottingHelper:
    """Professional plotting utilities for valve sizing"""

    def __init__(self):
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd'
        }

    def create_cavitation_chart(self, cavitation_results: Dict[str, Any]) -> go.Figure:
        """Create ISA RP75.23 cavitation analysis chart"""

        fig = go.Figure()

        sigma_service = cavitation_results.get('sigma_service', 0)
        scaled_sigmas = cavitation_results.get('scaled_sigmas', {})

        # Add sigma level bars
        levels = ['choking', 'damage', 'constant', 'incipient', 'manufacturer']
        colors = ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c', '#1f77b4']

        for level, color in zip(levels, colors):
            if level in scaled_sigmas:
                fig.add_trace(go.Bar(
                    x=[scaled_sigmas[level]],
                    y=[level.title()],
                    orientation='h',
                    marker_color=color,
                    name=f'{level.title()} Limit',
                    opacity=0.7
                ))

        # Add service operating point
        fig.add_vline(
            x=sigma_service,
            line=dict(color='red', width=3, dash='dash'),
            annotation_text=f'Service σ = {sigma_service:.1f}'
        )

        fig.update_layout(
            title='ISA RP75.23 Cavitation Analysis',
            xaxis_title='Sigma (σ) Value',
            yaxis_title='Cavitation Level',
            showlegend=False,
            height=400
        )

        return fig

    def create_valve_characteristic_curve(self, valve_config: Dict[str, Any]) -> go.Figure:
        """Create valve flow characteristic curve"""

        characteristic = valve_config.get('valve_characteristic', 'Equal Percentage')
        openings = np.linspace(0, 100, 101)

        if characteristic == 'Equal Percentage':
            flows = np.power(50, (openings - 100) / 100) * 100
        elif characteristic == 'Linear':
            flows = openings
        else:  # Quick Opening
            flows = 100 * np.sqrt(openings / 100)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=openings,
            y=flows,
            mode='lines',
            name=f'{characteristic} Characteristic',
            line=dict(color=self.colors['primary'], width=3)
        ))

        fig.update_layout(
            title='Valve Flow Characteristic Curve',
            xaxis_title='Valve Opening (%)',
            yaxis_title='Relative Flow (%)',
            height=400
        )

        return fig
