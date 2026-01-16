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
    
    def _escape_html(self, text: str) -> str:
        """Escape special characters for HTML/XML in PDF paragraphs and convert markdown bold"""
        import re
        text = str(text)
        # Convert markdown bold (**text**) to HTML bold (<b>text</b>)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Escape special characters
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # But allow our bold tags through
        text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        return text
    
    def _create_cell_style(self, font_size: int = 9, leading: int = 11) -> ParagraphStyle:
        """Create a reusable cell style for table cells"""
        return ParagraphStyle(
            f'TableCell_{font_size}',
            parent=self.styles['BodyText'],
            fontSize=font_size,
            leading=leading,
            alignment=TA_LEFT,
            wordWrap='CJK'
        )
    
    def _create_cell_para(self, text: str, style: ParagraphStyle) -> Paragraph:
        """Create a paragraph for table cell with escaped text"""
        return Paragraph(self._escape_html(text), style)
        
    def export(
        self,
        syllabus_data: Dict[str, Any],
        output_path: str,
        include_mapping: bool = True,
        analysis_data: Optional[Dict[str, Any]] = None  # Added parameter
    ) -> bool:
        """
        Export syllabus to PDF
        
        Args:
            syllabus_data: Syllabus structure
            output_path: Output PDF file path
            include_mapping: Include CO-PO mapping
            analysis_data: Optional analysis results to include
            
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
            
            # --- NEW: Analysis Report Section ---
            if analysis_data:
                story.extend(self._create_analysis_section(analysis_data))
                story.append(PageBreak())  # Start syllabus on new page
            
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
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _create_analysis_section(self, analysis: Dict[str, Any]) -> list:
        """Create analysis report section"""
        elements = []
        
        # Section Title
        elements.append(Paragraph("Syllabus Analysis Report", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 1. Quality Score
        quality = analysis.get('content_quality', {})
        if quality:
            score = quality.get('quality_score', {}).get('total_score', 0)
            grade = quality.get('quality_score', {}).get('grade', 'N/A')
            status = quality.get('quality_score', {}).get('status', 'N/A')
            
            # Create a visual score box
            score_text = f"Quality Score: {score}/100 ({grade})"
            status_text = f"Status: {status}"
            
            elements.append(Paragraph(score_text, ParagraphStyle(
                'ScoreHeader', parent=self.styles['Heading2'], fontSize=16, textColor=colors.HexColor('#2980b9')
            )))
            elements.append(Paragraph(status_text, self.styles['BodyText']))
            elements.append(Spacer(1, 0.2*inch))

        # 2. Bloom's Taxonomy Coverage
        bloom = analysis.get('bloom_coverage', {})
        if bloom and bloom.get('percentages'):
            elements.append(Paragraph("Bloom's Taxonomy Distribution", self.styles['SectionHeading']))
            
            # Create table for Bloom's distribution
            table_data = [['Bloom\'s Level', 'Coverage (%)', 'Target Range']]
            
            # Define target ranges (approximate standard)
            targets = {
                'remember': '10-20%',
                'understand': '20-30%',
                'apply': '25-35%',
                'analyze': '15-25%',
                'evaluate': '5-15%',
                'create': '5-10%'
            }
            
            for level, pct in bloom.get('percentages', {}).items():
                level_name = level.replace('_', ' ').capitalize()
                row = [
                    level_name,
                    f"{pct:.1f}%",
                    targets.get(level.lower(), 'N/A')
                ]
                table_data.append(row)
                
            table = Table(table_data, colWidths=[2.5*inch, 2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
            
        # 3. Validation Issues / Gaps
        validation = analysis.get('validation_issues', {})
        if validation:
            elements.append(Paragraph("Identified Gaps & Issues", self.styles['SectionHeading']))
            
            issues_found = False
            
            # Missing Sections
            missing = validation.get('missing_sections', [])
            if missing:
                issues_found = True
                elements.append(Paragraph("Missing Sections:", self.styles['SubsectionHeading']))
                for item in missing:
                    elements.append(Paragraph(f"• {item.replace('_', ' ').title()}", self.styles['BodyText']))
            
            # Content Gaps
            gaps = analysis.get('gaps', [])
            if gaps:
                issues_found = True
                elements.append(Paragraph("Content Gaps:", self.styles['SubsectionHeading']))
                for gap in gaps:
                     # Handle gap as string or dict
                    gap_desc = gap.get('description', '') if isinstance(gap, dict) else str(gap)
                    elements.append(Paragraph(f"• {self._escape_html(gap_desc)}", self.styles['BodyText']))
            
            if not issues_found:
                elements.append(Paragraph("No critical gaps identified.", self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.2*inch))

        # 4. Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("Recommendations", self.styles['SectionHeading']))
            for rec in recommendations:
                 # API might return list of strings or dicts
                rec_text = rec.get('action', '') if isinstance(rec, dict) else str(rec)
                elements.append(Paragraph(f"• {self._escape_html(rec_text)}", self.styles['BodyText']))
            elements.append(Spacer(1, 0.3*inch))
            
        return elements
            
    def _create_header(self, data: Dict[str, Any]) -> list:
        """Create PDF header with institution details"""
        elements = []
        
        # Institution header
        if data.get('university_name'):
            elements.append(Paragraph(
                self._escape_html(data['university_name']),
                ParagraphStyle('UniName', parent=self.styles['Normal'], 
                    fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER)
            ))
            
        if data.get('faculty_name'):
            elements.append(Paragraph(
                self._escape_html(data['faculty_name']),
                ParagraphStyle('FacName', parent=self.styles['Normal'],
                    fontSize=11, alignment=TA_CENTER)
            ))
            
        if data.get('program') or data.get('department'):
            program_text = data.get('program') or data.get('department', '')
            elements.append(Paragraph(
                self._escape_html(program_text),
                ParagraphStyle('ProgName', parent=self.styles['Normal'],
                    fontSize=10, alignment=TA_CENTER)
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Course Title
        course_code = data.get('course_code', '')
        course_title = data.get('course_title', 'Course Syllabus')
        title_text = f"{course_code}: {course_title}" if course_code else course_title
        elements.append(Paragraph(title_text, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Course details table - academic format
        cell_style = ParagraphStyle(
            'HeaderCell',
            parent=self.styles['BodyText'],
            fontSize=10
        )
        
        # Teaching scheme and credits in table format
        details = []
        
        # Course Type and Semester
        if data.get('course_type') or data.get('semester'):
            course_type = data.get('course_type', 'DSC')
            semester = data.get('semester', 'I')
            details.append([
                Paragraph(f'<b>Course Type:</b> {course_type}', cell_style),
                Paragraph(f'<b>Semester:</b> {semester}', cell_style)
            ])
        
        # Credits (L-T-P format)
        credits = data.get('credits', '3-0-0')
        year = data.get('year', '')
        details.append([
            Paragraph(f'<b>Credits (L-T-P):</b> {credits}', cell_style),
            Paragraph(f'<b>Academic Year:</b> {year}', cell_style) if year else Paragraph('', cell_style)
        ])
        
        if details:
            table = Table(details, colWidths=[3.2*inch, 3.2*inch])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _create_overview(self, data: Dict[str, Any]) -> list:
        """Create course overview section"""
        elements = []
        
        elements.append(Paragraph("Course Overview", self.styles['SectionHeading']))
        overview_text = self._escape_html(data.get('overview', ''))
        elements.append(Paragraph(overview_text, self.styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
        
    def _create_objectives(self, data: Dict[str, Any]) -> list:
        """Create objectives section"""
        elements = []
        
        elements.append(Paragraph("Course Objectives", self.styles['SectionHeading']))
        
        objectives = data.get('objectives', [])
        for i, obj in enumerate(objectives, 1):
            text = f"{i}. {self._escape_html(obj)}"
            elements.append(Paragraph(text, self.styles['BodyText']))
            elements.append(Spacer(1, 0.05*inch))
            
        elements.append(Spacer(1, 0.15*inch))
        return elements
        
    def _create_outcomes(self, data: Dict[str, Any]) -> list:
        """Create learning outcomes section"""
        elements = []
        
        elements.append(Paragraph("Course Learning Outcomes", self.styles['SectionHeading']))
        
        outcomes = data.get('learning_outcomes', [])
        
        # Create table with wrapped text
        table_data = [['CO', 'Description', "Bloom's Level"]]
        
        # Create cell style
        cell_style = self._create_cell_style(font_size=8, leading=10)
        
        for outcome in outcomes:
            co_code = outcome.get('code', '')
            description = outcome.get('description', '')
            bloom = outcome.get('bloom_level', '').capitalize()
            
            # Create paragraphs for all cells
            co_para = self._create_cell_para(co_code, cell_style)
            desc_para = self._create_cell_para(description, cell_style)
            bloom_para = self._create_cell_para(bloom, cell_style)
            
            table_data.append([co_para, desc_para, bloom_para])
        
        # More conservative widths: 0.5 + 4.3 + 1.0 = 5.8 inches (well within 6.77" available)
        table = Table(table_data, colWidths=[0.5*inch, 4.3*inch, 1.0*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # CO code centered
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),     # Description left
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),   # Bloom centered
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _create_units(self, data: Dict[str, Any]) -> list:
        """Create units section in academic format"""
        elements = []
        
        elements.append(Paragraph("Course Content", self.styles['SectionHeading']))
        
        units = data.get('units', [])
        cell_style = self._create_cell_style(font_size=9, leading=11)
        
        for unit in units:
            unit_num = unit.get('unit_number', '')
            title = unit.get('title', 'Untitled')
            hours = unit.get('hours', 0)
            
            # Unit header row
            unit_header = f"<b>Unit {unit_num}: {title}</b>"
            hours_text = f"<b>{hours} Hours</b>"
            
            header_table = Table([
                [Paragraph(unit_header, cell_style), Paragraph(hours_text, cell_style)]
            ], colWidths=[5.5*inch, 1*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f4f8')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(header_table)
            
            # Topics
            topics = unit.get('topics', [])
            if topics:
                for topic in topics:
                    # Handle both dict and string topics
                    if isinstance(topic, dict):
                        topic_name = topic.get('topic', str(topic))
                        topic_desc = topic.get('description', '')
                        subtopics = topic.get('subtopics', [])
                        key_concepts = topic.get('key_concepts', [])
                        
                        # Topic name as bold
                        elements.append(Paragraph(f"<b>{self._escape_html(topic_name)}</b>", self.styles['BodyText']))
                        
                        # Description if present
                        if topic_desc:
                            elements.append(Paragraph(self._escape_html(topic_desc), self.styles['BodyText']))
                        
                        # Subtopics as bullets
                        if subtopics:
                            for st in subtopics:
                                elements.append(Paragraph(f"  • {self._escape_html(str(st))}", self.styles['BodyText']))
                        
                        # Key concepts inline
                        if key_concepts:
                            concepts = ", ".join([self._escape_html(str(c)) for c in key_concepts])
                            elements.append(Paragraph(f"<i>Key Concepts: {concepts}</i>", self.styles['BodyText']))
                        
                        elements.append(Spacer(1, 0.05*inch))
                    else:
                        # Simple string topic
                        elements.append(Paragraph(f"• {self._escape_html(str(topic))}", self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.15*inch))
        
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
                elements.append(Paragraph(f"• {self._escape_html(method)}", self.styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
            
        # Learning activities
        if methodology.get('learning_activities'):
            elements.append(Paragraph("Learning Activities:", self.styles['SubsectionHeading']))
            for activity in methodology['learning_activities']:
                elements.append(Paragraph(f"• {self._escape_html(activity)}", self.styles['BodyText']))
                
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
        
        # Calculate adaptive column width to fit page
        # Available width: A4 (8.27") - margins (1.5") = 6.77 inches
        num_cols = len(all_pos) + 1
        available_width = 6.7*inch
        col_width = available_width / num_cols
        
        # But don't make columns too narrow
        if col_width < 0.35*inch:
            col_width = 0.35*inch
        
        table = Table(table_data, colWidths=[col_width] * num_cols)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7 if num_cols > 12 else 9),  # Smaller font for many cols
            ('FONTSIZE', (0, 1), (-1, -1), 7 if num_cols > 12 else 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
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
                    elements.append(Paragraph(f"• {self._escape_html(ref)}", self.styles['BodyText']))
                    
            if references.get('references'):
                elements.append(Paragraph("Reference Books:", self.styles['SubsectionHeading']))
                for ref in references['references']:
                    elements.append(Paragraph(f"• {self._escape_html(ref)}", self.styles['BodyText']))
        else:
            # Simple list
            for i, ref in enumerate(references, 1):
                elements.append(Paragraph(f"{i}. {self._escape_html(ref)}", self.styles['BodyText']))
                
        return elements
