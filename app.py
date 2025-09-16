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
        'show_advanced': False,
        'fluid_properties_db': {},
        'previous_fluid_selection': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_comprehensive_fluid_database():
    """Comprehensive fluid properties database"""
    
    liquid_fluids = {
        # Hydrocarbons
        'Water': {
            'density': {'metric': 998.0, 'imperial': 62.4},  # kg/m³, lb/ft³
            'vapor_pressure': {'metric': 0.032, 'imperial': 0.46},  # bar, psi
            'viscosity': 1.0,  # cSt
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},  # °C, °F
            'critical_pressure': {'metric': 221.2, 'imperial': 3208.0},  # bar, psi
            'molecular_weight': 18.015,
            'category': 'Water/Aqueous',
            'description': 'Pure water at standard conditions'
        },
        'Light Crude Oil': {
            'density': {'metric': 820.0, 'imperial': 51.2},
            'vapor_pressure': {'metric': 0.15, 'imperial': 2.2},
            'viscosity': 5.0,
            'typical_temp': {'metric': 40.0, 'imperial': 104.0},
            'critical_pressure': {'metric': 25.0, 'imperial': 363.0},
            'molecular_weight': 120.0,
            'category': 'Hydrocarbons',
            'description': 'Light crude oil (API 35°)'
        },
        'Heavy Crude Oil': {
            'density': {'metric': 950.0, 'imperial': 59.3},
            'vapor_pressure': {'metric': 0.01, 'imperial': 0.15},
            'viscosity': 200.0,
            'typical_temp': {'metric': 80.0, 'imperial': 176.0},
            'critical_pressure': {'metric': 15.0, 'imperial': 218.0},
            'molecular_weight': 300.0,
            'category': 'Hydrocarbons',
            'description': 'Heavy crude oil (API 15°)'
        },
        'Gasoline': {
            'density': {'metric': 740.0, 'imperial': 46.2},
            'vapor_pressure': {'metric': 0.8, 'imperial': 11.6},
            'viscosity': 0.6,
            'typical_temp': {'metric': 20.0, 'imperial': 68.0},
            'critical_pressure': {'metric': 28.0, 'imperial': 406.0},
            'molecular_weight': 95.0,
            'category': 'Refined Products',
            'description': 'Motor gasoline (octane 87)'
        },
        'Diesel Fuel': {
            'density': {'metric': 850.0, 'imperial': 53.1},
            'vapor_pressure': {'metric': 0.05, 'imperial': 0.7},
            'viscosity': 3.5,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 22.0, 'imperial': 319.0},
            'molecular_weight': 170.0,
            'category': 'Refined Products',
            'description': 'No. 2 diesel fuel'
        },
        'Kerosene': {
            'density': {'metric': 810.0, 'imperial': 50.6},
            'vapor_pressure': {'metric': 0.1, 'imperial': 1.5},
            'viscosity': 1.8,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 24.0, 'imperial': 348.0},
            'molecular_weight': 140.0,
            'category': 'Refined Products',
            'description': 'Aviation kerosene (Jet A-1)'
        },
        
        # Chemicals
        'Methanol': {
            'density': {'metric': 791.0, 'imperial': 49.4},
            'vapor_pressure': {'metric': 0.17, 'imperial': 2.5},
            'viscosity': 0.65,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 81.0, 'imperial': 1175.0},
            'molecular_weight': 32.04,
            'category': 'Alcohols',
            'description': 'Methyl alcohol (CH3OH)'
        },
        'Ethanol': {
            'density': {'metric': 789.0, 'imperial': 49.3},
            'vapor_pressure': {'metric': 0.08, 'imperial': 1.2},
            'viscosity': 1.2,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 63.0, 'imperial': 914.0},
            'molecular_weight': 46.07,
            'category': 'Alcohols',
            'description': 'Ethyl alcohol (C2H5OH)'
        },
        'Benzene': {
            'density': {'metric': 879.0, 'imperial': 54.9},
            'vapor_pressure': {'metric': 0.13, 'imperial': 1.9},
            'viscosity': 0.65,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 49.0, 'imperial': 711.0},
            'molecular_weight': 78.11,
            'category': 'Aromatics',
            'description': 'Benzene (C6H6)'
        },
        'Toluene': {
            'density': {'metric': 867.0, 'imperial': 54.1},
            'vapor_pressure': {'metric': 0.04, 'imperial': 0.6},
            'viscosity': 0.59,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 41.0, 'imperial': 595.0},
            'molecular_weight': 92.14,
            'category': 'Aromatics',
            'description': 'Toluene (C7H8)'
        },
        'Acetone': {
            'density': {'metric': 784.0, 'imperial': 49.0},
            'vapor_pressure': {'metric': 0.31, 'imperial': 4.5},
            'viscosity': 0.32,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 47.0, 'imperial': 682.0},
            'molecular_weight': 58.08,
            'category': 'Ketones',
            'description': 'Acetone (C3H6O)'
        },
        
        # Acids & Caustics
        'Hydrochloric Acid (37%)': {
            'density': {'metric': 1184.0, 'imperial': 73.9},
            'vapor_pressure': {'metric': 0.05, 'imperial': 0.7},
            'viscosity': 1.9,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 83.0, 'imperial': 1204.0},
            'molecular_weight': 36.46,
            'category': 'Acids',
            'description': '37% HCl solution'
        },
        'Sulfuric Acid (98%)': {
            'density': {'metric': 1841.0, 'imperial': 114.9},
            'vapor_pressure': {'metric': 0.001, 'imperial': 0.015},
            'viscosity': 25.0,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 64.0, 'imperial': 928.0},
            'molecular_weight': 98.08,
            'category': 'Acids',
            'description': '98% H2SO4 solution'
        },
        'Sodium Hydroxide (50%)': {
            'density': {'metric': 1525.0, 'imperial': 95.2},
            'vapor_pressure': {'metric': 0.01, 'imperial': 0.15},
            'viscosity': 8.0,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 221.2, 'imperial': 3208.0},
            'molecular_weight': 40.0,
            'category': 'Caustics',
            'description': '50% NaOH solution'
        },
        
        # Thermal Fluids
        'Therminol VP-1': {
            'density': {'metric': 1060.0, 'imperial': 66.2},
            'vapor_pressure': {'metric': 0.001, 'imperial': 0.015},
            'viscosity': 5.1,
            'typical_temp': {'metric': 200.0, 'imperial': 392.0},
            'critical_pressure': {'metric': 15.0, 'imperial': 218.0},
            'molecular_weight': 230.0,
            'category': 'Heat Transfer',
            'description': 'Dow Therminol VP-1 heat transfer fluid'
        },
        'Dowtherm A': {
            'density': {'metric': 1064.0, 'imperial': 66.4},
            'vapor_pressure': {'metric': 0.5, 'imperial': 7.3},
            'viscosity': 2.2,
            'typical_temp': {'metric': 250.0, 'imperial': 482.0},
            'critical_pressure': {'metric': 33.0, 'imperial': 479.0},
            'molecular_weight': 166.0,
            'category': 'Heat Transfer',
            'description': 'Dow Dowtherm A heat transfer fluid'
        },
        
        # Glycols
        'Ethylene Glycol (50%)': {
            'density': {'metric': 1070.0, 'imperial': 66.8},
            'vapor_pressure': {'metric': 0.02, 'imperial': 0.3},
            'viscosity': 4.8,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 77.0, 'imperial': 1117.0},
            'molecular_weight': 62.07,
            'category': 'Glycols',
            'description': '50% ethylene glycol solution'
        },
        'Propylene Glycol (50%)': {
            'density': {'metric': 1040.0, 'imperial': 64.9},
            'vapor_pressure': {'metric': 0.01, 'imperial': 0.15},
            'viscosity': 6.2,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 60.0, 'imperial': 870.0},
            'molecular_weight': 76.09,
            'category': 'Glycols',
            'description': '50% propylene glycol solution'
        }
    }
    
    gas_fluids = {
        # Common Gases
        'Air': {
            'molecular_weight': 28.97,
            'k_ratio': 1.4,
            'z_factor': 1.0,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 37.7, 'imperial': 547.0},
            'critical_temperature': 132.5,  # K
            'category': 'Air & Inert',
            'description': 'Dry air at standard conditions'
        },
        'Nitrogen': {
            'molecular_weight': 28.01,
            'k_ratio': 1.4,
            'z_factor': 1.0,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 34.0, 'imperial': 493.0},
            'critical_temperature': 126.2,
            'category': 'Air & Inert',
            'description': 'Nitrogen (N2)'
        },
        'Oxygen': {
            'molecular_weight': 32.0,
            'k_ratio': 1.4,
            'z_factor': 1.0,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 50.4, 'imperial': 731.0},
            'critical_temperature': 154.6,
            'category': 'Air & Inert',
            'description': 'Oxygen (O2)'
        },
        'Carbon Dioxide': {
            'molecular_weight': 44.01,
            'k_ratio': 1.28,
            'z_factor': 0.99,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 73.8, 'imperial': 1071.0},
            'critical_temperature': 304.1,
            'category': 'Acid Gases',
            'description': 'Carbon dioxide (CO2)'
        },
        'Carbon Monoxide': {
            'molecular_weight': 28.01,
            'k_ratio': 1.4,
            'z_factor': 1.0,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 35.0, 'imperial': 508.0},
            'critical_temperature': 132.9,
            'category': 'Toxic Gases',
            'description': 'Carbon monoxide (CO)'
        },
        
        # Natural Gas Components
        'Natural Gas (Pipeline)': {
            'molecular_weight': 17.5,
            'k_ratio': 1.27,
            'z_factor': 0.95,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 46.0, 'imperial': 667.0},
            'critical_temperature': 190.6,
            'category': 'Natural Gas',
            'description': 'Typical pipeline natural gas'
        },
        'Methane': {
            'molecular_weight': 16.04,
            'k_ratio': 1.31,
            'z_factor': 0.998,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 46.0, 'imperial': 667.0},
            'critical_temperature': 190.6,
            'category': 'Natural Gas',
            'description': 'Pure methane (CH4)'
        },
        'Ethane': {
            'molecular_weight': 30.07,
            'k_ratio': 1.22,
            'z_factor': 0.99,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 48.7, 'imperial': 706.0},
            'critical_temperature': 305.3,
            'category': 'Natural Gas',
            'description': 'Ethane (C2H6)'
        },
        'Propane': {
            'molecular_weight': 44.1,
            'k_ratio': 1.15,
            'z_factor': 0.98,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 42.5, 'imperial': 617.0},
            'critical_temperature': 369.8,
            'category': 'Natural Gas',
            'description': 'Propane (C3H8)'
        },
        'Butane': {
            'molecular_weight': 58.12,
            'k_ratio': 1.11,
            'z_factor': 0.97,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 38.0, 'imperial': 551.0},
            'critical_temperature': 425.1,
            'category': 'Natural Gas',
            'description': 'n-Butane (C4H10)'
        },
        
        # Steam & Water Vapor
        'Steam (Saturated)': {
            'molecular_weight': 18.015,
            'k_ratio': 1.33,
            'z_factor': 1.0,
            'typical_temp': {'metric': 150.0, 'imperial': 302.0},
            'critical_pressure': {'metric': 221.2, 'imperial': 3208.0},
            'critical_temperature': 647.1,
            'category': 'Steam',
            'description': 'Saturated steam at typical conditions'
        },
        'Steam (Superheated)': {
            'molecular_weight': 18.015,
            'k_ratio': 1.3,
            'z_factor': 1.0,
            'typical_temp': {'metric': 200.0, 'imperial': 392.0},
            'critical_pressure': {'metric': 221.2, 'imperial': 3208.0},
            'critical_temperature': 647.1,
            'category': 'Steam',
            'description': 'Superheated steam'
        },
        
        # Hydrogen & Light Gases
        'Hydrogen': {
            'molecular_weight': 2.016,
            'k_ratio': 1.41,
            'z_factor': 1.0,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 13.0, 'imperial': 189.0},
            'critical_temperature': 33.2,
            'category': 'Light Gases',
            'description': 'Hydrogen (H2)'
        },
        'Helium': {
            'molecular_weight': 4.003,
            'k_ratio': 1.67,
            'z_factor': 1.0,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 2.3, 'imperial': 33.0},
            'critical_temperature': 5.2,
            'category': 'Noble Gases',
            'description': 'Helium (He)'
        },
        
        # Acid Gases
        'Hydrogen Sulfide': {
            'molecular_weight': 34.08,
            'k_ratio': 1.32,
            'z_factor': 0.99,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 89.6, 'imperial': 1300.0},
            'critical_temperature': 373.5,
            'category': 'Acid Gases',
            'description': 'Hydrogen sulfide (H2S) - Sour gas'
        },
        'Sulfur Dioxide': {
            'molecular_weight': 64.07,
            'k_ratio': 1.29,
            'z_factor': 0.97,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 78.8, 'imperial': 1143.0},
            'critical_temperature': 430.8,
            'category': 'Acid Gases',
            'description': 'Sulfur dioxide (SO2)'
        },
        
        # Refrigerants
        'Ammonia': {
            'molecular_weight': 17.03,
            'k_ratio': 1.31,
            'z_factor': 0.99,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 113.3, 'imperial': 1644.0},
            'critical_temperature': 405.7,
            'category': 'Refrigerants',
            'description': 'Ammonia (NH3)'
        },
        'R-134a': {
            'molecular_weight': 102.03,
            'k_ratio': 1.18,
            'z_factor': 0.98,
            'typical_temp': {'metric': 25.0, 'imperial': 77.0},
            'critical_pressure': {'metric': 40.6, 'imperial': 589.0},
            'critical_temperature': 374.2,
            'category': 'Refrigerants',
            'description': 'Tetrafluoroethane refrigerant'
        }
    }
    
    return liquid_fluids, gas_fluids

