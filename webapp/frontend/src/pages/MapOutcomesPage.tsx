import React, { useState, useEffect, useCallback } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { mapOutcomes } from '../services/api';
import { COPOMapping } from '../types';
import COPOHeatmap from '../components/COPOHeatmap';
import ThreeForceGraph from '../components/ThreeForceGraph';
import SkeletonLoader from '../components/SkeletonLoader';
import { ShieldCheck, ShieldAlert, Activity, Plus, Trash2, GripVertical, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import './MapOutcomesPage.css';

interface COEntry {
  id: string;
  code: string;
  description: string;
}

const MapOutcomesPage: React.FC = () => {
  const { currentSyllabus, coPoMapping, setCoPoMapping } = useSyllabus();
  const [isLoading, setIsLoading] = useState(false);
  const [coEntries, setCoEntries] = useState<COEntry[]>([
    { id: crypto.randomUUID(), code: 'CO1', description: '' }
  ]);

  useEffect(() => {
    if (currentSyllabus?.learning_outcomes && currentSyllabus.learning_outcomes.length > 0) {
      setCoEntries(
        currentSyllabus.learning_outcomes.map((lo, i) => ({
          id: crypto.randomUUID(),
          code: lo.code || `CO${i + 1}`,
          description: lo.description
        }))
      );
    }
  }, [currentSyllabus]);

  const updateEntry = useCallback((id: string, field: keyof COEntry, value: string) => {
    setCoEntries(prev => prev.map(e => e.id === id ? { ...e, [field]: value } : e));
  }, []);

  const addEntry = useCallback(() => {
    const nextNum = coEntries.length + 1;
    setCoEntries(prev => [...prev, { id: crypto.randomUUID(), code: `CO${nextNum}`, description: '' }]);
  }, [coEntries.length]);

  const removeEntry = useCallback((id: string) => {
    setCoEntries(prev => {
      const filtered = prev.filter(e => e.id !== id);
      return filtered.map((e, i) => ({ ...e, code: `CO${i + 1}` }));
    });
  }, []);

  const handleMap = async (): Promise<void> => {
    const validEntries = coEntries.filter(e => e.description.trim());
    if (validEntries.length === 0) {
      toast.error('Add at least one course outcome with a description.');
      return;
    }

    setIsLoading(true);
    const t = toast.loading('Calculating semantic embeddings...');
    try {
      const res: COPOMapping = await mapOutcomes({
        course_outcomes: validEntries.map(e => ({ code: e.code, description: e.description })),
        domain: currentSyllabus?.domain || 'engineering'
      });
      setCoPoMapping(res);
      toast.success('Matrix Generated!', { id: t });
    } catch {
      toast.error('Error mapping outcomes.', { id: t });
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

      <div className="map-layout">
        <div className="map-input-panel glass-card">
          <div className="co-editor-header">
            <h3>Course Outcomes</h3>
            <button className="btn-secondary btn-sm" onClick={addEntry}>
              <Plus size={16} /> Add CO
            </button>
          </div>

          <div className="co-list">
            <AnimatePresence mode="popLayout">
              {coEntries.map((entry) => (
                <motion.div
                  key={entry.id}
                  className="co-row"
                  initial={{ opacity: 0, y: -10, height: 0 }}
                  animate={{ opacity: 1, y: 0, height: 'auto' }}
                  exit={{ opacity: 0, x: -20, height: 0 }}
                  transition={{ duration: 0.2 }}
                  layout
                >
                  <GripVertical size={16} className="grip-icon" />
                  <input
                    className="co-code-input"
                    value={entry.code}
                    onChange={e => updateEntry(entry.id, 'code', e.target.value)}
                    placeholder="CO1"
                  />
                  <input
                    className="co-desc-input"
                    value={entry.description}
                    onChange={e => updateEntry(entry.id, 'description', e.target.value)}
                    placeholder="Describe the course outcome..."
                  />
                  {coEntries.length > 1 && (
                    <button className="co-remove-btn" onClick={() => removeEntry(entry.id)} aria-label="Remove outcome">
                      <Trash2 size={14} />
                    </button>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {currentSyllabus?.learning_outcomes && (
            <p className="co-hint">
              <Sparkles size={14} /> Auto-populated from your current syllabus context
            </p>
          )}

          <button
            className="btn-primary btn-generate"
            onClick={handleMap}
            disabled={isLoading}
          >
            {isLoading ? 'Mapping...' : <><Activity size={18} /> Generate Heatmap</>}
          </button>
        </div>

        <div className="map-results-panel glass-card">
          <h3>Correlation Matrix</h3>

          {!coPoMapping && !isLoading && (
            <div className="map-empty-state">
              <div className="empty-illustration">
                <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
                  <rect x="20" y="20" width="80" height="80" rx="8" stroke="var(--border-subtle)" strokeWidth="2" strokeDasharray="6 4" />
                  <line x1="20" y1="45" x2="100" y2="45" stroke="var(--border-subtle)" strokeWidth="1.5" />
                  <line x1="20" y1="70" x2="100" y2="70" stroke="var(--border-subtle)" strokeWidth="1.5" />
                  <line x1="45" y1="20" x2="45" y2="100" stroke="var(--border-subtle)" strokeWidth="1.5" />
                  <line x1="70" y1="20" x2="70" y2="100" stroke="var(--border-subtle)" strokeWidth="1.5" />
                  <circle cx="57" cy="57" r="8" fill="var(--accent-indigo)" opacity="0.2" />
                  <circle cx="57" cy="57" r="4" fill="var(--accent-indigo)" opacity="0.5" />
                </svg>
              </div>
              <h4>No Mapping Yet</h4>
              <p>Add course outcomes and click Generate to build the correlation matrix.</p>
            </div>
          )}

          {isLoading && (
            <div className="map-loading">
              <SkeletonLoader type="chart" />
              <p className="shimmer-text">Processing AI cross-correlations...</p>
            </div>
          )}

          {coPoMapping && !isLoading && (
            <motion.div
              className="map-results-content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
            >
              <ThreeForceGraph mapping={coPoMapping.mapping} />

              <h4 className="section-heading">Correlation Matrix</h4>
              <COPOHeatmap mapping={coPoMapping.mapping} />

              <div className="validation-section">
                <h4 className="section-heading">Validation Report</h4>
                <div className="validation-cards">
                  {coPoMapping.validation?.unmapped_cos?.length > 0 ? (
                    <div className="finding-card warning">
                      <ShieldAlert size={20} className="text-amber" />
                      <div>
                        <strong>Unmapped COs</strong>
                        <p>{coPoMapping.validation.unmapped_cos.join(', ')}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="finding-card success">
                      <ShieldCheck size={20} />
                      <div>
                        <strong>All COs Mapped</strong>
                        <p>No orphaned course outcomes.</p>
                      </div>
                    </div>
                  )}

                  <div className="finding-card info">
                    <Activity size={20} />
                    <div>
                      <strong>PO Coverage</strong>
                      <p>{((coPoMapping.validation?.po_coverage ?? 0) * 100).toFixed(0)}% mapped</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapOutcomesPage;
