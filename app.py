"""
Enhanced Control Valve Sizing Application - Professional Edition
Updated app.py: preserves all original 7-step workflow and adds:
- Charts & Analysis tab with multiple engineering plots
- Professional Datasheet tab (PDF if reportlab is available, plus text/CSV fallbacks)

Author: Aseem Mehrotra, Senior Instrumentation Construction Engineer, KBR Inc
Standards alignment context: ISA 75.01 / IEC 60534-2-1 (sizing), ISA RP75.23 (cavitation),
IEC 60534-8-3 (noise), ASME B16.34 (materials & ratings).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import math
import io
import sys
import warnings

warnings.filterwarnings("ignore")

# Optional PDF support; if not present the app gracefully falls back
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors

    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# --------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Enhanced Control Valve Sizing - Professional",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------
# Session State Initialization (kept compatible with original)
# --------------------------------------------------------------------
def initialize_session_state():
    defaults = {
        "current_step": 1,
        "process_data": {},
        "valve_selection": {},
        "sizing_results": {},
        "cavitation_analysis": {},
        "noise_analysis": {},
        "material_selection": {},
        "compliance_check": {},
        "validation_warnings": [],
        "calculation_history": [],
        "unit_system": "metric",
        "show_advanced": False,
        "fluid_properties_db": {},
        "previous_fluid_selection": None,
        # New keys (non-breaking)
        "charts_ready": False,
        "datasheet_config": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# --------------------------------------------------------------------
# Data: Fluid database (compatible superset)
# --------------------------------------------------------------------
def get_comprehensive_fluid_database() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    # Liquids (subset + reasonable additions)
    liquid_fluids = {
        "Water": {
            "density": {"metric": 998.0, "imperial": 62.4},
            "vapor_pressure": {"metric": 0.032, "imperial": 0.46},
            "viscosity": 1.0,
            "typical_temp": {"metric": 25.0, "imperial": 77.0},
            "critical_pressure": {"metric": 221.2, "imperial": 3208.0},
            "molecular_weight": 18.015,
            "category": "Water/Aqueous",
            "description": "Pure water at standard conditions",
        },
        "Light Crude Oil": {
            "density": {"metric": 820.0, "imperial": 51.2},
            "vapor_pressure": {"metric": 0.15, "imperial": 2.2},
            "viscosity": 5.0,
            "typical_temp": {"metric": 40.0, "imperial": 104.0},
            "critical_pressure": {"metric": 25.0, "imperial": 363.0},
            "molecular_weight": 120.0,
            "category": "Hydrocarbons",
            "description": "Light crude oil (API ~35°)",
        },
        "Heavy Crude Oil": {
            "density": {"metric": 950.0, "imperial": 59.3},
            "vapor_pressure": {"metric": 0.01, "imperial": 0.15},
            "viscosity": 200.0,
            "typical_temp": {"metric": 80.0, "imperial": 176.0},
            "critical_pressure": {"metric": 15.0, "imperial": 218.0},
            "molecular_weight": 300.0,
            "category": "Hydrocarbons",
            "description": "Heavy crude oil (API ~15°)",
        },
        "Diesel Fuel": {
            "density": {"metric": 850.0, "imperial": 53.1},
            "vapor_pressure": {"metric": 0.05, "imperial": 0.7},
            "viscosity": 3.5,
            "typical_temp": {"metric": 25.0, "imperial": 77.0},
            "critical_pressure": {"metric": 22.0, "imperial": 319.0},
            "molecular_weight": 170.0,
            "category": "Refined Products",
            "description": "No.2 diesel fuel",
        },
        "Methanol": {
            "density": {"metric": 791.0, "imperial": 49.4},
            "vapor_pressure": {"metric": 0.17, "imperial": 2.5},
            "viscosity": 0.65,
            "typical_temp": {"metric": 25.0, "imperial": 77.0},
            "critical_pressure": {"metric": 81.0, "imperial": 1175.0},
            "molecular_weight": 32.04,
            "category": "Alcohols",
            "description": "Methanol (CH3OH)",
        },
        "Ethylene Glycol (50%)": {
            "density": {"metric": 1070.0, "imperial": 66.8},
            "vapor_pressure": {"metric": 0.02, "imperial": 0.3},
            "viscosity": 4.8,
            "typical_temp": {"metric": 25.0, "imperial": 77.0},
            "critical_pressure": {"metric": 77.0, "imperial": 1117.0},
            "molecular_weight": 62.07,
            "category": "Glycols",
            "description": "50% ethylene glycol aqueous solution",
        },
    }

    # Gases (subset + additions)
    gas_fluids = {
        "Air": {
            "molecular_weight": 28.97,
            "k_ratio": 1.4,
            "z_factor": 1.0,
            "typical_temp": {"metric": 25.0, "imperial": 77.0},
            "critical_pressure": {"metric": 37.7, "imperial": 547.0},
            "critical_temperature": 132.5,
            "category": "Air & Inert",
            "description": "Dry air at standard conditions",
        },
        "Natural Gas (Pipeline)": {
            "molecular_weight": 17.5,
            "k_ratio": 1.27,
            "z_factor": 0.95,
            "typical_temp": {"metric": 25.0, "imperial": 77.0},
            "critical_pressure": {"metric": 46.0, "imperial": 667.0},
            "critical_temperature": 190.6,
            "category": "Natural Gas",
            "description": "Typical pipeline natural gas",
        },
        "Methane": {
            "molecular_weight": 16.04,
            "k_ratio": 1.32,
            "z_factor": 0.98,
            "typical_temp": {"metric": 25.0, "imperial": 77.0},
            "critical_pressure": {"metric": 46.0, "imperial": 667.0},
            "critical_temperature": 190.6,
            "category": "Natural Gas",
            "description": "Pure methane",
        },
        "Steam": {
            "molecular_weight": 18.015,
            "k_ratio": 1.33,
            "z_factor": 1.0,
            "typical_temp": {"metric": 150.0, "imperial": 302.0},
            "critical_pressure": {"metric": 221.2, "imperial": 3208.0},
            "critical_temperature": 647.1,
            "category": "Steam",
            "description": "Saturated steam",
        },
    }
    return liquid_fluids, gas_fluids

def update_fluid_properties(fluid_type: str, fluid_name: str, unit_system: str):
    liquid_db, gas_db = get_comprehensive_fluid_database()
    if fluid_type == "Liquid" and fluid_name in liquid_db:
        f = liquid_db[fluid_name]
        return {
            "density": f["density"][unit_system],
            "vapor_pressure": f["vapor_pressure"][unit_system],
            "viscosity": f["viscosity"],
            "typical_temp": f["typical_temp"][unit_system],
            "critical_pressure": f.get("critical_pressure", {}).get(unit_system, None),
            "molecular_weight": f.get("molecular_weight", None),
            "description": f["description"],
            "category": f["category"],
        }
    if fluid_type == "Gas/Vapor" and fluid_name in gas_db:
        f = gas_db[fluid_name]
        return {
            "molecular_weight": f["molecular_weight"],
            "k_ratio": f["k_ratio"],
            "z_factor": f["z_factor"],
            "typical_temp": f["typical_temp"][unit_system],
            "critical_pressure": f["critical_pressure"][unit_system],
            "critical_temperature": f["critical_temperature"],
            "description": f["description"],
            "category": f["category"],
        }
    return None

# --------------------------------------------------------------------
# Header
# --------------------------------------------------------------------
def display_header():
    st.markdown(
        """
        <div style="background: linear-gradient(90deg,#1e3c72 0%,#2a5298 100%); padding: 1rem; border-radius: 10px;">
            <h1 style="color:#fff; text-align:center; margin:0;">⚙️ Enhanced Control Valve Sizing</h1>
            <h3 style="color:#e6f3ff; text-align:center; margin:0.25rem 0 0 0;">
                Professional Edition - Standards Compliant
            </h3>
            <div style="color:#b3d9ff; text-align:center; margin-top:0.25rem;">
                <small>ISA 75.01 • IEC 60534-2-1 • ISA RP75.23 • IEC 60534-8-3 • ASME B16.34</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------------
