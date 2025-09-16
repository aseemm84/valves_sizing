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

# Import calculation modules
from calculations.liquid_sizing import LiquidSizing
from calculations.gas_sizing import GasSizing
from calculations.geometry_factors import GeometryFactors
from calculations.reynolds_correction import ReynoldsCorrection

# Import standards modules
from standards.isa_rp75_23 import ISAStandardRP7523
from standards.iec_60534_8_3 import NoisePredictor
from standards.api_standards import APIStandards

# Import material modules
from materials.asme_b16_34 import ASMEB1634
from materials.nace_mr0175 import NACEMR0175
from materials.material_database import MaterialDatabase

# Import data modules
from data.valve_database import ValveDatabase
from data.fluid_properties import FluidProperties
from data.manufacturer_data import ManufacturerData

# Import utility modules
from utils.validators import ValidationHelper
from utils.unit_converters import UnitConverter
from utils.plotting import PlottingHelper
from utils.helpers import SafetyFactorCalculator

# Import reporting modules
from reporting.pdf_generator import PDFReportGenerator
from reporting.excel_export import ExcelExporter

# Import configuration
from config.constants import EngineeringConstants
from config.settings import AppSettings

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
    
    # Initialize modules
    fluid_props = FluidProperties()
    validator = ValidationHelper()
    unit_converter = UnitConverter()
    
    # Unit system selection
    st.session_state.unit_system = st.radio(
        "Unit System", 
        ["Metric (SI)", "Imperial (US)"], 
        index=0 if st.session_state.unit_system == 'metric' else 1,
        horizontal=True
    ).lower().split()[0]
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 🧪 Fluid Properties")
        
        fluid_type = st.selectbox(
            "Fluid Phase",
            ["Liquid", "Gas/Vapor"],
            help="Select the primary phase of the fluid at operating conditions"
        )
        
        # Fluid selection with property lookup
        if fluid_type == "Liquid":
            fluid_name = st.selectbox(
                "Fluid Type",
                ["Water", "Light Oil", "Heavy Oil", "Custom"],
                help="Select fluid for automatic property estimation"
            )
            
            # Get fluid properties from database
            if fluid_name != "Custom":
                fluid_data = fluid_props.get_liquid_properties(fluid_name)
            else:
                fluid_data = {}
            
            temperature = st.number_input(
                f"Temperature ({'°C' if st.session_state.unit_system == 'metric' else '°F'})",
                min_value=-50.0 if st.session_state.unit_system == 'metric' else -58.0,
                max_value=500.0 if st.session_state.unit_system == 'metric' else 932.0,
                value=fluid_data.get('typical_temp', 25.0 if st.session_state.unit_system == 'metric' else 77.0),
                step=1.0,
                help="Operating temperature of the fluid"
            )
            
            density = st.number_input(
                f"Density ({'kg/m³' if st.session_state.unit_system == 'metric' else 'lb/ft³'})",
                min_value=0.1,
                max_value=3000.0 if st.session_state.unit_system == 'metric' else 187.0,
                value=fluid_data.get('density', 998.0 if st.session_state.unit_system == 'metric' else 62.4),
                step=1.0,
                help="Fluid density at operating temperature"
            )
            
            vapor_pressure = st.number_input(
                f"Vapor Pressure ({'bar' if st.session_state.unit_system == 'metric' else 'psi'})",
                min_value=0.0,
                max_value=50.0 if st.session_state.unit_system == 'metric' else 725.0,
                value=fluid_data.get('vapor_pressure', 0.032 if st.session_state.unit_system == 'metric' else 0.46),
                step=0.001,
                format="%.3f",
                help="Vapor pressure at operating temperature"
            )
            
            viscosity = st.number_input(
                "Kinematic Viscosity (cSt)",
                min_value=0.1,
                max_value=10000.0,
                value=fluid_data.get('viscosity', 1.0),
                step=0.1,
                help="Kinematic viscosity for Reynolds number correction"
            )
            
        else:  # Gas/Vapor
            fluid_name = st.selectbox(
                "Gas Type",
                ["Air", "Natural Gas", "Nitrogen", "Custom"],
                help="Select gas for automatic property estimation"
            )
            
            # Get gas properties from database
            if fluid_name != "Custom":
                fluid_data = fluid_props.get_gas_properties(fluid_name)
            else:
                fluid_data = {}
            
            temperature = st.number_input(
                f"Temperature ({'°C' if st.session_state.unit_system == 'metric' else '°F'})",
                min_value=-50.0 if st.session_state.unit_system == 'metric' else -58.0,
                max_value=1000.0 if st.session_state.unit_system == 'metric' else 1832.0,
                value=fluid_data.get('typical_temp', 25.0 if st.session_state.unit_system == 'metric' else 77.0),
                step=1.0
            )
            
            molecular_weight = st.number_input(
                "Molecular Weight (kg/kmol)",
                min_value=1.0,
                max_value=200.0,
                value=fluid_data.get('molecular_weight', 28.97),
                step=0.01,
                help="Molecular weight for gas calculations"
            )
            
            specific_heat_ratio = st.number_input(
                "Specific Heat Ratio (k = Cp/Cv)",
                min_value=1.0,
                max_value=2.0,
                value=fluid_data.get('k_ratio', 1.4),
                step=0.01,
                help="Ratio of specific heats"
            )
            
            compressibility = st.number_input(
                "Compressibility Factor (Z)",
                min_value=0.1,
                max_value=2.0,
                value=fluid_data.get('z_factor', 1.0),
                step=0.01,
                help="Gas compressibility factor (Z=1 for ideal gas)"
            )
    
    with col2:
        st.markdown("#### 🔧 Operating Conditions")
        
        pressure_units = "bar" if st.session_state.unit_system == 'metric' else "psi"
        flow_units_liquid = ["m³/h", "L/s", "L/min"] if st.session_state.unit_system == 'metric' else ["GPM", "ft³/s", "bbl/h"]
        flow_units_gas = ["Nm³/h", "Sm³/h", "kg/h"] if st.session_state.unit_system == 'metric' else ["SCFH", "ACFM", "lb/h"]
        
        p1 = st.number_input(
            f"Inlet Pressure P1 ({pressure_units} abs)",
            min_value=0.1,
            max_value=500.0 if st.session_state.unit_system == 'metric' else 7250.0,
            value=10.0 if st.session_state.unit_system == 'metric' else 145.0,
            step=0.1,
            help="Absolute upstream pressure"
        )
        
        p2 = st.number_input(
            f"Outlet Pressure P2 ({pressure_units} abs)",
            min_value=0.01,
            max_value=p1 - 0.01,
            value=2.0 if st.session_state.unit_system == 'metric' else 29.0,
            step=0.1,
            help="Absolute downstream pressure"
        )
        
        delta_p = p1 - p2
        st.info(f"**Pressure Drop (ΔP):** {delta_p:.2f} {pressure_units}")
        
        # Flow rate inputs
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
    
    # Validation
    st.markdown("#### ✅ Input Validation")
    
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
    
    # Perform validation
    validation_errors = validator.validate_process_data(process_data)
    
    if validation_errors:
        st.error("⚠️ **Validation Errors:**")
        for error in validation_errors:
            st.error(f"• {error}")
    else:
        st.success("✅ **All inputs validated successfully**")
        
        # Calculate safety factor
        safety_calc = SafetyFactorCalculator()
        safety_factor = safety_calc.calculate_safety_factor(
            criticality=criticality,
            service_type=service_type,
            control_mode=control_mode,
            h2s_service=h2s_present
        )
        
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
    
    # Initialize valve database
    valve_db = ValveDatabase()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 🎛️ Valve Type Selection")
        
        valve_type = st.selectbox(
            "Valve Type",
            ["Globe Valve", "Ball Valve (Segmented)", "Butterfly Valve"],
            help="Select primary valve type based on application requirements"
        )
        
        if valve_type == "Globe Valve":
            valve_style = st.selectbox(
                "Globe Valve Style",
                ["Single Seat", "Cage Guided", "Double Seat"],
                help="Globe valve trim configuration"
            )
        elif valve_type == "Ball Valve (Segmented)":
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
        
        # Get valve data from database
        valve_data = valve_db.get_valve_data(valve_type, valve_style, valve_size)
        
        st.info("**Database Values (Can be modified if manufacturer data available)**")
        
        fl_factor = st.number_input(
            "FL Factor (Liquid Pressure Recovery)",
            min_value=0.1,
            max_value=1.0,
            value=valve_data.get('FL', 0.9),
            step=0.01,
            format="%.2f",
            help="Liquid pressure recovery factor"
        )
        
        xt_factor = st.number_input(
            "xT Factor (Gas Terminal Pressure Drop)",
            min_value=0.1,
            max_value=1.0,
            value=valve_data.get('xT', 0.7),
            step=0.01,
            format="%.2f", 
            help="Gas terminal pressure drop ratio"
        )
        
        fd_factor = st.number_input(
            "Fd Factor (Style Modifier)",
            min_value=0.1,
            max_value=2.0,
            value=valve_data.get('Fd', 1.0),
            step=0.1,
            format="%.1f",
            help="Valve style modifier factor"
        )
        
        max_cv = st.number_input(
            "Maximum Cv (Wide Open)",
            min_value=1.0,
            max_value=10000.0,
            value=valve_data.get('max_cv', 100.0),
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
            value=valve_data.get('rangeability', 50.0),
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
    
    # Initialize sizing modules
    if process_data['fluid_type'] == 'Liquid':
        sizer = LiquidSizing()
    else:
        sizer = GasSizing()
    
    geometry = GeometryFactors()
    
    # Perform sizing calculations
    with st.spinner("🔄 Performing professional sizing calculations..."):
        try:
            if process_data['fluid_type'] == 'Liquid':
                sizing_results = sizer.calculate_required_cv(
                    flow_rate=process_data['normal_flow'],
                    inlet_pressure=process_data['p1'],
                    outlet_pressure=process_data['p2'],
                    temperature=process_data['temperature'],
                    density=process_data['density'],
                    viscosity=process_data['viscosity'],
                    vapor_pressure=process_data['vapor_pressure'],
                    fl_factor=valve_selection['fl_factor'],
                    fd_factor=valve_selection['fd_factor'],
                    pipe_size=process_data['pipe_size'],
                    valve_size=valve_selection['valve_size'],
                    valve_style=valve_selection['valve_style'],
                    units=process_data['unit_system']
                )
            else:
                sizing_results = sizer.calculate_required_cv(
                    flow_rate=process_data['normal_flow'],
                    inlet_pressure=process_data['p1'],
                    outlet_pressure=process_data['p2'],
                    temperature=process_data['temperature'],
                    molecular_weight=process_data['molecular_weight'],
                    specific_heat_ratio=process_data['specific_heat_ratio'],
                    compressibility=process_data['compressibility'],
                    xt_factor=valve_selection['xt_factor'],
                    fd_factor=valve_selection['fd_factor'],
                    pipe_size=process_data['pipe_size'],
                    valve_size=valve_selection['valve_size'],
                    flow_units=process_data['flow_units'],
                    pressure_units='bar' if process_data['unit_system'] == 'metric' else 'psi',
                    units=process_data['unit_system']
                )
            
            # Apply safety factor
            cv_required = sizing_results['cv_required']
            safety_factor = process_data.get('safety_factor', 1.2)
            cv_with_safety = cv_required * safety_factor
            
            sizing_results['cv_with_safety_factor'] = cv_with_safety
            sizing_results['safety_factor_applied'] = safety_factor
            
        except Exception as e:
            st.error(f"❌ Sizing calculation failed: {str(e)}")
            return
    
    # Display results
    st.success("✅ **Sizing calculations completed successfully**")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 📊 Sizing Results")
        
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
            reynolds_data = sizing_results.get('reynolds_analysis', {})
            reynolds_number = reynolds_data.get('reynolds_number', 0)
            fr_factor = reynolds_data.get('fr_factor', 1.0)
            
            st.info(f"**Reynolds Number:** {reynolds_number:.0f}")
            st.info(f"**Fr Correction Factor:** {fr_factor:.3f}")
            
            # Choked flow analysis
            choked_data = sizing_results.get('choked_analysis', {})
            is_choked = choked_data.get('is_choked', False)
            sigma_service = choked_data.get('sigma_service', 0)
            
            st.info(f"**Choked Flow:** {'Yes' if is_choked else 'No'}")
            st.info(f"**Service Sigma:** {sigma_service:.1f}")
            
        else:
            # Gas analysis
            critical_data = sizing_results.get('critical_analysis', {})
            is_choked = critical_data.get('is_choked', False)
            pressure_ratio = sizing_results.get('pressure_ratio', 0)
            expansion_factor = sizing_results.get('expansion_factor', 1.0)
            
            st.info(f"**Choked Flow:** {'Yes' if is_choked else 'No'}")
            st.info(f"**Pressure Ratio:** {pressure_ratio:.3f}")
            st.info(f"**Expansion Factor (Y):** {expansion_factor:.3f}")
        
        # Piping effects
        fp_factor = sizing_results.get('fp_factor', 1.0)
        st.info(f"**Piping Geometry Factor (Fp):** {fp_factor:.3f}")
    
    with col3:
        st.markdown("#### ⚠️ Warnings & Recommendations")
        
        warnings = sizing_results.get('warnings', [])
        recommendations = sizing_results.get('recommendations', [])
        
        if warnings:
            for warning in warnings:
                st.warning(f"⚠️ {warning}")
        
        if recommendations:
            for rec in recommendations:
                st.info(f"💡 {rec}")
        
        # Opening assessment
        if opening_percent < 20:
            st.warning("⚠️ Low valve opening - consider smaller valve")
        elif opening_percent > 80:
            st.warning("⚠️ High valve opening - consider larger valve")
        else:
            st.success("✅ Good valve opening range")
        
        # Authority assessment
        authority_data = sizing_results.get('valve_authority', {})
        if authority_data:
            authority = authority_data.get('authority', 0)
            if authority < 0.25:
                st.warning("⚠️ Poor valve authority - increase pressure drop")
            else:
                st.success("✅ Adequate valve authority")
    
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
        
        # Additional parameters
        if process_data['fluid_type'] == 'Liquid':
            results_data.append(["Reynolds Number", f"{reynolds_data.get('reynolds_number', 0):.0f}", "-", "Flow regime indicator"])
            results_data.append(["Fr Factor", f"{fr_factor:.3f}", "-", "Viscous correction"])
            results_data.append(["Sigma Service", f"{sigma_service:.1f}", "-", "Cavitation parameter"])
        else:
            results_data.append(["Pressure Ratio", f"{pressure_ratio:.3f}", "-", "P2/P1"])
            results_data.append(["Expansion Factor Y", f"{expansion_factor:.3f}", "-", "Gas expansion correction"])
            results_data.append(["Critical Flow", "Yes" if is_choked else "No", "", "Sonic conditions"])
        
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
    
    # Initialize cavitation analyzer
    cavitation_analyzer = ISAStandardRP7523()
    
    # Perform cavitation analysis
    with st.spinner("🔄 Performing ISA RP75.23 cavitation analysis..."):
        try:
            cavitation_results = cavitation_analyzer.analyze_cavitation(
                inlet_pressure=process_data['p1'],
                outlet_pressure=process_data['p2'],
                vapor_pressure=process_data['vapor_pressure'],
                fl_factor=valve_selection['fl_factor'],
                valve_size=float(valve_selection['valve_size'].replace('"', '')),
                valve_type=valve_selection['valve_type'].lower(),
                units=process_data['unit_system']
            )
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
        pressure_params = cavitation_results['pressure_parameters']
        st.info(f"**Pressure Drop:** {pressure_params['delta_p']:.2f} bar")
        st.info(f"**Pressure Margin:** {pressure_params['pressure_diff']:.2f} bar")
    
    with col2:
        st.markdown("#### 🎯 Cavitation Assessment")
        
        assessment = cavitation_results['cavitation_assessment']
        
        # Current cavitation level
        current_level = assessment['current_level']
        risk_level = assessment['risk_level']
        
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
        
        st.markdown(f"**Current Level:** {level_color} {current_level}")
        st.markdown(f"**Risk Level:** {risk_level}")
        st.markdown(f"**Description:** {assessment['risk_description']}")
        
        # Sigma limits comparison
        scaled_sigmas = cavitation_results['scaled_sigmas']
        
        st.markdown("**Sigma Limits:**")
        for level, sigma_limit in scaled_sigmas.items():
            status = "✅" if sigma_fl_corrected > sigma_limit else "❌"
            st.text(f"{status} {level.title()}: {sigma_limit:.1f}")
    
    with col3:
        st.markdown("#### 💡 Recommendations")
        
        recommendations = cavitation_results['recommendations']
        primary_recs = recommendations.get('primary_recommendations', [])
        required_actions = recommendations.get('required_actions', [])
        
        if primary_recs:
            st.markdown("**Primary Recommendations:**")
            for rec in primary_recs:
                st.info(f"• {rec}")
        
        if required_actions:
            st.markdown("**Required Actions:**")
            for action in required_actions:
                st.warning(f"• {action}")
        
        # Monitoring requirements
        monitoring = recommendations.get('monitoring_requirements', {})
        if monitoring:
            frequency = monitoring.get('frequency', 'Standard')
            st.info(f"**Monitoring:** {frequency}")
    
    # Cavitation visualization
    st.markdown("#### 📈 Cavitation Analysis Chart")
    
    # Create cavitation chart
    try:
        plotter = PlottingHelper()
        fig = plotter.create_cavitation_chart(cavitation_results)
        st.plotly_chart(fig, use_container_width=True)
    except:
        # Fallback chart
        levels = ['choking', 'damage', 'constant', 'incipient', 'manufacturer']
        sigma_values = [scaled_sigmas.get(level, 0) for level in levels]
        
        fig = go.Figure()
        
        # Add sigma level bars
        colors = ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c', '#1f77b4']
        for i, (level, sigma_val, color) in enumerate(zip(levels, sigma_values, colors)):
            fig.add_trace(go.Bar(
                x=[sigma_val],
                y=[level.title()],
                orientation='h',
                marker_color=color,
                name=f'{level.title()} Limit',
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
    
    # Detailed cavitation results
    with st.expander("📋 Detailed Cavitation Analysis", expanded=False):
        
        # Scaling analysis
        scaling_analysis = cavitation_results.get('scaling_analysis', {})
        
        scaling_data = []
        scaling_data.append(["Cavitation Level", "Reference σ", "PSE", "SSE", "Scaled σ"])
        
        for level, analysis in scaling_analysis.items():
            scaling_data.append([
                level.title(),
                f"{analysis['sigma_reference']:.1f}",
                f"{analysis['pse']:.3f}",
                f"{analysis['sse']:.3f}",
                f"{analysis['sigma_scaled']:.1f}"
            ])
        
        df_scaling = pd.DataFrame(scaling_data[1:], columns=scaling_data[0])
        st.dataframe(df_scaling, use_container_width=True)
        
        # Allowable pressure drops
        allowable_drops = cavitation_results.get('allowable_drops', {})
        if allowable_drops:
            st.markdown("**Allowable Pressure Drops:**")
            for level, dp_allow in allowable_drops.items():
                st.text(f"{level.title()}: {dp_allow:.2f} bar")
    
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
    
    # Only analyze for gas service (can be extended for liquid)
    if process_data['fluid_type'] != 'Gas/Vapor':
        st.info("🔵 **Detailed noise analysis is primarily for gas/vapor service.**")
        st.markdown("For liquid service, noise is typically not a major concern unless high velocity conditions exist.")
        
        # Simple liquid noise assessment
        delta_p = process_data['p1'] - process_data['p2']
        if delta_p > 20:  # High pressure drop
            st.warning("⚠️ High pressure drop detected - consider noise evaluation")
        else:
            st.success("✅ Low pressure drop - minimal noise expected")
        
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
        return
    
    # Initialize noise predictor
    noise_predictor = NoisePredictor()
    
    # Additional noise parameters
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
        
        pipe_schedule = st.selectbox(
            "Pipe Schedule",
            ["SCH40", "SCH80", "SCH160"],
            help="Pipe wall thickness for transmission loss calculation"
        )
    
    with col2:
        st.markdown("#### ⚙️ Valve Flow Data")
        
        cv_required = sizing_results.get('cv_with_safety_factor', sizing_results.get('cv_required', 100))
        
        st.info(f"**Required Cv:** {cv_required:.1f}")
        st.info(f"**Valve Type:** {valve_selection['valve_type']}")
        st.info(f"**Valve Size:** {valve_selection['valve_size']}")
        st.info(f"**Flow Rate:** {process_data['normal_flow']:.1f} {process_data['flow_units']}")
    
    # Perform noise analysis
    with st.spinner("🔄 Performing IEC 60534-8-3 noise prediction..."):
        try:
            noise_results = noise_predictor.predict_noise_level(
                flow_rate=process_data['normal_flow'],
                inlet_pressure=process_data['p1'],
                outlet_pressure=process_data['p2'],
                temperature=process_data['temperature'],
                molecular_weight=process_data['molecular_weight'],
                specific_heat_ratio=process_data['specific_heat_ratio'],
                cv=cv_required,
                pipe_diameter=pipe_diameter_mm,
                pipe_schedule=pipe_schedule,
                distance=distance,
                units=process_data['unit_system']
        )
        except Exception as e:
            st.error(f"❌ Noise prediction failed: {str(e)}")
            return
    
    st.success("✅ **IEC 60534-8-3 noise prediction completed**")
    
    # Display results
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 📊 Noise Levels")
        
        acoustic_power = noise_results['acoustic_power']
        sound_pressure = noise_results['sound_pressure']
        
        st.metric(
            label="Sound Power Level (Lw)",
            value=f"{acoustic_power['lw_total']:.1f} dB",
            help="Acoustic power generated by valve"
        )
        
        st.metric(
            label="Sound Pressure Level (1m)",
            value=f"{sound_pressure['spl_1m']:.1f} dBA",
            help="Sound pressure level at 1 meter from pipe"
        )
        
        st.metric(
            label=f"Sound Pressure Level ({distance}m)",
            value=f"{sound_pressure['spl_at_distance']:.1f} dBA",
            help=f"Sound pressure level at {distance} meters"
        )
        
        # Peak frequency
        peak_freq = noise_results['peak_frequency']
        st.info(f"**Peak Frequency:** {peak_freq:.0f} Hz")
    
    with col2:
        st.markdown("#### 🎯 Noise Assessment")
        
        assessment = noise_results['assessment']
        spl_final = sound_pressure['spl_at_distance']
        
        # Color coding based on noise level
        if spl_final >= 90:
            noise_color = "🔴"
            noise_status = "Critical"
        elif spl_final >= 85:
            noise_color = "🟠" 
            noise_status = "High"
        elif spl_final >= 75:
            noise_color = "🟡"
            noise_status = "Moderate"
        else:
            noise_color = "🟢"
            noise_status = "Acceptable"
        
        st.markdown(f"**Noise Level:** {noise_color} {assessment['level']}")
        st.markdown(f"**Description:** {assessment['description']}")
        
        # Regulatory compliance
        compliance = assessment.get('regulatory_compliance', {})
        st.markdown("**Regulatory Compliance:**")
        for standard, data in compliance.items():
            status_icon = "✅" if data['status'] == 'Pass' else "❌"
            st.text(f"{status_icon} {standard}: {data['limit']} dBA")
    
    with col3:
        st.markdown("#### 💡 Mitigation Recommendations")
        
        recommended_actions = assessment.get('recommended_actions', [])
        
        if recommended_actions:
            for action in recommended_actions:
                if "Critical" in assessment['level'] or "High" in assessment['level']:
                    st.error(f"• {action}")
                elif "Moderate" in assessment['level']:
                    st.warning(f"• {action}")
                else:
                    st.info(f"• {action}")
        
        # Specific recommendations based on noise level
        if spl_final > 90:
            st.error("🚨 **Immediate Action Required**")
            st.markdown("""
            - Install acoustic insulation
            - Consider low-noise trim
            - Implement hearing protection
            """)
        elif spl_final > 85:
            st.warning("⚠️ **Mitigation Recommended**")
            st.markdown("""
            - Evaluate acoustic treatment
            - Monitor noise levels
            - Consider trim modifications
            """)
        else:
            st.success("✅ **Acceptable Noise Level**")
    
    # Noise analysis details
    with st.expander("📋 Detailed Noise Analysis", expanded=False):
        
        # Acoustic power breakdown
        st.markdown("**Acoustic Power Analysis:**")
        power_data = [
            ["Parameter", "Value", "Units"],
            ["Mass Flow Rate", f"{acoustic_power['mass_flow']:.2f}", "kg/s"],
            ["Mechanical Power", f"{acoustic_power['mechanical_power']:.1f}", "W"],
            ["Acoustic Efficiency", f"{acoustic_power['acoustic_efficiency']:.6f}", "-"],
            ["Acoustic Power", f"{acoustic_power['acoustic_power']:.3f}", "W"],
            ["Sound Power Level", f"{acoustic_power['lw_total']:.1f}", "dB"]
        ]
        
        df_power = pd.DataFrame(power_data[1:], columns=power_data[0])
        st.dataframe(df_power, use_container_width=True)
        
        # Transmission loss
        transmission = noise_results['transmission_loss']
        st.markdown("**Pipe Transmission Loss:**")
        trans_data = [
            ["Parameter", "Value", "Units"],
            ["Wall Thickness", f"{transmission['wall_thickness']:.3f}", "m"],
            ["Surface Mass", f"{transmission['surface_mass']:.1f}", "kg/m²"],
            ["Mass Law TL", f"{transmission['mass_law_tl']:.1f}", "dB"],
            ["Total Loss", f"{transmission['total_loss']:.1f}", "dB"]
        ]
        
        df_trans = pd.DataFrame(trans_data[1:], columns=trans_data[0])
        st.dataframe(df_trans, use_container_width=True)
    
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
    
    # Initialize material modules
    asme_checker = ASMEB1634()
    nace_checker = NACEMR0175()
    api_checker = APIStandards()
    material_db = MaterialDatabase()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 🔩 ASME B16.34 Compliance")
        
        # Material selection
        available_materials = asme_checker.get_available_materials()
        material_names = {
            'A216_WCB': 'Carbon Steel (WCB)',
            'A351_CF8M': 'Stainless Steel 316 (CF8M)', 
            'A351_CF3M': 'Stainless Steel 316L (CF3M)'
        }
        
        selected_material = st.selectbox(
            "Valve Body Material",
            available_materials,
            format_func=lambda x: material_names.get(x, x),
            help="Select valve body material"
        )
        
        pressure_class = st.selectbox(
            "Pressure Class",
            ["class_150", "class_300", "class_600", "class_900", "class_1500"],
            index=1,  # Default to Class 300
            format_func=lambda x: x.replace('class_', 'Class '),
            help="ASME pressure class rating"
        )
        
        # Check ASME compliance
        operating_pressure = max(process_data['p1'], process_data['p2'])
        operating_temp = process_data['temperature']
        
        asme_results = asme_checker.check_pressure_temperature_compliance(
            material=selected_material,
            pressure_class=pressure_class,
            operating_pressure=operating_pressure,
            operating_temperature=operating_temp
        )
        
        if 'error' not in asme_results:
            compliant = asme_results['compliant']
            safety_margin = asme_results['safety_margin_percent']
            
            if compliant:
                st.success(f"✅ ASME Compliant")
                st.info(f"Safety Margin: {safety_margin:.1f}%")
            else:
                st.error("❌ Non-compliant with ASME B16.34")
            
            st.info(f"**Allowable Pressure:** {asme_results['allowable_pressure_bar']:.1f} bar")
            st.info(f"**Operating Pressure:** {operating_pressure:.1f} bar")
        else:
            st.error(f"ASME Check Error: {asme_results['error']}")
    
    with col2:
        st.markdown("#### ☠️ NACE MR0175 Compliance")
        
        h2s_present = process_data.get('h2s_present', False)
        
        if h2s_present:
            h2s_partial_pressure = process_data.get('h2s_partial_pressure', 0)
            
            # H2S calculation
            total_pressure = process_data['p1']
            h2s_mole_percent = st.number_input(
                "H2S Mole Percent (%)",
                min_value=0.0,
                max_value=100.0,
                value=1.0,
                step=0.1,
                help="H2S concentration in mol%"
            )
            
            h2s_calc = nace_checker.calculate_h2s_partial_pressure(
                total_pressure=total_pressure,
                h2s_mole_percent=h2s_mole_percent,
                pressure_units='bar'
            )
            
            st.info(f"**H2S Partial Pressure:** {h2s_calc['h2s_partial_pressure_bar']:.4f} bar")
            
            if h2s_calc['exceeds_threshold']:
                st.warning("⚠️ NACE MR0175 applicable")
                
                # Environmental severity
                ph_value = st.number_input("pH Value", 3.0, 14.0, 7.0, 0.1)
                chloride_ppm = st.number_input("Chloride (ppm)", 0, 50000, 0, 100)
                
                env_assessment = nace_checker.assess_environmental_severity(
                    h2s_partial_pressure_bar=h2s_calc['h2s_partial_pressure_bar'],
                    temperature_c=operating_temp,
                    ph=ph_value,
                    chloride_ppm=chloride_ppm
                )
                
                severity = env_assessment['overall_severity']
                st.info(f"**Severity:** {severity}")
                st.caption(env_assessment['overall_description'])
                
                # Material compliance
                material_category = 'stainless_steel_316' if 'CF8M' in selected_material else 'carbon_steel'
                hardness_hrc = st.number_input("Material Hardness (HRC)", 10, 40, 20, 1)
                
                material_compliance = nace_checker.check_material_compliance(
                    material_category=material_category,
                    hardness_hrc=hardness_hrc,
                    environmental_severity=severity
                )
                
                if material_compliance['overall_compliant']:
                    st.success("✅ NACE Compliant")
                else:
                    st.error("❌ NACE Non-compliant")
                    
            else:
                st.success("✅ Below NACE threshold")
        else:
            st.info("🔵 No H2S - NACE not applicable")
    
    with col3:
        st.markdown("#### 🛢️ API 6D Compliance")
        
        # API 6D requirements
        fire_safe_req = process_data.get('fire_safe_required', False)
        fugitive_class = process_data.get('fugitive_emissions', 'Standard')
        
        api_config = {
            'fire_safe_required': fire_safe_req,
            'fugitive_emissions': fugitive_class,
            'double_block_bleed': st.checkbox("Double Block & Bleed", help="DBB capability required"),
            'full_port': st.checkbox("Full Port Design", help="For pipeline pigging")
        }
        
        api_compliance = api_checker.check_api_6d_compliance(api_config)
        
        compliance_level = api_compliance['compliance_level']
        requirements_met = api_compliance['requirements_met']
        certifications = api_compliance['certification_needed']
        
        st.info(f"**Compliance:** {compliance_level}")
        
        if requirements_met:
            st.success("✅ Requirements Met:")
            for req in requirements_met:
                st.text(f"• {req}")
        
        if certifications:
            st.warning("📋 Certifications Needed:")
            for cert in certifications:
                st.text(f"• {cert}")
    
    # Material recommendation
    st.markdown("#### 🎯 Material Recommendations")
    
    material_recommendations = material_db.recommend_materials(
        temperature_c=operating_temp,
        service_type=process_data['service_type'].lower().replace(' ', '_'),
        pressure_bar=operating_pressure,
        sour_service=h2s_present,
        budget_factor=1.0
    )
    
    recommended_materials = material_recommendations['recommended_materials']
    
    if recommended_materials:
        st.success("✅ **Recommended Materials (Ranked by Suitability):**")
        
        # Create DataFrame for display
        material_data = []
        for i, material in enumerate(recommended_materials[:5], 1):  # Top 5
            material_data.append([
                f"{i}",
                material['material_name'],
                material['category'],
                f"{material['suitability_score']:.0f}/100",
                f"{material['cost_factor']:.1f}x",
                material['corrosion_resistance'],
                material['sour_service_rating']
            ])
        
        df_materials = pd.DataFrame(
            material_data,
            columns=["Rank", "Material", "Category", "Score", "Cost", "Corrosion", "Sour Service"]
        )
        
        st.dataframe(df_materials, use_container_width=True)
        
        # Selection notes
        selection_notes = material_recommendations['selection_notes']
        if selection_notes:
            with st.expander("📝 Material Selection Notes", expanded=False):
                for note in selection_notes:
                    st.info(f"• {note}")
    
    # Compliance summary
    st.markdown("#### 📋 Compliance Summary")
    
    compliance_summary = {
        'ASME B16.34': asme_results.get('compliant', False) if 'error' not in asme_results else False,
        'NACE MR0175': material_compliance.get('overall_compliant', True) if h2s_present else True,
        'API 6D': len(api_compliance['requirements_met']) > 0 if fire_safe_req or fugitive_class != 'Standard' else True
    }
    
    col1, col2, col3 = st.columns(3)
    
    for i, (standard, compliant) in enumerate(compliance_summary.items()):
        with [col1, col2, col3][i]:
            status = "✅ Compliant" if compliant else "❌ Non-compliant"
            color = "green" if compliant else "red"
            st.markdown(f"**{standard}:** :{color}[{status}]")
    
    # Store results
    material_analysis = {
        'selected_material': selected_material,
        'pressure_class': pressure_class,
        'asme_compliance': asme_results,
        'nace_compliance': material_compliance if h2s_present else {'overall_compliant': True},
        'api_compliance': api_compliance,
        'material_recommendations': material_recommendations,
        'compliance_summary': compliance_summary
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
        include_charts = st.checkbox("Include Charts and Graphs", value=True)
        
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
        total_standards = len(compliance_summary) if compliance_summary else 3
        compliant_standards = sum(compliance_summary.values()) if compliance_summary else 2
        
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
        findings.append("⚠️ Valve opening outside recommended range")
    
    # Cavitation findings
    if cavitation_analysis:
        risk_level = cavitation_analysis.get('cavitation_assessment', {}).get('risk_level', 'Unknown')
        if risk_level in ['None', 'Low']:
            findings.append("✅ No significant cavitation concerns")
        else:
            findings.append(f"⚠️ {risk_level} cavitation risk detected")
    
    # Noise findings
    if noise_analysis:
        noise_level = noise_analysis.get('sound_pressure', {}).get('spl_at_distance', 0)
        if noise_level < 85:
            findings.append("✅ Noise level within acceptable limits")
        else:
            findings.append(f"⚠️ High noise level predicted ({noise_level:.0f} dBA)")
    
    # Material findings
    if material_selection:
        compliance_sum = material_selection.get('compliance_summary', {})
        if all(compliance_sum.values()):
            findings.append("✅ Material selection meets all applicable standards")
        else:
            findings.append("⚠️ Material compliance issues identified")
    
    for finding in findings:
        st.markdown(f"• {finding}")
    
    # Report generation
    st.markdown("#### 📥 Generate Reports")
    
    col1, col2 = st.columns(2)
    
    # Compile all data for report generation
    project_data = {
        'project_name': project_name,
        'tag_number': tag_number,
        'engineer': engineer_name,
        'service_description': service_description,
        **process_data
    }
    
    analysis_results = {
        'sizing_results': sizing_results,
        'cavitation_analysis': cavitation_analysis,
        'noise_analysis': noise_analysis,
        'material_analysis': material_selection
    }
    
    with col1:
        st.markdown("**PDF Report**")
        
        if st.button("📄 Generate PDF Report", use_container_width=True):
            try:
                pdf_generator = PDFReportGenerator()
                pdf_data = pdf_generator.generate_complete_report(
                    project_data=project_data,
                    sizing_results=sizing_results,
                    analysis_results=analysis_results
                )
                
                if isinstance(pdf_data, bytes) and len(pdf_data) > 100:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_data,
                        file_name=f"{tag_number}_Valve_Sizing_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF report generated successfully!")
                else:
                    st.error("❌ PDF generation failed - check ReportLab installation")
                    
            except Exception as e:
                st.error(f"❌ PDF generation error: {str(e)}")
    
    with col2:
        st.markdown("**Excel Export**")
        
        if st.button("📊 Generate Excel Export", use_container_width=True):
            try:
                excel_exporter = ExcelExporter()
                excel_data = excel_exporter.export_complete_results(
                    project_data=project_data,
                    sizing_results=sizing_results,
                    analysis_results=analysis_results
                )
                
                if isinstance(excel_data, bytes) and len(excel_data) > 100:
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_data,
                        file_name=f"{tag_number}_Valve_Sizing_Data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.success("✅ Excel export generated successfully!")
                else:
                    st.error("❌ Excel generation failed - check openpyxl installation")
                    
            except Exception as e:
                st.error(f"❌ Excel generation error: {str(e)}")
    
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
    
    # Calculation summary table
    with st.expander("📊 Complete Calculation Summary", expanded=False):
        
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
            noise_level = noise_analysis.get('sound_pressure', {}).get('spl_at_distance', 0)
            summary_data.append(["Sound Pressure Level", f"{noise_level:.1f}", "dBA", "IEC 60534-8-3"])
        
        # Create and display summary table
        df_summary = pd.DataFrame(summary_data[1:], columns=summary_data[0])
        st.dataframe(df_summary, use_container_width=True)
    
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
        
        # Settings
        st.markdown("#### ⚙️ Settings")
        st.session_state.show_advanced = st.checkbox("Show Advanced Options", value=st.session_state.show_advanced)
        
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
        - ISA RP75.23
        - IEC 60534-8-3
        - ASME B16.34
        - NACE MR0175
        - API 6D
        
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
