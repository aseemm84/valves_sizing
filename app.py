# Enhanced Control Valve Sizing Application - Professional Edition with Full Integration
# Author: Aseem Mehrotra, Senior Instrumentation Construction Engineer, KBR Inc
# Updated with complete datasheet generation and enhanced charts integration

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import warnings
import io
import base64
from datetime import datetime

# Import the complete step functions and supporting modules
from complete_step_functions import *
from datasheet_generator import ProfessionalDatasheetGenerator
from enhanced_charts import EnhancedChartsGenerator

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
        'current_tab': 'main',  # Added for tab navigation
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
        'previous_fluid_selection': None,
        'charts_generated': False,  # Added for charts tracking
        'datasheet_ready': False,  # Added for datasheet tracking
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_header():
    """Display professional application header with tab navigation"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e5d85 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .tab-container {
        margin: 1rem 0;
    }
    </style>
    
    <div class="main-header">
        <h1>⚙️ Enhanced Control Valve Sizing</h1>
        <h3>Professional Edition - Standards Compliant with Full Documentation</h3>
        <p>🏆 ISA 75.01 | IEC 60534-2-1 | ISA RP75.23 | IEC 60534-8-3 | ASME B16.34 | NACE MR0175</p>
    </div>
    """, unsafe_allow_html=True)

def create_main_tabs():
    """Create main application tabs"""
    tab1, tab2, tab3 = st.tabs(["🔧 Main Application", "📊 Engineering Charts & Analysis", "📋 Professional Datasheet"])
    
    with tab1:
        st.session_state.current_tab = 'main'
        display_main_application()
    
    with tab2:
        st.session_state.current_tab = 'charts'
        display_charts_and_analysis()
    
    with tab3:
        st.session_state.current_tab = 'datasheet'
        display_datasheet_generation()

def display_main_application():
    """Display the main valve sizing application"""
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