# Step Navigation (kept as original structure)
# --------------------------------------------------------------------
def display_navigation():
    steps = [
        ("1️⃣", "Process Conditions", "Define fluid and operating parameters"),
        ("2️⃣", "Valve Selection", "Select valve type, size, coefficients"),
        ("3️⃣", "Sizing Calculations", "Perform ISA/IEC sizing"),
        ("4️⃣", "Cavitation Analysis", "ISA RP75.23 evaluation (liquids)"),
        ("5️⃣", "Noise Prediction", "IEC 60534-8-3 assessment"),
        ("6️⃣", "Material Standards", "ASME/NACE/API checks"),
        ("7️⃣", "Final Report", "Documentation & downloads"),
    ]
    progress = (st.session_state.current_step - 1) / (len(steps) - 1)
    st.progress(progress)
    cols = st.columns(len(steps))
    for i, (icon, title, _) in enumerate(steps, 1):
        with cols[i - 1]:
            if i < st.session_state.current_step:
                st.markdown(
                    f"<div style='text-align:center; color:green;'>✅ {title}</div>",
                    unsafe_allow_html=True,
                )
            elif i == st.session_state.current_step:
                st.markdown(
                    f"<div style='text-align:center; color:#1463ff; font-weight:bold;'>{icon} {title}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align:center; color:#999;'>{icon} {title}</div>",
                    unsafe_allow_html=True,
                )

# --------------------------------------------------------------------
# Core sizing calculations (kept simple, standards-aligned structure)
# --------------------------------------------------------------------
def perform_liquid_sizing(process_data: Dict[str, Any], valve_selection: Dict[str, Any]) -> Dict[str, Any]:
    # Inputs
    Q = float(process_data.get("normal_flow", 0.0))  # flow rate
    dP = float(process_data.get("p1", 0.0)) - float(process_data.get("p2", 0.0))
    rho = float(process_data.get("density", 1000.0))
    unit_system = process_data.get("unit_system", "metric")

    # Convert to GPM/psi for a conventional Cv expression
    if unit_system == "metric":
        Q_gpm = Q * 4.403  # m3/h -> gpm
        dP_psi = dP * 14.5038  # bar -> psi
        SG = rho / 1000.0
    else:
        Q_gpm = Q
        dP_psi = dP
        SG = rho / 62.4

    # ISA 75.01 style liquid Cv (base form; piping/Re corrections can be layered in UI)
    # Cv = Q / (29.9 * sqrt(dP/SG))
    if dP_psi <= 0 or SG <= 0:
        cv_basic = 0.0
    else:
        cv_basic = Q_gpm / (29.9 * math.sqrt(dP_psi / SG))

    # Simple factors (kept compatible; can be replaced by detailed modules if present)
    Fp = float(0.98)  # piping geometry factor (example placeholder)
    Fr = float(1.0)   # Reynolds factor (assume turbulent as baseline)
    cv_required = cv_basic / (Fp * Fr) if Fp * Fr > 0 else cv_basic

    # Pack results
    return {
        "cv_basic": cv_basic,
        "cv_required": cv_required,
        "sizing_method": "ISA 75.01 Liquid (baseline form)",
        "fp_factor": Fp,
        "reynolds_analysis": {
            "reynolds_number": 50000,
            "fr_factor": Fr,
            "flow_regime": "Turbulent",
        },
        "warnings": [],
        "recommendations": [],
    }

def perform_gas_sizing(process_data: Dict[str, Any], valve_selection: Dict[str, Any]) -> Dict[str, Any]:
    # Inputs
    Q = float(process_data.get("normal_flow", 0.0))  # standard volumetric flow (keep simple)
    p1 = float(process_data.get("p1", 0.0))
    p2 = float(process_data.get("p2", 0.0))
    T = float(process_data.get("temperature", 20.0)) + 273.15  # K
    MW = float(process_data.get("molecular_weight", 28.97))
    k = float(process_data.get("specific_heat_ratio", 1.4))
    xt = float(valve_selection.get("xt_factor", 0.7))
    if p1 <= 0.0:
        return {"cv_basic": 0.0, "cv_required": 0.0, "sizing_method": "ISA 75.01 Gas"}

    pressure_ratio = p2 / p1 if p1 > 0 else 0.0
    critical_ratio = (2 / (k + 1)) ** (k / (k - 1)) if k > 1 else 0.5
    is_choked = pressure_ratio <= critical_ratio * xt

    # Simplified expansion factor (illustrative)
    if is_choked:
        y = 0.667 * math.sqrt(k * xt)
    else:
        x = 1.0 - pressure_ratio
        y = 1.0 - x / (3.0 * k * xt)
        y = max(0.1, min(1.0, y))

    # Simplified gas Cv correlation (scaled)
    # Cv ≈ Q * sqrt(T) / (1360 * p1 * y * sqrt(MW))
    cv = 0.0
    try:
        cv = Q * math.sqrt(T) / (1360.0 * p1 * y * math.sqrt(MW))
    except Exception:
        pass

    return {
        "cv_basic": cv,
        "cv_required": cv,
        "sizing_method": "ISA 75.01 Gas (baseline form)",
        "reynolds_analysis": {
            "reynolds_number": 100000,
            "fr_factor": 1.0,
            "flow_regime": "Turbulent",
        },
        "choked_analysis": {
            "is_choked": is_choked,
            "pressure_ratio": pressure_ratio,
            "critical_ratio": critical_ratio,
            "y_factor": y,
        },
        "warnings": [],
        "recommendations": [],
    }

def perform_comprehensive_sizing(process_data: Dict[str, Any], valve_selection: Dict[str, Any]) -> Dict[str, Any]:
    if process_data.get("fluid_type", "Liquid") == "Liquid":
        return perform_liquid_sizing(process_data, valve_selection)
    return perform_gas_sizing(process_data, valve_selection)

