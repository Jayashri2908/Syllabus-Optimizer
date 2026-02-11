"""
PDF Exporter for SCDO
Exports syllabi to PDF format
"""

from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
    from reportlab.platypus import Image
except ImportError:
    logging.warning("reportlab or dependencies not installed. Install with: pip install reportlab matplotlib")

import matplotlib.pyplot as plt
import io
import os
import tempfile


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
        
        # Bullet point style with indentation
        self.styles.add(ParagraphStyle(
            name='BulletItem',
            parent=self.styles['BodyText'],
            fontSize=10,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=4,
            leading=14
        ))
        
        # Numbered list style
        self.styles.add(ParagraphStyle(
            name='NumberedItem',
            parent=self.styles['BodyText'],
            fontSize=10,
            leftIndent=25,
            bulletIndent=0,
            spaceAfter=6,
            leading=14
        ))
        
        # Info box / highlight style
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['BodyText'],
            fontSize=10,
            backColor=colors.HexColor('#e8f4f8'),
            borderColor=colors.HexColor('#3498db'),
            borderWidth=1,
            borderPadding=8,
            spaceAfter=10,
            spaceBefore=6,
            leading=14
        ))
        
        # Report subtitle / date stamp
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Date stamp style
        self.styles.add(ParagraphStyle(
            name='DateStamp',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#95a5a6'),
            alignment=TA_RIGHT,
            spaceAfter=10
        ))
    
    def _escape_html(self, text: str) -> str:
        """Escape special characters for HTML/XML in PDF paragraphs and convert markdown bold"""
        import re
        text = str(text)
        
        # Clean up problematic Unicode characters first
        text = text.replace('■', '•')  # Black square to bullet
        text = text.replace('□', '○')  # White square to circle
        text = text.replace('▪', '•')  # Small black square to bullet
        text = text.replace('►', '→')  # Arrow replacement
        
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
    
    def _add_page_footer(self, canvas, doc):
        """Add page number and SCDO branding to each page"""
        canvas.saveState()
        
        # Page number at bottom center
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawCentredString(A4[0] / 2, 0.5 * inch, text)
        
        # SCDO branding at bottom right
        canvas.setFont('Helvetica-Oblique', 8)
        canvas.setFillColor(colors.HexColor('#95a5a6'))
        canvas.drawRightString(A4[0] - 0.75 * inch, 0.5 * inch, "Generated by SCDO")
        
        canvas.restoreState()
    
    def _create_horizontal_line(self, width=6.5, thickness=1, color='#bdc3c7'):
        """Create a horizontal line separator"""
        return HRFlowable(
            width=width * inch,
            thickness=thickness,
            color=colors.HexColor(color),
            spaceBefore=0.1 * inch,
            spaceAfter=0.15 * inch
        )

    def _generate_bloom_chart(self, distribution: Dict[str, float]) -> Optional[Image]:
        """Generate a bar chart for Bloom's distribution using matplotlib"""
        try:
            # Prepare data with safe type coercion
            levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
            values = []
            for level in levels:
                val = distribution.get(level.lower(), 0)
                try:
                    values.append(float(val) if val else 0.0)
                except (ValueError, TypeError):
                    values.append(0.0)
            
            # Skip if all zeros
            if sum(values) == 0:
                return None
            
            # Create plot
            fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
            colors_list = ['#3498db', '#2ecc71', '#f1c40f', '#e67e22', '#e74c3c', '#9b59b6']
            bars = ax.bar(levels, values, color=colors_list)
            
            ax.set_title("Bloom's Taxonomy Level Distribution (%)", fontsize=10, fontweight='bold')
            ax.set_ylabel("Percentage Coverage", fontsize=8)
            ax.tick_params(axis='x', labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom', fontsize=7)
            
            plt.tight_layout()
            
            # Save to buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            # Create ReportLab Image
            img = Image(buf, width=5*inch, height=2.5*inch)
            return img
        except Exception as e:
            self.logger.warning(f"Failed to generate Bloom chart: {e}")
            plt.close('all')  # Ensure no figure leak
            return None

    def _create_comparison_table(self, changes: List[Dict[str, str]]) -> list:
        """Create a table showing original vs optimized changes"""
        table_data = [['Aspect', 'Original', 'Optimized', 'Impact/Benefit']]
        cell_style = self._create_cell_style(font_size=8, leading=10)
        
        for change in changes:
            if isinstance(change, dict):
                # Safely convert all values to strings
                aspect = str(change.get('aspect', 'N/A') or 'N/A')
                original = str(change.get('original', 'N/A') or 'N/A')
                optimized = str(change.get('optimized', 'N/A') or 'N/A')
                impact = str(change.get('impact', 'N/A') or 'N/A')
                
                table_data.append([
                    Paragraph(f"<b>{self._escape_html(aspect)}</b>", cell_style),
                    Paragraph(self._escape_html(original), cell_style),
                    Paragraph(self._escape_html(optimized), cell_style),
                    Paragraph(self._escape_html(impact), cell_style)
                ])
        
        if len(table_data) <= 1:
            return []
            
        table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 2.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fa')),
        ]))
        
        return [table]
        
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
            
            # Merge analysis_data fields into syllabus_data if present
            # This ensures CO-PO mapping and other optimization results are available
            if analysis_data:
                if analysis_data.get('co_po_mapping') and not syllabus_data.get('co_po_mapping'):
                    syllabus_data['co_po_mapping'] = analysis_data['co_po_mapping']
                if analysis_data.get('bloom_analysis') and not syllabus_data.get('bloom_analysis'):
                    syllabus_data['bloom_analysis'] = analysis_data['bloom_analysis']
            
            # Check if this is an Optimize export (has analysis_data) with parsed syllabus
            # vs a Generate export (has full syllabus data)
            is_optimize_export = analysis_data is not None
            has_real_course_data = (
                syllabus_data.get('course_code', 'UNKNOWN') != 'UNKNOWN' and
                syllabus_data.get('course_title', 'Unknown Course') != 'Unknown Course'
            )
            
            # For Optimize exports, show optimization report (no header page with Teaching Scheme)
            if is_optimize_export:
                self.logger.info(f"Optimize export path: has_real_course_data={has_real_course_data}")
                self.logger.info(f"Analysis data keys: {list(analysis_data.keys()) if analysis_data else 'None'}")
                if analysis_data and analysis_data.get('ai_analysis'):
                    self.logger.info(f"AI analysis present: {len(analysis_data['ai_analysis'])} chars")
                
                # For Optimize exports, start directly with the analysis/optimization report
                # (No header page with Teaching Scheme - that's only for Generate exports)
                story.extend(self._create_analysis_section(analysis_data))
                
                # Only include syllabus content sections if successfully parsed
                if has_real_course_data:
                    if syllabus_data.get('learning_outcomes'):
                        story.append(PageBreak())
                        story.extend(self._create_outcomes(syllabus_data))
                    if syllabus_data.get('units'):
                        story.extend(self._create_units(syllabus_data))
                    if syllabus_data.get('co_po_mapping') or analysis_data.get('co_po_mapping'):
                        if not syllabus_data.get('co_po_mapping'):
                            syllabus_data['co_po_mapping'] = analysis_data.get('co_po_mapping')
                        story.extend(self._create_mapping(syllabus_data))
                    # Include textbooks/references from optimized syllabus
                    if syllabus_data.get('textbooks') or syllabus_data.get('references'):
                        story.extend(self._create_references(syllabus_data))
            else:
                # Generate export - show full syllabus structure
                story.extend(self._create_header(syllabus_data))
                
                if syllabus_data.get('overview'):
                    story.extend(self._create_overview(syllabus_data))
                if syllabus_data.get('objectives'):
                    story.extend(self._create_objectives(syllabus_data))
                if syllabus_data.get('learning_outcomes'):
                    story.extend(self._create_outcomes(syllabus_data))
                if syllabus_data.get('units'):
                    story.extend(self._create_units(syllabus_data))
                if syllabus_data.get('teaching_methodology'):
                    story.extend(self._create_methodology(syllabus_data))
                if syllabus_data.get('assessment_pattern'):
                    story.extend(self._create_assessment(syllabus_data))
                if include_mapping and syllabus_data.get('co_po_mapping'):
                    story.extend(self._create_mapping(syllabus_data))
                if syllabus_data.get('references'):
                    story.extend(self._create_references(syllabus_data))
                
            # Build PDF with page footer
            doc.build(story, onFirstPage=self._add_page_footer, onLaterPages=self._add_page_footer)
            
            self.logger.info(f"PDF exported successfully to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"PDF export failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _create_analysis_section(self, analysis: Dict[str, Any]) -> list:
        """Create analysis/optimization report section - handles both Analyze and Optimize page data"""
        elements = []
        
        # Determine if this is an Optimization or Analysis report
        # Optimization page data typically has 'rebalancing_suggestions' or 'bloom_analysis' with 'comparison'
        is_optimization = any(k in analysis for k in ['rebalancing_suggestions', 'sequence_optimization', 'modern_topics'])
        if not is_optimization and analysis.get('bloom_analysis'):
            # Double check bloom_analysis structure
            bloom = analysis.get('bloom_analysis', {})
            if isinstance(bloom, dict) and 'comparison' in bloom:
                is_optimization = True
                
        report_title = "Syllabus Optimization Report" if is_optimization else "Syllabus Analysis Report"
        
        # Section Title with date stamp
        elements.append(Paragraph(report_title, self.styles['CustomTitle']))
        
        # Add date stamp
        current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        elements.append(Paragraph(f"Generated on {current_date}", self.styles['ReportSubtitle']))
        
        # Horizontal line separator
        elements.append(self._create_horizontal_line(thickness=2, color='#3498db'))
        
        # 0. Industry Relevance & Rationale (New)
        if is_optimization:
            try:
                score = int(analysis.get('industry_relevance_score', 0) or 0)
            except (ValueError, TypeError):
                score = 0
            if score > 0:
                elements.append(Paragraph(f"<b>Industry Relevance Score:</b> {score}/100", self.styles['BodyText']))
                
            rationale = analysis.get('rationale', '')
            if rationale:
                elements.append(Paragraph("<b>Optimization Rationale:</b>", self.styles['BodyText']))
                elements.append(Paragraph(self._escape_html(str(rationale)), self.styles['InfoBox']))
                
            prereq = analysis.get('prerequisite_rationale', '')
            if prereq:
                elements.append(Paragraph("<b>Prerequisite & Sequencing Logic:</b>", self.styles['BodyText']))
                elements.append(Paragraph(self._escape_html(str(prereq)), self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.2*inch))

        # 1. Comparison Table (New)
        changes = analysis.get('changes_summary', [])
        # Check first element to determine if it's a structured dict format
        if changes and len(changes) > 0 and isinstance(changes[0], dict):
             elements.append(Paragraph("Summary of Changes", self.styles['SectionHeading']))
             elements.extend(self._create_comparison_table(changes))
             elements.append(Spacer(1, 0.2*inch))
        
        # 1.5 Bloom's Taxonomy Visual (New) - prefer chart if bloom_distribution exists
        bloom_dist = analysis.get('bloom_distribution', {})
        bloom_analysis = analysis.get('bloom_analysis', {})
        bloom_heading_added = False
        
        if bloom_dist:
            elements.append(Paragraph("Bloom's Taxonomy Distribution", self.styles['SectionHeading']))
            bloom_heading_added = True
            chart_img = self._generate_bloom_chart(bloom_dist)
            if chart_img:
                elements.append(chart_img)
                elements.append(Spacer(1, 0.2*inch))
        
        # Fallback to table if no chart was generated but bloom_analysis exists
        if bloom_analysis and bloom_analysis.get('comparison'):
            if not bloom_heading_added:
                elements.append(Paragraph("Bloom's Taxonomy Distribution", self.styles['SectionHeading']))
            
            table_data = [['Level', 'Current %', 'Target Range', 'Status']]
            
            for level, data in bloom_analysis.get('comparison', {}).items():
                if isinstance(data, dict):
                    try:
                        current = float(data.get('current', 0) or 0)
                        rec_min = int(data.get('recommended_min', 0) or 0)
                        rec_max = int(data.get('recommended_max', 100) or 100)
                    except (ValueError, TypeError):
                        current, rec_min, rec_max = 0, 0, 100
                    status = str(data.get('status', 'unknown') or 'unknown')
                    table_data.append([
                        level.capitalize(),
                        f"{current:.1f}%",
                        f"{rec_min}-{rec_max}%",
                        status.capitalize()
                    ])
            
            if len(table_data) > 1:
                table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1.5*inch, 1.3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 0.2*inch))
        
        # Fallback: Analyze page bloom_coverage format
        bloom_coverage = analysis.get('bloom_coverage', {})
        if not (bloom_analysis and bloom_analysis.get('comparison')) and bloom_coverage and bloom_coverage.get('percentages'):
            elements.append(Paragraph("Bloom's Taxonomy Coverage", self.styles['SectionHeading']))
            table_data = [['Level', 'Coverage %']]
            for level, pct in bloom_coverage.get('percentages', {}).items():
                table_data.append([level.capitalize(), f"{pct:.1f}%"])
            if len(table_data) > 1:
                table = Table(table_data, colWidths=[2.5*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 0.2*inch))
        
        # 2. Rebalancing Suggestions (Optimize page)
        rebalancing = analysis.get('rebalancing_suggestions', [])
        if rebalancing:
            elements.append(Paragraph("Curriculum Rebalancing Suggestions", self.styles['SectionHeading']))
            for suggestion in rebalancing:
                elements.append(Paragraph(f"• {self._escape_html(str(suggestion))}", self.styles['BodyText']))
            elements.append(Spacer(1, 0.2*inch))
        
        # 3. Modern Topics Suggestions (Optimize page)
        modern_topics = analysis.get('modern_topics', [])
        if modern_topics and isinstance(modern_topics, list):
            elements.append(Paragraph("Modern Topics Integration", self.styles['SectionHeading']))
            topics_text = ", ".join(modern_topics[:10])
            elements.append(Paragraph(topics_text, self.styles['BodyText']))
            elements.append(Spacer(1, 0.2*inch))
        
        # 4. Compliance Scores (Both)
        nep = analysis.get('nep_2020_compliance', {})
        if nep and nep.get('status') == 'success':
            elements.append(Paragraph("NEP 2020 Compliance Assessment", self.styles['SectionHeading']))
            pct = nep.get('compliance_percentage', 0)
            level = nep.get('compliance_level', 'Unknown')
            elements.append(Paragraph(f"Compliance Score: {pct}% - {level}", self.styles['BodyText']))
            elements.append(Spacer(1, 0.15*inch))
        
        accred = analysis.get('accreditation_compliance', {})
        if accred:
            nba = accred.get('nba', {})
            naac = accred.get('naac', {})
            if nba.get('compliance_percentage') or naac.get('compliance_percentage'):
                elements.append(Paragraph("Accreditation Compliance Status", self.styles['SectionHeading']))
                if nba.get('compliance_percentage'):
                    elements.append(Paragraph(f"NBA: {nba['compliance_percentage']}% - {nba.get('compliance_level', '')}", self.styles['BodyText']))
                if naac.get('compliance_percentage'):
                    elements.append(Paragraph(f"NAAC: {naac['compliance_percentage']}% - {naac.get('compliance_level', '')}", self.styles['BodyText']))
                elements.append(Spacer(1, 0.2*inch))
        

        
        # 6. Content Quality Analysis (Analyze page format)
        quality = analysis.get('content_quality', {})
        if quality:
            # Quality Score
            if quality.get('quality_score'):
                score_data = quality.get('quality_score', {})
                score = score_data.get('total_score', 0)
                grade = score_data.get('grade', 'N/A')
                elements.append(Paragraph(f"Quality Assessment: {score}/100 ({grade})", self.styles['SectionHeading']))
                
                # Add breakdown if available
                breakdown = score_data.get('breakdown', {})
                if breakdown:
                    breakdown_text = ", ".join([f"{k.replace('_', ' ').capitalize()}: {v}/25" for k, v in breakdown.items()])
                    elements.append(Paragraph(breakdown_text, self.styles['BodyText']))
                    
                elements.append(Spacer(1, 0.15*inch))
            
            # Hours Distribution Section
            hours_dist = quality.get('hours_distribution', {})
            if hours_dist and hours_dist.get('distribution'):
                elements.append(Paragraph("Hours Distribution Analysis", self.styles['SubsectionHeading']))
                
                # Create hours table
                hours_table_data = [['Unit', 'Title', 'Hours', 'Topics', '%']]
                for item in hours_dist.get('distribution', []):
                    hours_table_data.append([
                        f"Unit {item.get('unit_number', '?')}",
                        str(item.get('title', 'Untitled'))[:35],
                        f"{item.get('hours', 0)}h",
                        str(item.get('topic_count', '-')),
                        f"{item.get('percentage', 0)}%"
                    ])
                
                if len(hours_table_data) > 1:
                    hours_table = Table(hours_table_data, colWidths=[0.7*inch, 2.5*inch, 0.6*inch, 0.6*inch, 0.6*inch])
                    hours_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    elements.append(hours_table)
                    
                    # Summary stats
                    total_hours = hours_dist.get('total_hours', 0)
                    avg_hours = hours_dist.get('average_hours', 0)
                    avg_per_topic = hours_dist.get('average_hours_per_topic', 0)
                    elements.append(Paragraph(
                        f"Total: {total_hours}h  |  Avg/Unit: {avg_hours}h  |  Avg/Topic: {avg_per_topic}h",
                        self.styles['BodyText']
                    ))
                    
                    # Imbalance warnings
                    imbalances = hours_dist.get('imbalances', [])
                    if imbalances:
                        elements.append(Paragraph("<b>Imbalances Detected:</b>", self.styles['BodyText']))
                        for imb in imbalances[:3]:
                            elements.append(Paragraph(f"• {imb.get('description', str(imb))}", self.styles['BulletItem']))
                
                elements.append(Spacer(1, 0.15*inch))
            
            # Unit Content Analysis (Theory/Practical)
            unit_analysis = quality.get('unit_analysis', {})
            if unit_analysis and unit_analysis.get('units'):
                elements.append(Paragraph("Unit Content Analysis", self.styles['SubsectionHeading']))
                
                # Theory/Practical ratio summary
                theory_ratio = unit_analysis.get('theory_ratio', 0)
                practical_ratio = unit_analysis.get('practical_ratio', 0)
                elements.append(Paragraph(
                    f"Overall Distribution: <b>{theory_ratio}% Theory</b> / <b>{practical_ratio}% Practical</b>",
                    self.styles['BodyText']
                ))
                
                # Unit details table
                unit_table_data = [['Unit', 'Title', 'Topics', 'Theory %', 'Key Concepts']]
                for unit in unit_analysis.get('units', [])[:8]:
                    key_concepts = unit.get('key_concepts', [])
                    concepts_text = ', '.join(key_concepts[:2]) if key_concepts else '-'
                    unit_table_data.append([
                        f"U{unit.get('unit_number', '?')}",
                        str(unit.get('title', 'Untitled'))[:25],
                        str(unit.get('total_topics', 0)),
                        f"{unit.get('theory_percentage', 0)}%",
                        concepts_text[:40]
                    ])
                
                if len(unit_table_data) > 1:
                    unit_table = Table(unit_table_data, colWidths=[0.5*inch, 1.8*inch, 0.6*inch, 0.7*inch, 2.4*inch])
                    unit_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    elements.append(unit_table)
                
                elements.append(Spacer(1, 0.15*inch))
            
            # Content Depth Analysis
            content_depth = quality.get('content_depth', {})
            if content_depth and content_depth.get('depth_distribution'):
                elements.append(Paragraph("Content Depth Distribution", self.styles['SubsectionHeading']))
                depth_dist = content_depth.get('depth_distribution', {})
                depth_text = f"Basic: {depth_dist.get('basic', 0)} units  |  " \
                            f"Intermediate: {depth_dist.get('intermediate', 0)} units  |  " \
                            f"Advanced: {depth_dist.get('advanced', 0)} units"
                elements.append(Paragraph(depth_text, self.styles['BodyText']))
                elements.append(Paragraph(f"Total Topics: {content_depth.get('total_topics', 0)}", self.styles['BodyText']))
                elements.append(Spacer(1, 0.15*inch))
        
        # 7. Detailed NEP 2020 Compliance Checks
        nep = analysis.get('nep_2020_compliance', {})
        if nep and nep.get('checks'):
            elements.append(Paragraph("NEP 2020 Compliance Details", self.styles['SectionHeading']))
            
            # Overall score
            score = nep.get('compliance_score', nep.get('compliance_percentage', 0))
            elements.append(Paragraph(f"<b>Compliance Score: {score}%</b>", self.styles['BodyText']))
            
            # Individual checks table
            nep_checks = nep.get('checks', {})
            if nep_checks:
                check_table_data = [['Criterion', 'Status', 'Details']]
                for check_name, check_data in nep_checks.items():
                    if isinstance(check_data, dict):
                        status = "✓ Pass" if check_data.get('passed') else "✗ Needs Attention"
                        details = str(check_data.get('details', '-'))[:50]
                        check_table_data.append([
                            check_name.replace('_', ' ').title(),
                            status,
                            details
                        ])
                
                if len(check_table_data) > 1:
                    check_table = Table(check_table_data, colWidths=[2*inch, 1*inch, 3*inch])
                    check_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    elements.append(check_table)
            
            elements.append(Spacer(1, 0.15*inch))
        
        # 8. Detailed Accreditation Compliance
        accred = analysis.get('accreditation_compliance', {})
        if accred and (accred.get('nba') or accred.get('naac')):
            elements.append(Paragraph("Accreditation Compliance Details", self.styles['SectionHeading']))
            
            for accred_type in ['nba', 'naac']:
                accred_data = accred.get(accred_type, {})
                if accred_data and accred_data.get('checks'):
                    score = accred_data.get('compliance_score', accred_data.get('compliance_percentage', 0))
                    elements.append(Paragraph(f"<b>{accred_type.upper()} - Score: {score}%</b>", self.styles['BodyText']))
                    
                    # Key checks
                    checks = accred_data.get('checks', {})
                    for check_name, check_data in list(checks.items())[:5]:
                        if isinstance(check_data, dict):
                            status = "✓" if check_data.get('passed') else "✗"
                            elements.append(Paragraph(
                                f"{status} {check_name.replace('_', ' ').title()}",
                                self.styles['BulletItem']
                            ))
                    
                    elements.append(Spacer(1, 0.1*inch))
            
            elements.append(Spacer(1, 0.15*inch))
        
        # 9. Recommendations (with priority support)
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("Actionable Recommendations", self.styles['SectionHeading']))
            
            for rec in recommendations[:10]:
                if isinstance(rec, dict):
                    rec_text = rec.get('text', rec.get('action', ''))
                    priority = rec.get('priority', '')
                    category = rec.get('category', '')
                    
                    # Format with priority indicator
                    priority_prefix = ""
                    if priority:
                        priority_upper = priority.upper()
                        priority_prefix = f"[{priority_upper}] "
                    
                    elements.append(Paragraph(
                        f"• <b>{priority_prefix}</b>{self._escape_html(rec_text)}",
                        self.styles['BodyText']
                    ))
                else:
                    elements.append(Paragraph(f"• {self._escape_html(str(rec))}", self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.2*inch))
        
        # 8. AI Analysis (when structured parsing was incomplete)
        ai_analysis = analysis.get('ai_analysis', '')
        if ai_analysis:
            ai_title = "AI-Powered Optimization Insights" if is_optimization else "AI-Powered Syllabus Analysis"
            elements.append(self._create_horizontal_line(thickness=1, color='#3498db'))
            elements.append(Paragraph(ai_title, self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Split by newlines and create paragraphs
            import re
            lines = ai_analysis.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    elements.append(Spacer(1, 0.05*inch))
                    continue
                    
                # Handle markdown-style headers (add separator before major sections)
                if line.startswith('## '):
                    elements.append(Spacer(1, 0.15*inch))
                    elements.append(self._create_horizontal_line(thickness=0.5, color='#ecf0f1'))
                    elements.append(Paragraph(self._escape_html(line[3:]), self.styles['SubsectionHeading']))
                elif line.startswith('# '):
                    elements.append(Spacer(1, 0.15*inch))
                    elements.append(self._create_horizontal_line(thickness=0.5, color='#bdc3c7'))
                    elements.append(Paragraph(self._escape_html(line[2:]), self.styles['SectionHeading']))
                elif line.startswith('### '):
                    elements.append(Spacer(1, 0.1*inch))
                    elements.append(Paragraph(f"<b>{self._escape_html(line[4:])}</b>", self.styles['BodyText']))
                # Bullet points with proper styling
                elif line.startswith('- ') or line.startswith('* '):
                    elements.append(Paragraph(f"• {self._escape_html(line[2:])}", self.styles['BulletItem']))
                # Numbered lists (1. 2. 3. or 1) 2) 3))
                elif re.match(r'^\d+[.)]\s', line):
                    match = re.match(r'^(\d+[.)]\s*)(.*)', line)
                    if match:
                        num_part = match.group(1)
                        text_part = match.group(2)
                        elements.append(Paragraph(f"<b>{num_part}</b>{self._escape_html(text_part)}", self.styles['NumberedItem']))
                # Bold lines
                elif line.startswith('**') and line.endswith('**'):
                    elements.append(Paragraph(f"<b>{self._escape_html(line[2:-2])}</b>", self.styles['BodyText']))
                # Regular text
                else:
                    elements.append(Paragraph(self._escape_html(line), self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.2*inch))
            
        return elements
            
    def _create_header(self, data: Dict[str, Any]) -> list:
        """Create PDF header with institution details and Teaching Scheme table"""
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
        
        # Course Type and Semester row
        cell_style = self._create_cell_style(font_size=9, leading=11)
        course_type = data.get('course_type', 'DSC')
        semester = data.get('semester', 'I')
        
        type_sem_table = Table([
            [
                Paragraph(f'<b>Course Type:</b> {course_type}', cell_style),
                Paragraph(f'<b>Semester:</b> {semester}', cell_style)
            ]
        ], colWidths=[3.2*inch, 3.2*inch])
        type_sem_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(type_sem_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Teaching Scheme table (L-T-P with Credits and Exam Scheme)
        # Parse credits string (e.g., "3-1-0")
        credits_str = data.get('credits', '3-0-0')
        try:
            l_credit, t_credit, p_credit = credits_str.split('-')
        except:
            l_credit, t_credit, p_credit = '3', '0', '0'
        
        # Get CIE/ESE marks
        cie_marks = data.get('cie_marks', 60)
        ese_marks = data.get('ese_marks', 40)
        total_marks = int(cie_marks) + int(ese_marks)
        total_credits = int(l_credit) + int(t_credit) + int(p_credit)
        
        # Teaching Scheme Table - matches university format
        header_style = self._create_cell_style(font_size=8, leading=10)
        
        teaching_data = [
            # Header row
            [
                Paragraph('<b>Teaching Scheme</b>', header_style),
                Paragraph('', header_style),
                Paragraph('<b>Credits</b>', header_style),
                Paragraph('', header_style),
                Paragraph('<b>Examination Scheme</b>', header_style),
                Paragraph('', header_style),
            ],
            # Lecture row
            [
                Paragraph('Lecture', header_style),
                Paragraph(f'{l_credit} Hr./Week', header_style),
                Paragraph('L', header_style),
                Paragraph(l_credit, header_style),
                Paragraph('CIE Marks', header_style),
                Paragraph(str(cie_marks), header_style),
            ],
            # Tutorial row
            [
                Paragraph('Tutorial', header_style),
                Paragraph(f'{t_credit} Hr./Week', header_style),
                Paragraph('T', header_style),
                Paragraph(t_credit, header_style),
                Paragraph('ESE Marks', header_style),
                Paragraph(str(ese_marks), header_style),
            ],
            # Practical row
            [
                Paragraph('Practical', header_style),
                Paragraph(f'{p_credit} Hr./Week', header_style),
                Paragraph('P', header_style),
                Paragraph(p_credit, header_style),
                Paragraph('Total Marks', header_style),
                Paragraph(str(total_marks), header_style),
            ],
            # Total row
            [
                Paragraph('<b>Total</b>', header_style),
                Paragraph(f'{total_credits} Hr./Week', header_style),
                Paragraph('<b>Total</b>', header_style),
                Paragraph(f'<b>{total_credits}</b>', header_style),
                Paragraph('', header_style),
                Paragraph('', header_style),
            ],
        ]
        
        teaching_table = Table(teaching_data, colWidths=[1.1*inch, 0.9*inch, 0.6*inch, 0.5*inch, 1.1*inch, 0.7*inch])
        teaching_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#e3f2fd')),  # Teaching header
            ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#e3f2fd')),  # Credits header
            ('BACKGROUND', (4, 0), (5, 0), colors.HexColor('#e3f2fd')),  # Exam header
            ('SPAN', (0, 0), (1, 0)),  # Merge Teaching Scheme cells
            ('SPAN', (2, 0), (3, 0)),  # Merge Credits cells
            ('SPAN', (4, 0), (5, 0)),  # Merge Exam Scheme cells
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(teaching_table)
        
        # Academic Year
        year = data.get('year', '')
        if year:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                f'<b>Academic Year:</b> {year}',
                ParagraphStyle('Year', parent=self.styles['Normal'], fontSize=10, alignment=TA_CENTER)
            ))
        
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
        
        elements.append(Paragraph("Course Outcomes", self.styles['SectionHeading']))
        
        outcomes = data.get('learning_outcomes', [])
        
        # Create table with wrapped text - headers match university format
        table_data = [['CO No.', 'Statement']]
        
        # Create cell style
        cell_style = self._create_cell_style(font_size=9, leading=11)
        
        for i, outcome in enumerate(outcomes, 1):
            description = outcome.get('description', '')
            
            # Create paragraphs for all cells - use just number for CO column
            co_para = self._create_cell_para(str(i), cell_style)
            desc_para = self._create_cell_para(description, cell_style)
            
            table_data.append([co_para, desc_para])
        
        # Two column layout: CO No. (narrow) + Statement (wide)
        table = Table(table_data, colWidths=[0.6*inch, 5.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # CO number centered
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),     # Statement left
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _create_units(self, data: Dict[str, Any]) -> list:
        """Create units section in university syllabus table format"""
        elements = []
        
        elements.append(Paragraph("Course Content", self.styles['SectionHeading']))
        
        units = data.get('units', [])
        cell_style = self._create_cell_style(font_size=9, leading=11)
        topic_style = self._create_cell_style(font_size=8, leading=10)
        
        # Create table data with headers
        table_data = []
        
        for unit in units:
            unit_num = unit.get('unit_number', '')
            title = unit.get('title', 'Untitled')
            hours = unit.get('hours', 0)
            
            # Get topics with their specific CO/BTL if available
            topics = unit.get('topics', [])
            topic_paras = []
            
            if topics:
                for t in topics:
                    if isinstance(t, dict):
                        name = t.get('name', t.get('topic', 'Untitled')) or 'Untitled'
                        co = t.get('co', '')
                        btl = t.get('btl', '')
                        # Build tag only with available info
                        tag_parts = []
                        if co:
                            tag_parts.append(str(co))
                        if btl:
                            tag_parts.append(f"BTL{btl}")
                        tag = f" [{', '.join(tag_parts)}]" if tag_parts else ""
                        topic_paras.append(Paragraph(f"{self._escape_html(str(name))}<font color='#7f8c8d'>{self._escape_html(tag)}</font>", topic_style))
                    else:
                        topic_paras.append(Paragraph(self._escape_html(str(t)), topic_style))
            
            # Get CO and BTL for this unit
            # Support both old 'co'/'btl' and new 'mapped_cos'/'btl_levels'
            # Filter out None values
            unit_cos = unit.get('mapped_cos', [unit.get('co')] if unit.get('co') else [])
            unit_btls = unit.get('btl_levels', [unit.get('btl')] if unit.get('btl') else [])
            
            # Filter out None and empty values
            unit_cos = [c for c in unit_cos if c is not None and c != '']
            unit_btls = [b for b in unit_btls if b is not None and b != '']
            
            cos_str = ", ".join(map(str, unit_cos))
            btls_str = ", ".join(map(str, unit_btls))
            
            # Unit header row
            table_data.append([
                Paragraph(f'<b>Unit No {unit_num}</b>', cell_style),
                Paragraph(f'<b>{self._escape_html(str(title))}</b>', cell_style),
                Paragraph(f'<b>{hours} Hours</b>', cell_style),
                Paragraph(f'<b>CO:</b> {cos_str}', cell_style),
                Paragraph(f'<b>BTL:</b> {btls_str}', cell_style),
            ])
            
            # Topics row - wrap topic_paras in a nested table for proper cell rendering
            if topic_paras:
                # Create a simple table from the list of paragraphs
                topics_table = Table([[p] for p in topic_paras], colWidths=[4.8*inch])
                topics_table.setStyle(TableStyle([
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ]))
                table_data.append([
                    topics_table,
                    Paragraph('', cell_style),
                    Paragraph('', cell_style),
                    Paragraph('', cell_style),
                    Paragraph('', cell_style),
                ])
        
        if table_data:
            # Column widths: Unit No (0.8") + Title/Topics (3.5") + Hours (0.8") + CO (0.6") + BTL (0.6")
            table = Table(table_data, colWidths=[0.8*inch, 3.5*inch, 0.8*inch, 0.7*inch, 0.7*inch])
            
            # Build styles
            styles = [
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]
            
            # Add background for unit header rows and span topics row
            for i in range(0, len(table_data), 2):
                styles.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#e8f4f8')))
                if i + 1 < len(table_data):
                    styles.append(('SPAN', (0, i+1), (2, i+1)))
                    # Span CO and BTL cells for the topics row too if they are empty
                    styles.append(('SPAN', (3, i+1), (4, i+1)))
            
            table.setStyle(TableStyle(styles))
            elements.append(table)
        
        elements.append(Spacer(1, 0.3*inch))
        
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
        """Create CO-PO-PSO mapping section with BTL column"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Mapping of COs to POs and PSOs", self.styles['SectionHeading']))
        
        mapping = data.get('co_po_mapping', {})
        outcomes = data.get('learning_outcomes', [])
        
        # Define all columns - match university format (PO1-10, PSO1-4, BTL)
        po_columns = ['PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'PO9', 'PO10']
        pso_columns = ['PSO1', 'PSO2', 'PSO3', 'PSO4']
        all_columns = po_columns + pso_columns
        
        # Create header rows (two row header like reference)
        header_row1 = ['CO Number'] + ['POs'] * 10 + ['PSOs'] * 4 + ['BTL']
        header_row2 = [''] + ['PO ' + str(i) for i in range(1, 11)] + ['PSO ' + str(i) for i in range(1, 5)] + ['']
        
        # Build data rows
        data_rows = []
        for i, outcome in enumerate(outcomes, 1):
            co_key = f'CO{i}'
            co_mapping = mapping.get(co_key, {})
            
            # Get BTL from outcome
            bloom_level = outcome.get('bloom_level', '')
            # Convert bloom level to BTL code
            btl_map = {
                'remember': '1', 'understand': '2', 'apply': '3',
                'analyze': '4', 'evaluate': '5', 'create': '6',
                'knowledge': '1', 'comprehension': '2', 'application': '3',
                'analysis': '4', 'synthesis': '5'
            }
            btl = btl_map.get(bloom_level.lower(), bloom_level[:3].upper() if bloom_level else '')
            
            row = [f'CO{i}']
            for col in all_columns:
                value = co_mapping.get(col, 0)
                row.append(str(value) if value > 0 else '-')
            row.append(btl)
            data_rows.append(row)
        
        # Combine all rows
        table_data = [header_row1, header_row2] + data_rows
        
        # Column widths - tight fit for 16 columns + BTL
        # CO Number: 0.55", POs (10x0.35=3.5"), PSOs (4x0.35=1.4"), BTL: 0.45"
        # Total = 0.55 + 3.5 + 1.4 + 0.45 = 5.9" (fits in 6.7")
        col_widths = [0.55*inch] + [0.35*inch] * 14 + [0.45*inch]
        
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 6),
            
            # Merge header cells
            ('SPAN', (0, 0), (0, 1)),  # CO Number spans 2 rows
            ('SPAN', (1, 0), (10, 0)),  # POs header spans 10 cols
            ('SPAN', (11, 0), (14, 0)),  # PSOs header spans 4 cols
            ('SPAN', (15, 0), (15, 1)),  # BTL spans 2 rows
            
            # Data styling
            ('FONTSIZE', (0, 2), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            
            # Alternate row colors
            ('ROWBACKGROUNDS', (0, 2), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Legend - match university format
        legend_text = "Affinity Level: 1- Slight, 2- Moderate, 3-Substantial, BTL: Bloom's Taxonomy Level"
        elements.append(Paragraph(legend_text, ParagraphStyle(
            'Legend', parent=self.styles['BodyText'], fontSize=8, fontName='Helvetica-Oblique'
        )))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _create_references(self, data: Dict[str, Any]) -> list:
        """Create references section with numbered format"""
        import re
        elements = []
        
        def parse_refs_string(text):
            """Parse a string of references into a list by splitting on numbered patterns"""
            if not text or not isinstance(text, str):
                return []
            
            # Find all numbered patterns like "1. ", "2. ", "3. " etc.
            pattern = r'(\d+)\.\s+'
            matches = list(re.finditer(pattern, text))
            refs = []
            
            if matches:
                for idx, match in enumerate(matches):
                    start = match.end()  # Start after "N. "
                    # End at next match start or end of string
                    if idx + 1 < len(matches):
                        end = matches[idx + 1].start()
                    else:
                        end = len(text)
                    
                    ref_text = text[start:end].strip()
                    if ref_text:
                        refs.append(ref_text)
            
            # If no numbered pattern found, return as single item
            if len(refs) == 0 and text.strip():
                refs = [text.strip()]
            
            return refs
        
        # Handle top-level textbooks array (from AI optimization)
        textbooks = data.get('textbooks', [])
        
        # Parse string textbooks
        if textbooks and isinstance(textbooks, str):
            textbooks = parse_refs_string(textbooks)
        
        if textbooks and isinstance(textbooks, list) and len(textbooks) > 0:
            elements.append(Paragraph("Textbooks", self.styles['SectionHeading']))
            for i, book in enumerate(textbooks, 1):
                book_text = str(book).strip()
                if book_text:
                    elements.append(Paragraph(f"{i}. {self._escape_html(book_text)}", self.styles['BodyText']))
                    elements.append(Spacer(1, 0.05*inch))
            elements.append(Spacer(1, 0.1*inch))
        
        # Handle top-level references array (from AI optimization)
        references = data.get('references', [])
        reference_books = data.get('reference_books', [])  # Alternative naming
        refs = references if references else reference_books
        
        # Parse string references
        if refs and isinstance(refs, str):
            refs = parse_refs_string(refs)
        
        if refs and isinstance(refs, list) and len(refs) > 0:
            elements.append(Paragraph("Reference Books", self.styles['SectionHeading']))
            for i, ref in enumerate(refs, 1):
                ref_text = str(ref).strip()
                if ref_text:
                    elements.append(Paragraph(f"{i}. {self._escape_html(ref_text)}", self.styles['BodyText']))
                    elements.append(Spacer(1, 0.05*inch))
            elements.append(Spacer(1, 0.1*inch))
        
        # Legacy: Handle nested references dict format
        elif isinstance(references, dict):
            if references.get('textbooks'):
                elements.append(Paragraph("Textbooks", self.styles['SectionHeading']))
                tb_list = references['textbooks']
                if isinstance(tb_list, str):
                    tb_list = parse_refs_string(tb_list)
                for i, ref in enumerate(tb_list, 1):
                    elements.append(Paragraph(f"{i}. {self._escape_html(ref)}", self.styles['BodyText']))
                    elements.append(Spacer(1, 0.05*inch))
                    
            if references.get('references'):
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph("Reference Books", self.styles['SubsectionHeading']))
                ref_list = references['references']
                if isinstance(ref_list, str):
                    ref_list = parse_refs_string(ref_list)
                for i, ref in enumerate(ref_list, 1):
                    elements.append(Paragraph(f"{i}. {self._escape_html(ref)}", self.styles['BodyText']))
                    elements.append(Spacer(1, 0.05*inch))
                
        return elements

