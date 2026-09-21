import React, { useState } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { uploadSyllabus, optimizeSyllabus, exportPDF } from '../services/api';
import { SyllabusData, LearningOutcome, Unit } from '../types';
import FileUploader from '../components/FileUploader';
import SkeletonLoader from '../components/SkeletonLoader';
import { Database, Check, Download, ArrowRight, RefreshCw, ChevronDown, ChevronUp, Zap, FileText, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import './OptimizePage.css';

const DiffOutcome: React.FC<{
  original?: LearningOutcome;
  optimized?: LearningOutcome;
  index: number;
}> = ({ original, optimized, index }) => {
  const isAdded = original && !optimized;
  const isNew = !original && optimized;
  const isModified = original && optimized && original.description !== optimized.description;
  const statusClass = isNew ? 'diff-added' : isModified ? 'diff-modified' : isAdded ? 'diff-removed' : 'diff-unchanged';
  const statusLabel = isNew ? 'Added' : isModified ? 'Modified' : isAdded ? 'Removed' : 'Unchanged';
  const statusIcon = isNew ? <Zap size={12} /> : isModified ? <RefreshCw size={12} /> : isAdded ? <FileText size={12} /> : <Check size={12} />;

  return (
    <div className={`diff-item ${statusClass}`}>
      <div className="diff-item-header">
        <span className="diff-status-badge">{statusIcon} {statusLabel}</span>
        <span className="diff-co-code">{(optimized || original)?.code || `CO${index + 1}`}</span>
        {(optimized || original)?.bloom_level && (
          <span className="mono-tag">{(optimized || original)?.bloom_level}</span>
        )}
      </div>
      {original && (
        <p className={`diff-text ${isModified || isAdded ? 'diff-old' : ''}`}>
          {original.description}
        </p>
      )}
      {isModified && (
        <div className="diff-arrow-row">
          <ArrowRight size={14} className="diff-arrow-icon" />
        </div>
      )}
      {optimized && (isModified || isNew) && (
        <p className="diff-text diff-new">
          {optimized.description}
        </p>
      )}
    </div>
  );
};

const DiffUnit: React.FC<{
  original?: Unit;
  optimized?: Unit;
  index: number;
}> = ({ original, optimized, index }) => {
  const [expanded, setExpanded] = useState(true);

  const origTopics = original?.topics || [];
  const optTopics = optimized?.topics || [];
  const addedTopics = optTopics.filter(t => !origTopics.includes(t));
  const removedTopics = origTopics.filter(t => !optTopics.includes(t));
  const hasChanges = addedTopics.length > 0 || removedTopics.length > 0 ||
    (original?.title !== optimized?.title);

  return (
    <div className={`diff-unit ${hasChanges ? 'has-changes' : ''}`}>
      <div className="diff-unit-header" onClick={() => setExpanded(!expanded)}>
        <div className="diff-unit-title">
          {hasChanges && <span className="change-dot" />}
          <strong>Unit {original?.unit_number || optimized?.unit_number || index + 1}</strong>
          <span className="diff-unit-name">{optimized?.title || original?.title || 'Untitled'}</span>
        </div>
        <div className="diff-unit-meta">
          {hasChanges && <span className="modified-badge"><RefreshCw size={12} /> Changed</span>}
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>
      <AnimatePresence>
        {expanded && (
          <motion.div
            className="diff-unit-body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {original?.title !== optimized?.title && (
              <div className="title-diff">
                <span className="diff-old-title">{original?.title}</span>
                <ArrowRight size={14} className="diff-arrow-icon" />
                <span className="diff-new-title">{optimized?.title}</span>
              </div>
            )}
            <div className="topics-diff">
              {optTopics.map((topic, i) => {
                const isAdded = addedTopics.includes(topic);
                return (
                  <span key={i} className={`topic-chip ${isAdded ? 'topic-added' : 'topic-kept'}`}>
                    {isAdded && <Zap size={10} />}{topic}
                  </span>
                );
              })}
              {removedTopics.map((topic, i) => (
                <span key={`rm-${i}`} className="topic-chip topic-removed">
                  {topic}
                </span>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const OptimizePage: React.FC = () => {
  const { setCurrentSyllabus, optimizedSyllabus, setOptimizedSyllabus } = useSyllabus();
  const [isLoading, setIsLoading] = useState(false);
  const [originalUpload, setOriginalUpload] = useState<SyllabusData | null>(null);
  const [activeTab, setActiveTab] = useState<'outcomes' | 'units' | 'summary'>('summary');

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
      toast.error('Optimization failed.', { id: t });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (): Promise<void> => {
    if (!optimizedSyllabus) return;
    const t = toast.loading('Generating optimized PDF...');
    try {
      const blob = await exportPDF(optimizedSyllabus);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `optimized_${optimizedSyllabus.course_code}.pdf`;
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Downloaded!', { id: t });
    } catch {
      toast.error('Failed to export', { id: t });
    }
  };

  const handleReset = (): void => {
    setOptimizedSyllabus(null);
    setCurrentSyllabus(null);
    setOriginalUpload(null);
  };

  const getDiffStats = () => {
    if (!originalUpload || !optimizedSyllabus) return { added: 0, modified: 0, removed: 0 };

    const origCOs = originalUpload.learning_outcomes || [];
    const optCOs = optimizedSyllabus.learning_outcomes || [];
    let added = 0, modified = 0, removed = 0;

    const maxLen = Math.max(origCOs.length, optCOs.length);
    for (let i = 0; i < maxLen; i++) {
      if (!origCOs[i] && optCOs[i]) added++;
      else if (origCOs[i] && !optCOs[i]) removed++;
      else if (origCOs[i] && optCOs[i] && origCOs[i].description !== optCOs[i].description) modified++;
    }

    return { added, modified, removed };
  };

  return (
    <div className="page-container animate-fade-in" style={{ maxWidth: '1400px' }}>
      <div className="page-header">
        <h1>Curriculum Optimization</h1>
        <p>RAG-grounded refactoring leveraging NBA/NAAC guidelines and Bloom's Taxonomy balancing.</p>
      </div>

      {!optimizedSyllabus && !isLoading && (
        <div className="upload-section animate-slide-up">
          <FileUploader onUpload={handleUpload} isLoading={isLoading} />
        </div>
      )}

      {isLoading && (
        <div className="opt-loading-container animate-fade-in">
          <div className="rag-notice mb-4">
            <Database size={16} />
            <span>Vector Grounding Active: Querying indexed materials from <strong>NBA Accreditation Manual</strong> and <strong>ABET Criteria</strong>.</span>
          </div>
          <div className="opt-loading-split">
            <div className="glass-card opt-load-col">
              <h3>Original Layout</h3>
              <SkeletonLoader type="card" count={3} />
            </div>
            <div className="opt-load-divider">
              <ArrowRight size={20} className="text-secondary" style={{ opacity: 0.3 }} />
              <ArrowRight size={20} className="text-indigo" />
              <ArrowRight size={20} className="text-secondary" style={{ opacity: 0.3 }} />
            </div>
            <div className="glass-card opt-load-col opt-col-optimized">
              <h3 className="text-indigo">AI Synthesis</h3>
              <SkeletonLoader type="card" count={3} />
            </div>
          </div>
        </div>
      )}

      {optimizedSyllabus && !isLoading && originalUpload && (
        <motion.div
          className="opt-results animate-slide-up"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="opt-results-header">
            <div>
              <h2>Optimization Results</h2>
              <p className="opt-subtitle">{originalUpload.course_code}: {originalUpload.course_title}</p>
            </div>
            <div className="opt-actions">
              <button className="btn-secondary" onClick={handleReset}>Start Over</button>
              <button className="btn-primary" onClick={handleExport}><Download size={18} /> Export Optimized PDF</button>
            </div>
          </div>

          <div className="opt-stats-row">
            {(() => {
              const stats = getDiffStats();
              return (
                <>
                  <div className="opt-stat-card glass-card">
                    <div className="opt-stat-icon stat-added"><Zap size={18} /></div>
                    <div className="opt-stat-value">{stats.added}</div>
                    <div className="opt-stat-label">Added</div>
                  </div>
                  <div className="opt-stat-card glass-card">
                    <div className="opt-stat-icon stat-modified"><RefreshCw size={18} /></div>
                    <div className="opt-stat-value">{stats.modified}</div>
                    <div className="opt-stat-label">Modified</div>
                  </div>
                  <div className="opt-stat-card glass-card">
                    <div className="opt-stat-icon stat-removed"><FileText size={18} /></div>
                    <div className="opt-stat-value">{stats.removed}</div>
                    <div className="opt-stat-label">Removed</div>
                  </div>
                  <div className="opt-stat-card glass-card">
                    <div className="opt-stat-icon stat-units"><Layers size={18} /></div>
                    <div className="opt-stat-value">{optimizedSyllabus.units?.length || 0}</div>
                    <div className="opt-stat-label">Units</div>
                  </div>
                </>
              );
            })()}
          </div>

          <div className="opt-tabs">
            <button
              className={`opt-tab ${activeTab === 'summary' ? 'active' : ''}`}
              onClick={() => setActiveTab('summary')}
            >
              Summary
            </button>
            <button
              className={`opt-tab ${activeTab === 'outcomes' ? 'active' : ''}`}
              onClick={() => setActiveTab('outcomes')}
            >
              Course Outcomes
            </button>
            <button
              className={`opt-tab ${activeTab === 'units' ? 'active' : ''}`}
              onClick={() => setActiveTab('units')}
            >
              Curriculum Units
            </button>
          </div>

          <AnimatePresence mode="wait">
            {activeTab === 'summary' && (
              <motion.div
                key="summary"
                className="opt-tab-content"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="opt-summary-grid">
                  <div className="glass-card opt-summary-col">
                    <div className="col-header">
                      <h3>Original Syllabus</h3>
                      <span className="badge-gray">Before</span>
                    </div>
                    <div className="summary-stats">
                      <div className="summary-stat">
                        <span className="summary-stat-label">Outcomes</span>
                        <span className="summary-stat-value">{originalUpload.learning_outcomes?.length || 0}</span>
                      </div>
                      <div className="summary-stat">
                        <span className="summary-stat-label">Units</span>
                        <span className="summary-stat-value">{originalUpload.units?.length || 0}</span>
                      </div>
                      <div className="summary-stat">
                        <span className="summary-stat-label">Bloom's Coverage</span>
                        <span className="summary-stat-value">{new Set(originalUpload.learning_outcomes?.map(co => co.bloom_level)).size} levels</span>
                      </div>
                    </div>
                  </div>
                  <div className="glass-card opt-summary-col opt-col-optimized">
                    <div className="col-header">
                      <h3 className="text-indigo">Optimized Syllabus</h3>
                      <span className="badge-green"><Check size={14} /> RAG Enhanced</span>
                    </div>
                    <div className="summary-stats">
                      <div className="summary-stat">
                        <span className="summary-stat-label">Outcomes</span>
                        <span className="summary-stat-value text-indigo">{optimizedSyllabus.learning_outcomes?.length || 0}</span>
                      </div>
                      <div className="summary-stat">
                        <span className="summary-stat-label">Units</span>
                        <span className="summary-stat-value text-indigo">{optimizedSyllabus.units?.length || 0}</span>
                      </div>
                      <div className="summary-stat">
                        <span className="summary-stat-label">Bloom's Coverage</span>
                        <span className="summary-stat-value text-indigo">{new Set(optimizedSyllabus.learning_outcomes?.map(co => co.bloom_level)).size} levels</span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'outcomes' && (
              <motion.div
                key="outcomes"
                className="opt-tab-content"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="diff-list">
                  {(() => {
                    const origCOs = originalUpload.learning_outcomes || [];
                    const optCOs = optimizedSyllabus.learning_outcomes || [];
                    const maxLen = Math.max(origCOs.length, optCOs.length);
                    const items = [];
                    for (let i = 0; i < maxLen; i++) {
                      items.push(
                        <DiffOutcome
                          key={i}
                          original={origCOs[i]}
                          optimized={optCOs[i]}
                          index={i}
                        />
                      );
                    }
                    return items;
                  })()}
                </div>
              </motion.div>
            )}

            {activeTab === 'units' && (
              <motion.div
                key="units"
                className="opt-tab-content"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="diff-list">
                  {(() => {
                    const origUnits = originalUpload.units || [];
                    const optUnits = optimizedSyllabus.units || [];
                    const maxLen = Math.max(origUnits.length, optUnits.length);
                    const items = [];
                    for (let i = 0; i < maxLen; i++) {
                      items.push(
                        <DiffUnit
                          key={i}
                          original={origUnits[i]}
                          optimized={optUnits[i]}
                          index={i}
                        />
                      );
                    }
                    return items;
                  })()}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  );
};

export default OptimizePage;