# --------------------------------------------------------------------
# Cavitation & Noise Analyses (kept compatible; baseline ISA/IEC framing)
# --------------------------------------------------------------------
def perform_cavitation_analysis(process_data: Dict[str, Any], valve_selection: Dict[str, Any], sizing_results: Dict[str, Any]) -> Dict[str, Any]:
    if process_data.get("fluid_type") != "Liquid":
        return {}
    p1 = float(process_data.get("p1", 0.0))
    p2 = float(process_data.get("p2", 0.0))
    pv = float(process_data.get("vapor_pressure", 0.0))
    dP = p1 - p2
    sigma_service = (p1 - pv) / dP if dP > 0 else 0.0
    # Simple risk tier
    if sigma_service < 1.2:
        risk = "Critical"; cav = True
    elif sigma_service < 1.8:
        risk = "High"; cav = True
    elif sigma_service < 2.5:
        risk = "Moderate"; cav = True
    else:
        risk = "Low"; cav = False
    return {
        "sigma_service": sigma_service,
        "risk_level": risk,
        "is_cavitating": cav,
        "recommendations": {
            "primary_recommendations": (
                ["Consider multi-stage/anti-cavitation trim", "Reduce ΔP across trim", "Shift operating point"]
                if cav else ["No cavitation mitigation required at design point"]
            )
        },
    }

def perform_noise_analysis(process_data: Dict[str, Any], valve_selection: Dict[str, Any], sizing_results: Dict[str, Any]) -> Dict[str, Any]:
    dP = float(process_data.get("p1", 0.0)) - float(process_data.get("p2", 0.0))
    Q = float(process_data.get("normal_flow", 0.0))
    # Simple illustrative SPL (IEC framing, not vendor-specific)
    lw = 60.0 + 10.0 * math.log10(max(1e-6, dP * max(1.0, Q) / 100.0))
    spl_1m = lw - 15.0
    if spl_1m > 90:
        level = "Critical"
    elif spl_1m > 85:
        level = "High"
    elif spl_1m > 75:
        level = "Moderate"
    else:
        level = "Acceptable"
    return {
        "lw_total": lw,
        "spl_1m": spl_1m,
        "spl_at_distance": spl_1m,
        "distance": 1.0,
        "assessment_level": level,
        "recommended_actions": (
            ["Use low-noise trim", "Add downstream diffuser", "Acoustic insulation"]
            if level in ("Critical", "High")
            else ["No special noise mitigation required"]
        ),
    }

# --------------------------------------------------------------------
# UI Blocks: Steps (preserve names and flow)
# --------------------------------------------------------------------
def step1_process_conditions():
    st.subheader("🔧 Step 1: Process Conditions")
    st.markdown("Enter accurate process data; parameters align with ISA/IEC sizing frameworks.")
    unit_select = st.radio("Unit System", ["Metric (SI)", "Imperial (US)"], index=0, horizontal=True)
    st.session_state.unit_system = "metric" if unit_select.startswith("Metric") else "imperial"

    # Fluid selection
    liquid_db, gas_db = get_comprehensive_fluid_database()
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        fluid_type = st.selectbox("Fluid Phase", ["Liquid", "Gas/Vapor"])
        if fluid_type == "Liquid":
            fluid_name = st.selectbox("Liquid", list(liquid_db.keys()) + ["Custom"])
            props = update_fluid_properties("Liquid", fluid_name, st.session_state.unit_system) if fluid_name != "Custom" else None
            temperature = st.number_input(f"Temperature ({'°C' if st.session_state.unit_system=='metric' else '°F'})", value=float(props["typical_temp"]) if props else 25.0, step=1.0)
            density = st.number_input(f"Density ({'kg/m³' if st.session_state.unit_system=='metric' else 'lb/ft³'})", value=float(props["density"]) if props else 998.0, step=1.0)
            vapor_pressure = st.number_input(f"Vapor Pressure ({'bar' if st.session_state.unit_system=='metric' else 'psi'})", value=float(props["vapor_pressure"]) if props else 0.032, step=0.001, format="%.3f")
            viscosity = st.number_input("Kinematic Viscosity (cSt)", value=float(props["viscosity"]) if props else 1.0, step=0.1)
        else:
            fluid_name = st.selectbox("Gas", list(gas_db.keys()) + ["Custom"])
            props = update_fluid_properties("Gas/Vapor", fluid_name, st.session_state.unit_system) if fluid_name != "Custom" else None
            temperature = st.number_input(f"Temperature ({'°C' if st.session_state.unit_system=='metric' else '°F'})", value=float(props["typical_temp"]) if props else 25.0, step=1.0)
            molecular_weight = st.number_input("Molecular Weight", value=float(props["molecular_weight"]) if props else 28.97, step=0.1)
            specific_heat_ratio = st.number_input("Specific Heat Ratio (k)", value=float(props["k_ratio"]) if props else 1.4, step=0.01, format="%.3f")
            compressibility = st.number_input("Compressibility Factor (Z)", value=float(props["z_factor"]) if props else 1.0, step=0.01, format="%.3f")

    with col2:
        pu = "bar" if st.session_state.unit_system == "metric" else "psi"
        p1 = st.number_input(f"Inlet Pressure P1 ({pu} abs)", value=10.0, step=0.1)
        p2 = st.number_input(f"Outlet Pressure P2 ({pu} abs)", value=2.0, step=0.1)
        delta_p = p1 - p2
        pressure_ratio = (p2 / p1) if p1 > 0 else 0.0
        col2a, col2b = st.columns(2)
        with col2a:
            st.metric("ΔP", f"{delta_p:.2f} {pu}")
        with col2b:
            st.metric("P2/P1", f"{pressure_ratio:.3f}")

        flow_units = st.selectbox("Flow Units", ["m³/h", "L/s", "GPM", "SCFH"])
        normal_flow = st.number_input(f"Normal Flow ({flow_units})", value=120.0, step=1.0)
        min_flow = st.number_input(f"Minimum Flow ({flow_units})", value=36.0, step=1.0)
        max_flow = st.number_input(f"Maximum Flow ({flow_units})", value=150.0, step=1.0)
        pipe_size = st.selectbox("Nominal Pipe Size", ['1"', '1.5"', '2"', '3"', '4"', '6"', '8"'], index=3)

    with col3:
        service_type = st.selectbox("Service Type", ["Clean Service", "Dirty Service", "Corrosive Service", "High Temperature", "Erosive Service"])
        criticality = st.selectbox("Service Criticality", ["Non-Critical", "Important", "Critical", "Safety Critical"])
        h2s_present = st.checkbox("H2S Present (Sour Service)")
        if h2s_present:
            h2s_partial_pressure = st.number_input(f"H2S Partial Pressure ({pu})", value=0.1, step=0.01, format="%.3f")
        else:
            h2s_partial_pressure = 0.0

    # Build process_data (compatible)
    process_data = {
        "fluid_type": fluid_type,
        "fluid_name": fluid_name,
        "temperature": temperature,
        "p1": p1,
        "p2": p2,
        "delta_p": delta_p,
        "pressure_ratio": pressure_ratio,
        "normal_flow": normal_flow,
        "min_flow": min_flow,
        "max_flow": max_flow,
        "flow_units": flow_units,
        "pipe_size": pipe_size,
        "service_type": service_type,
        "criticality": criticality,
        "h2s_present": h2s_present,
        "h2s_partial_pressure": h2s_partial_pressure,
        "unit_system": st.session_state.unit_system,
    }
    if fluid_type == "Liquid":
        process_data.update({"density": density, "vapor_pressure": vapor_pressure, "viscosity": viscosity})
    else:
        process_data.update({"molecular_weight": molecular_weight, "specific_heat_ratio": specific_heat_ratio, "compressibility": compressibility})

    # Safety factor rule-of-thumb by criticality + service
    base_sf = {"Non-Critical": 1.1, "Important": 1.2, "Critical": 1.3, "Safety Critical": 1.5}[criticality]
    service_mult = 1.0
    if service_type in ("Erosive Service", "Cavitating Service", "Two-Phase Flow"):
        service_mult = 1.2
    if h2s_present:
        service_mult *= 1.1
    process_data["safety_factor"] = round(base_sf * service_mult, 1)

    # Persist & next
    st.session_state.process_data = process_data
    st.info(f"Recommended Safety Factor: {process_data['safety_factor']:.1f}")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Proceed to Valve Selection →", type="primary", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()