def display_charts_and_analysis():
    """Display comprehensive engineering charts and analysis"""
    st.header("📊 Engineering Charts & Analysis")
    st.markdown("**Complete technical analysis with professional engineering charts based on your valve sizing calculations.**")
    
    # Check if we have sufficient data for charts
    if not st.session_state.get('sizing_results') or not st.session_state.get('process_data'):
        st.warning("⚠️ **Please complete at least Steps 1-3 in the Main Application to generate charts.**")
        st.info("👆 Navigate to the **Main Application** tab to perform valve sizing calculations first.")
        return
    
    # Initialize charts generator
    charts_generator = EnhancedChartsGenerator()
    
    # Get data
    process_data = st.session_state.get('process_data', {})
    valve_selection = st.session_state.get('valve_selection', {})
    sizing_results = st.session_state.get('sizing_results', {})
    cavitation_analysis = st.session_state.get('cavitation_analysis', {})
    noise_analysis = st.session_state.get('noise_analysis', {})
    
    st.markdown("---")
    
    # Chart selection
    st.subheader("🎯 Select Charts to Display")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_characteristic = st.checkbox("✅ Valve Characteristic Curve", value=True, 
                                        help="Flow characteristic curve with operating point analysis")
        show_opening_analysis = st.checkbox("✅ Valve Opening vs Flow Analysis", value=True,
                                          help="Operating range analysis across all flow conditions")
        show_pressure_analysis = st.checkbox("🔧 Pressure Drop Analysis", value=True,
                                           help="System pressure profile and valve authority")
    
    with col2:
        show_cavitation = st.checkbox("🌊 Cavitation Analysis", value=bool(cavitation_analysis),
                                    help="ISA RP75.23 cavitation analysis with risk assessment")
        show_noise = st.checkbox("🔊 Noise Analysis", value=bool(noise_analysis),
                                help="IEC 60534-8-3 noise prediction and compliance")
        show_reynolds = st.checkbox("🔬 Reynolds Analysis", value=True,
                                  help="Reynolds number analysis and correction factors")
    
    with col3:
        show_safety_factor = st.checkbox("🛡️ Safety Factor Analysis", value=True,
                                       help="Safety factor breakdown and standards comparison")
        show_service_overview = st.checkbox("📋 Service Conditions Overview", value=True,
                                          help="Normalized radar chart of all service parameters")
        show_all = st.checkbox("🔄 **Generate All Available Charts**", value=False,
                              help="Generate all applicable charts at once")
    
    if show_all:
        show_characteristic = show_opening_analysis = show_pressure_analysis = True
        show_cavitation = bool(cavitation_analysis)
        show_noise = bool(noise_analysis) 
        show_reynolds = show_safety_factor = show_service_overview = True
    
    st.markdown("---")
    
    # Generate and display selected charts
    if st.button("🚀 **Generate Selected Charts**", type="primary", use_container_width=True):
        with st.spinner("🔄 Generating professional engineering charts..."):
            
            # 1. Valve Characteristic Curve
            if show_characteristic:
                st.subheader("🎯 Valve Flow Characteristic Curve")
                st.markdown("**Professional analysis of valve flow characteristic with operating point assessment**")
                try:
                    fig_char = charts_generator.create_valve_characteristic_curve(valve_selection, sizing_results)
                    st.plotly_chart(fig_char, use_container_width=True)
                    st.markdown("**Analysis:** This chart shows the valve's inherent flow characteristic and identifies the operating point at normal flow conditions.")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Error generating characteristic curve: {str(e)}")
            
            # 2. Valve Opening Analysis
            if show_opening_analysis:
                st.subheader("⚙️ Valve Opening vs Flow Rate Analysis") 
                st.markdown("**Complete operating range analysis across minimum, normal, and maximum flow conditions**")
                try:
                    fig_opening = charts_generator.create_valve_opening_vs_flow_chart(
                        process_data, valve_selection, sizing_results
                    )
                    st.plotly_chart(fig_opening, use_container_width=True)
                    st.markdown("**Analysis:** This chart validates that the valve operates within the recommended 20-80% opening range across all flow conditions.")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Error generating opening analysis: {str(e)}")
            
            # 3. Pressure Drop Analysis
            if show_pressure_analysis:
                st.subheader("🔧 Comprehensive Pressure Drop Analysis")
                st.markdown("**System pressure profile with valve authority and pressure distribution analysis**")
                try:
                    fig_pressure = charts_generator.create_pressure_drop_analysis_chart(process_data)
                    st.plotly_chart(fig_pressure, use_container_width=True)
                    st.markdown("**Analysis:** This chart shows the complete system pressure profile and evaluates valve authority for optimal control performance.")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Error generating pressure analysis: {str(e)}")
            
            # 4. Cavitation Analysis
            if show_cavitation and cavitation_analysis:
                st.subheader("🌊 ISA RP75.23 Cavitation Analysis")
                st.markdown("**Professional cavitation risk assessment with five-level sigma methodology**")
                try:
                    fig_cavitation = charts_generator.create_cavitation_analysis_chart(cavitation_analysis)
                    st.plotly_chart(fig_cavitation, use_container_width=True)
                    risk_level = cavitation_analysis.get('risk_level', 'Unknown')
                    if risk_level in ['High', 'Critical']:
                        st.error(f"⚠️ **Cavitation Risk: {risk_level}** - Review design and consider mitigation measures")
                    else:
                        st.success(f"✅ **Cavitation Risk: {risk_level}** - Acceptable for standard operation")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Error generating cavitation analysis: {str(e)}")
            
            # 5. Noise Analysis
            if show_noise and noise_analysis:
                st.subheader("🔊 IEC 60534-8-3 Noise Analysis")
                st.markdown("**Complete aerodynamic noise prediction with regulatory compliance assessment**")
                try:
                    fig_noise = charts_generator.create_noise_analysis_chart(noise_analysis)
                    st.plotly_chart(fig_noise, use_container_width=True)
                    spl_level = noise_analysis.get('spl_at_distance', 0)
                    if spl_level > 85:
                        st.warning(f"⚠️ **Noise Level: {spl_level:.1f} dBA** - Consider noise mitigation measures")
                    else:
                        st.success(f"✅ **Noise Level: {spl_level:.1f} dBA** - Compliant with industrial standards")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Error generating noise analysis: {str(e)}")
            
            # 6. Reynolds Analysis
            if show_reynolds:
                st.subheader("🔬 Reynolds Number Analysis & Correction Factors")
                st.markdown("**Flow regime classification and viscous correction factor analysis**")
                try:
                    fig_reynolds = charts_generator.create_reynolds_analysis_chart(sizing_results)
                    st.plotly_chart(fig_reynolds, use_container_width=True)
                    reynolds_data = sizing_results.get('reynolds_analysis', {})
                    flow_regime = reynolds_data.get('flow_regime', 'Unknown')
                    fr_factor = reynolds_data.get('fr_factor', 1.0)
                    st.info(f"🔬 **Flow Regime:** {flow_regime} | **Fr Factor:** {fr_factor:.3f}")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Error generating Reynolds analysis: {str(e)}")
            
            # 7. Safety Factor Analysis
            if show_safety_factor:
                st.subheader("🛡️ Safety Factor Analysis & Standards Comparison")
                st.markdown("**Comprehensive safety factor breakdown with industry standards comparison**")
                try:  
                    fig_safety = charts_generator.create_safety_factor_analysis_chart(process_data)
                    st.plotly_chart(fig_safety, use_container_width=True)
                    safety_factor = process_data.get('safety_factor', 1.2)
                    criticality = process_data.get('criticality', 'Important')
                    st.info(f"🛡️ **Applied Safety Factor:** {safety_factor:.1f} for **{criticality}** service")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Error generating safety factor analysis: {str(e)}")
            
            # 8. Service Conditions Overview
            if show_service_overview:
                st.subheader("📋 Service Conditions Overview")
                st.markdown("**Normalized radar chart assessment of all service parameters**")
                try:
                    fig_service = charts_generator.create_service_conditions_overview_chart(
                        process_data, sizing_results
                    )
                    st.plotly_chart(fig_service, use_container_width=True)
                    st.markdown("**Analysis:** This radar chart provides a normalized view of all service parameters, helping identify potential areas of concern.")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Error generating service overview: {str(e)}")
        
        st.session_state.charts_generated = True
        st.success("✅ **Charts generated successfully!** All selected engineering analyses are now complete.")
        
        # Chart summary
        st.markdown("### 📊 Chart Generation Summary")
        charts_created = []
        if show_characteristic: charts_created.append("✅ Valve Characteristic Curve")
        if show_opening_analysis: charts_created.append("✅ Opening vs Flow Analysis") 
        if show_pressure_analysis: charts_created.append("✅ Pressure Drop Analysis")
        if show_cavitation and cavitation_analysis: charts_created.append("✅ Cavitation Analysis")
        if show_noise and noise_analysis: charts_created.append("✅ Noise Analysis")
        if show_reynolds: charts_created.append("✅ Reynolds Analysis")
        if show_safety_factor: charts_created.append("✅ Safety Factor Analysis")
        if show_service_overview: charts_created.append("✅ Service Conditions Overview")
        
        for chart in charts_created:
            st.markdown(f"• {chart}")
    
    # Additional information
    st.markdown("---")
    st.markdown("### 🎯 Chart Interpretation Guide")
    
    with st.expander("📖 **How to Interpret the Engineering Charts**", expanded=False):
        st.markdown("""
        **🎯 Valve Characteristic Curve:**
        - Shows relationship between valve opening and flow coefficient (Cv)
        - Operating point should be in the 20-80% range for good control
        - Equal percentage curves provide better control at low flows
        
        **⚙️ Opening vs Flow Analysis:**
        - Validates valve performance across full operating range
        - Green zones indicate good control regions
        - Red zones indicate poor control (avoid operation here)
        
        **🔧 Pressure Drop Analysis:**
        - System pressure profile shows where pressure losses occur
        - Valve authority >0.5 is excellent, >0.25 is acceptable
        - Higher valve authority provides better control response
        
        **🌊 Cavitation Analysis:**
        - Service sigma compared to ISA RP75.23 limits
        - Risk levels: None/Low (good), Moderate (monitor), High/Critical (mitigate)
        - FL factor from valve manufacturer is critical for accuracy
        
        **🔊 Noise Analysis:**
        - Sound pressure levels at various distances
        - OSHA limit: 85 dBA for 8-hour exposure
        - Frequency analysis helps select appropriate mitigation
        
        **🔬 Reynolds Analysis:**
        - Flow regime affects sizing accuracy
        - Fr factor <1.0 indicates viscous effects
        - Turbulent flow (Re >40,000) is ideal for standard equations
        
        **🛡️ Safety Factor Analysis:**
        - Shows breakdown of safety factor components
        - Compares with industry standards (ISA, API, IEC)
        - Higher factors for critical services
        
        **📋 Service Overview:**
        - Radar chart normalizes all parameters (0-10 scale)
        - Shows relative severity of each service aspect
        - Helps identify dominant design factors
        """)

