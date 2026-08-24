import React, { useState, useEffect, ChangeEvent } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { mapOutcomes } from '../services/api';
import { COPOMapping } from '../types';
import COPOHeatmap from '../components/COPOHeatmap';
import ThreeForceGraph from '../components/ThreeForceGraph';
import SkeletonLoader from '../components/SkeletonLoader';
import { ShieldCheck, ShieldAlert, Activity } from 'lucide-react';
import toast from 'react-hot-toast';

const MapOutcomesPage: React.FC = () => {
  const { currentSyllabus, coPoMapping, setCoPoMapping } = useSyllabus();
  const [isLoading, setIsLoading] = useState(false);
  const [inputData, setInputData] = useState('[\n  {\n    "code": "CO1",\n    "description": "Understand core concepts"\n  }\n]');
  
  // Set initial data when syllabus exists
  useEffect(() => {
    if (currentSyllabus?.learning_outcomes) {
      setInputData(JSON.stringify(currentSyllabus.learning_outcomes, null, 2));
    }
  }, [currentSyllabus]);
  
  const handleMap = async (): Promise<void> => {
    setIsLoading(true);
    let cos: Array<{ code?: string; description: string }>;
    try {
      cos = JSON.parse(inputData);
    } catch {
      toast.error('Invalid JSON format in Course Outcomes.');
      setIsLoading(false);
      return;
    }

    const t = toast.loading('Calculating semantic embeddings...');
    try {
      const res: COPOMapping = await mapOutcomes({
        course_outcomes: cos,
        domain: currentSyllabus?.domain || "engineering"
      });
      setCoPoMapping(res);
      toast.success('Matrix Generated!', { id: t });
    } catch {
      toast.error("Error mapping outcomes.", { id: t });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <h1>CO-PO Mapping Matrix</h1>
        <p>Generate correlation matrices between Course Outcomes and Program Outcomes.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* Left Side: Input */}
        <div className="glass-card p-6">
           <h3>Course Outcomes (JSON)</h3>
           <textarea 
             className="mt-4 w-full"
             style={{ width: '100%', minHeight: '300px', padding: '1rem', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', borderRadius: '0.5rem', border: '1px solid var(--border-subtle)', background: 'rgba(255,255,255,0.5)' }}
             value={inputData}
             onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setInputData(e.target.value)}
           />
           <button 
             className="btn-primary" 
             style={{ width: '100%', marginTop: '1rem', justifyContent: 'center' }}
             onClick={handleMap}
             disabled={isLoading}
           >
             {isLoading ? 'Mapping...' : <><Activity size={18}/> Generate Headmap</>}
           </button>
        </div>

        {/* Right Side: Map */}
        <div className="glass-card p-6" style={{ overflowX: 'auto' }}>
          <h3>Correlation Matrix</h3>
          
          {!coPoMapping && !isLoading && (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Click Generate to analyze semantic relationships and build the matrix.
            </div>
          )}

          {isLoading && (
            <div style={{ padding: '3rem' }}>
              <SkeletonLoader type="chart" />
              <p className="shimmer-text text-center mt-4">Processing AI cross-correlations...</p>
            </div>
          )}

          {coPoMapping && !isLoading && (
            <div className="mt-4 animate-slide-up">
              
              <ThreeForceGraph mapping={coPoMapping.mapping} />

              <h4 className="mt-4 mb-2">Correlation Matrix</h4>
              <COPOHeatmap mapping={coPoMapping.mapping} />

              <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid var(--border-subtle)' }}>
                <h4>Validation Report</h4>
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                  {coPoMapping.validation.unmapped_cos.length > 0 ? (
                     <div className="finding-item warning" style={{ flex: 1, minWidth: '200px' }}>
                       <ShieldAlert size={20} className="text-amber" />
                       <div>
                         <strong>Unmapped COs</strong>
                         <p>{coPoMapping.validation.unmapped_cos.join(', ')}</p>
                       </div>
                     </div>
                  ) : (
                    <div className="finding-item info" style={{ flex: 1, minWidth: '200px' }}>
                       <ShieldCheck size={20} className="text-indigo" />
                       <div>
                         <strong>All COs Mapped</strong>
                         <p>No orphaned course outcomes.</p>
                       </div>
                     </div>
                  )}
                  
                  <div className="finding-item info" style={{ flex: 1, minWidth: '200px' }}>
                     <Activity size={20} className="text-indigo" />
                     <div>
                       <strong>PO Coverage</strong>
                       <p>{(coPoMapping.validation.po_coverage * 100).toFixed(0)}% mapped</p>
                     </div>
                   </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default MapOutcomesPage;