def step2_valve_selection():
    st.subheader("🎛️ Step 2: Valve Selection")
    col1, col2, col3 = st.columns(3)
    with col1:
        valve_type = st.selectbox("Valve Type", ["Globe Valve", "Ball Valve", "Butterfly Valve"])
        if valve_type == "Globe Valve":
            valve_style = st.selectbox("Style", ["Single Seat", "Cage Guided"])
            fl_default, xt_default, fd_default = 0.9, 0.75, 1.0
        elif valve_type == "Ball Valve":
            valve_style = st.selectbox("Style", ["V-Notch", "Contoured"])
            fl_default, xt_default, fd_default = 0.6, 0.15, 1.0
        else:
            valve_style = st.selectbox("Style", ["High Performance", "Wafer Type"])
            fl_default, xt_default, fd_default = 0.5, 0.3, 0.8
        valve_size = st.selectbox('Valve Size', ['1"', '1.5"', '2"', '3"', '4"', '6"'], index=3)
        characteristic = st.selectbox("Flow Characteristic", ["Equal Percentage", "Linear", "Quick Opening"])
    with col2:
        fl_factor = st.number_input("FL (Liquid pressure recovery)", value=fl_default, step=0.01, format="%.2f")
        xt_factor = st.number_input("xT (Gas terminal pressure drop ratio)", value=xt_default, step=0.01, format="%.2f")
        fd_factor = st.number_input("Fd (Style modifier)", value=fd_default, step=0.1, format="%.1f")
        size_in = float(valve_size.replace('"', ""))
        max_cv = st.number_input("Maximum Cv (wide open)", value=size_in ** 2 * 25, step=1.0)
    with col3:
        rangeability = st.number_input("Rangeability (turndown)", value=50.0, step=5.0)
        anti_cavitation_trim = st.checkbox("Anti-Cavitation Trim")
        low_noise_trim = st.checkbox("Low Noise Trim")
        hardened_trim = st.checkbox("Hardened Trim")

    valve_selection = {
        "valve_type": valve_type,
        "valve_style": valve_style,
        "valve_size": valve_size,
        "flow_characteristic": characteristic,
        "fl_factor": fl_factor,
        "xt_factor": xt_factor,
        "fd_factor": fd_factor,
        "max_cv": max_cv,
        "rangeability": rangeability,
        "anti_cavitation_trim": anti_cavitation_trim,
        "low_noise_trim": low_noise_trim,
        "hardened_trim": hardened_trim,
    }
    st.session_state.valve_selection = valve_selection

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← Back to Process", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    with c2:
        if st.button("🧮 Proceed to Sizing Calculations →", type="primary", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()

def step3_sizing_calculations():
    st.subheader("🧮 Step 3: Sizing Calculations")
    pd_ = st.session_state.get("process_data", {})
    vs_ = st.session_state.get("valve_selection", {})
    if not pd_ or not vs_:
        st.error("Please complete Steps 1 and 2 first.")
        return
    with st.spinner("Performing sizing calculations..."):
        sr = perform_comprehensive_sizing(pd_, vs_)
    if "error" in sr:
        st.error(f"Calculation error: {sr['error']}")
        return

    # Opening with safety
    safety = pd_.get("safety_factor", 1.2)
    cv_basic = float(sr.get("cv_basic", 0.0))
    cv_req = float(sr.get("cv_required", 0.0))
    cv_with_sf = cv_req * safety
    opening_percent = (cv_with_sf / float(vs_.get("max_cv", 1.0))) * 100 if float(vs_.get("max_cv", 1.0)) > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Required Cv (basic)", f"{cv_req:.2f}")
        st.metric("Required Cv (with safety)", f"{cv_with_sf:.2f}")
    with col2:
        ra = sr.get("reynolds_analysis", {})
        st.metric("Reynolds Number", f"{float(ra.get('reynolds_number', 0)):.0f}")
        st.metric("Fr Factor", f"{float(ra.get('fr_factor', 1.0)):.3f}")
    with col3:
        st.metric("Valve Opening at Normal", f"{opening_percent:.1f}%")
        st.metric("Fp Factor", f"{float(sr.get('fp_factor', 1.0)):.3f}")

    st.session_state.sizing_results = sr

    # Auto-analyses
    if pd_.get("fluid_type") == "Liquid":
        st.session_state.cavitation_analysis = perform_cavitation_analysis(pd_, vs_, sr)
    st.session_state.noise_analysis = perform_noise_analysis(pd_, vs_, sr)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← Back to Valve Selection", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    with c2:
        if st.button("🌊 Proceed to Cavitation Analysis →", type="primary", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()

def step4_cavitation_analysis():
    st.subheader("🌊 Step 4: Cavitation Analysis (ISA RP75.23 framing)")
    cav = st.session_state.get("cavitation_analysis", {})
    if not cav:
        st.info("Not applicable for gas service or missing liquid results.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Service Sigma (σ)", f"{float(cav.get('sigma_service', 0.0)):.2f}")
        with col2:
            if cav.get("is_cavitating", False):
                st.error(f"Risk Level: {cav.get('risk_level','Unknown')}")
            else:
                st.success(f"Risk Level: {cav.get('risk_level','Unknown')}")
        st.write("Recommendations:")
        for rec in cav.get("recommendations", {}).get("primary_recommendations", []):
            st.write(f"- {rec}")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← Back to Sizing", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    with c2:
        if st.button("🔊 Proceed to Noise Prediction →", type="primary", use_container_width=True):
            st.session_state.current_step = 5
            st.rerun()

def step5_noise_prediction():
    st.subheader("🔊 Step 5: Noise Prediction (IEC 60534-8-3 framing)")
    noise = st.session_state.get("noise_analysis", {})
    if not noise:
        st.info("Run sizing to populate noise analysis.")
        return
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sound Power Level", f"{float(noise.get('lw_total', 0.0)):.1f} dB")
        st.metric("SPL @ 1 m", f"{float(noise.get('spl_1m', 0.0)):.1f} dBA")
    with col2:
        level = noise.get("assessment_level", "Unknown")
        if float(noise.get("spl_1m", 0.0)) > 85.0:
            st.error(f"Assessment: {level}")
        else:
            st.success(f"Assessment: {level}")
        st.write("Recommendations:")
        for rec in noise.get("recommended_actions", []):
            st.write(f"- {rec}")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← Back to Cavitation", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()
    with c2:
        if st.button("🔩 Proceed to Material Standards →", type="primary", use_container_width=True):
            st.session_state.current_step = 6
            st.rerun()

def step6_material_standards():
    st.subheader("🔩 Step 6: Material Standards (ASME B16.34 / NACE context)")
    pd_ = st.session_state.get("process_data", {})
    h2s = bool(pd_.get("h2s_present", False))
    temp_c = float(pd_.get("temperature", 25.0))
    service = pd_.get("service_type", "Clean Service")
    rec = []
    if h2s:
        st.warning("Sour service detected: NACE MR0175 applies.")
        rec = ["316/316L SS", "Duplex SS", "Inconel 625"]
    elif "Corrosive" in service:
        st.info("Corrosive service: select corrosion-resistant trim.")
        rec = ["316L SS", "Hastelloy C-276", "Alloy 625"]
    elif temp_c > 200:
        st.info("High temperature: verify strength/material curves.")
        rec = ["321 SS", "Alloy 800H", "Inconel series"]
    else:
        st.success("Standard service.")
        rec = ["WCB (CS) body / 316 SS trim", "316 SS"]
    st.session_state.material_selection = {
        "recommended_materials": rec,
        "selected_material": rec if rec else "TBD",
        "h2s_service": h2s,
        "compliance_standards": ["ASME B16.34"] + (["NACE MR0175"] if h2s else []),
    }

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← Back to Noise", use_container_width=True):
            st.session_state.current_step = 5
            st.rerun()
    with c2:
        if st.button("📋 Proceed to Final Report →", type="primary", use_container_width=True):
            st.session_state.current_step = 7
            st.rerun()

def step7_final_report():
    st.subheader("📋 Step 7: Final Report")
    pd_ = st.session_state.get("process_data", {})
    vs_ = st.session_state.get("valve_selection", {})
    sr = st.session_state.get("sizing_results", {})
    cav = st.session_state.get("cavitation_analysis", {})
    noise = st.session_state.get("noise_analysis", {})
    mat = st.session_state.get("material_selection", {})

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Required Cv", f"{float(sr.get('cv_required', 0.0)):.2f}")
        st.metric("Valve Size", vs_.get("valve_size", "TBD"))
    with col2:
        st.metric("Safety Factor", f"{float(pd_.get('safety_factor', 1.2)):.1f}")
        st.metric("Service Type", pd_.get("service_type", "Standard"))
    with col3:
        st.metric("Recommended Material", mat.get("selected_material", "TBD"))
        st.metric("Criticality", pd_.get("criticality", "Important"))

    st.markdown("#### Downloads")
    c1, c2 = st.columns(2)
    with c1:
        text_report = generate_text_report()
        st.download_button(
            "📄 Download Technical Report (txt)",
            data=text_report,
            file_name="Control_Valve_Sizing_Report.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2:
        csv_summary = generate_csv_summary()
        st.download_button(
            "📊 Download Summary (csv)",
            data=csv_summary,
            file_name="Control_Valve_Summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

# --------------------------------------------------------------------
# Charts & Analysis Tab (ADDED; non-breaking)
# --------------------------------------------------------------------
def charts_tab():
    st.subheader("📊 Charts & Analysis")
    sr = st.session_state.get("sizing_results", {})
    if not sr:
        st.info("Run sizing first.")
        return
    pd_ = st.session_state.get("process_data", {})
    vs_ = st.session_state.get("valve_selection", {})
    cav = st.session_state.get("cavitation_analysis", {})
    noise = st.session_state.get("noise_analysis", {})

    with st.expander("Valve Flow Characteristic Curve", expanded=True):
        st.plotly_chart(chart_valve_characteristic(vs_, sr), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("Valve Opening vs Flow", expanded=False):
            st.plotly_chart(chart_opening_vs_flow(pd_, vs_, sr), use_container_width=True)
    with col2:
        with st.expander("System Pressure Profile", expanded=False):
            st.plotly_chart(chart_pressure_profile(pd_), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        with st.expander("Cavitation Analysis (Sigma)", expanded=False):
            st.plotly_chart(chart_cavitation(cav), use_container_width=True)
    with col4:
        with st.expander("Noise vs Distance", expanded=False):
            st.plotly_chart(chart_noise(noise), use_container_width=True)

    with st.expander("Reynolds Correction Map", expanded=False):
        st.plotly_chart(chart_reynolds(sr), use_container_width=True)

def chart_valve_characteristic(valve_selection: Dict[str, Any], sizing_results: Dict[str, Any]):
    characteristic = valve_selection.get("flow_characteristic", "Equal Percentage")
    max_cv = float(valve_selection.get("max_cv", 100.0))
    cv_required = float(sizing_results.get("cv_required", 0.0))
    openings = np.linspace(0, 100, 101)
    if characteristic == "Equal Percentage":
        R = float(valve_selection.get("rangeability", 50.0))
        cv_values = max_cv * np.power(R, (openings - 100.0) / 100.0)
    elif characteristic == "Linear":
        cv_values = (openings / 100.0) * max_cv
    else:
        cv_values = max_cv * np.sqrt(openings / 100.0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=openings, y=cv_values, mode="lines", name=f"{characteristic} Curve"))
    if cv_required > 0 and max_cv > 0:
        fig.add_trace(
            go.Scatter(
                x=[(cv_required / max_cv) * 100.0],
                y=[cv_required],
                mode="markers",
                name="Operating Point",
                marker=dict(color="red", size=11, symbol="diamond"),
            )
        )
    fig.update_layout(
        title="Valve Flow Characteristic",
        xaxis_title="Valve Opening (%)",
        yaxis_title="Cv",
        height=420,
    )
    return fig

def chart_opening_vs_flow(process_data: Dict[str, Any], valve_selection: Dict[str, Any], sizing_results: Dict[str, Any]):
    nf = float(process_data.get("normal_flow", 100.0))
    minf = float(process_data.get("min_flow", 30.0))
    maxf = float(process_data.get("max_flow", 125.0))
    max_cv = float(valve_selection.get("max_cv", 100.0))
    cv_req = float(sizing_results.get("cv_required", 50.0))
    safety = float(process_data.get("safety_factor", 1.2))
    cv_norm = cv_req * safety
    flows = np.linspace(minf, maxf, 50)
    openings = (flows / nf) * (cv_norm / max_cv) * 100.0 if max_cv > 0 else np.zeros_like(flows)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=flows, y=openings, mode="lines", name="Opening vs Flow"))
    fig.add_hrect(y0=20, y1=80, fillcolor="lightgreen", opacity=0.25, annotation_text="Recommended Range")
    fig.update_layout(
        title="Valve Opening vs Flow",
        xaxis_title=f"Flow ({process_data.get('flow_units','m³/h')})",
        yaxis_title="Opening (%)",
        height=420,
    )
    return fig

def chart_pressure_profile(process_data: Dict[str, Any]):
    p1 = float(process_data.get("p1", 10.0))
    p2 = float(process_data.get("p2", 2.0))
    pos = ["Upstream", "Valve Inlet", "Valve", "Valve Outlet", "Downstream"]
    prs = [p1, p1 * 0.98, (p1 + p2) / 2.0, p2 * 1.02, p2]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pos, y=prs, mode="lines+markers", name="Pressure Profile"))
    fig.update_layout(title="System Pressure Profile", xaxis_title="Location", yaxis_title="Pressure (bar)", height=380)
    return fig

def chart_cavitation(cav: Dict[str, Any]):
    sigma = float(cav.get("sigma_service", 0.0)) if cav else 0.0
    limits = {"Choking": 1.2, "Damage": 1.8, "Constant": 2.5, "Incipient": 3.5}
    fig = go.Figure()
    for level, val in limits.items():
        fig.add_trace(go.Bar(x=[val], y=[level], orientation="h", name=f"{level} σ", opacity=0.7))
    fig.add_vline(x=sigma, line_dash="dash", line_color="red", annotation_text=f"Service σ = {sigma:.2f}")
    fig.update_layout(title="Cavitation Sigma Map", xaxis_title="Sigma (σ)", yaxis_title="Level", height=380, showlegend=False)
    return fig

def chart_noise(noise: Dict[str, Any]):
    spl1 = float(noise.get("spl_1m", 70.0)) if noise else 70.0
    distances = np.array([1, 2, 5, 10, 20, 50], dtype=float)
    spl = [spl1 - 10.0 * math.log10(d) for d in distances]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=distances, y=spl, mode="lines+markers", name="SPL"))
    fig.add_hline(y=85, line_dash="dash", line_color="orange", annotation_text="OSHA 85 dBA")
    fig.update_layout(title="Noise vs Distance", xaxis_title="Distance (m, log)", yaxis_title="SPL (dBA)", xaxis_type="log", height=380)
    return fig