def display_datasheet_generation():
    """Display professional datasheet generation interface"""
    st.header("📋 Professional Control Valve Datasheet")
    st.markdown("**Generate complete, standards-compliant valve datasheets with all calculations, charts, and specifications.**")
    
    # Check if we have sufficient data
    if not st.session_state.get('sizing_results') or not st.session_state.get('process_data'):
        st.warning("⚠️ **Please complete at least Steps 1-3 in the Main Application to generate datasheets.**")
        st.info("👆 Navigate to the **Main Application** tab to perform valve sizing calculations first.")
        return
    
    st.markdown("---")
    
    # Initialize datasheet generator
    datasheet_generator = ProfessionalDatasheetGenerator()
    
    # Project information section
    st.subheader("📝 Project Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input(
            "Project Name",
            value="Control Valve Sizing Project",
            help="Enter the project name for the datasheet header"
        )
        
        tag_number = st.text_input(
            "Valve Tag Number",
            value="CV-001",
            help="Unique valve identifier (e.g., CV-001, PCV-123)"
        )
        
        datasheet_number = st.text_input(
            "Datasheet Number", 
            value="DS-CV-001",
            help="Document control number for the datasheet"
        )
        
        revision = st.text_input(
            "Revision",
            value="A",
            help="Document revision (A, B, C, etc.)"
        )
    
    with col2:
        engineer_name = st.text_input(
            "Engineer Name",
            value="Aseem Mehrotra, KBR Inc",
            help="Responsible engineer for the design"
        )
        
        client_name = st.text_input(
            "Client Name",
            value="TBD",
            help="Client or end user name"
        )
        
        service_description = st.text_area(
            "Service Description",
            value=f"{st.session_state.process_data.get('fluid_name', 'Process fluid')} control service",
            height=100,
            help="Brief description of the valve service application"
        )
    
    # Datasheet options
    st.subheader("⚙️ Datasheet Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        include_calculations = st.checkbox("📊 Include Detailed Calculations", value=True,
                                         help="Include step-by-step sizing calculations")
        include_process_data = st.checkbox("🔧 Include Process Conditions", value=True,
                                         help="Include complete process data table")
        include_valve_specs = st.checkbox("⚙️ Include Valve Specifications", value=True,
                                        help="Include valve technical specifications")
    
    with col2:
        include_charts = st.checkbox("📈 Include Engineering Charts", value=True,
                                   help="Embed charts and graphs in datasheet")
        include_analysis = st.checkbox("🔬 Include Technical Analysis", value=True,
                                     help="Include cavitation and noise analysis")
        include_materials = st.checkbox("🏗️ Include Material Specifications", value=True,
                                      help="Include material selection and standards")
    
    with col3:
        include_standards = st.checkbox("📋 Include Standards Compliance", value=True,
                                      help="Include standards and code compliance")
        include_recommendations = st.checkbox("💡 Include Recommendations", value=True,
                                            help="Include engineering recommendations")
        professional_format = st.checkbox("🏆 Professional Format", value=True,
                                         help="Use professional formatting and layout")
    
    # Generate datasheet
    st.markdown("---")
    st.subheader("🚀 Generate Professional Datasheet")
    
    col1, col2 = st.columns(2)
    
    project_data = {
        'project_name': project_name,
        'tag_number': tag_number,
        'datasheet_number': datasheet_number,
        'revision': revision,
        'engineer_name': engineer_name,
        'client_name': client_name,
        'service_description': service_description
    }
    
    # Compile all analysis results
    analysis_results = {
        'cavitation_analysis': st.session_state.get('cavitation_analysis', {}),
        'noise_analysis': st.session_state.get('noise_analysis', {}),
        'material_selection': st.session_state.get('material_selection', {})
    }
    
    with col1:
        if st.button("📄 **Generate PDF Datasheet**", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating professional PDF datasheet..."):
                try:
                    # Generate PDF datasheet
                    pdf_data = datasheet_generator.generate_complete_pdf_datasheet(
                        project_data=project_data,
                        process_data=st.session_state.process_data,
                        valve_selection=st.session_state.valve_selection,
                        sizing_results=st.session_state.sizing_results,
                        analysis_results=analysis_results,
                        include_charts=include_charts
                    )
                    
                    if isinstance(pdf_data, bytes) and len(pdf_data) > 100:  # Valid PDF
                        # Provide download button
                        st.download_button(
                            label="📥 **Download Professional PDF Datasheet**",
                            data=pdf_data,
                            file_name=f"{tag_number}_Professional_Datasheet.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("✅ **PDF datasheet generated successfully!**")
                        st.session_state.datasheet_ready = True
                    else:
                        # Fallback to text report
                        text_report = generate_comprehensive_text_datasheet(
                            project_data, st.session_state.process_data,
                            st.session_state.valve_selection, st.session_state.sizing_results,
                            analysis_results
                        )
                        
                        st.download_button(
                            label="📥 **Download Text Datasheet**",
                            data=text_report,
                            file_name=f"{tag_number}_Technical_Datasheet.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                        st.info("📄 **Text datasheet generated** (PDF generation requires additional packages)")
                
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
                    # Generate fallback text datasheet
                    text_report = generate_comprehensive_text_datasheet(
                        project_data, st.session_state.process_data,
                        st.session_state.valve_selection, st.session_state.sizing_results,
                        analysis_results
                    )
                    
                    st.download_button(
                        label="📥 **Download Technical Datasheet (Text)**",
                        data=text_report,
                        file_name=f"{tag_number}_Technical_Datasheet.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    st.warning("⚠️ **PDF generation failed** - Text datasheet provided as backup")
    
    with col2:
        if st.button("📊 **Generate Excel Datasheet**", use_container_width=True):
            with st.spinner("🔄 Generating Excel datasheet with embedded charts..."):
                try:
                    # Generate Excel datasheet
                    excel_data = datasheet_generator.generate_excel_datasheet(
                        project_data=project_data,
                        process_data=st.session_state.process_data,
                        valve_selection=st.session_state.valve_selection,
                        sizing_results=st.session_state.sizing_results,
                        analysis_results=analysis_results,
                        include_charts=include_charts
                    )
                    
                    if isinstance(excel_data, bytes) and len(excel_data) > 100:  # Valid Excel
                        st.download_button(
                            label="📥 **Download Excel Datasheet**",
                            data=excel_data,
                            file_name=f"{tag_number}_Professional_Datasheet.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.success("✅ **Excel datasheet generated successfully!**")
                    else:
                        # Fallback to CSV
                        csv_data = generate_csv_summary(
                            st.session_state.process_data, st.session_state.valve_selection,
                            st.session_state.sizing_results, analysis_results
                        )
                        
                        st.download_button(
                            label="📥 **Download CSV Summary**",
                            data=csv_data,
                            file_name=f"{tag_number}_Summary.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        st.info("📊 **CSV summary generated** (Excel generation requires additional packages)")
                
                except Exception as e:
                    st.error(f"❌ Error generating Excel: {str(e)}")
                    # Generate fallback CSV
                    csv_data = generate_csv_summary(
                        st.session_state.process_data, st.session_state.valve_selection,
                        st.session_state.sizing_results, analysis_results
                    )
                    
                    st.download_button(
                        label="📥 **Download CSV Summary**",
                        data=csv_data,
                        file_name=f"{tag_number}_Summary.csv", 
                        mime="text/csv",
                        use_container_width=True
                    )
                    st.warning("⚠️ **Excel generation failed** - CSV summary provided as backup")
    
    # Datasheet preview section
    if st.session_state.get('datasheet_ready', False) or st.button("👁️ **Preview Datasheet Content**"):
        st.markdown("---")
        st.subheader("👁️ Datasheet Preview")
        
        with st.expander("📋 **Complete Datasheet Content Preview**", expanded=True):
            preview_content = generate_datasheet_preview(
                project_data, st.session_state.process_data,
                st.session_state.valve_selection, st.session_state.sizing_results,
                analysis_results
            )
            st.markdown(preview_content)
    
    # Additional information
    st.markdown("---")
    st.markdown("### 📚 Datasheet Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📄 PDF Datasheet Includes:**
        - Professional header with project information
        - Complete process conditions table
        - Valve specifications and performance data
        - Detailed sizing calculations with methods
        - Technical analysis (cavitation, noise, materials)
        - Engineering charts and graphs
        - Standards compliance documentation
        - Professional recommendations and notes
        """)
    
    with col2:
        st.markdown("""
        **📊 Excel Datasheet Features:**
        - Multiple worksheets for different sections
        - Embedded charts and analysis graphs
        - Data tables with professional formatting
        - Summary dashboard with key metrics
        - Export capability for further analysis
        - Template for future similar applications
        """)
    
    # Professional disclaimer
    st.markdown("---")
    st.markdown("### ⚠️ Professional Engineering Disclaimer")
    st.warning(f"""
    **PROFESSIONAL ENGINEERING DATASHEET**
    
    ✅ **Standards Applied:** ISA 75.01, IEC 60534-2-1, ISA RP75.23, IEC 60534-8-3, ASME B16.34, NACE MR0175
    
    ✅ **Generated By:** {engineer_name}
    
    ✅ **Quality Level:** Professional engineering analysis with comprehensive documentation
    
    ⚠️ **Important:** This datasheet provides professional valve sizing calculations based on industry standards. 
    For critical applications, results must be validated against manufacturer data and reviewed by a licensed 
    Professional Engineer. Final material selections must be verified against actual service conditions.
    
    📋 **Usage:** Suitable for engineering documentation, tender specifications, and detailed design.
    """)

def generate_comprehensive_text_datasheet(project_data, process_data, valve_selection, sizing_results, analysis_results):
    """Generate comprehensive text datasheet"""
    
    content = f"""
PROFESSIONAL CONTROL VALVE DATASHEET
=====================================

PROJECT INFORMATION
-------------------
Project Name: {project_data.get('project_name', 'TBD')}
Valve Tag: {project_data.get('tag_number', 'TBD')}  
Datasheet No.: {project_data.get('datasheet_number', 'TBD')}
Revision: {project_data.get('revision', 'A')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Engineer: {project_data.get('engineer_name', 'TBD')}
Client: {project_data.get('client_name', 'TBD')}
Service: {project_data.get('service_description', 'TBD')}

PROCESS CONDITIONS
-----------------
Fluid: {process_data.get('fluid_name', 'TBD')}
Temperature: {process_data.get('temperature', 0):.1f}°C
Inlet Pressure: {process_data.get('p1', 0):.1f} bar abs
Outlet Pressure: {process_data.get('p2', 0):.1f} bar abs
Pressure Drop: {process_data.get('p1', 0) - process_data.get('p2', 0):.1f} bar
Normal Flow: {process_data.get('normal_flow', 0):.1f} {process_data.get('flow_units', 'm³/h')}
Min Flow: {process_data.get('min_flow', 0):.1f} {process_data.get('flow_units', 'm³/h')}
Max Flow: {process_data.get('max_flow', 0):.1f} {process_data.get('flow_units', 'm³/h')}
Service Type: {process_data.get('service_type', 'Standard')}
Criticality: {process_data.get('criticality', 'Important')}

VALVE SPECIFICATIONS
-------------------
Type: {valve_selection.get('valve_type', 'TBD')}
Style: {valve_selection.get('valve_style', 'TBD')}
Size: {valve_selection.get('valve_size', 'TBD')}
Flow Characteristic: {valve_selection.get('flow_characteristic', 'TBD')}
Body Material: To be determined per material analysis
Trim Material: To be determined per service requirements
Max Cv: {valve_selection.get('max_cv', 0):.1f}
FL Factor: {valve_selection.get('fl_factor', 0):.3f}
xT Factor: {valve_selection.get('xt_factor', 0):.3f}

SIZING RESULTS
--------------
Sizing Method: {sizing_results.get('sizing_method', 'ISA 75.01')}
Required Cv: {sizing_results.get('cv_required', 0):.3f}
Safety Factor: {process_data.get('safety_factor', 1.2):.1f}
Opening at Normal Flow: {(sizing_results.get('cv_required', 0)/valve_selection.get('max_cv', 100)*100):.1f}%

TECHNICAL ANALYSIS
-----------------
"""
    
    # Add cavitation analysis if available
    if analysis_results.get('cavitation_analysis'):
        cav = analysis_results['cavitation_analysis']
        content += f"""
Cavitation Analysis (ISA RP75.23):
- Service Sigma: {cav.get('sigma_service', 0):.1f}
- Risk Level: {cav.get('risk_level', 'Unknown')}
- Status: {'Cavitating' if cav.get('is_cavitating', False) else 'No Cavitation'}
"""
    
    # Add noise analysis if available
    if analysis_results.get('noise_analysis'):
        noise = analysis_results['noise_analysis']
        content += f"""
Noise Analysis (IEC 60534-8-3):
- Sound Power Level: {noise.get('lw_total', 0):.1f} dB
- Sound Pressure Level (1m): {noise.get('spl_1m', 0):.1f} dBA
- Assessment: {noise.get('assessment_level', 'Unknown')}
"""
    
    content += f"""

STANDARDS COMPLIANCE
-------------------
• ISA 75.01-2012: Flow equations for sizing control valves
• IEC 60534-2-1:2011: Industrial-process control valves  
• ISA RP75.23-1995: Considerations for evaluating control valve cavitation
• IEC 60534-8-3:2010: Control valve aerodynamic noise prediction
• ASME B16.34-2017: Valves - Flanged, threaded, and welding end
• NACE MR0175/ISO 15156: Materials for use in H2S-containing environments

PROFESSIONAL NOTES
-----------------
• This datasheet provides professional valve sizing calculations based on industry standards
• For critical applications, validate results against manufacturer data
• Final material selections must be verified against actual service conditions  
• Installation must follow manufacturer recommendations
• Regular maintenance schedule should be established

Generated by: Enhanced Control Valve Sizing Application - Professional Edition
Author: {project_data.get('engineer_name', 'Aseem Mehrotra, KBR Inc')}
Standards: Complete ISA/IEC/ASME/NACE compliance
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return content

def generate_csv_summary(process_data, valve_selection, sizing_results, analysis_results):
    """Generate CSV summary of key results"""
    
    data = []
    
    # Project data
    data.append(['Category', 'Parameter', 'Value', 'Units', 'Notes'])
    data.append(['Process', 'Fluid', process_data.get('fluid_name', 'TBD'), '-', ''])
    data.append(['Process', 'Temperature', f"{process_data.get('temperature', 0):.1f}", '°C', ''])
    data.append(['Process', 'Inlet Pressure', f"{process_data.get('p1', 0):.1f}", 'bar', ''])
    data.append(['Process', 'Outlet Pressure', f"{process_data.get('p2', 0):.1f}", 'bar', ''])
    data.append(['Process', 'Normal Flow', f"{process_data.get('normal_flow', 0):.1f}", process_data.get('flow_units', 'm³/h'), ''])
    
    # Valve data
    data.append(['Valve', 'Type', valve_selection.get('valve_type', 'TBD'), '-', ''])
    data.append(['Valve', 'Size', valve_selection.get('valve_size', 'TBD'), 'NPS', ''])
    data.append(['Valve', 'Max Cv', f"{valve_selection.get('max_cv', 0):.1f}", '-', ''])
    
    # Results
    data.append(['Results', 'Required Cv', f"{sizing_results.get('cv_required', 0):.3f}", '-', 'ISA 75.01'])
    data.append(['Results', 'Safety Factor', f"{process_data.get('safety_factor', 1.2):.1f}", '-', ''])
    data.append(['Results', 'Opening %', f"{(sizing_results.get('cv_required', 0)/valve_selection.get('max_cv', 100)*100):.1f}%", '%', 'At normal flow'])
    
    # Analysis results
    if analysis_results.get('cavitation_analysis'):
        cav = analysis_results['cavitation_analysis']
        data.append(['Analysis', 'Cavitation Risk', cav.get('risk_level', 'Unknown'), '-', 'ISA RP75.23'])
    
    if analysis_results.get('noise_analysis'):
        noise = analysis_results['noise_analysis']
        data.append(['Analysis', 'Noise Level', f"{noise.get('spl_1m', 0):.1f}", 'dBA', 'IEC 60534-8-3'])
    
    # Convert to CSV string
    csv_content = ""
    for row in data:
        csv_content += ','.join([f'"{item}"' for item in row]) + '\n'
    
    return csv_content

def generate_datasheet_preview(project_data, process_data, valve_selection, sizing_results, analysis_results):
    """Generate markdown preview of datasheet content"""
    
    cv_required = sizing_results.get('cv_required', 0)
    max_cv = valve_selection.get('max_cv', 100)
    opening_percent = (cv_required / max_cv * 100) if max_cv > 0 else 0
    
    preview = f"""
## 📋 Professional Control Valve Datasheet Preview

### Project Information
| Parameter | Value |
|-----------|-------|
| **Project** | {project_data.get('project_name', 'TBD')} |
| **Tag Number** | {project_data.get('tag_number', 'TBD')} |
| **Engineer** | {project_data.get('engineer_name', 'Aseem Mehrotra, KBR Inc')} |
| **Date** | {datetime.now().strftime('%Y-%m-%d')} |

### Process Conditions Summary
| Parameter | Value | Units |
|-----------|-------|-------|
| **Fluid** | {process_data.get('fluid_name', 'TBD')} | - |
| **Temperature** | {process_data.get('temperature', 0):.1f} | °C |
| **Pressure Drop** | {process_data.get('p1', 0) - process_data.get('p2', 0):.1f} | bar |
| **Normal Flow** | {process_data.get('normal_flow', 0):.1f} | {process_data.get('flow_units', 'm³/h')} |
| **Service Type** | {process_data.get('service_type', 'Standard')} | - |

### Valve Specifications
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Type & Style** | {valve_selection.get('valve_type', 'TBD')} - {valve_selection.get('valve_style', 'TBD')} | - |
| **Size** | {valve_selection.get('valve_size', 'TBD')} | NPS |
| **Flow Characteristic** | {valve_selection.get('flow_characteristic', 'TBD')} | - |
| **Maximum Cv** | {max_cv:.1f} | At 100% opening |

### Sizing Results
| Parameter | Value | Method |
|-----------|-------|--------|
| **Required Cv** | {cv_required:.3f} | {sizing_results.get('sizing_method', 'ISA 75.01')} |
| **Safety Factor** | {process_data.get('safety_factor', 1.2):.1f} | Based on criticality |
| **Normal Opening** | {opening_percent:.1f}% | Design point |

### Key Findings
"""
    
    # Add analysis results
    if analysis_results.get('cavitation_analysis'):
        cav = analysis_results['cavitation_analysis']
        risk_emoji = "🔴" if cav.get('risk_level') in ['High', 'Critical'] else "🟢"
        preview += f"- **Cavitation Risk:** {risk_emoji} {cav.get('risk_level', 'Unknown')}\n"
    
    if analysis_results.get('noise_analysis'):
        noise = analysis_results['noise_analysis']
        noise_level = noise.get('spl_1m', 0)
        noise_emoji = "🔴" if noise_level > 85 else "🟢"
        preview += f"- **Noise Level:** {noise_emoji} {noise_level:.1f} dBA\n"
    
    # Add valve opening assessment
    if 20 <= opening_percent <= 80:
        preview += f"- **Valve Opening:** ✅ {opening_percent:.1f}% (Good control range)\n"
    else:
        preview += f"- **Valve Opening:** ⚠️ {opening_percent:.1f}% (Outside recommended range)\n"
    
    preview += f"""

### Standards Applied
- ✅ ISA 75.01-2012: Flow equations for sizing control valves
- ✅ IEC 60534-2-1:2011: Industrial-process control valves
- ✅ ISA RP75.23-1995: Cavitation evaluation  
- ✅ IEC 60534-8-3:2010: Noise prediction
- ✅ ASME B16.34-2017: Valve standards
- ✅ NACE MR0175: Sour service materials

### Professional Notes
This datasheet provides comprehensive valve sizing with complete technical analysis. 
All calculations follow industry standards and include appropriate safety factors 
based on service criticality.

**Generated by:** Enhanced Control Valve Sizing - Professional Edition  
**Author:** {project_data.get('engineer_name', 'Aseem Mehrotra, KBR Inc')}  
**Quality:** Professional engineering documentation
"""
    
    return preview

def display_navigation():
    """Enhanced navigation with current progress"""
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
                <div style='text-align: center; color: green;'>
                ✅ <strong>{title}</strong>
                </div>
                """, unsafe_allow_html=True)
            elif i == st.session_state.current_step:
                st.markdown(f"""
                <div style='text-align: center; color: blue;'>
                {icon} <strong>{title}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='text-align: center; color: gray;'>
                {icon} {title}
                </div>
                """, unsafe_allow_html=True)

def main():
    """Enhanced main application function with full integration"""
    initialize_session_state()
    display_header()
    
    # Enhanced sidebar navigation
    with st.sidebar:
        st.header("🧭 Enhanced Navigation")
        
        # Tab selection
        current_tab = st.radio(
            "Application Sections",
            ["🔧 Main Application", "📊 Engineering Charts", "📋 Professional Datasheet"],
            help="Navigate between different sections of the application"
        )
        
        if current_tab == "🔧 Main Application":
            st.session_state.current_tab = 'main'
        elif current_tab == "📊 Engineering Charts":
            st.session_state.current_tab = 'charts'  
        else:
            st.session_state.current_tab = 'datasheet'
        
        st.markdown("---")
        
        # Main application step navigation (only show when in main tab)
        if st.session_state.current_tab == 'main':
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
        st.markdown("#### 📊 Progress Summary")
        progress_items = [
            ("Process Data", bool(st.session_state.get('process_data'))),
            ("Valve Selection", bool(st.session_state.get('valve_selection'))),
            ("Sizing Results", bool(st.session_state.get('sizing_results'))),
            ("Cavitation Analysis", bool(st.session_state.get('cavitation_analysis'))),
            ("Noise Analysis", bool(st.session_state.get('noise_analysis'))),
            ("Material Analysis", bool(st.session_state.get('material_selection'))),
            ("Charts Generated", bool(st.session_state.get('charts_generated'))),
            ("Datasheet Ready", bool(st.session_state.get('datasheet_ready')))
        ]
        
        for item, completed in progress_items:
            status = "✅" if completed else "⭕"
            st.text(f"{status} {item}")
        
        st.markdown("---")
        
        # Enhanced features status
        st.markdown("#### 🔬 Enhanced Features")
        
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
        
        # Integration status
        try:
            from complete_step_functions import step1_process_conditions
            from datasheet_generator import ProfessionalDatasheetGenerator  
            from enhanced_charts import EnhancedChartsGenerator
            st.success("🔗 Full Integration: Active")
            st.caption("All modules loaded successfully")
        except ImportError as e:
            st.error(f"🔗 Integration Issue: {str(e)}")
        
        st.markdown("---")
        
        # Database and feature information
        liquid_db, gas_db = get_comprehensive_fluid_database()
        st.markdown("#### 📊 System Capabilities")
        st.info(f"**Liquid Fluids:** {len(liquid_db)}")
        st.info(f"**Gas/Vapor Fluids:** {len(gas_db)}")
        st.info(f"**Professional Charts:** 8+ types")
        st.info(f"**Datasheet Formats:** PDF, Excel, Text")
        
        # Help section
        st.markdown("#### ❓ Enhanced Help")
        with st.expander("📚 **User Guide**", expanded=False):
            st.markdown("""
            **🔧 Main Application:**
            - Complete 7-step valve sizing workflow
            - Professional calculations per ISA/IEC standards
            - Comprehensive validation and warnings
            
            **📊 Engineering Charts:**
            - 8+ professional engineering charts
            - Cavitation, noise, and performance analysis
            - Interactive plotly charts with hover details
            
            **📋 Professional Datasheet:**
            - Complete PDF/Excel datasheets
            - Standards-compliant documentation
            - Ready for engineering deliverables
            
            **💡 Pro Tips:**
            - Complete Main Application steps 1-3 minimum
            - Use Advanced Options for detailed analysis
            - Generate charts before creating datasheet
            - Validate critical applications with manufacturers
            """)
    
    # Main content area with tab navigation
    create_main_tabs()

if __name__ == "__main__":
    main()
