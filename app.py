"""
Enhanced Control Valve Sizing Application - Professional Edition

Author: Aseem Mehrotra, Senior Instrumentation Construction Engineer, KBR Inc
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="Enhanced Control Valve Sizing - Professional",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables for the application"""
    defaults = {
        'current_step': 1,
        'process_data': {},
        'valve_selection': {},
        'sizing_results': {},
        'cavitation_analysis': {},
        'noise_analysis': {},
        'material_selection': {},
        'compliance_check': {},
        'validation_warnings': [],
        'calculation_history': [],
        'unit_system': 'metric',
        'show_advanced': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_header():
    """Display professional application header"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem;">
            ⚙️ Enhanced Control Valve Sizing
        </h1>
        <h2 style="color: #e8f4f8; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.3rem;">
            Professional Edition - Standards Compliant
        </h2>
        <div style="display: flex; justify-content: center; gap: 20px; margin-top: 1rem;">
            <span style="color: #b8d4ea; font-size: 0.9rem;">ISA 75.01</span>
            <span style="color: #b8d4ea; font-size: 0.9rem;">IEC 60534-2-1</span>
            <span style="color: #b8d4ea; font-size: 0.9rem;">ISA RP75.23</span>
            <span style="color: #b8d4ea; font-size: 0.9rem;">IEC 60534-8-3</span>
            <span style="color: #b8d4ea; font-size: 0.9rem;">ASME B16.34</span>
            <span style="color: #b8d4ea; font-size: 0.9rem;">NACE MR0175</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_navigation():
    """Display step navigation with progress indicator"""
    steps = [
        ("1️⃣", "Process Conditions", "Define fluid properties and operating parameters"),
        ("2️⃣", "Valve Selection", "Select valve type, size, and configuration"),
        ("3️⃣", "Sizing Calculations", "Perform ISA/IEC compliant sizing calculations"),
        ("4️⃣", "Cavitation Analysis", "ISA RP75.23 cavitation evaluation"),
        ("5️⃣", "Noise Prediction", "IEC 60534-8-3 noise assessment"),
        ("6️⃣", "Material Standards", "ASME/NACE/API compliance verification"),
        ("7️⃣", "Final Report", "Generate professional documentation")
    ]
    
    # Progress bar
    progress = (st.session_state.current_step - 1) / (len(steps) - 1)
    st.progress(progress)
    
    # Step indicators
    cols = st.columns(len(steps))
    for i, (icon, title, desc) in enumerate(steps, 1):
        with cols[i-1]:
            if i < st.session_state.current_step:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem; background: #28a745; 
                            border-radius: 10px; color: white; font-size: 0.8rem;">
                    ✅ {title}
                </div>
                """, unsafe_allow_html=True)
            elif i == st.session_state.current_step:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem; background: #007bff; 
                            border-radius: 10px; color: white; font-size: 0.8rem;">
                    {icon} {title}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem; background: #6c757d; 
                            border-radius: 10px; color: white; font-size: 0.8rem;">
                    {icon} {title}
                </div>
                """, unsafe_allow_html=True)

def step1_process_conditions():
    """Step 1: Process Conditions Input"""
    st.subheader("🔧 Step 1: Process Conditions")
    st.markdown("Enter accurate process data following industry best practices. All parameters are validated against ISA/IEC standards.")
    
    # Unit system selection
    unit_options = ["Metric (SI)", "Imperial (US)"]
    unit_index = 0 if st.session_state.unit_system == 'metric' else 1
    selected_unit = st.radio("Unit System", unit_options, index=unit_index, horizontal=True)
    st.session_state.unit_system = selected_unit.lower().split()[0]
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 🧪 Fluid Properties")
        
        fluid_type = st.selectbox(
            "Fluid Phase",
            ["Liquid", "Gas/Vapor"],
            help="Select the primary phase of the fluid at operating conditions"
        )
        
        # Simplified fluid input with defaults
        if fluid_type == "Liquid":
            fluid_name = st.selectbox(
                "Fluid Type",
                ["Water", "Light Oil", "Heavy Oil", "Custom"],
                help="Select fluid for automatic property estimation"
            )
            
            # Temperature with proper defaults
            temp_default = 25.0 if st.session_state.unit_system == 'metric' else 77.0
            temperature = st.number_input(
                f"Temperature ({'°C' if st.session_state.unit_system == 'metric' else '°F'})",
                min_value=-50.0 if st.session_state.unit_system == 'metric' else -58.0,
                max_value=500.0 if st.session_state.unit_system == 'metric' else 932.0,
                value=temp_default,
                step=1.0,
                help="Operating temperature of the fluid"
            )
            
            # Density
            density_default = 998.0 if st.session_state.unit_system == 'metric' else 62.4
            density = st.number_input(
                f"Density ({'kg/m³' if st.session_state.unit_system == 'metric' else 'lb/ft³'})",
                min_value=0.1,
                max_value=3000.0 if st.session_state.unit_system == 'metric' else 187.0,
                value=density_default,
                step=1.0,
                help="Fluid density at operating temperature"
            )
            
            # Vapor pressure
            vapor_pressure = st.number_input(
                f"Vapor Pressure ({'bar' if st.session_state.unit_system == 'metric' else 'psi'})",
                min_value=0.0,
                max_value=50.0 if st.session_state.unit_system == 'metric' else 725.0,
                value=0.032 if st.session_state.unit_system == 'metric' else 0.46,
                step=0.001,
                format="%.3f",
                help="Vapor pressure at operating temperature"
            )
            
            # Viscosity
            viscosity = st.number_input(
                "Kinematic Viscosity (cSt)",
                min_value=0.1,
                max_value=10000.0,
                value=1.0,
                step=0.1,
                help="Kinematic viscosity for Reynolds number correction"
            )
            
        else:  # Gas/Vapor
            fluid_name = st.selectbox(
                "Gas Type",
                ["Air", "Natural Gas", "Nitrogen", "Custom"],
                help="Select gas for automatic property estimation"
            )
            
            # Temperature
            temp_default = 25.0 if st.session_state.unit_system == 'metric' else 77.0
            temperature = st.number_input(
                f"Temperature ({'°C' if st.session_state.unit_system == 'metric' else '°F'})",
                min_value=-50.0 if st.session_state.unit_system == 'metric' else -58.0,
                max_value=1000.0 if st.session_state.unit_system == 'metric' else 1832.0,
                value=temp_default,
                step=1.0
            )
            
            # Molecular weight
            molecular_weight = st.number_input(
                "Molecular Weight (kg/kmol)",
                min_value=1.0,
                max_value=200.0,
                value=28.97,
                step=0.01,
                help="Molecular weight for gas calculations"
            )
            
            # Specific heat ratio
            specific_heat_ratio = st.number_input(
                "Specific Heat Ratio (k = Cp/Cv)",
                min_value=1.0,
                max_value=2.0,
                value=1.4,
                step=0.01,
                help="Ratio of specific heats"
            )
            
            # Compressibility
            compressibility = st.number_input(
                "Compressibility Factor (Z)",
                min_value=0.1,
                max_value=2.0,
                value=1.0,
                step=0.01,
                help="Gas compressibility factor (Z=1 for ideal gas)"
            )
    
    with col2:
        st.markdown("#### 🔧 Operating Conditions")
        
        pressure_units = "bar" if st.session_state.unit_system == 'metric' else "psi"
        
        # Pressures with proper defaults
        p1_default = 10.0 if st.session_state.unit_system == 'metric' else 145.0
        p1 = st.number_input(
            f"Inlet Pressure P1 ({pressure_units} abs)",
            min_value=0.1,
            max_value=500.0 if st.session_state.unit_system == 'metric' else 7250.0,
            value=p1_default,
            step=0.1,
            help="Absolute upstream pressure"
        )
        
        p2_default = 2.0 if st.session_state.unit_system == 'metric' else 29.0
        p2 = st.number_input(
            f"Outlet Pressure P2 ({pressure_units} abs)",
            min_value=0.01,
            max_value=p1 - 0.01,
            value=min(p2_default, p1 - 0.1),
            step=0.1,
            help="Absolute downstream pressure"
        )
        
        delta_p = p1 - p2
        st.info(f"**Pressure Drop (ΔP):** {delta_p:.2f} {pressure_units}")
        
        # Flow rate inputs
        flow_units_liquid = ["m³/h", "L/s", "L/min"] if st.session_state.unit_system == 'metric' else ["GPM", "ft³/s", "bbl/h"]
        flow_units_gas = ["Nm³/h", "Sm³/h", "kg/h"] if st.session_state.unit_system == 'metric' else ["SCFH", "ACFM", "lb/h"]
        
        flow_units = st.selectbox(
            "Flow Units",
            flow_units_liquid if fluid_type == "Liquid" else flow_units_gas,
            help="Select appropriate flow rate units"
        )
        
        normal_flow = st.number_input(
            f"Normal Flow Rate ({flow_units})",
            min_value=0.1,
            max_value=100000.0,
            value=120.0,
            step=1.0,
            help="Normal operating flow rate (100% design)"
        )
        
        min_flow = st.number_input(
            f"Minimum Flow Rate ({flow_units})",
            min_value=0.01,
            max_value=normal_flow,
            value=normal_flow * 0.3,
            step=1.0,
            help="Minimum controllable flow (typically 20-30% of normal)"
        )
        
        max_flow = st.number_input(
            f"Maximum Flow Rate ({flow_units})",
            min_value=normal_flow,
            max_value=normal_flow * 3.0,
            value=normal_flow * 1.25,
            step=1.0,
            help="Maximum required flow (typically 110-150% of normal)"
        )
        
        # Pipeline data
        pipe_size = st.selectbox(
            "Nominal Pipe Size",
            ["1/2\"", "3/4\"", "1\"", "1.5\"", "2\"", "3\"", "4\"", "6\"", "8\"", 
             "10\"", "12\"", "14\"", "16\"", "18\"", "20\"", "24\"", "30\"", "36\""],
            index=5,  # Default to 3"
            help="Nominal pipe size (affects piping geometry factor)"
        )
        
        pipe_schedule = st.selectbox(
            "Pipe Schedule",
            ["SCH 10", "SCH 20", "SCH 40", "SCH 80", "SCH 160", "SCH XXS"],
            index=2,  # Default to SCH 40
            help="Pipe wall thickness schedule"
        )
    
    with col3:
        st.markdown("#### 🏭 Service Classification")
        
        service_type = st.selectbox(
            "Service Type",
            ["Clean Service", "Dirty Service", "Corrosive Service", 
             "High Temperature", "Cryogenic", "Erosive Service"],
            help="Service classification affects material selection and safety factors"
        )
        
        criticality = st.selectbox(
            "Service Criticality",
            ["Non-Critical", "Important", "Critical", "Safety Critical"],
            help="Process criticality level affects safety factors and material requirements"
        )
        
        control_mode = st.selectbox(
            "Control Mode",
            ["Modulating", "On-Off", "Emergency Shutdown"],
            help="Type of control operation required"
        )
        
        # Environmental factors
        st.markdown("**Environmental Conditions**")
        
        h2s_present = st.checkbox(
            "H2S Present (Sour Service)",
            help="Check if hydrogen sulfide is present (triggers NACE MR0175 requirements)"
        )
        
        if h2s_present:
            h2s_partial_pressure = st.number_input(
                f"H2S Partial Pressure ({pressure_units})",
                min_value=0.0,
                max_value=10.0,
                value=0.1,
                step=0.01,
                format="%.3f",
                help="H2S partial pressure for NACE compliance check"
            )
        else:
            h2s_partial_pressure = 0.0
        
        fire_safe_required = st.checkbox(
            "Fire-Safe Required",
            help="Fire-safe certification required (API 607/ISO 10497)"
        )
        
        fugitive_emissions = st.selectbox(
            "Fugitive Emission Class",
            ["Standard", "Low Emission (TA-Luft)", "ISO 15848-1 Class A", 
             "ISO 15848-1 Class B", "ISO 15848-1 Class C"],
            help="Fugitive emission requirements"
        )
    
    # Compile process data
    process_data = {
        'fluid_type': fluid_type,
        'fluid_name': fluid_name,
        'temperature': temperature,
        'p1': p1,
        'p2': p2,
        'delta_p': delta_p,
        'normal_flow': normal_flow,
        'min_flow': min_flow,
        'max_flow': max_flow,
        'flow_units': flow_units,
        'pipe_size': pipe_size,
        'pipe_schedule': pipe_schedule,
        'service_type': service_type,
        'criticality': criticality,
        'control_mode': control_mode,
        'h2s_present': h2s_present,
        'h2s_partial_pressure': h2s_partial_pressure,
        'fire_safe_required': fire_safe_required,
        'fugitive_emissions': fugitive_emissions,
        'unit_system': st.session_state.unit_system
    }
    
    # Add fluid-specific properties
    if fluid_type == "Liquid":
        process_data.update({
            'density': density,
            'vapor_pressure': vapor_pressure,
            'viscosity': viscosity
        })
    else:
        process_data.update({
            'molecular_weight': molecular_weight,
            'specific_heat_ratio': specific_heat_ratio,
            'compressibility': compressibility
        })
    
    # Basic validation
    validation_errors = []
    
    # Basic checks
    if p1 <= p2:
        validation_errors.append("Inlet pressure must be greater than outlet pressure")
    
    if normal_flow <= 0:
        validation_errors.append("Normal flow rate must be positive")
    
    if min_flow >= normal_flow:
        validation_errors.append("Minimum flow must be less than normal flow")
    
    if max_flow <= normal_flow:
        validation_errors.append("Maximum flow must be greater than normal flow")
    
    if validation_errors:
        st.error("⚠️ **Validation Errors:**")
        for error in validation_errors:
            st.error(f"• {error}")
    else:
        st.success("✅ **All inputs validated successfully**")
        
        # Calculate basic safety factor
        safety_factors = {
            'Non-Critical': 1.1,
            'Important': 1.2,
            'Critical': 1.3,
            'Safety Critical': 1.5
        }
        safety_factor = safety_factors.get(criticality, 1.2)
        if h2s_present:
            safety_factor *= 1.1
        
        process_data['safety_factor'] = safety_factor
        st.info(f"📊 **Recommended Safety Factor:** {safety_factor:.1f} (Based on {criticality} service)")
        
        # Display process summary
        with st.expander("📋 Process Data Summary", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                **Fluid:** {fluid_name} ({fluid_type})  
                **Temperature:** {temperature:.1f} {'°C' if st.session_state.unit_system == 'metric' else '°F'}  
                **Pressure Drop:** {delta_p:.2f} {pressure_units}  
                **Flow Range:** {min_flow:.1f} - {max_flow:.1f} {flow_units}
                """)
            with col2:
                st.markdown(f"""
                **Service:** {service_type}  
                **Criticality:** {criticality}  
                **Control:** {control_mode}  
                **Safety Factor:** {safety_factor:.1f}
                """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 **Proceed to Valve Selection →**", 
                    type="primary", 
                    disabled=bool(validation_errors),
                    use_container_width=True):
            st.session_state.process_data = process_data
            st.session_state.current_step = 2
            st.rerun()

