import React, { useState } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { uploadSyllabus, analyzeSyllabus, exportPDF } from '../services/api';
import FileUploader from '../components/FileUploader';
import ThreeBloomChart from '../components/ThreeBloomChart';
import { ShieldAlert, CheckCircle, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import './AnalyzePage.css';

const AnalyzePage: React.FC = () => {
  const { currentSyllabus, setCurrentSyllabus, analysisResult, setAnalysisResult } = useSyllabus();
  const [isLoading, setIsLoading] = useState(false);

  const handleUpload = async (file: File): Promise<void> => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.docx') && !file.name.endsWith('.pdf') && !file.name.endsWith('.txt')) {
      toast.error('Please upload a valid PDF, DOCX, or TXT file.');
      return;
    }

    setIsLoading(true);
    const loadingToast = toast.loading('Parsing syllabus and detecting gaps...');
    try {
      // 1. Upload & Parse
      const uploadRes = await uploadSyllabus(file);
      setCurrentSyllabus(uploadRes.data);
      
      // 2. Analyze
      const analysisRes = await analyzeSyllabus(uploadRes.data);
      setAnalysisResult(analysisRes.analysis);
      
      toast.success('Analysis complete!', { id: loadingToast });
    } catch (err: unknown) {
      console.error(err);
      const message = err instanceof Error ? err.message : "An error occurred during analysis.";
      toast.error(message, { id: loadingToast });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (): Promise<void> => {
    if (!currentSyllabus) return;
    const t = toast.loading('Generating PDF report...');
    try {
      const blob = await exportPDF(currentSyllabus, analysisResult);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentSyllabus.course_code || 'syllabus'}_analysis.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      toast.success('Downloaded!', { id: t });
    } catch {
      toast.error("Failed to export PDF", { id: t });
    }
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <h1>Gap Analyzer</h1>
        <p>Upload a syllabus document to extract course outcomes and detect pedagogical gaps.</p>
      </div>

      {!currentSyllabus && (
        <div className="upload-section">
          <FileUploader onUpload={handleUpload} isLoading={isLoading} />
        </div>
      )}

      {currentSyllabus && analysisResult && !isLoading && (
        <div className="results-container animate-slide-up">
          <div className="results-header">
            <div>
              <h2>{currentSyllabus.course_code}: {currentSyllabus.course_title}</h2>
              <span className="mono-tag" style={{ marginLeft: 0 }}>Parsed Successfully</span>
            </div>
            <div className="actions">
              <button 
                className="btn-secondary" 
                onClick={() => {
                  setCurrentSyllabus(null); 
                  setAnalysisResult(null);
                }}>
                New Analysis
              </button>
              <button className="btn-primary" onClick={handleExport}><Download size={18}/> Export Report</button>
            </div>
          </div>

          <div className="analysis-grid">
            <div className="glass-card p-6" style={{ gridColumn: '1 / -1' }}>
              <h3>Bloom's Taxonomy Distribution (3D Visualizer)</h3>
              <div className="mt-4">
                <ThreeBloomChart data={analysisResult.bloom_analysis?.distribution || {}} />
              </div>
            </div>

            <div className="glass-card p-6 gap-findings" style={{ gridColumn: '1 / -1' }}>
              <h3>Pedagogical Findings</h3>
              <div className="findings-list mt-4">
                {analysisResult.bloom_analysis?.missing_levels && analysisResult.bloom_analysis.missing_levels.length > 0 && (
                  <div className="finding-item warning">
                    <ShieldAlert size={20} className="text-amber" />
                    <div>
                      <strong>Missing Cognitive Levels</strong>
                      <p>Syllabus lacks outcomes at: {analysisResult.bloom_analysis.missing_levels.join(', ')}</p>
                    </div>
                  </div>
                )}
                
                {analysisResult.ai_analysis ? (
                   <div className="finding-item info mt-4">
                     <CheckCircle size={20} className="text-indigo" />
                     <div>
                       <strong>RAG Grounded Insights</strong>
                       <p className="text-sm mt-1 leading-relaxed">{analysisResult.ai_analysis}</p>
                     </div>
                   </div>
                ) : (
                  <div className="finding-item info mt-4">
                    <CheckCircle size={20} className="text-indigo" />
                    <div>
                       <strong>Structure Analysis</strong>
                       <p>Found {currentSyllabus.units?.length || 0} units and {currentSyllabus.learning_outcomes?.length || 0} learning outcomes.</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyzePage;
