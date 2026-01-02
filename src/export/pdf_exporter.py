"""
PDF Exporter for SCDO
Exports syllabi to PDF format
"""

from typing import Dict, Any, Optional
import logging
from pathlib import Path
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
except ImportError:
    logging.warning("reportlab not installed. Install with: pip install reportlab")


class PDFExporter:
    """Export syllabus to PDF format"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Set up custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
    def export(
        self,
        syllabus_data: Dict[str, Any],
        output_path: str,
        include_mapping: bool = True
    ) -> bool:
        """
        Export syllabus to PDF
        
        Args:
            syllabus_data: Syllabus structure
            output_path: Output PDF file path
            include_mapping: Include CO-PO mapping
            
        Returns:
            True if successful
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=0.75*inch
            )
            
            # Build content
            story = []
            
            # Header
            story.extend(self._create_header(syllabus_data))
            
            # Course overview
            if syllabus_data.get('overview'):
                story.extend(self._create_overview(syllabus_data))
                
            # Objectives
            if syllabus_data.get('objectives'):
                story.extend(self._create_objectives(syllabus_data))
                
            # Learning outcomes
            if syllabus_data.get('learning_outcomes'):
                story.extend(self._create_outcomes(syllabus_data))
                
            # Units
            if syllabus_data.get('units'):
                story.extend(self._create_units(syllabus_data))
                
            # Teaching methodology
            if syllabus_data.get('teaching_methodology'):
                story.extend(self._create_methodology(syllabus_data))
                
            # Assessment
            if syllabus_data.get('assessment_pattern'):
                story.extend(self._create_assessment(syllabus_data))
                
            # CO-PO Mapping
            if include_mapping and syllabus_data.get('co_po_mapping'):
                story.extend(self._create_mapping(syllabus_data))
                
            # References
            if syllabus_data.get('references'):
                story.extend(self._create_references(syllabus_data))
                
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF exported successfully to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"PDF export failed: {e}")
            return False
            
    def _create_header(self, data: Dict[str, Any]) -> list:
        """Create PDF header"""
        elements = []
        
        # Title
        title = data.get('course_title', 'Course Syllabus')
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Course details table
        details = [
            ['Course Code:', data.get('course_code', 'N/A')],
            ['Credits (L-T-P):', data.get('credits', '0-0-0')],
        ]
        
        if data.get('prerequisites'):
            prereqs = ', '.join(data['prerequisites'])
            details.append(['Prerequisites:', prereqs])
            
        table = Table(details, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _create_overview(self, data: Dict[str, Any]) -> list:
        """Create course overview section"""
        elements = []
        
        elements.append(Paragraph("Course Overview", self.styles['SectionHeading']))
        overview_text = data.get('overview', '')
        elements.append(Paragraph(overview_text, self.styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
        
    def _create_objectives(self, data: Dict[str, Any]) -> list:
        """Create objectives section"""
        elements = []
        
        elements.append(Paragraph("Course Objectives", self.styles['SectionHeading']))
        
        objectives = data.get('objectives', [])
        for i, obj in enumerate(objectives, 1):
            text = f"{i}. {obj}"
            elements.append(Paragraph(text, self.styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
            
        elements.append(Spacer(1, 0.2*inch))
        return elements
        
    def _create_outcomes(self, data: Dict[str, Any]) -> list:
        """Create learning outcomes section"""
        elements = []
        
        elements.append(Paragraph("Course Learning Outcomes", self.styles['SectionHeading']))
        
        outcomes = data.get('learning_outcomes', [])
        
        # Create table
        table_data = [['CO', 'Description', 'Bloom\'s Level']]
        
        for outcome in outcomes:
            co_code = outcome.get('code', '')
            description = outcome.get('description', '')
            bloom = outcome.get('bloom_level', '').capitalize()
            
            table_data.append([co_code, description, bloom])
            
        table = Table(table_data, colWidths=[0.7*inch, 4*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _create_units(self, data: Dict[str, Any]) -> list:
        """Create units section"""
        elements = []
        
        elements.append(Paragraph("Unit-wise Syllabus", self.styles['SectionHeading']))
        
        units = data.get('units', [])
        for unit in units:
            unit_num = unit.get('unit_number', '')
            title = unit.get('title', 'Untitled')
            hours = unit.get('hours', 0)
            
            # Unit header
            unit_header = f"Unit {unit_num}: {title} ({hours} hours)"
            elements.append(Paragraph(unit_header, self.styles['SubsectionHeading']))
            
            # Topics
            topics = unit.get('topics', [])
            for topic in topics:
                elements.append(Paragraph(f"• {topic}", self.styles['BodyText']))
                
            elements.append(Spacer(1, 0.2*inch))
            
        return elements
        
    def _create_methodology(self, data: Dict[str, Any]) -> list:
        """Create teaching methodology section"""
        elements = []
        
        elements.append(Paragraph("Teaching-Learning Methodology", self.styles['SectionHeading']))
        
        methodology = data.get('teaching_methodology', {})
        
        # Teaching methods
        if methodology.get('teaching_methods'):
            elements.append(Paragraph("Teaching Methods:", self.styles['SubsectionHeading']))
            for method in methodology['teaching_methods']:
                elements.append(Paragraph(f"• {method}", self.styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
            
        # Learning activities
        if methodology.get('learning_activities'):
            elements.append(Paragraph("Learning Activities:", self.styles['SubsectionHeading']))
            for activity in methodology['learning_activities']:
                elements.append(Paragraph(f"• {activity}", self.styles['BodyText']))
                
        elements.append(Spacer(1, 0.2*inch))
        return elements
        
    def _create_assessment(self, data: Dict[str, Any]) -> list:
        """Create assessment section"""
        elements = []
        
        elements.append(Paragraph("Assessment Pattern", self.styles['SectionHeading']))
        
        assessment = data.get('assessment_pattern', {})
        
        # Create assessment table
        table_data = [['Component', 'Weightage (%)']]
        
        for component, value in assessment.items():
            if isinstance(value, dict):
                # Nested structure
                table_data.append([component.replace('_', ' ').title(), value.get('weightage', '')])
            else:
                table_data.append([component.replace('_', ' ').title(), str(value)])
                
        table = Table(table_data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _create_mapping(self, data: Dict[str, Any]) -> list:
        """Create CO-PO mapping section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("CO-PO Mapping Matrix", self.styles['SectionHeading']))
        
        mapping = data.get('co_po_mapping', {})
        
        # Get all POs
        all_pos = set()
        for po_dict in mapping.values():
            all_pos.update(po_dict.keys())
        all_pos = sorted(all_pos)
        
        # Create table
        table_data = [['CO'] + all_pos]
        
        for co in sorted(mapping.keys()):
            row = [co]
            for po in all_pos:
                value = mapping[co].get(po, 0)
                row.append(str(value) if value > 0 else '-')
            table_data.append(row)
            
        col_width = 0.5*inch
        table = Table(table_data, colWidths=[col_width] * (len(all_pos) + 1))
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Legend
        legend_text = "Correlation Levels: 1 = Low, 2 = Medium, 3 = High"
        elements.append(Paragraph(legend_text, self.styles['BodyText']))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _create_references(self, data: Dict[str, Any]) -> list:
        """Create references section"""
        elements = []
        
        elements.append(Paragraph("References", self.styles['SectionHeading']))
        
        references = data.get('references', [])
        
        if isinstance(references, dict):
            # Structured references
            if references.get('textbooks'):
                elements.append(Paragraph("Textbooks:", self.styles['SubsectionHeading']))
                for ref in references['textbooks']:
                    elements.append(Paragraph(f"• {ref}", self.styles['BodyText']))
                    
            if references.get('references'):
                elements.append(Paragraph("Reference Books:", self.styles['SubsectionHeading']))
                for ref in references['references']:
                    elements.append(Paragraph(f"• {ref}", self.styles['BodyText']))
        else:
            # Simple list
            for i, ref in enumerate(references, 1):
                elements.append(Paragraph(f"{i}. {ref}", self.styles['BodyText']))
                
        return elements
