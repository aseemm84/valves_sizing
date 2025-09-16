# Enhanced Control Valve Sizing - Professional Edition

A comprehensive, standards-compliant control valve sizing application implementing industry-leading calculation methods and professional engineering standards.

## 🎯 Overview

This application provides a complete framework for professional control valve sizing, incorporating:

- **ISA 75.01 / IEC 60534-2-1**: Complete liquid and gas sizing calculations
- **ISA RP75.23**: Five-level cavitation analysis with scaling corrections
- **IEC 60534-8-3**: Aerodynamic noise prediction methodology
- **ASME B16.34**: Pressure-temperature ratings and material standards
- **NACE MR0175**: Sour service material compliance
- **API 6D**: Pipeline valve requirements

## 🚀 Quick Start

1. **Install Python 3.8+**
2. **Create virtual environment:**
   ```bash
   python -m venv valve_env
   source valve_env/bin/activate  # Linux/Mac
   valve_env\Scripts\activate     # Windows
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run application:**
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
Enhanced_CV_Sizing_Professional/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── calculations/              # Core sizing calculations
│   ├── liquid_sizing.py      # ISA 75.01 liquid sizing
│   ├── gas_sizing.py         # ISA 75.01 gas sizing
│   ├── geometry_factors.py   # Piping geometry (Fp)
│   └── reynolds_correction.py # Viscous flow correction
├── standards/                 # Standards implementation
│   ├── isa_rp75_23.py       # Cavitation analysis
│   └── iec_60534_8_3.py     # Noise prediction
├── data/                     # Valve and fluid databases
│   ├── valve_database.py    # Valve coefficients
│   ├── fluid_properties.py  # Fluid property database
│   └── manufacturer_data.py # Vendor-specific data
├── utils/                    # Utilities and helpers
│   ├── validators.py        # Input validation
│   ├── unit_converters.py   # Unit conversions
│   ├── plotting.py          # Visualization
│   └── helpers.py           # General utilities
└── config/                   # Configuration
    ├── constants.py         # Engineering constants
    └── settings.py          # Application settings
```

## 🔧 Features

### Professional Sizing Calculations
- Complete ISA 75.01/IEC 60534-2-1 implementation
- Piping geometry factors (Fp) for accurate sizing
- Reynolds correction (Fr) with iterative solution
- Choked flow analysis for liquids and gases
- Multi-scenario validation across operating range

### Advanced Cavitation Analysis
- ISA RP75.23 five-level sigma methodology
- Pressure Scale Effect (PSE) and Size Scale Effect (SSE) corrections
- Professional mitigation recommendations
- Damage potential assessment

### Noise Prediction
- IEC 60534-8-3 aerodynamic noise calculation
- Sound pressure level prediction at specified distances
- Pipe wall transmission loss analysis
- Mitigation strategy recommendations

### Material Standards Compliance
- ASME B16.34 pressure-temperature rating verification
- NACE MR0175 sour service material compliance
- API 6D pipeline valve requirements
- Comprehensive material selection guidance

## ⚠️ Important Validation Requirements

**For Critical Applications:**

1. **Standards Verification**: Validate all calculations against official ISA/IEC/API standards
2. **Manufacturer Cross-Check**: Compare results with vendor-specific sizing software
3. **Professional Review**: Have calculations reviewed by licensed Professional Engineer
4. **Field Validation**: Verify material selections against actual service conditions

## 📊 Calculation Methods

### Liquid Sizing (ISA 75.01)
- Basic equation: `Cv = Q / (N1 * Fp * √(ΔP/SG))`
- Reynolds correction: `Cv_final = Cv_basic / Fr`
- Choked flow: `ΔP_allowable = FL² * (P1 - Ff * Pv)`

### Gas Sizing (ISA 75.01)
- Unchoked: `Cv = Q / (N9 * Y * P1 * √(ΔP * ρ/ρ0))`
- Choked: `Cv = Q / (N6 * P1 * Y * √(ρ/ρ0))`
- Critical pressure ratio: `Pcrit/P1 = xT * (2/(k+1))^(k/(k-1))`

### Cavitation Analysis (ISA RP75.23)
- Service sigma: `σ = (P1 - Pv) / ΔP`
- Scaled sigma: `σ_scaled = (σ_ref * SSE - 1) * PSE + 1`
- Five levels: Incipient, Constant, Damage, Choking, Manufacturer

## 🛠️ Configuration

### Engineering Constants
Located in `config/constants.py`:
- ISA/IEC sizing constants (N1, N2, N4, N6, N7, N8, N9)
- Physical constants (gas constant, standard conditions)
- Unit conversion factors
- Standard pipe dimensions

### Application Settings  
Located in `config/settings.py`:
- Calculation tolerances and iteration limits
- Validation limits and safety margins
- Display formatting preferences

## 📈 Validation Features

### Input Validation
- Pressure ratio limits and reasonableness checks
- Temperature range validation for fluid phases
- Flow rate consistency verification
- Fluid property range checking

### Engineering Validation
- Valve authority calculations and warnings
- Operating range assessment (20-80% recommended)
- Reynolds number regime classification
- Cavitation risk assessment with mitigation advice

### Standards Compliance
- NACE MR0175 H2S partial pressure calculations
- ASME B16.34 pressure-temperature rating checks
- API 6D fire-safe and emission requirements
- Professional safety factor recommendations

## 🎓 Educational Use

This application is excellent for:
- Control valve engineering training
- University coursework in process control
- Professional development and certification prep
- Understanding industry standards implementation

## 📝 License and Disclaimer

**Professional Engineering Tool** - Educational and preliminary engineering use.

**Important:** This application provides professional-grade calculations but requires validation against official standards and manufacturer data for critical applications. Final valve selections must be verified by licensed professional engineers.

**Standards References:**
- ISA-75.01-2012: Flow equations for sizing control valves
- IEC 60534-2-1:2011: Industrial-process control valves
- ISA-RP75.23-1995: Considerations for evaluating control valve cavitation
- IEC 60534-8-3:2010: Control valve aerodynamic noise prediction

## 👨‍💻 Author

**Aseem Mehrotra**  
Senior Instrumentation Construction Engineer, KBR Inc  
Professional implementation of industry standards for control valve sizing

## 🔗 Support

For technical questions or feature requests:
- Create GitHub issues for bug reports
- Submit pull requests for improvements
- Contact for professional training or consulting

---

**Remember:** Always validate critical calculations against manufacturer software and official standards!