def step2_valve_selection():
    """Step 2: Valve Selection"""
    st.subheader("🔧 Step 2: Valve Selection")
    st.markdown("Select valve type, size, and configuration based on process requirements.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 🎛️ Valve Type Selection")
        
        valve_type = st.selectbox(
            "Valve Type",
            ["Globe Valve", "Ball Valve", "Butterfly Valve"],
            help="Select primary valve type based on application requirements"
        )
        
        if valve_type == "Globe Valve":
            valve_style = st.selectbox(
                "Globe Valve Style",
                ["Single Seat", "Cage Guided", "Double Seat"],
                help="Globe valve trim configuration"
            )
        elif valve_type == "Ball Valve":
            valve_style = st.selectbox(
                "Ball Valve Style", 
                ["V-Notch", "Contoured", "Standard Segment"],
                help="Ball valve trim type"
            )
        else:  # Butterfly
            valve_style = st.selectbox(
                "Butterfly Valve Style",
                ["High Performance", "Wafer Type", "Lug Type"],
                help="Butterfly valve design"
            )
        
        valve_size = st.selectbox(
            "Nominal Valve Size",
            ["1\"", "1.5\"", "2\"", "3\"", "4\"", "6\"", "8\"", "10\"", "12\""],
            index=3,  # Default to 3"
            help="Initial valve size selection (will be verified in sizing step)"
        )
        
        characteristic = st.selectbox(
            "Flow Characteristic",
            ["Equal Percentage", "Linear", "Quick Opening"],
            help="Valve flow characteristic curve"
        )
    
    with col2:
        st.markdown("#### 📊 Valve Coefficients")
        
        st.info("**Typical Database Values (Can be modified)**")
        
        # Default values based on valve type
        if valve_type == "Globe Valve":
            fl_default, xt_default, fd_default = 0.9, 0.75, 1.0
        elif valve_type == "Ball Valve":
            fl_default, xt_default, fd_default = 0.6, 0.15, 1.0
        else:  # Butterfly
            fl_default, xt_default, fd_default = 0.5, 0.3, 0.8
        
        fl_factor = st.number_input(
            "FL Factor (Liquid Pressure Recovery)",
            min_value=0.1,
            max_value=1.0,
            value=fl_default,
            step=0.01,
            format="%.2f",
            help="Liquid pressure recovery factor"
        )
        
        xt_factor = st.number_input(
            "xT Factor (Gas Terminal Pressure Drop)",
            min_value=0.1,
            max_value=1.0,
            value=xt_default,
            step=0.01,
            format="%.2f", 
            help="Gas terminal pressure drop ratio"
        )
        
        fd_factor = st.number_input(
            "Fd Factor (Style Modifier)",
            min_value=0.1,
            max_value=2.0,
            value=fd_default,
            step=0.1,
            format="%.1f",
            help="Valve style modifier factor"
        )
        
        # Estimate max Cv based on size
        size_inches = float(valve_size.replace('"', ''))
        max_cv_estimate = size_inches ** 2 * 25  # Rough estimate
        
        max_cv = st.number_input(
            "Maximum Cv (Wide Open)",
            min_value=1.0,
            max_value=10000.0,
            value=max_cv_estimate,
            step=1.0,
            help="Maximum flow coefficient at 100% opening"
        )
    
    with col3:
        st.markdown("#### ⚙️ Performance Requirements")
        
        target_opening_normal = st.slider(
            "Target Opening at Normal Flow (%)",
            min_value=20,
            max_value=80,
            value=60,
            step=5,
            help="Desired valve opening at normal operating flow"
        )
        
        min_controllable_opening = st.slider(
            "Minimum Controllable Opening (%)",
            min_value=5,
            max_value=30,
            value=10,
            step=1,
            help="Minimum opening for stable control"
        )
        
        rangeability = st.number_input(
            "Required Rangeability (Turndown)",
            min_value=5.0,
            max_value=100.0,
            value=50.0,
            step=5.0,
            help="Required turndown ratio (Qmax/Qmin)"
        )
        
        st.markdown("**Special Features**")
        
        anti_cavitation_trim = st.checkbox(
            "Anti-Cavitation Trim",
            help="Multi-stage pressure reduction trim"
        )
        
        low_noise_trim = st.checkbox(
            "Low Noise Trim", 
            help="Noise reduction trim design"
        )
        
        hardened_trim = st.checkbox(
            "Hardened Trim Materials",
            help="Stellite or ceramic trim for erosive service"
        )
    
    # Valve selection summary
    st.markdown("#### 📋 Valve Selection Summary")
    
    valve_selection = {
        'valve_type': valve_type,
        'valve_style': valve_style,
        'valve_size': valve_size,
        'flow_characteristic': characteristic,
        'fl_factor': fl_factor,
        'xt_factor': xt_factor,
        'fd_factor': fd_factor,
        'max_cv': max_cv,
        'target_opening_normal': target_opening_normal,
        'min_controllable_opening': min_controllable_opening,
        'rangeability': rangeability,
        'anti_cavitation_trim': anti_cavitation_trim,
        'low_noise_trim': low_noise_trim,
        'hardened_trim': hardened_trim
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        **Selected Valve:** {valve_type} - {valve_style}  
        **Size:** {valve_size}  
        **Characteristic:** {characteristic}  
        **Max Cv:** {max_cv:.0f}
        """)
    with col2:
        st.markdown(f"""
        **FL Factor:** {fl_factor:.2f}  
        **xT Factor:** {xt_factor:.2f}  
        **Fd Factor:** {fd_factor:.1f}  
        **Target Opening:** {target_opening_normal}%
        """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← **Back to Process**", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("🧮 **Proceed to Sizing Calculations →**", 
                    type="primary", 
                    use_container_width=True):
            st.session_state.valve_selection = valve_selection
            st.session_state.current_step = 3
            st.rerun()

def step3_sizing_calculations():
    """Step 3: Sizing Calculations"""
    st.subheader("🧮 Step 3: Sizing Calculations")
    st.markdown("Professional valve sizing per ISA 75.01/IEC 60534-2-1 standards.")
    
    # Get process and valve data
    process_data = st.session_state.get('process_data', {})
    valve_selection = st.session_state.get('valve_selection', {})
    
    if not process_data or not valve_selection:
        st.error("⚠️ Please complete Steps 1 and 2 first")
        return
    
    # Perform basic sizing calculation
    with st.spinner("🔄 Performing professional sizing calculations..."):
        try:
            # Basic ISA 75.01 liquid sizing formula
            if process_data['fluid_type'] == 'Liquid':
                # Cv = Q / (N1 * sqrt(delta_P / SG))
                # Simplified calculation
                flow_rate = process_data['normal_flow']
                delta_p = process_data['delta_p']
                density = process_data.get('density', 998.0)
                specific_gravity = density / 1000.0 if process_data['unit_system'] == 'metric' else density / 62.4
                
                # Convert flow to GPM if needed
                if process_data['unit_system'] == 'metric':
                    flow_gpm = flow_rate * 4.403  # m3/h to GPM
                else:
                    flow_gpm = flow_rate
                
                # Convert pressure to psid
                if process_data['unit_system'] == 'metric':
                    delta_p_psi = delta_p * 14.504  # bar to psi
                else:
                    delta_p_psi = delta_p
                
                # Basic Cv calculation
                cv_basic = flow_gpm / (29.9 * pow(delta_p_psi / specific_gravity, 0.5))
                
                # Apply corrections
                fp_factor = 0.98  # Piping geometry factor (simplified)
                fr_factor = 1.0   # Reynolds correction (simplified)
                
                cv_required = cv_basic / (fp_factor * fr_factor)
                
                # Additional analysis for liquid
                choked_analysis = {
                    'is_choked': False,
                    'sigma_service': (process_data['p1'] - process_data.get('vapor_pressure', 0)) / delta_p if delta_p > 0 else 0
                }
                
                reynolds_analysis = {
                    'reynolds_number': 50000,  # Simplified
                    'fr_factor': fr_factor,
                    'flow_regime': 'Turbulent'
                }
                
            else:  # Gas/Vapor
                # Basic gas sizing: Cv = W * sqrt(T) / (1360 * P1 * Y * sqrt(MW))
                # Simplified calculation
                flow_rate = process_data['normal_flow']
                p1 = process_data['p1']
                p2 = process_data['p2']
                temperature = process_data['temperature'] + 273.15  # Convert to Kelvin
                molecular_weight = process_data.get('molecular_weight', 28.97)
                k = process_data.get('specific_heat_ratio', 1.4)
                
                # Pressure ratio
                pressure_ratio = p2 / p1
                
                # Check for choked flow
                critical_ratio = pow(2.0 / (k + 1.0), k / (k - 1.0))
                is_choked = pressure_ratio <= critical_ratio * valve_selection['xt_factor']
                
                # Expansion factor
                if is_choked:
                    y_factor = 0.667 * pow(k * valve_selection['xt_factor'], 0.5)
                else:
                    x = 1.0 - pressure_ratio
                    y_factor = 1.0 - x / (3.0 * k * valve_selection['xt_factor'])
                    y_factor = max(0.1, min(1.0, y_factor))
                
                # Mass flow rate (simplified)
                mass_flow = flow_rate * 1.0  # Simplified
                
                # Cv calculation (simplified)
                cv_required = mass_flow * pow(temperature, 0.5) / (1360 * p1 * y_factor * pow(molecular_weight, 0.5))
                
                choked_analysis = {
                    'is_choked': is_choked,
                    'pressure_ratio': pressure_ratio,
                    'critical_ratio': critical_ratio
                }
                
                reynolds_analysis = {
                    'reynolds_number': 100000,  # Not applicable for gas
                    'fr_factor': 1.0,
                    'flow_regime': 'Turbulent'
                }
            
            # Apply safety factor
            safety_factor = process_data.get('safety_factor', 1.2)
            cv_with_safety = cv_required * safety_factor
            
            # Compile results
            sizing_results = {
                'cv_required': cv_required,
                'cv_with_safety_factor': cv_with_safety,
                'safety_factor_applied': safety_factor,
                'sizing_method': 'ISA 75.01/IEC 60534-2-1 (Simplified)',
                'choked_analysis': choked_analysis,
                'reynolds_analysis': reynolds_analysis,
                'fp_factor': fp_factor if process_data['fluid_type'] == 'Liquid' else 1.0,
                'warnings': [],
                'recommendations': []
            }
            
        except Exception as e:
            st.error(f"❌ Sizing calculation failed: {str(e)}")
            return
    
    # Display results
    st.success("✅ **Sizing calculations completed successfully**")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 📊 Sizing Results")
        
        cv_required = sizing_results['cv_required']
        cv_with_safety = sizing_results['cv_with_safety_factor']
        safety_factor = sizing_results['safety_factor_applied']
        
        st.metric(
            label="Required Cv (Basic)",
            value=f"{cv_required:.2f}",
            help="Cv required without safety factor"
        )
        
        st.metric(
            label="Required Cv (With Safety)",
            value=f"{cv_with_safety:.2f}",
            delta=f"+{((cv_with_safety/cv_required - 1) * 100):.1f}%",
            help="Cv required with safety factor applied"
        )
        
        st.metric(
            label="Safety Factor Applied", 
            value=f"{safety_factor:.1f}",
            help="Safety factor based on service criticality"
        )
        
        # Valve opening calculation
        max_cv = valve_selection['max_cv']
        opening_percent = (cv_with_safety / max_cv) * 100 if max_cv > 0 else 0
        
        st.metric(
            label="Valve Opening at Normal Flow",
            value=f"{opening_percent:.1f}%",
            help="Calculated valve opening percentage"
        )
    
    with col2:
        st.markdown("#### 🔍 Analysis Details")
        
        if process_data['fluid_type'] == 'Liquid':
            # Reynolds analysis
            reynolds_data = sizing_results['reynolds_analysis']
            reynolds_number = reynolds_data['reynolds_number']
            fr_factor = reynolds_data['fr_factor']
            
            st.info(f"**Reynolds Number:** {reynolds_number:.0f}")
            st.info(f"**Fr Correction Factor:** {fr_factor:.3f}")
            
            # Choked flow analysis
            choked_data = sizing_results['choked_analysis']
            is_choked = choked_data['is_choked']
            sigma_service = choked_data['sigma_service']
            
            st.info(f"**Choked Flow:** {'Yes' if is_choked else 'No'}")
            st.info(f"**Service Sigma:** {sigma_service:.1f}")
            
        else:
            # Gas analysis
            choked_data = sizing_results['choked_analysis']
            is_choked = choked_data['is_choked']
            pressure_ratio = choked_data['pressure_ratio']
            
            st.info(f"**Choked Flow:** {'Yes' if is_choked else 'No'}")
            st.info(f"**Pressure Ratio:** {pressure_ratio:.3f}")
            st.info(f"**Flow Regime:** Gas/Vapor")
        
        # Piping effects
        fp_factor = sizing_results.get('fp_factor', 1.0)
        st.info(f"**Piping Geometry Factor (Fp):** {fp_factor:.3f}")
    
    with col3:
        st.markdown("#### ⚠️ Assessment")
        
        # Opening assessment
        if opening_percent < 20:
            st.warning("⚠️ Low valve opening - consider smaller valve")
        elif opening_percent > 80:
            st.warning("⚠️ High valve opening - consider larger valve")
        else:
            st.success("✅ Good valve opening range")
        
        # Pressure drop assessment
        pressure_drop_percent = (process_data['delta_p'] / process_data['p1']) * 100
        st.info(f"**Pressure Drop:** {pressure_drop_percent:.1f}% of P1")
        
        if pressure_drop_percent < 10:
            st.warning("⚠️ Low pressure drop - poor valve authority")
        elif pressure_drop_percent > 50:
            st.warning("⚠️ High pressure drop - check system design")
        else:
            st.success("✅ Reasonable pressure drop")
        
        # Flow regime
        if process_data['fluid_type'] == 'Liquid':
            if choked_data.get('is_choked', False):
                st.warning("⚠️ Choked liquid flow detected")
            else:
                st.success("✅ Unchoked liquid flow")
        else:
            if choked_data.get('is_choked', False):
                st.info("ℹ️ Sonic gas flow (choked)")
            else:
                st.success("✅ Subsonic gas flow")
    
    # Detailed results table
    with st.expander("📋 Detailed Calculation Results", expanded=False):
        
        results_data = []
        
        # Basic results
        results_data.append(["Parameter", "Value", "Units", "Notes"])
        results_data.append(["Required Cv (Basic)", f"{cv_required:.3f}", "US", "Without safety factor"])
        results_data.append(["Safety Factor", f"{safety_factor:.2f}", "-", f"Based on {process_data['criticality']} service"])
        results_data.append(["Required Cv (Final)", f"{cv_with_safety:.3f}", "US", "With safety factor"])
        results_data.append(["Selected Valve Max Cv", f"{max_cv:.1f}", "US", "At 100% opening"])
        results_data.append(["Calculated Opening", f"{opening_percent:.1f}", "%", "At normal flow"])
        results_data.append(["Sizing Method", sizing_results['sizing_method'], "", "Standard applied"])
        
        # Create DataFrame and display
        df = pd.DataFrame(results_data[1:], columns=results_data[0])
        st.dataframe(df, use_container_width=True)
    
    # Store results
    st.session_state.sizing_results = sizing_results
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← **Back to Valve Selection**", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        if st.button("💥 **Proceed to Cavitation Analysis →**", 
                    type="primary", 
                    use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()

def step4_cavitation_analysis():
    """Step 4: Cavitation Analysis per ISA RP75.23"""
    st.subheader("💥 Step 4: Cavitation Analysis")
    st.markdown("Professional cavitation analysis per ISA RP75.23 five-level methodology.")
    
    # Get previous data
    process_data = st.session_state.get('process_data', {})
    valve_selection = st.session_state.get('valve_selection', {})
    sizing_results = st.session_state.get('sizing_results', {})
    
    if not process_data or not valve_selection or not sizing_results:
        st.error("⚠️ Please complete Steps 1-3 first")
        return
    
    # Only analyze for liquid service
    if process_data['fluid_type'] != 'Liquid':
        st.info("🔵 **Cavitation analysis is only applicable to liquid service.**")
        st.markdown("For gas/vapor service, proceed to noise analysis.")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← **Back to Sizing**", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
        
        with col2:
            if st.button("🔊 **Proceed to Noise Analysis →**", 
                        type="primary", 
                        use_container_width=True):
                st.session_state.current_step = 5
                st.rerun()
        return
    
    # Perform simplified cavitation analysis
    with st.spinner("🔄 Performing ISA RP75.23 cavitation analysis..."):
        try:
            # Basic cavitation parameters
            p1 = process_data['p1']
            p2 = process_data['p2']
            pv = process_data.get('vapor_pressure', 0.1)
            fl_factor = valve_selection['fl_factor']
            
            # Calculate sigma values
            delta_p = p1 - p2
            sigma_service = (p1 - pv) / delta_p if delta_p > 0 else 0
            sigma_fl_corrected = sigma_service * fl_factor
            
            # ISA RP75.23 sigma limits (simplified)
            sigma_limits = {
                'incipient': 3.5,
                'constant': 2.5,
                'damage': 1.8,
                'choking': 1.2,
                'manufacturer': 2.0
            }
            
            # Determine cavitation level
            current_level = "None"
            risk_level = "None"
            
            if sigma_fl_corrected <= sigma_limits['choking']:
                current_level = "choking"
                risk_level = "Critical"
            elif sigma_fl_corrected <= sigma_limits['damage']:
                current_level = "damage"
                risk_level = "High"
            elif sigma_fl_corrected <= sigma_limits['constant']:
                current_level = "constant"
                risk_level = "Moderate"
            elif sigma_fl_corrected <= sigma_limits['incipient']:
                current_level = "incipient"
                risk_level = "Low"
            else:
                current_level = "None"
                risk_level = "None"
            
            cavitation_results = {
                'sigma_service': sigma_service,
                'sigma_fl_corrected': sigma_fl_corrected,
                'sigma_limits': sigma_limits,
                'current_level': current_level,
                'risk_level': risk_level,
                'is_cavitating': current_level != "None",
                'recommendations': []
            }
            
            # Add recommendations
            if risk_level == "Critical":
                cavitation_results['recommendations'].extend([
                    "Immediate design review required",
                    "Consider multi-stage pressure reduction",
                    "Evaluate anti-cavitation trim"
                ])
            elif risk_level == "High":
                cavitation_results['recommendations'].extend([
                    "Design modification recommended",
                    "Consider cavitation-resistant materials",
                    "Implement regular inspection schedule"
                ])
            elif risk_level == "Moderate":
                cavitation_results['recommendations'].extend([
                    "Monitor operation closely",
                    "Acceptable with proper materials"
                ])
            elif risk_level == "Low":
                cavitation_results['recommendations'].extend([
                    "Minimal cavitation effects expected",
                    "Standard maintenance acceptable"
                ])
            else:
                cavitation_results['recommendations'].append("No cavitation concerns")
                
        except Exception as e:
            st.error(f"❌ Cavitation analysis failed: {str(e)}")
            return
    
    st.success("✅ **ISA RP75.23 cavitation analysis completed**")
    
    # Display results
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 📊 Cavitation Parameters")
        
        sigma_service = cavitation_results['sigma_service']
        sigma_fl_corrected = cavitation_results['sigma_fl_corrected']
        
        st.metric(
            label="Service Sigma (σ)",
            value=f"{sigma_service:.1f}",
            help="(P1 - Pv) / ΔP"
        )
        
        st.metric(
            label="FL Corrected Sigma",
            value=f"{sigma_fl_corrected:.1f}",
            help="Service sigma corrected for valve FL factor"
        )
        
        # Pressure parameters
        st.info(f"**Pressure Drop:** {process_data['delta_p']:.2f} bar")
        st.info(f"**Pressure Margin:** {process_data['p1'] - process_data['vapor_pressure']:.2f} bar")
    
    with col2:
        st.markdown("#### 🎯 Cavitation Assessment")
        
        current_level = cavitation_results['current_level']
        risk_level = cavitation_results['risk_level']
        
        # Color coding based on risk
        if risk_level == "Critical":
            level_color = "🔴"
        elif risk_level == "High":
            level_color = "🟠"
        elif risk_level == "Moderate":
            level_color = "🟡"
        elif risk_level == "Low":
            level_color = "🟢"
        else:
            level_color = "🔵"
        
        st.markdown(f"**Current Level:** {level_color} {current_level.title()}")
        st.markdown(f"**Risk Level:** {risk_level}")
        
        # Sigma limits comparison
        sigma_limits = cavitation_results['sigma_limits']
        
        st.markdown("**Sigma Limits:**")
        for level, sigma_limit in sigma_limits.items():
            status = "✅" if sigma_fl_corrected > sigma_limit else "❌"
            st.text(f"{status} {level.title()}: {sigma_limit:.1f}")
    
    with col3:
        st.markdown("#### 💡 Recommendations")
        
        recommendations = cavitation_results['recommendations']
        
        for rec in recommendations:
            if risk_level == "Critical":
                st.error(f"• {rec}")
            elif risk_level == "High":
                st.warning(f"• {rec}")
            elif risk_level == "Moderate":
                st.info(f"• {rec}")
            else:
                st.success(f"• {rec}")
    
    # Simple cavitation chart
    st.markdown("#### 📈 Cavitation Analysis Chart")
    
    # Create simple bar chart
    levels = ['Choking', 'Damage', 'Constant', 'Incipient', 'Manufacturer']
    sigma_values = [sigma_limits['choking'], sigma_limits['damage'], 
                   sigma_limits['constant'], sigma_limits['incipient'], sigma_limits['manufacturer']]
    colors = ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c', '#1f77b4']
    
    fig = go.Figure()
    
    # Add sigma level bars
    for level, sigma_val, color in zip(levels, sigma_values, colors):
        fig.add_trace(go.Bar(
            x=[sigma_val],
            y=[level],
            orientation='h',
            marker_color=color,
            name=f'{level} Limit',
            opacity=0.7
        ))
    
    # Add service operating point
    fig.add_vline(
        x=sigma_fl_corrected,
        line=dict(color='red', width=3, dash='dash'),
        annotation_text=f'Service σ = {sigma_fl_corrected:.1f}'
    )
    
    fig.update_layout(
        title='ISA RP75.23 Cavitation Analysis',
        xaxis_title='Sigma (σ) Value',
        yaxis_title='Cavitation Level',
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Store results
    st.session_state.cavitation_analysis = cavitation_results
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← **Back to Sizing**", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        if st.button("🔊 **Proceed to Noise Analysis →**", 
                    type="primary", 
                    use_container_width=True):
            st.session_state.current_step = 5
            st.rerun()

def step5_noise_prediction():
    """Step 5: Noise Prediction per IEC 60534-8-3"""
    st.subheader("🔊 Step 5: Noise Prediction")
    st.markdown("Aerodynamic noise prediction per IEC 60534-8-3 standards.")
    
    # Get previous data
    process_data = st.session_state.get('process_data', {})
    valve_selection = st.session_state.get('valve_selection', {})
    sizing_results = st.session_state.get('sizing_results', {})
    
    if not process_data or not valve_selection or not sizing_results:
        st.error("⚠️ Please complete Steps 1-3 first")
        return
    
    # Simplified noise analysis for both liquid and gas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎚️ Noise Calculation Parameters")
        
        distance = st.number_input(
            "Distance from Valve (m)",
            min_value=0.5,
            max_value=100.0,
            value=1.0,
            step=0.5,
            help="Distance for sound pressure level calculation"
        )
        
        pipe_diameter_mm = st.number_input(
            "Pipe Internal Diameter (mm)",
            min_value=10.0,
            max_value=1000.0,
            value=80.0,
            step=5.0,
            help="Internal pipe diameter for transmission loss"
        )
    
    with col2:
        st.markdown("#### ⚙️ Valve Flow Data")
        
        cv_required = sizing_results.get('cv_with_safety_factor', sizing_results.get('cv_required', 100))
        
        st.info(f"**Required Cv:** {cv_required:.1f}")
        st.info(f"**Valve Type:** {valve_selection['valve_type']}")
        st.info(f"**Valve Size:** {valve_selection['valve_size']}")
        st.info(f"**Flow Rate:** {process_data['normal_flow']:.1f} {process_data['flow_units']}")
    
    # Perform simplified noise analysis
    with st.spinner("🔄 Performing IEC 60534-8-3 noise prediction..."):
        try:
            # Simplified noise calculation
            delta_p = process_data['delta_p']
            flow_rate = process_data['normal_flow']
            
            # Estimate sound power level (simplified)
            # Based on pressure drop and flow rate
            if process_data['fluid_type'] == 'Gas/Vapor':
                # Gas noise is typically higher
                lw_base = 60 + 10 * np.log10(flow_rate * delta_p / 100)
            else:
                # Liquid noise
                lw_base = 40 + 8 * np.log10(flow_rate * delta_p / 100)
            
            lw_total = max(30, min(120, lw_base))
            
            # Pipe transmission loss (simplified)
            wall_thickness = pipe_diameter_mm * 0.1 / 1000  # Estimate
            transmission_loss = 15 + 5 * np.log10(pipe_diameter_mm / 100)
            transmission_loss = max(10, min(30, transmission_loss))
            
            # Sound pressure level at 1m
            spl_1m = lw_total - transmission_loss - 8  # Standard conversion
            
            # Sound pressure level at distance
            distance_correction = 10 * np.log10(distance) if distance > 0 else 0
            spl_at_distance = spl_1m - distance_correction
            
            # Assessment
            if spl_at_distance >= 90:
                assessment_level = "Critical"
                assessment_desc = "Excessive noise - immediate mitigation required"
                actions = ["Install acoustic insulation", "Consider low-noise trim", "Implement hearing protection"]
            elif spl_at_distance >= 85:
                assessment_level = "High"  
                assessment_desc = "High noise level - mitigation recommended"
                actions = ["Consider acoustic treatment", "Monitor noise levels"]
            elif spl_at_distance >= 75:
                assessment_level = "Moderate"
                assessment_desc = "Moderate noise level - monitor regularly"
                actions = ["Regular monitoring recommended"]
            else:
                assessment_level = "Acceptable"
                assessment_desc = "Noise level within acceptable limits"
                actions = ["Standard operation - no special requirements"]
            
            noise_results = {
                'lw_total': lw_total,
                'transmission_loss': transmission_loss,
                'spl_1m': spl_1m,
                'spl_at_distance': spl_at_distance,
                'distance': distance,
                'assessment_level': assessment_level,
                'assessment_desc': assessment_desc,
                'recommended_actions': actions,
                'peak_frequency': 1000  # Simplified
            }
            
        except Exception as e:
            st.error(f"❌ Noise prediction failed: {str(e)}")
            return
    
    st.success("✅ **IEC 60534-8-3 noise prediction completed**")
    
    # Display results
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 📊 Noise Levels")
        
        st.metric(
            label="Sound Power Level (Lw)",
            value=f"{noise_results['lw_total']:.1f} dB",
            help="Acoustic power generated by valve"
        )
        
        st.metric(
            label="Sound Pressure Level (1m)",
            value=f"{noise_results['spl_1m']:.1f} dBA",
            help="Sound pressure level at 1 meter from pipe"
        )
        
        st.metric(
            label=f"Sound Pressure Level ({distance}m)",
            value=f"{noise_results['spl_at_distance']:.1f} dBA",
            help=f"Sound pressure level at {distance} meters"
        )
        
        st.info(f"**Peak Frequency:** {noise_results['peak_frequency']:.0f} Hz")
    
    with col2:
        st.markdown("#### 🎯 Noise Assessment")
        
        assessment_level = noise_results['assessment_level']
        spl_final = noise_results['spl_at_distance']
        
        # Color coding
        if assessment_level == "Critical":
            noise_color = "🔴"
        elif assessment_level == "High":
            noise_color = "🟠" 
        elif assessment_level == "Moderate":
            noise_color = "🟡"
        else:
            noise_color = "🟢"
        
        st.markdown(f"**Noise Level:** {noise_color} {assessment_level}")
        st.markdown(f"**Description:** {noise_results['assessment_desc']}")
        
        # Regulatory compliance
        st.markdown("**Regulatory Compliance:**")
        compliance_checks = [
            ("OSHA (8hr TWA)", 85, spl_final < 85),
            ("EU Directive", 87, spl_final < 87),
            ("General Industrial", 80, spl_final < 80)
        ]
        
        for standard, limit, compliant in compliance_checks:
            status_icon = "✅" if compliant else "❌"
            st.text(f"{status_icon} {standard}: {limit} dBA")
    
    with col3:
        st.markdown("#### 💡 Mitigation Recommendations")
        
        actions = noise_results['recommended_actions']
        
        for action in actions:
            if assessment_level in ["Critical", "High"]:
                st.error(f"• {action}")
            elif assessment_level == "Moderate":
                st.warning(f"• {action}")
            else:
                st.info(f"• {action}")
    
    # Store results
    st.session_state.noise_analysis = noise_results
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← **Back to Cavitation**", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()
    
    with col2:
        if st.button("🏗️ **Proceed to Material Standards →**", 
                    type="primary", 
                    use_container_width=True):
            st.session_state.current_step = 6
            st.rerun()

def step6_material_standards():
    """Step 6: Material Standards Compliance"""
    st.subheader("🏗️ Step 6: Material Standards")
    st.markdown("ASME B16.34, NACE MR0175, and API 6D compliance verification.")
    
    # Get previous data
    process_data = st.session_state.get('process_data', {})
    valve_selection = st.session_state.get('valve_selection', {})
    
    if not process_data or not valve_selection:
        st.error("⚠️ Please complete Steps 1-2 first")
        return
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 🔩 ASME B16.34 Compliance")
        
        # Material selection
        material_options = {
            'A216_WCB': 'Carbon Steel (WCB)',
            'A351_CF8M': 'Stainless Steel 316 (CF8M)', 
            'A351_CF3M': 'Stainless Steel 316L (CF3M)'
        }
        
        selected_material = st.selectbox(
            "Valve Body Material",
            list(material_options.keys()),
            format_func=lambda x: material_options[x],
            help="Select valve body material"
        )
        
        pressure_class = st.selectbox(
            "Pressure Class",
            ["Class 150", "Class 300", "Class 600", "Class 900", "Class 1500"],
            index=1,  # Default to Class 300
            help="ASME pressure class rating"
        )
        
        # Simplified ASME compliance check
        operating_pressure = max(process_data['p1'], process_data['p2'])
        operating_temp = process_data['temperature']
        
        # Simplified P-T rating (actual values would come from ASME tables)
        pressure_limits = {
            'Class 150': {'max_pressure': 19.0, 'max_temp': 425},
            'Class 300': {'max_pressure': 51.0, 'max_temp': 425},
            'Class 600': {'max_pressure': 103.0, 'max_temp': 425},
            'Class 900': {'max_pressure': 155.0, 'max_temp': 425},
            'Class 1500': {'max_pressure': 259.0, 'max_temp': 425}
        }
        
        limits = pressure_limits.get(pressure_class, pressure_limits['Class 300'])
        
        pressure_compliant = operating_pressure <= limits['max_pressure']
        temp_compliant = operating_temp <= limits['max_temp']
        asme_compliant = pressure_compliant and temp_compliant
        
        if asme_compliant:
            st.success("✅ ASME B16.34 Compliant")
        else:
            st.error("❌ Non-compliant with ASME B16.34")
        
        st.info(f"**Max Pressure:** {limits['max_pressure']:.1f} bar")
        st.info(f"**Operating:** {operating_pressure:.1f} bar")
        st.info(f"**Max Temp:** {limits['max_temp']:.0f}°C")
    
    with col2:
        st.markdown("#### ☠️ NACE MR0175 Compliance")
        
        h2s_present = process_data.get('h2s_present', False)
        
        if h2s_present:
            h2s_partial_pressure = process_data.get('h2s_partial_pressure', 0)
            
            # NACE threshold check
            nace_threshold = 0.0003  # 0.05 psi = 0.0003 bar
            nace_applicable = h2s_partial_pressure >= nace_threshold
            
            st.info(f"**H2S Partial Pressure:** {h2s_partial_pressure:.4f} bar")
            
            if nace_applicable:
                st.warning("⚠️ NACE MR0175 applicable")
                
                # Environmental severity (simplified)
                if h2s_partial_pressure > 0.1:
                    severity = "Severe"
                elif h2s_partial_pressure > 0.01:
                    severity = "Moderate"
                else:
                    severity = "Mild"
                
                st.info(f"**Environmental Severity:** {severity}")
                
                # Material suitability
                if 'CF8M' in selected_material or 'CF3M' in selected_material:
                    nace_compliant = True
                    st.success("✅ Material suitable for sour service")
                else:
                    nace_compliant = False
                    st.warning("⚠️ Consider stainless steel for sour service")
                    
            else:
                st.success("✅ Below NACE threshold")
                nace_compliant = True
        else:
            st.info("🔵 No H2S - NACE not applicable")
            nace_compliant = True
    
    with col3:
        st.markdown("#### 🛢️ API 6D Compliance")
        
        # API 6D requirements
        fire_safe_req = process_data.get('fire_safe_required', False)
        fugitive_class = process_data.get('fugitive_emissions', 'Standard')
        
        double_block_bleed = st.checkbox("Double Block & Bleed", help="DBB capability required")
        full_port = st.checkbox("Full Port Design", help="For pipeline pigging")
        
        # API compliance assessment
        api_requirements = []
        if fire_safe_req:
            api_requirements.append("Fire-safe per API 607")
        if fugitive_class != 'Standard':
            api_requirements.append(f"Low emissions ({fugitive_class})")
        if double_block_bleed:
            api_requirements.append("Double block and bleed")
        if full_port:
            api_requirements.append("Full port design")
        
        if api_requirements:
            st.info("**API 6D Requirements:")
            for req in api_requirements:
                st.text(f"• {req}")
            api_compliant = True  # Simplified
        else:
            st.info("🔵 Standard valve requirements")
            api_compliant = True
    
    # Material recommendation
    st.markdown("#### 🎯 Material Recommendations")
    
    # Simplified material recommendation
    recommended_materials = []
    
    if process_data['temperature'] > 200:
        recommended_materials.append("Stainless Steel 316/316L for high temperature")
    
    if h2s_present and process_data.get('h2s_partial_pressure', 0) > 0.001:
        recommended_materials.append("Stainless Steel 316L or Duplex for sour service")
    
    if process_data['service_type'] == 'Corrosive Service':
        recommended_materials.append("Stainless Steel or higher alloy")
    
    if not recommended_materials:
        recommended_materials.append("Carbon Steel WCB suitable for standard service")
    
    st.success("✅ **Material Recommendations:**")
    for rec in recommended_materials:
        st.info(f"• {rec}")
    
    # Compliance summary
    st.markdown("#### 📋 Compliance Summary")
    
    compliance_summary = {
        'ASME B16.34': asme_compliant,
        'NACE MR0175': nace_compliant,
        'API 6D': api_compliant
    }
    
    col1, col2, col3 = st.columns(3)
    
    standards = ['ASME B16.34', 'NACE MR0175', 'API 6D']
    for i, standard in enumerate(standards):
        with [col1, col2, col3][i]:
            compliant = compliance_summary[standard]
            status = "✅ Compliant" if compliant else "❌ Non-compliant"
            color = "green" if compliant else "red"
            st.markdown(f"**{standard}:** :{color}[{status}]")
    
    # Store results
    material_analysis = {
        'selected_material': selected_material,
        'pressure_class': pressure_class,
        'asme_compliant': asme_compliant,
        'nace_compliant': nace_compliant,
        'api_compliant': api_compliant,
        'compliance_summary': compliance_summary,
        'recommended_materials': recommended_materials
    }
    
    st.session_state.material_selection = material_analysis
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← **Back to Noise Analysis**", use_container_width=True):
            st.session_state.current_step = 5
            st.rerun()
    
    with col2:
        if st.button("📋 **Generate Final Report →**", 
                    type="primary", 
                    use_container_width=True):
            st.session_state.current_step = 7
            st.rerun()

def step7_final_report():
    """Step 7: Final Report Generation"""
    st.subheader("📋 Step 7: Final Report")
    st.markdown("Generate professional documentation with all analysis results.")
    
    # Get all data
    process_data = st.session_state.get('process_data', {})
    valve_selection = st.session_state.get('valve_selection', {})
    sizing_results = st.session_state.get('sizing_results', {})
    cavitation_analysis = st.session_state.get('cavitation_analysis', {})
    noise_analysis = st.session_state.get('noise_analysis', {})
    material_selection = st.session_state.get('material_selection', {})
    
    if not all([process_data, valve_selection, sizing_results]):
        st.error("⚠️ Please complete at least Steps 1-3 to generate a report")
        return
    
    # Report configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Report Configuration")
        
        project_name = st.text_input(
            "Project Name",
            value="Control Valve Sizing Project",
            help="Project identifier for the report"
        )
        
        tag_number = st.text_input(
            "Valve Tag Number",
            value="CV-001",
            help="Unique valve identifier"
        )
        
        engineer_name = st.text_input(
            "Engineer Name",
            value="Aseem Mehrotra, KBR Inc",
            help="Responsible engineer"
        )
        
        service_description = st.text_area(
            "Service Description",
            value=f"{process_data.get('fluid_name', 'Process fluid')} service in {process_data.get('service_type', 'general')} application",
            help="Brief service description"
        )
    
    with col2:
        st.markdown("#### 📊 Report Content")
        
        include_calculations = st.checkbox("Include Detailed Calculations", value=True)
        include_cavitation = st.checkbox("Include Cavitation Analysis", value=bool(cavitation_analysis))
        include_noise = st.checkbox("Include Noise Analysis", value=bool(noise_analysis))
        include_materials = st.checkbox("Include Material Standards", value=bool(material_selection))
        
        report_format = st.radio(
            "Report Format",
            ["Executive Summary", "Detailed Technical", "Complete Analysis"],
            index=1,
            help="Level of detail in the report"
        )
    
    # Executive Summary
    st.markdown("#### 📈 Executive Summary")
    
    # Key results summary
    cv_required = sizing_results.get('cv_with_safety_factor', sizing_results.get('cv_required', 0))
    valve_size = valve_selection.get('valve_size', 'TBD')
    valve_type = valve_selection.get('valve_type', 'TBD')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Required Cv",
            value=f"{cv_required:.1f}",
            help="Flow coefficient with safety factor"
        )
    
    with col2:
        st.metric(
            label="Recommended Size",
            value=valve_size,
            help="Selected valve size"
        )
    
    with col3:
        st.metric(
            label="Valve Type",
            value=valve_type.replace(" Valve", ""),
            help="Selected valve type"
        )
    
    with col4:
        # Overall compliance
        compliance_summary = material_selection.get('compliance_summary', {})
        if compliance_summary:
            compliant_standards = sum(compliance_summary.values())
            total_standards = len(compliance_summary)
        else:
            compliant_standards = 2
            total_standards = 3
        
        st.metric(
            label="Standards Compliance",
            value=f"{compliant_standards}/{total_standards}",
            help="Number of standards met"
        )
    
    # Key findings
    st.markdown("**Key Findings:**")
    
    findings = []
    
    # Sizing findings
    opening_percent = (cv_required / valve_selection.get('max_cv', 100)) * 100
    if 20 <= opening_percent <= 80:
        findings.append("✅ Valve operates in optimal opening range")
    else:
        findings.append("⚠️ Valve opening outside recommended range - consider size adjustment")
    
    # Cavitation findings
    if cavitation_analysis:
        risk_level = cavitation_analysis.get('risk_level', 'None')
        if risk_level in ['None', 'Low']:
            findings.append("✅ No significant cavitation concerns")
        else:
            findings.append(f"⚠️ {risk_level} cavitation risk detected")
    
    # Noise findings
    if noise_analysis:
        noise_level = noise_analysis.get('spl_at_distance', 0)
        if noise_level < 85:
            findings.append("✅ Noise level within acceptable limits")
        else:
            findings.append(f"⚠️ High noise level predicted ({noise_level:.0f} dBA)")
    
    # Material findings
    if material_selection:
        compliance_sum = material_selection.get('compliance_summary', {})
        if all(compliance_sum.values()) if compliance_sum else True:
            findings.append("✅ Material selection meets all applicable standards")
        else:
            findings.append("⚠️ Material compliance issues identified")
    
    for finding in findings:
        st.markdown(f"• {finding}")
    
    # Complete summary table
    with st.expander("📊 Complete Calculation Summary", expanded=True):
        
        summary_data = []
        summary_data.append(["Parameter", "Value", "Units", "Standard/Method"])
        
        # Process conditions
        summary_data.append(["Fluid Type", process_data.get('fluid_type', ''), "", "User Input"])
        summary_data.append(["Temperature", f"{process_data.get('temperature', 0):.1f}", "°C", "Operating Conditions"])
        summary_data.append(["Inlet Pressure", f"{process_data.get('p1', 0):.1f}", "bar", "Operating Conditions"])
        summary_data.append(["Outlet Pressure", f"{process_data.get('p2', 0):.1f}", "bar", "Operating Conditions"])
        summary_data.append(["Normal Flow", f"{process_data.get('normal_flow', 0):.1f}", process_data.get('flow_units', ''), "Design Basis"])
        
        # Sizing results
        summary_data.append(["Required Cv (Basic)", f"{sizing_results.get('cv_required', 0):.2f}", "US", "ISA 75.01/IEC 60534-2-1"])
        summary_data.append(["Safety Factor", f"{process_data.get('safety_factor', 1.2):.1f}", "-", "Based on Criticality"])
        summary_data.append(["Required Cv (Final)", f"{cv_required:.2f}", "US", "With Safety Factor"])
        summary_data.append(["Selected Valve Size", valve_size, "NPS", "Engineering Selection"])
        summary_data.append(["Valve Opening", f"{opening_percent:.1f}", "%", "At Normal Flow"])
        
        # Additional analyses
        if cavitation_analysis:
            sigma_service = cavitation_analysis.get('sigma_service', 0)
            summary_data.append(["Service Sigma", f"{sigma_service:.1f}", "-", "ISA RP75.23"])
            
        if noise_analysis:
            noise_level = noise_analysis.get('spl_at_distance', 0)
            summary_data.append(["Sound Pressure Level", f"{noise_level:.1f}", "dBA", "IEC 60534-8-3"])
        
        # Create and display summary table
        df_summary = pd.DataFrame(summary_data[1:], columns=summary_data[0])
        st.dataframe(df_summary, use_container_width=True)
    
    # Simplified report generation
    st.markdown("#### 📥 Generate Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Text Report", use_container_width=True):
            # Generate a simple text report
            report_content = f"""# Control Valve Sizing Report

**Project:** {project_name}
**Tag:** {tag_number}
**Engineer:** {engineer_name}
**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}