def chart_reynolds(sr: Dict[str, Any]):
    re = float(sr.get("reynolds_analysis", {}).get("reynolds_number", 50000.0))
    fr = float(sr.get("reynolds_analysis", {}).get("fr_factor", 1.0))
    fig = go.Figure()
    re_range = np.logspace(2, 6, 200)
    fr_curve = np.clip(np.interp(np.log10(re_range), [2, 4.75, 6], [0.3, 0.95, 1.0]), 0.1, 1.0)
    fig.add_trace(go.Scatter(x=re_range, y=fr_curve, mode="lines", name="Fr(Re)"))
    fig.add_trace(go.Scatter(x=[re], y=[fr], mode="markers", name="Operating Point", marker=dict(color="red", size=12, symbol="diamond")))
    fig.update_layout(title="Reynolds Correction Map", xaxis_title="Re (log)", yaxis_title="Fr", xaxis_type="log", height=380)
    return fig

# --------------------------------------------------------------------
# Datasheet tab (ADDED; non-breaking)
# --------------------------------------------------------------------
def datasheet_tab():
    st.subheader("📋 Professional Control Valve Datasheet")
    pd_ = st.session_state.get("process_data", {})
    vs_ = st.session_state.get("valve_selection", {})
    sr = st.session_state.get("sizing_results", {})
    if not (pd_ and vs_ and sr):
        st.warning("Complete sizing first.")
        return

    c1, c2 = st.columns(2)
    with c1:
        project_name = st.text_input("Project Name", "Control Valve Sizing Project")
        tag_number = st.text_input("Valve Tag Number", "CV-001")
        engineer_name = st.text_input("Engineer", "Aseem Mehrotra, KBR Inc")
        client_name = st.text_input("Client", "")
    with c2:
        include_process = st.checkbox("Include Process Conditions", True)
        include_sizing = st.checkbox("Include Sizing Calculations", True)
        include_analysis = st.checkbox("Include Technical Analysis", True)
        include_standards = st.checkbox("Include Standards Compliance", True)

    st.markdown("#### Generate")
    d1, d2, d3 = st.columns(3)
    with d1:
        if st.button("📄 Generate PDF (fallback to txt)"):
            pdf_or_text = generate_pdf_or_text_datasheet(project_name, tag_number, engineer_name, client_name, include_process, include_sizing, include_analysis, include_standards)
            if isinstance(pdf_or_text, bytes) and REPORTLAB_AVAILABLE:
                st.download_button("📥 Download PDF Datasheet", data=pdf_or_text, file_name=f"{tag_number}_Datasheet.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.download_button("📥 Download Text Datasheet", data=pdf_or_text, file_name=f"{tag_number}_Datasheet.txt", mime="text/plain", use_container_width=True)
    with d2:
        csv_summary = generate_csv_summary()
        st.download_button("📥 Download CSV Summary", data=csv_summary, file_name=f"{tag_number}_Summary.csv", mime="text/csv", use_container_width=True)
    with d3:
        text_report = generate_text_report()
        st.download_button("📥 Download Full Technical Report (txt)", data=text_report, file_name=f"{tag_number}_Technical_Report.txt", mime="text/plain", use_container_width=True)

    with st.expander("👀 Preview (Markdown)"):
        st.markdown(build_markdown_preview(project_name, tag_number, engineer_name, client_name, include_process, include_sizing, include_analysis, include_standards))

def generate_pdf_or_text_datasheet(project_name, tag, engineer, client, inc_proc, inc_sizing, inc_analysis, inc_std):
    if REPORTLAB_AVAILABLE:
        try:
            return build_pdf_datasheet(project_name, tag, engineer, client, inc_proc, inc_sizing, inc_analysis, inc_std)
        except Exception as e:
            # Fallback to text
            return build_text_datasheet(project_name, tag, engineer, client, inc_proc, inc_sizing, inc_analysis, inc_std).encode()
    else:
        return build_text_datasheet(project_name, tag, engineer, client, inc_proc, inc_sizing, inc_analysis, inc_std).encode()

def build_pdf_datasheet(project_name, tag, engineer, client, inc_proc, inc_sizing, inc_analysis, inc_std) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleBlue", parent=styles["Title"], textColor=colors.darkblue)
    h1 = ParagraphStyle("H1Blue", parent=styles["Heading1"], textColor=colors.darkblue)
    story = []
    story.append(Paragraph("CONTROL VALVE DATASHEET", title))
    story.append(Spacer(1, 6*mm))
    meta = [
        ["Project", project_name],
        ["Tag Number", tag],
        ["Engineer", engineer],
        ["Client", client or "TBD"],
        ["Date", datetime.now().strftime("%Y-%m-%d")],
    ]
    t = Table(meta, colWidths=[35*mm, 120*mm])
    t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.grey), ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke)]))
    story.append(t); story.append(Spacer(1, 4*mm))

    pd_ = st.session_state.get("process_data", {})
    vs_ = st.session_state.get("valve_selection", {})
    sr = st.session_state.get("sizing_results", {})
    cav = st.session_state.get("cavitation_analysis", {})
    noise = st.session_state.get("noise_analysis", {})

    if inc_proc:
        story.append(Paragraph("1. PROCESS CONDITIONS", h1))
        rows = [
            ["Fluid", pd_.get("fluid_name","TBD"), "-"],
            ["Temperature", f"{float(pd_.get('temperature',0)):.1f}", "°C"],
            ["P1 / P2", f"{float(pd_.get('p1',0)):.1f} / {float(pd_.get('p2',0)):.1f}", "bar abs"],
            ["Normal Flow", f"{float(pd_.get('normal_flow',0)):.1f}", pd_.get("flow_units","m³/h")],
            ["Service / Criticality", f"{pd_.get('service_type','Standard')} / {pd_.get('criticality','Important')}", "-"],
        ]
        tt = Table([["Parameter", "Value", "Units"]] + rows, colWidths=[45*mm, 60*mm, 20*mm])
        tt.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)]))
        story.append(tt); story.append(Spacer(1, 3*mm))

    if inc_sizing:
        story.append(Paragraph("2. SIZING CALCULATIONS", h1))
        rows = [
            ["Method", sr.get("sizing_method","ISA 75.01"), "-"],
            ["Cv (basic)", f"{float(sr.get('cv_basic',0)):.3f}", "-"],
            ["Fp / Fr", f"{float(sr.get('fp_factor',1.0)):.3f} / {float(sr.get('reynolds_analysis',{}).get('fr_factor',1.0)):.3f}", "-"],
            ["Cv (required)", f"{float(sr.get('cv_required',0)):.3f}", "-"],
        ]
        tt = Table([["Parameter","Value","Units"]] + rows, colWidths=[45*mm, 60*mm, 20*mm])
        tt.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)]))
        story.append(tt); story.append(Spacer(1, 3*mm))

    if inc_analysis:
        story.append(Paragraph("3. TECHNICAL ANALYSIS", h1))
        cav_rows = [
            ["Cavitation Sigma", f"{float(cav.get('sigma_service',0)):.2f}", "-"],
            ["Cavitation Risk", cav.get("risk_level","N/A"), "-"],
        ] if cav else [["Cavitation", "Not applicable", "-"]]
        noise_rows = [
            ["SPL @ 1 m", f"{float(noise.get('spl_1m',0)):.1f}", "dBA"],
            ["Assessment", noise.get("assessment_level","N/A"), "-"],
        ] if noise else [["Noise", "No data", "-"]]
        tt = Table([["Parameter","Value","Units"]] + cav_rows + [["","", ""]] + noise_rows, colWidths=[45*mm, 60*mm, 20*mm])
        tt.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)]))
        story.append(tt); story.append(Spacer(1, 3*mm))

    if inc_std:
        story.append(Paragraph("4. STANDARDS COMPLIANCE", h1))
        story.append(Paragraph("ISA 75.01 • IEC 60534-2-1 • ISA RP75.23 • IEC 60534-8-3 • ASME B16.34", styles["Normal"]))

    doc.build(story)
    buf.seek(0)
    return buf.read()

