"""
Enhanced Control Valve Sizing Application - Professional Edition
Main Streamlit Application with Complete Standards Implementation

Features:
- ISA 75.01/IEC 60534-2-1 compliant sizing
- ISA RP75.23 cavitation analysis
- IEC 60534-8-3 noise prediction
- ASME B16.34, NACE MR0175, API 6D material standards
- Professional reporting and validation

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
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/aseemm84/CV_Sizing',
        'Report a bug': 'https://github.com/aseemm84/CV_Sizing/issues',
        'About': """
        # Enhanced Control Valve Sizing - Professional Edition
        
        Professional-grade control valve sizing application implementing:
        - ISA 75.01/IEC 60534-2-1 sizing standards
        - ISA RP75.23 cavitation analysis
        - IEC 60534-8-3 noise prediction
        - ASME B16.34, NACE MR0175, API 6D material standards
        
        **Important**: Validate calculations against official standards 
        and manufacturer software for critical applications.
        
        Author: Aseem Mehrotra, KBR Inc
        """
    }
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
            ["Liquid", "Gas/Vapor", "Steam", "Two-Phase"],
            help="Select the primary phase of the fluid at operating conditions"
        )
        
        # Fluid selection with property lookup
        if fluid_type == "Liquid":
            fluid_name = st.selectbox(
                "Fluid Type",
                ["Water", "Light Oil", "Heavy Oil", "Acids (HCl, H2SO4)", 
                 "Caustic (NaOH)", "Glycol", "Methanol", "Custom"],
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
                ["Air", "Natural Gas", "Nitrogen", "Steam", "Hydrogen", 
                 "Carbon Dioxide", "Methane", "Custom"],
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
            ["Modulating", "On-Off", "Emergency Shutdown", "Three-Way Mixing"],
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
        
        future_expansion = st.checkbox(
            "Consider Future Expansion",
            value=False,
            help="Include margin for future process modifications"
        )
        
        if future_expansion:
            expansion_factor = st.number_input(
                "Expansion Factor (%)",
                min_value=0,
                max_value=100,
                value=15,
                step=5,
                help="Additional capacity margin for future expansion"
            )
        else:
            expansion_factor = 0
    
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
        'expansion_factor': expansion_factor,
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
            expansion_factor=expansion_factor,
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
            st.experimental_rerun()

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
            st.experimental_rerun()
        
        st.markdown("---")
        
        # Settings
        st.markdown("#### ⚙️ Settings")
        st.session_state.show_advanced = st.checkbox("Show Advanced Options", value=st.session_state.show_advanced)
        
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

# Placeholder functions for remaining steps
def step2_valve_selection():
    st.subheader("🔧 Step 2: Valve Selection")
    st.info("This step will be implemented with complete valve database and manufacturer data.")
    
def step3_sizing_calculations():
    st.subheader("🧮 Step 3: Sizing Calculations")
    st.info("This step will implement complete ISA 75.01/IEC 60534-2-1 calculations.")
    
def step4_cavitation_analysis():
    st.subheader("💥 Step 4: Cavitation Analysis")
    st.info("This step will implement ISA RP75.23 five-level cavitation analysis.")
    
def step5_noise_prediction():
    st.subheader("🔊 Step 5: Noise Prediction")
    st.info("This step will implement IEC 60534-8-3 noise calculation.")
    
def step6_material_standards():
    st.subheader("🏗️ Step 6: Material Standards")
    st.info("This step will implement ASME B16.34, NACE MR0175, and API 6D compliance.")
    
def step7_final_report():
    st.subheader("📋 Step 7: Final Report")
    st.info("This step will generate professional PDF and Excel reports.")

if __name__ == "__main__":
    main()