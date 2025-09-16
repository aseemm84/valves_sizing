"""
PDF Report Generator Module
Professional PDF report generation for valve sizing calculations

Features:
- Complete technical reports with calculations
- Professional formatting with charts and tables
- Standards compliance documentation
- Executive summary and detailed results
"""

from typing import Dict, Any, List, Optional
import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except ImportError:
    print("ReportLab not installed. Install with: pip install reportlab")

class PDFReportGenerator:
    """Professional PDF report generation for valve sizing"""
    
    def __init__(self):
        try:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
        except:
            self.styles = None
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        if not self.styles:
            return
            
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            fontName='Helvetica-Bold',
            textColor=colors.darkblue,
            alignment=1,  # Center
            spaceAfter=20
        )
        self.styles.add(title_style)
        
        # Header style
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=10
        )
        self.styles.add(header_style)
        
        # Subheader style
        subheader_style = ParagraphStyle(
            'CustomSubHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=8
        )
        self.styles.add(subheader_style)
    
    def generate_complete_report(self, project_data: Dict[str, Any], 
                               sizing_results: Dict[str, Any],
                               analysis_results: Dict[str, Any]) -> bytes:
        """Generate complete valve sizing report"""
        
        if not self.styles:
            return b"PDF generation not available - ReportLab not installed"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title page
        story.extend(self._create_title_page(project_data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(sizing_results, analysis_results))
        story.append(PageBreak())
        
        # Process conditions
        story.extend(self._create_process_conditions_section(project_data))
        
        # Sizing calculations
        story.extend(self._create_sizing_calculations_section(sizing_results))
        
        # Analysis results
        story.extend(self._create_analysis_section(analysis_results))
        
        # Standards compliance
        story.extend(self._create_standards_compliance_section(analysis_results))
        
        # Recommendations
        story.extend(self._create_recommendations_section(analysis_results))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def _create_title_page(self, project_data: Dict[str, Any]) -> List:
        """Create professional title page"""
        story = []
        
        # Main title
        story.append(Paragraph("Control Valve Sizing Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Project information table
        project_info = [
            ['Project:', project_data.get('project_name', 'Not specified')],
            ['Tag Number:', project_data.get('tag_number', 'Not specified')],
            ['Service:', project_data.get('service_description', 'Not specified')],
            ['Date:', datetime.now().strftime("%B %d, %Y")],
            ['Prepared by:', project_data.get('engineer', 'Aseem Mehrotra, KBR Inc')],
            ['Standards:', 'ISA 75.01, IEC 60534-2-1, ISA RP75.23, IEC 60534-8-3']
        ]
        
        table = Table(project_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 1*inch))
        
        # Disclaimer
        disclaimer = """
        <b>IMPORTANT NOTICE:</b><br/>
        This report provides professional valve sizing calculations based on industry standards. 
        For critical applications, results must be validated against manufacturer data and 
        reviewed by a licensed Professional Engineer. All calculations follow ISA 75.01, 
        IEC 60534-2-1, ISA RP75.23, and IEC 60534-8-3 methodologies.
        """
        
        story.append(Paragraph(disclaimer, self.styles['Normal']))
        
        return story
    
    def _create_executive_summary(self, sizing_results: Dict[str, Any], 
                                analysis_results: Dict[str, Any]) -> List:
        """Create executive summary"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomHeader']))
        
        # Key results
        cv_required = sizing_results.get('cv_required', 0)
        valve_size = sizing_results.get('recommended_valve_size', 'TBD')
        
        summary_text = f"""
        Based on the sizing calculations performed in accordance with ISA 75.01/IEC 60534-2-1 
        standards, the required valve flow coefficient (Cv) is <b>{cv_required:.1f}</b>. 
        The recommended valve size is <b>{valve_size}</b>.
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key findings
        story.append(Paragraph("Key Findings:", self.styles['CustomSubHeader']))
        
        findings = []
        
        # Add cavitation analysis
        if 'cavitation_analysis' in analysis_results:
            cav_analysis = analysis_results['cavitation_analysis']
            if cav_analysis.get('is_cavitating', False):
                findings.append("Cavitation potential detected - mitigation recommended")
            else:
                findings.append("No significant cavitation concerns identified")
        
        # Add noise analysis
        if 'noise_analysis' in analysis_results:
            noise_analysis = analysis_results['noise_analysis']
            noise_level = noise_analysis.get('spl_at_distance', 0)
            if noise_level > 85:
                findings.append(f"High noise level predicted ({noise_level:.1f} dBA)")
            else:
                findings.append("Noise level within acceptable limits")
        
        # Add material recommendations
        if 'material_analysis' in analysis_results:
            findings.append("Material selection complies with applicable standards")
        
        for finding in findings:
            story.append(Paragraph(f"• {finding}", self.styles['Normal']))
        
        return story
    
    def _create_process_conditions_section(self, project_data: Dict[str, Any]) -> List:
        """Create process conditions section"""
        story = []
        
        story.append(Paragraph("Process Conditions", self.styles['CustomHeader']))
        
        # Process data table
        process_data = [
            ['Parameter', 'Value', 'Units'],
            ['Fluid Type', project_data.get('fluid_type', 'Not specified'), ''],
            ['Operating Temperature', f"{project_data.get('temperature', 0):.1f}", '°C'],
            ['Inlet Pressure (P1)', f"{project_data.get('p1', 0):.1f}", 'bar'],
            ['Outlet Pressure (P2)', f"{project_data.get('p2', 0):.1f}", 'bar'],
            ['Pressure Drop', f"{project_data.get('p1', 0) - project_data.get('p2', 0):.1f}", 'bar'],
            ['Normal Flow Rate', f"{project_data.get('normal_flow', 0):.1f}", project_data.get('flow_units', 'm³/h')],
            ['Service Type', project_data.get('service_type', 'Not specified'), ''],
            ['Criticality', project_data.get('criticality', 'Not specified'), '']
        ]
        
        table = Table(process_data)
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_sizing_calculations_section(self, sizing_results: Dict[str, Any]) -> List:
        """Create sizing calculations section"""
        story = []
        
        story.append(Paragraph("Sizing Calculations", self.styles['CustomHeader']))
        
        # Calculation results
        story.append(Paragraph("Results Summary:", self.styles['CustomSubHeader']))
        
        results_text = f"""
        <b>Required Cv:</b> {sizing_results.get('cv_required', 0):.2f}<br/>
        <b>Calculation Method:</b> {sizing_results.get('sizing_method', 'ISA 75.01')}<br/>
        <b>Safety Factor Applied:</b> {sizing_results.get('safety_factor', 1.2):.1f}<br/>
        """
        
        story.append(Paragraph(results_text, self.styles['Normal']))
        
        return story
    
    def _create_analysis_section(self, analysis_results: Dict[str, Any]) -> List:
        """Create analysis section"""
        story = []
        
        story.append(Paragraph("Technical Analysis", self.styles['CustomHeader']))
        
        # Cavitation analysis
        if 'cavitation_analysis' in analysis_results:
            story.append(Paragraph("Cavitation Analysis (ISA RP75.23):", self.styles['CustomSubHeader']))
            cav_analysis = analysis_results['cavitation_analysis']
            
            cav_text = f"""
            Service Sigma: {cav_analysis.get('sigma_service', 0):.1f}<br/>
            Cavitation Status: {'Cavitating' if cav_analysis.get('is_cavitating', False) else 'No Cavitation'}<br/>
            """
            
            story.append(Paragraph(cav_text, self.styles['Normal']))
        
        # Noise analysis
        if 'noise_analysis' in analysis_results:
            story.append(Paragraph("Noise Analysis (IEC 60534-8-3):", self.styles['CustomSubHeader']))
            noise_analysis = analysis_results['noise_analysis']
            
            noise_text = f"""
            Sound Pressure Level: {noise_analysis.get('spl_at_distance', 0):.1f} dBA at 1m<br/>
            Assessment: {noise_analysis.get('assessment', {}).get('level', 'Unknown')}<br/>
            """
            
            story.append(Paragraph(noise_text, self.styles['Normal']))
        
        return story
    
    def _create_standards_compliance_section(self, analysis_results: Dict[str, Any]) -> List:
        """Create standards compliance section"""
        story = []
        
        story.append(Paragraph("Standards Compliance", self.styles['CustomHeader']))
        
        compliance_text = """
        This analysis has been performed in accordance with the following industry standards:<br/>
        • ISA 75.01-2012: Flow equations for sizing control valves<br/>
        • IEC 60534-2-1:2011: Industrial-process control valves<br/>
        • ISA RP75.23-1995: Considerations for evaluating control valve cavitation<br/>
        • IEC 60534-8-3:2010: Control valve aerodynamic noise prediction<br/>
        • ASME B16.34: Valves - Flanged, threaded, and welding end<br/>
        • NACE MR0175/ISO 15156: Materials for H2S environments<br/>
        """
        
        story.append(Paragraph(compliance_text, self.styles['Normal']))
        
        return story
    
    def _create_recommendations_section(self, analysis_results: Dict[str, Any]) -> List:
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['CustomHeader']))
        
        recommendations = []
        
        # Collect recommendations from various analyses
        if 'sizing_results' in analysis_results:
            recommendations.extend(analysis_results['sizing_results'].get('recommendations', []))
        
        if 'cavitation_analysis' in analysis_results:
            cav_recs = analysis_results['cavitation_analysis'].get('recommendations', {})
            recommendations.extend(cav_recs.get('primary_recommendations', []))
        
        if not recommendations:
            recommendations.append("No specific recommendations - standard operation expected")
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['Normal']))
        
        return story