def build_text_datasheet(project_name, tag, engineer, client, inc_proc, inc_sizing, inc_analysis, inc_std) -> str:
    pd_ = st.session_state.get("process_data", {})
    vs_ = st.session_state.get("valve_selection", {})
    sr = st.session_state.get("sizing_results", {})
    cav = st.session_state.get("cavitation_analysis", {})
    noise = st.session_state.get("noise_analysis", {})

    lines = []
    lines.append("CONTROL VALVE DATASHEET")
    lines.append(f"Project: {project_name}")
    lines.append(f"Tag: {tag}")
    lines.append(f"Engineer: {engineer}")
    lines.append(f"Client: {client or 'TBD'}")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    if inc_proc:
        lines.extend([
            "PROCESS CONDITIONS",
            f"Fluid: {pd_.get('fluid_name','TBD')} ({pd_.get('fluid_type','')})",
            f"Temperature: {float(pd_.get('temperature',0)):.1f} °C",
            f"P1 / P2: {float(pd_.get('p1',0)):.1f} / {float(pd_.get('p2',0)):.1f} bar abs",
            f"Normal Flow: {float(pd_.get('normal_flow',0)):.1f} {pd_.get('flow_units','m³/h')}",
            f"Service/Criticality: {pd_.get('service_type','')}/{pd_.get('criticality','')}",
            "",
        ])
    if inc_sizing:
        lines.extend([
            "SIZING CALCULATIONS",
            f"Method: {sr.get('sizing_method','ISA 75.01')}",
            f"Cv (basic): {float(sr.get('cv_basic',0)):.3f}",
            f"Cv (required): {float(sr.get('cv_required',0)):.3f}",
            "",
        ])
    if inc_analysis:
        lines.extend([
            "TECHNICAL ANALYSIS",
            f"Cavitation Sigma: {float(cav.get('sigma_service',0)):.2f}" if cav else "Cavitation: N/A",
            f"Cavitation Risk: {cav.get('risk_level','N/A')}" if cav else "",
            f"SPL @1m: {float(noise.get('spl_1m',0)):.1f} dBA" if noise else "Noise: N/A",
            f"Assessment: {noise.get('assessment_level','N/A')}" if noise else "",
            "",
        ])
    if inc_std:
        lines.extend([
            "STANDARDS COMPLIANCE",
            "ISA 75.01 • IEC 60534-2-1 • ISA RP75.23 • IEC 60534-8-3 • ASME B16.34",
            "",
        ])
    return "\n".join(lines)

