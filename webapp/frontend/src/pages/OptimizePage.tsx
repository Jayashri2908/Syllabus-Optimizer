import React, { useState } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { uploadSyllabus, optimizeSyllabus, exportPDF } from '../services/api';
import { SyllabusData } from '../types';
import FileUploader from '../components/FileUploader';
import SkeletonLoader from '../components/SkeletonLoader';
import { Database, Check, ChevronRight, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import './OptimizePage.css';

const OptimizePage: React.FC = () => {
  const { currentSyllabus, setCurrentSyllabus, optimizedSyllabus, setOptimizedSyllabus } = useSyllabus();
  const [isLoading, setIsLoading] = useState(false);
  const [originalUpload, setOriginalUpload] = useState<SyllabusData | null>(null);

  const handleUpload = async (file: File): Promise<void> => {
    setIsLoading(true);
    const t = toast.loading('Parsing and initiating RAG refactor...');
    try {
      const res = await uploadSyllabus(file);
      setOriginalUpload(res.data);
      setCurrentSyllabus(res.data);
      
      const optRes = await optimizeSyllabus(res.data);
      setOptimizedSyllabus(optRes.optimized_syllabus);
      toast.success('Curriculum officially optimized!', { id: t });
    } catch (err: unknown) {
      console.error(err);
      toast.error("Optimization failed.", { id: t });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (): Promise<void> => {
    if (!optimizedSyllabus) return;
    const t = toast.loading('Generating specific PDF mapping...');
    try {
      const blob = await exportPDF(optimizedSyllabus);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `optimized_${optimizedSyllabus.course_code}.pdf`;
      a.click();
      toast.success('Downloaded!', { id: t });
    } catch {
      toast.error('Failed to export', { id: t });
    }
  };

  return (
    <div className="page-container animate-fade-in" style={{ maxWidth: '1400px' }}>
      <div className="page-header">
        <h1>Curriculum Optimization</h1>
        <p>RAG-grounded refactoring leveraging NBA/NAAC guidelines and Bloom's Taxonomy balancing.</p>
      </div>

      {!optimizedSyllabus && !isLoading && (
        <div className="upload-section animate-slide-up">
           <FileUploader onUpload={handleUpload} isLoading={false} />
        </div>
      )}

      {isLoading && (
         <div className="comparison-container animate-fade-in">
           <div className="rag-notice mb-4">
              <Database size={16} />
              <span>Vector Grounding Active: Querying indexed materials from <strong>NBA Accreditation Manual</strong> and <strong>ABET Criteria</strong>.</span>
           </div>
           
           <div className="split-view">
              <div className="syllabus-column glass-card p-6">
                 <div className="col-header">
                   <h3>Original Layout</h3>
                 </div>
                 <div className="mt-4"><SkeletonLoader type="card" count={3} /></div>
              </div>
              <div className="divider"></div>
              <div className="syllabus-column glass-card p-6 border-indigo">
                 <div className="col-header">
                   <h3 className="text-indigo">AI Synthesis</h3>
                 </div>
                 <div className="mt-4"><SkeletonLoader type="card" count={3} /></div>
              </div>
           </div>
         </div>
      )}

      {optimizedSyllabus && !isLoading && (
        <div className="comparison-container animate-slide-up">
           <div className="results-header">
              <h2>Optimization Results</h2>
              <div className="actions">
                <button 
                  className="btn-secondary" 
                  onClick={() => { setOptimizedSyllabus(null); setCurrentSyllabus(null); setOriginalUpload(null); }}
                >
                  Start Over
                </button>
                <button className="btn-primary" onClick={handleExport}><Download size={18}/> Export Optimized PDF</button>
              </div>
           </div>
           
           <div className="split-view mt-4">
              {/* Original */}
              <div className="syllabus-column glass-card p-6">
                 <div className="col-header">
                   <h3>Original Syllabus</h3>
                   <span className="badge-gray">Before</span>
                 </div>
                 <div className="mt-4">
                    <strong>Course Outcomes</strong>
                    <div className="outcomes-list mt-2">
                       {originalUpload?.learning_outcomes?.map((co, i) => (
                         <div key={i} className="co-item bg-gray">
                           {co.description}
                         </div>
                       ))}
                    </div>
                 </div>
              </div>
              
              <div className="divider">
                 <ChevronRight size={24} className="text-secondary opacity-50" />
                 <ChevronRight size={24} className="text-indigo" />
                 <ChevronRight size={24} className="text-secondary opacity-50" />
              </div>

              {/* Optimized */}
              <div className="syllabus-column glass-card p-6 border-indigo">
                 <div className="col-header">
                   <h3 className="text-indigo">Optimized Syllabus</h3>
                   <span className="badge-green"><Check size={14}/> RAG Enhanced</span>
                 </div>
                 <div className="mt-4">
                    <strong>Refactored Course Outcomes</strong>
                    <div className="outcomes-list mt-2">
                       {optimizedSyllabus?.learning_outcomes?.map((co, i) => (
                         <div key={i} className="co-item opt-bg-indigo-light">
                           <div className="co-text">{co.description}</div>
                           <div className="co-meta">
                             <span className="mono-tag" style={{backgroundColor: '#fff'}}>{co.bloom_level}</span>
                           </div>
                         </div>
                       ))}
                    </div>
                 </div>
              </div>
           </div>
        </div>
      )}
    </div>
  );
};
export default OptimizePage;