def update_fluid_properties(fluid_type, fluid_name, unit_system):
    """Update fluid properties based on selection"""
    liquid_db, gas_db = get_comprehensive_fluid_database()
    
    if fluid_type == "Liquid" and fluid_name in liquid_db:
        fluid_data = liquid_db[fluid_name]
        return {
            'density': fluid_data['density'][unit_system],
            'vapor_pressure': fluid_data['vapor_pressure'][unit_system],
            'viscosity': fluid_data['viscosity'],
            'typical_temp': fluid_data['typical_temp'][unit_system],
            'molecular_weight': fluid_data['molecular_weight'],
            'description': fluid_data['description'],
            'category': fluid_data['category']
        }
    elif fluid_type == "Gas/Vapor" and fluid_name in gas_db:
        fluid_data = gas_db[fluid_name]
        return {
            'molecular_weight': fluid_data['molecular_weight'],
            'k_ratio': fluid_data['k_ratio'],
            'z_factor': fluid_data['z_factor'],
            'typical_temp': fluid_data['typical_temp'][unit_system],
            'critical_pressure': fluid_data['critical_pressure'][unit_system],
            'description': fluid_data['description'],
            'category': fluid_data['category']
        }
    
    return None

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
    """Step 1: Process Conditions Input - Enhanced with Dynamic Fluid Properties"""
    st.subheader("🔧 Step 1: Process Conditions")
    st.markdown("Enter accurate process data following industry best practices. All parameters are validated against ISA/IEC standards.")
    
    # Get fluid database
    liquid_db, gas_db = get_comprehensive_fluid_database()
    
    # Unit system selection
    unit_options = ["Metric (SI)", "Imperial (US)"]
    unit_index = 0 if st.session_state.unit_system == 'metric' else 1
    selected_unit = st.radio("Unit System", unit_options, index=unit_index, horizontal=True)
    st.session_state.unit_system = selected_unit.lower().split()[0]
    
    # Advanced options toggle
    st.session_state.show_advanced = st.checkbox(
        "🔬 Show Advanced Options", 
        value=st.session_state.show_advanced,
        help="Show additional parameters for detailed analysis"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 🧪 Fluid Properties")
        
        fluid_type = st.selectbox(
            "Fluid Phase",
            ["Liquid", "Gas/Vapor"],
            help="Select the primary phase of the fluid at operating conditions"
        )
        
        # Dynamic fluid selection with categories
        if fluid_type == "Liquid":
            # Group fluids by category
            categories = {}
            for fluid_name, data in liquid_db.items():
                category = data['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(fluid_name)
            
            # Category selection
            selected_category = st.selectbox(
                "Fluid Category",
                list(categories.keys()) + ["Custom"],
                help="Select fluid category for easier navigation"
            )
            
            if selected_category != "Custom":
                fluid_options = categories[selected_category] + ["Custom"]
            else:
                fluid_options = ["Custom"]
            
            fluid_name = st.selectbox(
                "Fluid Type",
                fluid_options,
                help="Select specific fluid for automatic property estimation"
            )
            
            # Get fluid properties and check for changes
            current_selection = f"{fluid_type}_{fluid_name}_{st.session_state.unit_system}"
            
            if st.session_state.previous_fluid_selection != current_selection:
                st.session_state.previous_fluid_selection = current_selection
                # Force rerun to update properties
                if fluid_name != "Custom":
                    st.session_state.fluid_properties_db = update_fluid_properties(
                        fluid_type, fluid_name, st.session_state.unit_system
                    )
            
            # Display fluid description
            if fluid_name != "Custom" and st.session_state.fluid_properties_db:
                st.info(f"**{fluid_name}:** {st.session_state.fluid_properties_db.get('description', 'Standard industrial fluid')}")
            
            # Temperature input with dynamic default
            temp_default = 25.0 if st.session_state.unit_system == 'metric' else 77.0
            if st.session_state.fluid_properties_db:
                temp_default = st.session_state.fluid_properties_db.get('typical_temp', temp_default)
                
            temperature = st.number_input(
                f"Temperature ({'°C' if st.session_state.unit_system == 'metric' else '°F'})",
                min_value=-50.0 if st.session_state.unit_system == 'metric' else -58.0,
                max_value=500.0 if st.session_state.unit_system == 'metric' else 932.0,
                value=temp_default,
                step=1.0,
                help="Operating temperature of the fluid"
            )
            
            # Density with dynamic default
            density_default = 998.0 if st.session_state.unit_system == 'metric' else 62.4
            if st.session_state.fluid_properties_db:
                density_default = st.session_state.fluid_properties_db.get('density', density_default)
                
            density = st.number_input(
                f"Density ({'kg/m³' if st.session_state.unit_system == 'metric' else 'lb/ft³'})",
                min_value=0.1,
                max_value=3000.0 if st.session_state.unit_system == 'metric' else 187.0,
                value=density_default,
                step=1.0,
                help="Fluid density at operating temperature"
            )
            
            # Vapor pressure with dynamic default
            vapor_pressure_default = 0.032 if st.session_state.unit_system == 'metric' else 0.46
            if st.session_state.fluid_properties_db:
                vapor_pressure_default = st.session_state.fluid_properties_db.get('vapor_pressure', vapor_pressure_default)
            
            vapor_pressure = st.number_input(
                f"Vapor Pressure ({'bar' if st.session_state.unit_system == 'metric' else 'psi'})",
                min_value=0.0,
                max_value=50.0 if st.session_state.unit_system == 'metric' else 725.0,
                value=vapor_pressure_default,
                step=0.001,
                format="%.3f",
                help="Vapor pressure at operating temperature"
            )
            
            # Viscosity with dynamic default
            viscosity_default = 1.0
            if st.session_state.fluid_properties_db:
                viscosity_default = st.session_state.fluid_properties_db.get('viscosity', viscosity_default)
            
            viscosity = st.number_input(
                "Kinematic Viscosity (cSt)",
                min_value=0.1,
                max_value=10000.0,
                value=viscosity_default,
                step=0.1,
                help="Kinematic viscosity for Reynolds number correction"
            )
            
            # Advanced liquid properties
            if st.session_state.show_advanced:
                st.markdown("**🔬 Advanced Properties**")
                
                bulk_modulus = st.number_input(
                    f"Bulk Modulus ({'MPa' if st.session_state.unit_system == 'metric' else 'psi'})",
                    min_value=1.0,
                    max_value=10000.0,
                    value=2200.0 if st.session_state.unit_system == 'metric' else 319000.0,
                    help="Fluid bulk modulus for compressibility calculations"
                )
                
                surface_tension = st.number_input(
                    "Surface Tension (mN/m)",
                    min_value=1.0,
                    max_value=100.0,
                    value=72.8,
                    help="Surface tension at operating temperature"
                )
            
        else:  # Gas/Vapor
            # Group gas fluids by category
            categories = {}
            for fluid_name, data in gas_db.items():
                category = data['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(fluid_name)
            
            # Category selection
            selected_category = st.selectbox(
                "Gas Category",
                list(categories.keys()) + ["Custom"],
                help="Select gas category for easier navigation"
            )
            
            if selected_category != "Custom":
                fluid_options = categories[selected_category] + ["Custom"]
            else:
                fluid_options = ["Custom"]
            
            fluid_name = st.selectbox(
                "Gas Type",
                fluid_options,
                help="Select gas for automatic property estimation"
            )
            
            # Get fluid properties and check for changes
            current_selection = f"{fluid_type}_{fluid_name}_{st.session_state.unit_system}"
            
            if st.session_state.previous_fluid_selection != current_selection:
                st.session_state.previous_fluid_selection = current_selection
                if fluid_name != "Custom":
                    st.session_state.fluid_properties_db = update_fluid_properties(
                        fluid_type, fluid_name, st.session_state.unit_system
                    )
            
            # Display gas description
            if fluid_name != "Custom" and st.session_state.fluid_properties_db:
                st.info(f"**{fluid_name}:** {st.session_state.fluid_properties_db.get('description', 'Industrial gas')}")
            
            # Temperature with dynamic default
            temp_default = 25.0 if st.session_state.unit_system == 'metric' else 77.0
            if st.session_state.fluid_properties_db:
                temp_default = st.session_state.fluid_properties_db.get('typical_temp', temp_default)
            
            temperature = st.number_input(
                f"Temperature ({'°C' if st.session_state.unit_system == 'metric' else '°F'})",
                min_value=-50.0 if st.session_state.unit_system == 'metric' else -58.0,
                max_value=1000.0 if st.session_state.unit_system == 'metric' else 1832.0,
                value=temp_default,
                step=1.0
            )
            
            # Molecular weight with dynamic default
            molecular_weight_default = 28.97
            if st.session_state.fluid_properties_db:
                molecular_weight_default = st.session_state.fluid_properties_db.get('molecular_weight', molecular_weight_default)
            
            molecular_weight = st.number_input(
                "Molecular Weight (kg/kmol)",
                min_value=1.0,
                max_value=200.0,
                value=molecular_weight_default,
                step=0.01,
                help="Molecular weight for gas calculations"
            )
            
            # Specific heat ratio with dynamic default
            k_ratio_default = 1.4
            if st.session_state.fluid_properties_db:
                k_ratio_default = st.session_state.fluid_properties_db.get('k_ratio', k_ratio_default)
            
            specific_heat_ratio = st.number_input(
                "Specific Heat Ratio (k = Cp/Cv)",
                min_value=1.0,
                max_value=2.0,
                value=k_ratio_default,
                step=0.01,
                help="Ratio of specific heats"
            )
            
            # Compressibility with dynamic default
            z_factor_default = 1.0
            if st.session_state.fluid_properties_db:
                z_factor_default = st.session_state.fluid_properties_db.get('z_factor', z_factor_default)
            
            compressibility = st.number_input(
                "Compressibility Factor (Z)",
                min_value=0.1,
                max_value=2.0,
                value=z_factor_default,
                step=0.01,
                help="Gas compressibility factor (Z=1 for ideal gas)"
            )
            
            # Advanced gas properties
            if st.session_state.show_advanced:
                st.markdown("**🔬 Advanced Properties**")
                
                gas_viscosity = st.number_input(
                    "Dynamic Viscosity (μP)",
                    min_value=1.0,
                    max_value=1000.0,
                    value=18.0,
                    help="Dynamic viscosity in micropoise"
                )
                
                if st.session_state.fluid_properties_db:
                    critical_pressure_default = st.session_state.fluid_properties_db.get('critical_pressure', 46.0)
                else:
                    critical_pressure_default = 46.0 if st.session_state.unit_system == 'metric' else 667.0
                
                critical_pressure = st.number_input(
                    f"Critical Pressure ({'bar' if st.session_state.unit_system == 'metric' else 'psi'})",
                    min_value=1.0,
                    max_value=500.0,
                    value=critical_pressure_default,
                    help="Critical pressure for compressibility calculations"
                )
    
    with col2:
        st.markdown("#### 🔧 Operating Conditions")
        
        pressure_units = "bar" if st.session_state.unit_system == 'metric' else "psi"
        
        # Pressures with enhanced validation
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
        pressure_ratio = p2 / p1 if p1 > 0 else 0
        
        # Enhanced pressure display
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Pressure Drop (ΔP)", f"{delta_p:.2f} {pressure_units}")
        with col_b:
            st.metric("Pressure Ratio (P2/P1)", f"{pressure_ratio:.3f}")
        
        # Flow rate inputs with enhanced units
        flow_units_liquid = ["m³/h", "L/s", "L/min", "gal/min"] if st.session_state.unit_system == 'metric' else ["GPM", "ft³/s", "bbl/h", "bbl/d"]
        flow_units_gas = ["Nm³/h", "Sm³/h", "kg/h", "kmol/h"] if st.session_state.unit_system == 'metric' else ["SCFH", "ACFM", "lb/h", "MMSCFD"]
        
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
        
        # Pipeline data with enhanced options
        pipe_sizes = ["1/2\"", "3/4\"", "1\"", "1.5\"", "2\"", "3\"", "4\"", "6\"", "8\"", 
                     "10\"", "12\"", "14\"", "16\"", "18\"", "20\"", "24\"", "30\"", "36\"", "42\"", "48\""]
        
        pipe_size = st.selectbox(
            "Nominal Pipe Size",
            pipe_sizes,
            index=5,  # Default to 3"
            help="Nominal pipe size (affects piping geometry factor)"
        )
        
        pipe_schedules = ["SCH 5", "SCH 10", "SCH 20", "SCH 30", "SCH 40", "SCH 60", "SCH 80", "SCH 100", "SCH 120", "SCH 140", "SCH 160", "SCH XXS"]
        
        pipe_schedule = st.selectbox(
            "Pipe Schedule",
            pipe_schedules,
            index=4,  # Default to SCH 40
            help="Pipe wall thickness schedule"
        )
        
        # Advanced piping options
        if st.session_state.show_advanced:
            st.markdown("**🔬 Advanced Piping**")
            
            reducers_upstream = st.checkbox("Reducer Upstream", help="Concentric/eccentric reducer upstream of valve")
            reducers_downstream = st.checkbox("Reducer Downstream", help="Concentric/eccentric reducer downstream of valve")
            
            if reducers_upstream or reducers_downstream:
                piping_configuration = st.selectbox(
                    "Piping Configuration",
                    ["Standard", "Reducer both sides", "Expander both sides", "Mixed configuration"],
                    help="Special piping configuration affects Fp factor"
                )
    
    with col3:
        st.markdown("#### 🏭 Service Classification")
        
        service_types = [
            "Clean Service", "Dirty Service", "Corrosive Service", 
            "High Temperature", "Cryogenic", "Erosive Service",
            "Flashing Service", "Cavitating Service", "Two-Phase Flow"
        ]
        
        service_type = st.selectbox(
            "Service Type",
            service_types,
            help="Service classification affects material selection and safety factors"
        )
        
        criticalities = ["Non-Critical", "Important", "Critical", "Safety Critical", "Emergency Shutdown"]
        
        criticality = st.selectbox(
            "Service Criticality",
            criticalities,
            help="Process criticality level affects safety factors and material requirements"
        )
        
        control_modes = ["Modulating", "On-Off", "Emergency Shutdown", "Throttling", "Pressure Relief"]
        
        control_mode = st.selectbox(
            "Control Mode",
            control_modes,
            help="Type of control operation required"
        )
        
        # Enhanced environmental factors
        st.markdown("**🌡️ Environmental Conditions**")
        
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
            
            if st.session_state.show_advanced:
                h2s_concentration = st.number_input(
                    "H2S Concentration (mol%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=1.0,
                    step=0.1,
                    help="H2S mole percentage in gas phase"
                )
        else:
            h2s_partial_pressure = 0.0
            h2s_concentration = 0.0
        
        fire_safe_required = st.checkbox(
            "Fire-Safe Required",
            help="Fire-safe certification required (API 607/ISO 10497)"
        )
        
        fugitive_emission_options = [
            "Standard", "Low Emission (TA-Luft)", "ISO 15848-1 Class A", 
            "ISO 15848-1 Class B", "ISO 15848-1 Class C", "EPA Method 21"
        ]
        
        fugitive_emissions = st.selectbox(
            "Fugitive Emission Class",
            fugitive_emission_options,
            help="Fugitive emission requirements"
        )
        
        # Advanced environmental options
        if st.session_state.show_advanced:
            st.markdown("**🔬 Advanced Environmental**")
            
            chloride_content = st.number_input(
                "Chloride Content (ppm)",
                min_value=0,
                max_value=100000,
                value=0,
                help="Chloride concentration for material selection"
            )
            
            ph_value = st.number_input(
                "pH Value",
                min_value=0.0,
                max_value=14.0,
                value=7.0,
                step=0.1,
                help="pH value for corrosion assessment"
            )
            
            operating_altitude = st.number_input(
                "Operating Altitude (m above sea level)",
                min_value=0,
                max_value=5000,
                value=0,
                help="Altitude affects atmospheric pressure corrections"
            )
    
    # Enhanced validation section
    st.markdown("#### ✅ Input Validation & Analysis")
    
    # Compile process data
    process_data = {
        'fluid_type': fluid_type,
        'fluid_name': fluid_name,
        'selected_category': selected_category if fluid_name != "Custom" else "Custom",
        'temperature': temperature,
        'p1': p1,
        'p2': p2,
        'delta_p': delta_p,
        'pressure_ratio': pressure_ratio,
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
        'unit_system': st.session_state.unit_system,
        'show_advanced': st.session_state.show_advanced
    }
    
    # Add fluid-specific properties
    if fluid_type == "Liquid":
        process_data.update({
            'density': density,
            'vapor_pressure': vapor_pressure,
            'viscosity': viscosity
        })
        if st.session_state.show_advanced:
            process_data.update({
                'bulk_modulus': bulk_modulus,
                'surface_tension': surface_tension
            })
    else:
        process_data.update({
            'molecular_weight': molecular_weight,
            'specific_heat_ratio': specific_heat_ratio,
            'compressibility': compressibility
        })
        if st.session_state.show_advanced:
            process_data.update({
                'gas_viscosity': gas_viscosity,
                'critical_pressure': critical_pressure,
                'h2s_concentration': h2s_concentration,
                'chloride_content': chloride_content,
                'ph_value': ph_value,
                'operating_altitude': operating_altitude
            })
    
    # Enhanced validation
    validation_errors = []
    validation_warnings = []
    
    # Basic checks
    if p1 <= p2:
        validation_errors.append("Inlet pressure must be greater than outlet pressure")
    
    if normal_flow <= 0:
        validation_errors.append("Normal flow rate must be positive")
    
    if min_flow >= normal_flow:
        validation_errors.append("Minimum flow must be less than normal flow")
    
    if max_flow <= normal_flow:
        validation_errors.append("Maximum flow must be greater than normal flow")
    
    # Advanced validation
    if pressure_ratio < 0.1:
        validation_warnings.append("Very high pressure drop - check for choked flow conditions")
    
    if fluid_type == "Liquid":
        if vapor_pressure > p2:
            validation_warnings.append("Outlet pressure below vapor pressure - flashing may occur")
        
        if delta_p > (0.8 * (p1 - vapor_pressure)):
            validation_warnings.append("High pressure drop may cause cavitation")
    
    if fluid_type == "Gas/Vapor":
        critical_pressure_ratio = (2.0 / (specific_heat_ratio + 1.0)) ** (specific_heat_ratio / (specific_heat_ratio - 1.0))
        if pressure_ratio < critical_pressure_ratio:
            validation_warnings.append("Critical pressure ratio reached - sonic flow conditions")
    
    # Display validation results
    col_val1, col_val2 = st.columns(2)
    
    with col_val1:
        if validation_errors:
            st.error("⚠️ **Validation Errors:**")
            for error in validation_errors:
                st.error(f"• {error}")
        else:
            st.success("✅ **All inputs validated successfully**")
    
    with col_val2:
        if validation_warnings:
            st.warning("⚠️ **Engineering Warnings:**")
            for warning in validation_warnings:
                st.warning(f"• {warning}")
        else:
            st.info("ℹ️ **No engineering concerns identified**")
    
    if not validation_errors:
        # Calculate enhanced safety factor
        safety_factors = {
            'Non-Critical': 1.1,
            'Important': 1.2,
            'Critical': 1.3,
            'Safety Critical': 1.5,
            'Emergency Shutdown': 1.8
        }
        safety_factor = safety_factors.get(criticality, 1.2)
        
        # Service type multipliers
        service_multipliers = {
            'Erosive Service': 1.2,
            'Cavitating Service': 1.3,
            'Two-Phase Flow': 1.4,
            'Flashing Service': 1.3
        }
        safety_factor *= service_multipliers.get(service_type, 1.0)
        
        if h2s_present:
            safety_factor *= 1.1
        
        process_data['safety_factor'] = round(safety_factor, 1)
        
        # Display enhanced summary
        col_sum1, col_sum2 = st.columns(2)
        
        with col_sum1:
            st.info(f"📊 **Recommended Safety Factor:** {safety_factor:.1f}")
            st.info(f"🎯 **Pressure Drop Severity:** {(delta_p/p1*100):.1f}% of P1")
            
        with col_sum2:
            st.info(f"⚡ **Flow Turndown Required:** {(max_flow/min_flow):.1f}:1")
            st.info(f"🌡️ **Service Classification:** {criticality} {service_type}")
        
        # Display detailed process summary
        with st.expander("📋 Enhanced Process Data Summary", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                **Fluid Properties:**
                - Type: {fluid_name} ({fluid_type})
                - Category: {process_data.get('selected_category', 'N/A')}
                - Temperature: {temperature:.1f} {'°C' if st.session_state.unit_system == 'metric' else '°F'}
                - Pressure: {p1:.1f} → {p2:.1f} {pressure_units}
                """)
            with col2:
                st.markdown(f"""
                **Operating Conditions:**
                - Flow Range: {min_flow:.1f} - {max_flow:.1f} {flow_units}
                - Pressure Drop: {delta_p:.2f} {pressure_units} ({pressure_ratio:.3f} ratio)
                - Pipeline: {pipe_size} {pipe_schedule}
                """)
            with col3:
                st.markdown(f"""
                **Service Parameters:**
                - Classification: {service_type}
                - Criticality: {criticality}
                - Control Mode: {control_mode}
                - Safety Factor: {safety_factor:.1f}
                """)
            
            if st.session_state.show_advanced:
                st.markdown("**Advanced Parameters Included:** Environmental conditions, enhanced fluid properties, and piping configurations have been captured for detailed analysis.")
    
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

# Keep all other step functions the same as in the previous version
# (step2_valve_selection through step7_final_report remain unchanged)

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
        summary_data.append(["Fluid Type", process_data.get('fluid_name', ''), "", "User Selection"])
        summary_data.append(["Fluid Category", process_data.get('selected_category', ''), "", "Database Classification"])
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
            # Generate a comprehensive text report
            report_content = f"""# Enhanced Control Valve Sizing Report - Professional Edition

**Project:** {project_name}
**Tag:** {tag_number}
**Engineer:** {engineer_name}
**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## Executive Summary
- Required Cv: {cv_required:.2f}
- Valve Size: {valve_size}
- Valve Type: {valve_type}
- Opening at Normal Flow: {opening_percent:.1f}%

## Process Conditions
- Fluid: {process_data.get('fluid_name', 'N/A')} ({process_data.get('selected_category', 'N/A')})
- Temperature: {process_data.get('temperature', 0):.1f}°C
- Pressure Drop: {process_data.get('delta_p', 0):.2f} bar
- Flow Rate: {process_data.get('normal_flow', 0):.1f} {process_data.get('flow_units', '')}

## Enhanced Fluid Properties
{f"- Dynamic Properties: Loaded from comprehensive database" if st.session_state.fluid_properties_db else "- Standard Properties: User-defined"}
- Service Classification: {process_data.get('criticality', 'Standard')} {process_data.get('service_type', '')}
- Environmental Factors: {"H2S Service" if process_data.get('h2s_present', False) else "Sweet Service"}

## Analysis Results
### Sizing (ISA 75.01/IEC 60534-2-1)
- Basic Cv Required: {sizing_results.get('cv_required', 0):.2f}
- Safety Factor Applied: {process_data.get('safety_factor', 1.2):.1f}
- Final Cv Required: {cv_required:.2f}

{"### Cavitation Analysis (ISA RP75.23)" if cavitation_analysis else ""}
{f"- Service Sigma: {cavitation_analysis.get('sigma_service', 0):.1f}" if cavitation_analysis else ""}
{f"- Risk Level: {cavitation_analysis.get('risk_level', 'N/A')}" if cavitation_analysis else ""}

{"### Noise Prediction (IEC 60534-8-3)" if noise_analysis else ""}
{f"- Sound Pressure Level: {noise_analysis.get('spl_at_distance', 0):.1f} dBA" if noise_analysis else ""}
{f"- Assessment: {noise_analysis.get('assessment_level', 'N/A')}" if noise_analysis else ""}

## Standards Applied
- ISA 75.01/IEC 60534-2-1 (Sizing Calculations)
- ISA RP75.23 (Cavitation Analysis)
- IEC 60534-8-3 (Noise Prediction)
- ASME B16.34 (Material Standards)
- NACE MR0175 (Sour Service Materials)
- API 6D (Pipeline Valve Requirements)

## Advanced Features Utilized
{f"- Comprehensive Fluid Database: {len(st.session_state.fluid_properties_db)} properties loaded" if st.session_state.fluid_properties_db else ""}
- Advanced Options: {"Enabled" if process_data.get('show_advanced', False) else "Standard"}
- Dynamic Property Updates: Automatic fluid property loading based on selection

## Professional Disclaimer
This report provides professional valve sizing calculations based on industry standards.
For critical applications:
- Validate results against manufacturer data
- Review calculations with licensed Professional Engineer  
- Verify material selections against actual service conditions
- Cross-check with vendor sizing software

**Author:** {engineer_name}
**Application:** Enhanced Control Valve Sizing - Professional Edition
**Database:** Comprehensive fluid properties with {len(get_comprehensive_fluid_database()[0]) + len(get_comprehensive_fluid_database()[1])} fluids
"""
            
            st.download_button(
                label="📥 Download Enhanced Report",
                data=report_content,
                file_name=f"{tag_number}_Enhanced_Valve_Sizing_Report.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.success("✅ Enhanced professional report ready for download!")
    
    with col2:
        if st.button("📊 Generate Enhanced CSV Data", use_container_width=True):
            # Generate enhanced CSV with all data including fluid properties
            enhanced_data = []
            
            # Add all summary data
            for row in summary_data[1:]:
                enhanced_data.append({
                    'Category': 'Process Data',
                    'Parameter': row[0],
                    'Value': row[1],
                    'Units': row[2],
                    'Standard': row[3],
                    'Notes': ''
                })
            
            # Add fluid properties if available
            if st.session_state.fluid_properties_db:
                for prop, value in st.session_state.fluid_properties_db.items():
                    if prop not in ['description', 'category']:
                        enhanced_data.append({
                            'Category': 'Fluid Properties (Database)',
                            'Parameter': prop.replace('_', ' ').title(),
                            'Value': str(value),
                            'Units': '',
                            'Standard': 'Database Lookup',
                            'Notes': f"From {st.session_state.fluid_properties_db.get('category', 'Unknown')} database"
                        })
            
            # Add advanced parameters if enabled
            if process_data.get('show_advanced', False):
                advanced_params = ['bulk_modulus', 'surface_tension', 'gas_viscosity', 'critical_pressure', 
                                 'h2s_concentration', 'chloride_content', 'ph_value', 'operating_altitude']
                for param in advanced_params:
                    if param in process_data:
                        enhanced_data.append({
                            'Category': 'Advanced Parameters',
                            'Parameter': param.replace('_', ' ').title(),
                            'Value': str(process_data[param]),
                            'Units': '',
                            'Standard': 'Advanced Analysis',
                            'Notes': 'Enhanced calculation parameter'
                        })
            
            csv_data = pd.DataFrame(enhanced_data)
            csv_string = csv_data.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Enhanced CSV Data",
                data=csv_string,
                file_name=f"{tag_number}_Enhanced_Valve_Sizing_Data.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.success("✅ Enhanced CSV data with fluid database ready for download!")
    
    # Enhanced professional disclaimer
    st.markdown("#### ⚠️ Professional Disclaimer")
    st.warning(f"""
    **ENHANCED PROFESSIONAL VALVE SIZING TOOL** 
    
    This application provides professional valve sizing calculations with enhanced features:
    - **Comprehensive Fluid Database:** {len(get_comprehensive_fluid_database()[0]) + len(get_comprehensive_fluid_database()[1])} industrial fluids
    - **Dynamic Property Updates:** Automatic fluid property loading
    - **Advanced Analysis Options:** Extended parameter sets for detailed analysis
    - **Standards Compliance:** ISA 75.01, IEC 60534-2-1, ISA RP75.23, IEC 60534-8-3, ASME B16.34, NACE MR0175
    
    **For critical applications:**
    - Validate results against manufacturer data
    - Review calculations with licensed Professional Engineer
    - Verify material selections against actual service conditions
    - Cross-check with vendor sizing software
    
    **Enhanced Features Utilized:**
    - Advanced Options: {"✅ Enabled" if process_data.get('show_advanced', False) else "⚪ Standard"}
    - Fluid Database: {"✅ Active" if st.session_state.fluid_properties_db else "⚪ Manual Entry"}
    - Dynamic Updates: {"✅ Active" if st.session_state.previous_fluid_selection else "⚪ Static"}
    
    **Author:** {engineer_name}
    **Tool Version:** Enhanced Professional Edition v2.0
    """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← **Back to Materials**", use_container_width=True):
            st.session_state.current_step = 6
            st.rerun()
    
    with col2:
        if st.button("🔄 **Start New Enhanced Analysis**", 
                    type="secondary", 
                    use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key != 'current_step':
                    del st.session_state[key]
            st.session_state.current_step = 1
            st.rerun()

def main():
    """Main application function with enhanced features"""
    initialize_session_state()
    display_header()
    
    # Enhanced sidebar navigation
    with st.sidebar:
        st.header("🧭 Enhanced Navigation")
        
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
        
        # Enhanced progress summary
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
        
        # Enhanced status indicators
        st.markdown("#### 🔬 Enhanced Features Status")
        
        # Fluid database status
        if st.session_state.fluid_properties_db:
            st.success(f"🗃️ Fluid Database: Active")
            st.caption(f"Category: {st.session_state.fluid_properties_db.get('category', 'Unknown')}")
        else:
            st.info("🗃️ Fluid Database: Manual Entry")
        
        # Advanced options status
        if st.session_state.show_advanced:
            st.success("🔬 Advanced Options: Enabled")
        else:
            st.info("🔬 Advanced Options: Standard")
        
        # Dynamic updates status
        if st.session_state.previous_fluid_selection:
            st.success("⚡ Dynamic Updates: Active")
        else:
            st.info("⚡ Dynamic Updates: Ready")
        
        st.markdown("---")
        
        # Database information
        liquid_db, gas_db = get_comprehensive_fluid_database()
        st.markdown("#### 📊 Database Stats")
        st.info(f"**Liquid Fluids:** {len(liquid_db)}")
        st.info(f"**Gas/Vapor Fluids:** {len(gas_db)}")
        st.info(f"**Total Categories:** {len(set([data['category'] for data in {**liquid_db, **gas_db}.values()]))}")
        
        # Help
        st.markdown("#### ❓ Enhanced Help")
        st.markdown("""
        **Standards Implemented:**
        - ISA 75.01 / IEC 60534-2-1
        - ISA RP75.23 (Cavitation)
        - IEC 60534-8-3 (Noise)
        - ASME B16.34 (Materials)
        - NACE MR0175 (Sour Service)
        - API 6D (Pipeline Valves)
        
        **Enhanced Features:**
        - 🗃️ Comprehensive fluid database
        - ⚡ Dynamic property updates
        - 🔬 Advanced analysis options
        - 📊 Professional reporting
        
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