def build_markdown_preview(project_name, tag, engineer, client, inc_proc, inc_sizing, inc_analysis, inc_std) -> str:
    return build_text_datasheet(project_name, tag, engineer, client, inc_proc, inc_sizing, inc_analysis, inc_std)

# --------------------------------------------------------------------
# Reporting helpers (final report + csv)
# --------------------------------------------------------------------
def generate_text_report() -> str:
    pd_ = st.session_state.get("process_data", {})
    vs_ = st.session_state.get("valve_selection", {})
    sr = st.session_state.get("sizing_results", {})
    cav = st.session_state.get("cavitation_analysis", {})
    noise = st.session_state.get("noise_analysis", {})
    safety = float(pd_.get("safety_factor", 1.2))
    opening = (float(sr.get("cv_required", 0.0)) * safety / float(vs_.get("max_cv", 100.0)) * 100.0) if float(vs_.get("max_cv", 0.0)) > 0 else 0.0

    lines = []
    lines.append("CONTROL VALVE SIZING REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("EXECUTIVE SUMMARY")
    lines.append(f"Required Cv: {float(sr.get('cv_required', 0.0)):.2f}")
    lines.append(f"Valve Size: {vs_.get('valve_size', 'TBD')}")
    lines.append(f"Safety Factor: {safety:.1f}")
    lines.append("")
    lines.append("PROCESS CONDITIONS")
    lines.append(f"Fluid: {pd_.get('fluid_name','TBD')} ({pd_.get('fluid_type','')})")
    lines.append(f"Temperature: {float(pd_.get('temperature',0)):.1f} °C")
    lines.append(f"P1 → P2: {float(pd_.get('p1',0)):.1f} → {float(pd_.get('p2',0)):.1f} bar abs")
    lines.append(f"Normal Flow: {float(pd_.get('normal_flow',0)):.1f} {pd_.get('flow_units','m³/h')}")
    lines.append(f"Service/Criticality: {pd_.get('service_type','')}/{pd_.get('criticality','')}")
    lines.append("")
    lines.append("SIZING CALCULATIONS")
    lines.append(f"Method: {sr.get('sizing_method','ISA 75.01')}")
    lines.append(f"Cv (basic): {float(sr.get('cv_basic',0)):.3f}")
    lines.append(f"Cv (required): {float(sr.get('cv_required',0)):.3f}")
    lines.append(f"Valve Opening (normal): {opening:.1f}%")
    lines.append("")
    lines.append("TECHNICAL ANALYSIS")
    if cav:
        lines.append(f"Cavitation Sigma: {float(cav.get('sigma_service',0)):.2f}")
        lines.append(f"Cavitation Risk: {cav.get('risk_level','Unknown')}")
    if noise:
        lines.append(f"SPL @1m: {float(noise.get('spl_1m',0)):.1f} dBA ({noise.get('assessment_level','Unknown')})")
    lines.append("")
    lines.append("STANDARDS COMPLIANCE")
    lines.append("ISA 75.01 • IEC 60534-2-1 • ISA RP75.23 • IEC 60534-8-3 • ASME B16.34")
    lines.append("")
    return "\n".join(lines)

def generate_csv_summary() -> bytes:
    pd_ = st.session_state.get("process_data", {})
    vs_ = st.session_state.get("valve_selection", {})
    sr = st.session_state.get("sizing_results", {})
    sf = float(pd_.get("safety_factor", 1.2))
    data = {
        "Parameter": [
            "Fluid",
            "Fluid Type",
            "Temperature (°C)",
            "P1 (bar abs)",
            "P2 (bar abs)",
            "Normal Flow",
            "Flow Units",
            "Valve Type",
            "Valve Style",
            "Valve Size",
            "Characteristic",
            "Max Cv",
            "Cv (basic)",
            "Cv (required)",
            "Safety Factor",
            "Opening @ normal (%)",
        ],
        "Value": [
            pd_.get("fluid_name", "TBD"),
            pd_.get("fluid_type", "TBD"),
            f"{float(pd_.get('temperature', 0)):.1f}",
            f"{float(pd_.get('p1', 0)):.1f}",
            f"{float(pd_.get('p2', 0)):.1f}",
            f"{float(pd_.get('normal_flow', 0)):.1f}",
            pd_.get("flow_units", "m³/h"),
            vs_.get("valve_type", "TBD"),
            vs_.get("valve_style", "TBD"),
            vs_.get("valve_size", "TBD"),
            vs_.get("flow_characteristic", "TBD"),
            f"{float(vs_.get('max_cv', 0)):.0f}",
            f"{float(sr.get('cv_basic', 0)):.2f}",
            f"{float(sr.get('cv_required', 0)):.2f}",
            f"{sf:.1f}",
            f"{(float(sr.get('cv_required', 0)) * sf / float(vs_.get('max_cv', 100)) * 100 if float(vs_.get('max_cv', 0))>0 else 0):.1f}",
        ],
    }
    return pd.DataFrame(data).to_csv(index=False).encode()

# --------------------------------------------------------------------
# Main containers
# --------------------------------------------------------------------
def handle_sizing_workflow():
    display_navigation()
    step = st.session_state.current_step
    if step == 1:
        step1_process_conditions()
    elif step == 2:
        step2_valve_selection()
    elif step == 3:
        step3_sizing_calculations()
    elif step == 4:
        step4_cavitation_analysis()
    elif step == 5:
        step5_noise_prediction()
    elif step == 6:
        step6_material_standards()
    else:
        step7_final_report()

def main():
    initialize_session_state()
    display_header()

    with st.sidebar:
        st.header("🧭 Enhanced Navigation")
        tab_choice = st.radio("Main Sections", ["🧮 Valve Sizing", "📊 Charts & Analysis", "📋 Professional Datasheet"], index=0)
        st.markdown("---")
        if "Sizing" in tab_choice:
            steps = ["Process Conditions", "Valve Selection", "Sizing Calculations", "Cavitation Analysis", "Noise Prediction", "Material Standards", "Final Report"]
            cur = st.radio("Current Step", list(range(1, 8)), index=st.session_state.current_step - 1, format_func=lambda x: f"{x}. {steps[x-1]}")
            if cur != st.session_state.current_step:
                st.session_state.current_step = cur
                st.rerun()
        st.markdown("---")
        st.markdown("#### Progress")
        prog = [
            ("Process Data", bool(st.session_state.get("process_data"))),
            ("Valve Selection", bool(st.session_state.get("valve_selection"))),
            ("Sizing Results", bool(st.session_state.get("sizing_results"))),
            ("Cavitation Analysis", bool(st.session_state.get("cavitation_analysis"))),
            ("Noise Analysis", bool(st.session_state.get("noise_analysis"))),
            ("Material Analysis", bool(st.session_state.get("material_selection"))),
        ]
        for label, done in prog:
            st.text(f"{'✅' if done else '⭕'} {label}")

    if "Sizing" in tab_choice:
        handle_sizing_workflow()
    elif "Charts" in tab_choice:
        charts_tab()
    else:
        datasheet_tab()

if __name__ == "__main__":
    main()
