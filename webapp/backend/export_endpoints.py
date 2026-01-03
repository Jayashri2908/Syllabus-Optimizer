"""
Export endpoints for PDF and Excel
"""

@app.post("/api/export/pdf")
async def export_pdf(request: OptimizeRequest):
    """Export syllabus to PDF"""
    try:
        syllabus_data = request.syllabus_data
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            output_path = tmp.name
            
        # Export to PDF
        pdf_exporter = PDFExporter()
        success = pdf_exporter.export(
            syllabus_data=syllabus_data,
            output_path=output_path,
            include_mapping=True
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="PDF export failed")
            
        # Return file
        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename=f"{syllabus_data.get('course_code', 'syllabus')}.pdf"
        )
        
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/excel")
async def export_excel(request: OptimizeRequest):
    """Export syllabus to Excel"""
    try:
        syllabus_data = request.syllabus_data
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            output_path = tmp.name
            
        # Export to Excel
        excel_exporter = ExcelExporter()
        success = excel_exporter.export_complete_syllabus(
            syllabus_data=syllabus_data,
            output_path=output_path,
            include_mapping=True,
            include_rubrics=True
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Excel export failed")
            
        # Return file
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"{syllabus_data.get('course_code', 'syllabus')}.xlsx"
        )
        
    except Exception as e:
        logger.error(f"Excel export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/mapping")
async def export_mapping(request: OptimizeRequest):
    """Export CO-PO-PSO mapping matrix to Excel"""
    try:
        syllabus_data = request.syllabus_data
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            output_path = tmp.name
            
        # Export mapping only
        excel_exporter = ExcelExporter()
        success = excel_exporter.export_mapping_only(
            syllabus_data=syllabus_data,
            output_path=output_path,
            include_pso=True
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Mapping export failed")
            
        # Return file
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"{syllabus_data.get('course_code', 'mapping')}_CO-PO-PSO.xlsx"
        )
        
    except Exception as e:
        logger.error(f"Mapping export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
