# Professional Datasheet Generator Module
# Author: Aseem Mehrotra, Senior Instrumentation Construction Engineer, KBR Inc

import io
from datetime import datetime
from typing import Dict, Any, List, Optional
import base64
import pandas as pd

# Optional imports with fallbacks
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.chart import LineChart, BarChart, ScatterChart, Reference
    from openpyxl.drawing.image import Image as XLImage
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

class ProfessionalDatasheetGenerator:
    """Professional control valve datasheet generator with full integration"""
    
    def __init__(self):
        self.company_info = {
            'name': 'KBR Inc',
            'address': 'Engineering Excellence Center',
            'phone': '+1-XXX-XXX-XXXX',
            'email': 'engineering@kbr.com',
            'website': 'www.kbr.com'
        }
        
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom ReportLab styles"""
        if not REPORTLAB_AVAILABLE:
            return
        
        # Title style
        title_style = ParagraphStyle(
            'DatasheetTitle',
            parent=self.styles['Title'],
            fontSize=20,
            fontName='Helvetica-Bold',
            textColor=colors.darkblue,
            alignment=1,  # Center
            spaceAfter=20
        )
        self.styles.add(title_style)
        
        # Header style
        header_style = ParagraphStyle(
            'DatasheetHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=10,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=5
        )
        self.styles.add(header_style)
    
    def generate_complete_pdf_datasheet(self, 
                                      project_data: Dict[str, Any],
                                      process_data: Dict[str, Any],
                                      valve_selection: Dict[str, Any],
                                      sizing_results: Dict[str, Any],
                                      analysis_results: Dict[str, Any],
                                      include_charts: bool = True) -> bytes:
        """Generate complete professional PDF datasheet"""
        
        if not REPORTLAB_AVAILABLE:
            # Fallback to text generation
            return self.generate_comprehensive_text_datasheet(
                project_data, process_data, valve_selection, 
                sizing_results, analysis_results
            ).encode('utf-8')
        
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=25*mm,
                bottomMargin=25*mm
            )
            
            story = []
            
            # Title page
            story.extend(self._create_pdf_title_page(project_data))
            story.append(PageBreak())
            
            # Process conditions
            story.extend(self._create_pdf_process_section(process_data))
            
            # Valve specifications 
            story.extend(self._create_pdf_valve_specs_section(valve_selection, sizing_results))
            
            # Sizing calculations
            story.extend(self._create_pdf_sizing_section(sizing_results))
            
            # Analysis results
            if analysis_results:
                story.extend(self._create_pdf_analysis_section(analysis_results))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            # Fallback to text content
            return self.generate_comprehensive_text_datasheet(
                project_data, process_data, valve_selection, 
                sizing_results, analysis_results
            ).encode('utf-8')
    
    def _create_pdf_title_page(self, project_data: Dict[str, Any]) -> List:
        """Create professional PDF title page"""
        story = []
        
        # Company header
        story.append(Paragraph(f"**{self.company_info['name']}**", self.styles['Title']))
        story.append(Paragraph("CONTROL VALVE DATASHEET", self.styles['DatasheetTitle']))
        story.append(Spacer(1, 20*mm))
        
        # Project information table
        project_info = [
            ['Parameter', 'Value'],
            ['Project Name', project_data.get('project_name', 'Not Specified')],
            ['Valve Tag Number', project_data.get('tag_number', 'Not Specified')],
            ['Datasheet Number', project_data.get('datasheet_number', 'DS-001')],
            ['Revision', project_data.get('revision', 'A')],
            ['Date', datetime.now().strftime("%B %d, %Y")],
            ['Prepared By', project_data.get('engineer_name', 'Aseem Mehrotra, KBR Inc')],
            ['Client', project_data.get('client_name', 'TBD')]
        ]
        
        table = Table(project_info, colWidths=[60*mm, 100*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20*mm))
        
        return story
    
    def _create_pdf_process_section(self, process_data: Dict[str, Any]) -> List:
        """Create process conditions section"""
        story = []
        
        story.append(Paragraph("1. PROCESS CONDITIONS", self.styles['DatasheetHeader']))
        
        # Process data table
        process_table_data = [
            ['Parameter', 'Value', 'Units', 'Notes'],
            ['Fluid Type', process_data.get('fluid_name', 'Not Specified'), '-', ''],
            ['Operating Temperature', f"{process_data.get('temperature', 0):.1f}", '°C', ''],
            ['Inlet Pressure (P1)', f"{process_data.get('p1', 0):.1f}", 'bar abs', ''],
            ['Outlet Pressure (P2)', f"{process_data.get('p2', 0):.1f}", 'bar abs', ''],
            ['Normal Flow Rate', f"{process_data.get('normal_flow', 0):.1f}", 
             process_data.get('flow_units', 'm³/h'), 'Design basis'],
        ]
        
        table = Table(process_table_data, colWidths=[45*mm, 25*mm, 20*mm, 40*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 10*mm))
        
        return story
    
    def _create_pdf_valve_specs_section(self, valve_selection: Dict[str, Any], 
                                      sizing_results: Dict[str, Any]) -> List:
        """Create valve specifications section"""
        story = []
        
        story.append(Paragraph("2. VALVE SPECIFICATIONS", self.styles['DatasheetHeader']))
        
        valve_specs_data = [
            ['Parameter', 'Specification', 'Notes'],
            ['Valve Type', valve_selection.get('valve_type', 'TBD'), ''],
            ['Valve Style', valve_selection.get('valve_style', 'TBD'), ''],
            ['Nominal Size', valve_selection.get('valve_size', 'TBD'), 'NPS'],
            ['Flow Characteristic', valve_selection.get('flow_characteristic', 'TBD'), ''],
            ['Maximum Cv', f"{valve_selection.get('max_cv', 0):.1f}", 'At 100% opening'],
            ['Required Cv', f"{sizing_results.get('cv_required', 0):.2f}", 'At normal flow']
        ]
        
        table = Table(valve_specs_data, colWidths=[50*mm, 40*mm, 40*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 10*mm))
        
        return story
    
    def _create_pdf_sizing_section(self, sizing_results: Dict[str, Any]) -> List:
        """Create sizing calculations section"""
        story = []
        
        story.append(Paragraph("3. SIZING CALCULATIONS", self.styles['DatasheetHeader']))
        
        sizing_summary_data = [
            ['Parameter', 'Value', 'Units', 'Method/Standard'],
            ['Calculation Method', sizing_results.get('sizing_method', 'ISA 75.01'), '-', 'Industry Standard'],
            ['Required Cv', f"{sizing_results.get('cv_required', 0):.3f}", '-', 'ISA 75.01'],
        ]
        
        table = Table(sizing_summary_data, colWidths=[50*mm, 25*mm, 20*mm, 35*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 10*mm))
        
        return story
    
    def _create_pdf_analysis_section(self, analysis_results: Dict[str, Any]) -> List:
        """Create analysis results section"""
        story = []
        
        story.append(Paragraph("4. TECHNICAL ANALYSIS", self.styles['DatasheetHeader']))
        
        # Cavitation analysis
        if 'cavitation_analysis' in analysis_results:
            story.append(Paragraph("4.1 Cavitation Analysis (ISA RP75.23)", self.styles['Heading2']))
            
            cav_analysis = analysis_results['cavitation_analysis']
            cav_data = [
                ['Parameter', 'Value', 'Assessment'],
                ['Service Sigma (σ)', f"{cav_analysis.get('sigma_service', 0):.1f}", ''],
                ['Risk Level', cav_analysis.get('risk_level', 'Unknown'), '']
            ]
            
            cav_table = Table(cav_data, colWidths=[50*mm, 30*mm, 50*mm])
            cav_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(cav_table)
            story.append(Spacer(1, 5*mm))
        
        return story
    
    def generate_excel_datasheet(self, 
                                project_data: Dict[str, Any],
                                process_data: Dict[str, Any],
                                valve_selection: Dict[str, Any],
                                sizing_results: Dict[str, Any],
                                analysis_results: Dict[str, Any],
                                include_charts: bool = True) -> bytes:
        """Generate professional Excel datasheet"""
        
        if not OPENPYXL_AVAILABLE:
            # Fallback to CSV
            return self.generate_csv_summary(
                process_data, valve_selection, sizing_results, analysis_results
            ).encode('utf-8')
        
        try:
            # Create workbook
            wb = openpyxl.Workbook()
            
            # Remove default sheet
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
            
            # Create worksheets
            self._create_excel_summary_sheet(wb, project_data, sizing_results)
            self._create_excel_process_sheet(wb, process_data)
            self._create_excel_valve_specs_sheet(wb, valve_selection, sizing_results)
            
            # Save to buffer
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            return self.generate_csv_summary(
                process_data, valve_selection, sizing_results, analysis_results
            ).encode('utf-8')
    
    def _create_excel_summary_sheet(self, wb, project_data: Dict[str, Any], sizing_results: Dict[str, Any]):
        """Create Excel summary sheet"""
        ws = wb.create_sheet("Executive Summary")
        
        # Header
        ws['A1'] = "CONTROL VALVE DATASHEET - EXECUTIVE SUMMARY"
        ws['A1'].font = Font(size=16, bold=True, color="1F4E79")
        ws.merge_cells('A1:E1')
        
        # Project info
        project_info = [
            ["Project:", project_data.get('project_name', 'TBD')],
            ["Tag Number:", project_data.get('tag_number', 'TBD')],
            ["Date:", datetime.now().strftime("%Y-%m-%d")],
            ["Engineer:", project_data.get('engineer_name', 'Aseem Mehrotra, KBR Inc')]
        ]
        
        for i, (label, value) in enumerate(project_info, 3):
            ws[f'A{i}'] = label
            ws[f'A{i}'].font = Font(bold=True)
            ws[f'B{i}'] = value
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 30
    
    def _create_excel_process_sheet(self, wb, process_data: Dict[str, Any]):
        """Create Excel process conditions sheet"""
        ws = wb.create_sheet("Process Conditions")
        
        # Headers
        headers = ['Parameter', 'Value', 'Units', 'Notes']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Process data
        process_table_data = [
            ('Fluid Type', process_data.get('fluid_name', 'TBD'), '-', ''),
            ('Temperature', f"{process_data.get('temperature', 0):.1f}", '°C', ''),
            ('Inlet Pressure', f"{process_data.get('p1', 0):.1f}", 'bar', ''),
            ('Outlet Pressure', f"{process_data.get('p2', 0):.1f}", 'bar', ''),
            ('Normal Flow', f"{process_data.get('normal_flow', 0):.1f}", process_data.get('flow_units', 'm³/h'), ''),
        ]
        
        for row, (param, value, unit, note) in enumerate(process_table_data, 2):
            ws.cell(row=row, column=1, value=param)
            ws.cell(row=row, column=2, value=value)
            ws.cell(row=row, column=3, value=unit)
            ws.cell(row=row, column=4, value=note)
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 20
    
    def _create_excel_valve_specs_sheet(self, wb, valve_selection: Dict[str, Any], sizing_results: Dict[str, Any]):
        """Create Excel valve specifications sheet"""
        ws = wb.create_sheet("Valve Specifications")
        
        # Headers
        headers = ['Parameter', 'Specification', 'Notes']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2E5D85", end_color="2E5D85", fill_type="solid")
        
        # Valve specifications
        valve_specs = [
            ('Valve Type', valve_selection.get('valve_type', 'TBD'), ''),
            ('Valve Style', valve_selection.get('valve_style', 'TBD'), ''),
            ('Nominal Size', valve_selection.get('valve_size', 'TBD'), 'NPS'),
            ('Flow Characteristic', valve_selection.get('flow_characteristic', 'TBD'), ''),
            ('Maximum Cv', f"{valve_selection.get('max_cv', 0):.1f}", 'At 100% opening'),
            ('Required Cv', f"{sizing_results.get('cv_required', 0):.2f}", 'At normal flow'),
        ]
        
        for row, (param, spec, note) in enumerate(valve_specs, 2):
            ws.cell(row=row, column=1, value=param)
            ws.cell(row=row, column=2, value=spec)
            ws.cell(row=row, column=3, value=note)
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 25
    
    def generate_comprehensive_text_datasheet(self, project_data, process_data, valve_selection, 
                                            sizing_results, analysis_results):
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
    
    def generate_csv_summary(self, process_data, valve_selection, sizing_results, analysis_results):
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