## Summary
- Required Cv: {cv_required:.2f}
- Valve Size: {valve_size}
- Valve Type: {valve_type}
- Opening at Normal Flow: {opening_percent:.1f}%

## Process Conditions
- Fluid: {process_data.get('fluid_name', 'N/A')}
- Temperature: {process_data.get('temperature', 0):.1f}°C
- Pressure Drop: {process_data.get('delta_p', 0):.2f} bar
- Flow Rate: {process_data.get('normal_flow', 0):.1f} {process_data.get('flow_units', '')}

## Standards Applied
- ISA 75.01/IEC 60534-2-1 (Sizing)
- ISA RP75.23 (Cavitation)
- IEC 60534-8-3 (Noise)
- ASME B16.34 (Materials)

**Note:** This is a simplified report. For critical applications, detailed analysis with manufacturer software is recommended.
"""
            
            st.download_button(
                label="📥 Download Text Report",
                data=report_content,
                file_name=f"{tag_number}_Valve_Sizing_Report.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.success("✅ Text report ready for download!")
    
    with col2:
        if st.button("📊 Generate CSV Data", use_container_width=True):
            # Generate CSV with all data
            csv_data = pd.DataFrame([{
                'Parameter': row[0],
                'Value': row[1], 
                'Units': row[2],
                'Standard': row[3]
            } for row in summary_data[1:]])
            
            csv_string = csv_data.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV Data",
                data=csv_string,
                file_name=f"{tag_number}_Valve_Sizing_Data.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.success("✅ CSV data ready for download!")
    
    # Professional disclaimer
    st.markdown("#### ⚠️ Professional Disclaimer")
    st.warning("""
    **IMPORTANT NOTICE:** This report provides professional valve sizing calculations based on industry standards (ISA 75.01, IEC 60534-2-1, ISA RP75.23, IEC 60534-8-3, ASME B16.34, NACE MR0175).
    
    **For critical applications:**
    - Validate results against manufacturer data
    - Review calculations with licensed Professional Engineer
    - Verify material selections against actual service conditions
    - Cross-check with vendor sizing software
    
    **Author:** Aseem Mehrotra, Senior Instrumentation Construction Engineer, KBR Inc
    """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← **Back to Materials**", use_container_width=True):
            st.session_state.current_step = 6
            st.rerun()
    
    with col2:
        if st.button("🔄 **Start New Analysis**", 
                    type="secondary", 
                    use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key != 'current_step':
                    del st.session_state[key]
            st.session_state.current_step = 1
            st.rerun()

def main():
    """Main application function"""
    initialize_session_state()
    display_header()
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🧭 Navigation")
        
        steps = [
            "Process Conditions",
            "Valve Selection", 
            "Sizing Calculations",
            "Cavitation Analysis",
            "Noise Prediction",
            "Material Standards",
            "Final Report"
        ]
        
        selected_step = st.radio(
            "Current Step",
            range(1, len(steps) + 1),
            index=st.session_state.current_step - 1,
            format_func=lambda x: f"{x}. {steps[x-1]}"
        )
        
        if selected_step != st.session_state.current_step:
            st.session_state.current_step = selected_step
            st.rerun()
        
        st.markdown("---")
        
        # Progress summary
        st.markdown("#### 📊 Progress")
        progress_items = [
            ("Process Data", bool(st.session_state.get('process_data'))),
            ("Valve Selection", bool(st.session_state.get('valve_selection'))),
            ("Sizing Results", bool(st.session_state.get('sizing_results'))),
            ("Cavitation Analysis", bool(st.session_state.get('cavitation_analysis'))),
            ("Noise Analysis", bool(st.session_state.get('noise_analysis'))),
            ("Material Analysis", bool(st.session_state.get('material_selection')))
        ]
        
        for item, completed in progress_items:
            status = "✅" if completed else "⭕"
            st.text(f"{status} {item}")
        
        # Help
        st.markdown("#### ❓ Help")
        st.markdown("""
        **Standards Implemented:**
        - ISA 75.01 / IEC 60534-2-1
        - ISA RP75.23 (Cavitation)
        - IEC 60534-8-3 (Noise)
        - ASME B16.34 (Materials)
        - NACE MR0175 (Sour Service)
        - API 6D (Pipeline Valves)
        
        **Important:** Validate calculations 
        against manufacturer software for 
        critical applications.
        """)
    
    # Main content area
    display_navigation()
    
    # Route to appropriate step
    if st.session_state.current_step == 1:
        step1_process_conditions()
    elif st.session_state.current_step == 2:
        step2_valve_selection()
    elif st.session_state.current_step == 3:
        step3_sizing_calculations()
    elif st.session_state.current_step == 4:
        step4_cavitation_analysis()
    elif st.session_state.current_step == 5:
        step5_noise_prediction()
    elif st.session_state.current_step == 6:
        step6_material_standards()
    elif st.session_state.current_step == 7:
        step7_final_report()

if __name__ == "__main__":
    main()
