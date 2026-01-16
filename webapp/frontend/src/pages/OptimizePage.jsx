import React, { useState } from 'react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';
import { BloomDistributionChart, BloomBalanceChart, COPOHeatmap } from '../components/Charts';
import '../components/Charts.css';

// Simple markdown to HTML converter for AI-generated content
const simpleMarkdown = (text) => {
  if (!text) return '';
  return text
    // Headers
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Bullet points
    .replace(/^\* (.+)$/gm, '<li>$1</li>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // Numbered lists  
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    // Wrap in paragraph
    .replace(/^/, '<p>')
    .replace(/$/, '</p>')
    // Fix list items (wrap consecutive li in ul)
    .replace(/(<li>.*<\/li>(<br\/>)?)+/g, '<ul>$&</ul>')
    .replace(/<br\/><\/ul>/g, '</ul>')
    .replace(/<ul><br\/>/g, '<ul>');
};

function OptimizePage() {
  // Global State
  const {
    optimizationResults, setOptimizationResults,
    optimizeFile, setOptimizeFile
  } = useSyllabus();

  // Local processing state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setOptimizeFile(file); // Persist file (metadata only in browser)
    setLoading(true);
    setError(null);

    try {
      // Upload returns { success, filename, data } - extract the data
      const uploadResponse = await apiService.uploadSyllabus(file);
      const syllabusData = uploadResponse.data || uploadResponse;

      // Get optimization suggestions - returns full response with optimization object
      const optResponse = await apiService.optimizeSyllabus(syllabusData);

      setOptimizationResults({
        syllabus: optResponse.syllabus || syllabusData,  // Use backend's syllabus or fallback
        optimization: optResponse.optimization  // Extract optimization from response
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to optimize syllabus');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      // Merge syllabus and optimization data for export
      const exportData = {
        ...optimizationResults.syllabus,
        co_po_mapping: optimizationResults.optimization?.co_po_mapping,
        rubrics: optimizationResults.optimization?.rubrics,
        bloom_analysis: optimizationResults.optimization?.bloom_analysis,
      };

      const response = await fetch(`http://localhost:8000/api/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ syllabus_data: exportData })
      });

      if (!response.ok) throw new Error(`Export failed`);

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Determine file extension based on format
      let ext = 'pdf';
      if (format === 'word') ext = 'docx';
      else if (format === 'latex-pdf') ext = 'pdf';

      a.download = `${exportData.course_code || 'syllabus'}.${ext}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(`Export failed: ${err.message}`);
    }
  };

  return (
    <div className="optimize-page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">Optimize Syllabus</h1>
          <p className="page-subtitle">
            Get AI-powered suggestions to improve your syllabus
          </p>
        </div>

        {!optimizationResults ? (
          <div className="upload-section">
            <div className="card upload-card">
              <div className="upload-content">
                <div className="upload-icon">✨</div>
                <h3>Upload Syllabus for Optimization</h3>
                <p className="text-muted">Get intelligent suggestions to enhance your curriculum</p>

                <input
                  type="file"
                  id="optimize-upload"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />

                <label htmlFor="optimize-upload" className="btn btn-primary btn-lg">
                  {loading ? 'Processing...' : 'Choose File'}
                </label>
              </div>
            </div>
          </div>
        ) : (
          <div className="optimization-results fade-in">
            {/* Export Buttons */}
            <div style={{ position: 'sticky', top: '20px', zIndex: 100, display: 'flex', gap: '10px', justifyContent: 'flex-end', marginBottom: '20px' }}>
              <button
                onClick={() => handleExport('pdf')}
                className="btn btn-secondary"
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                📄 Export PDF
              </button>
              <button
                onClick={() => handleExport('latex-pdf')}
                className="btn btn-secondary"
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                📐 Export LaTeX PDF
              </button>
              <button
                onClick={() => handleExport('word')}
                className="btn btn-secondary"
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                📝 Export Word
              </button>
            </div>

            {/* Bloom's Analysis */}
            {optimizationResults.optimization?.bloom_analysis && (
              <>
                <div className="card">
                  <div className="card-header">
                    <h3 className="card-title">📊 Bloom's Taxonomy Distribution</h3>
                  </div>
                  <div className="bloom-distribution">
                    {Object.entries(optimizationResults.optimization.bloom_analysis.comparison).map(([level, data]) => (
                      <div key={level} className="distribution-item">
                        <div className="level-header">
                          <span className="level-name">{level.charAt(0).toUpperCase() + level.slice(1)}</span>
                          <span className={`status-badge ${data.status}`}>{data.status}</span>
                        </div>
                        <div className="level-stats">
                          <span>Current: {data.current.toFixed(1)}%</span>
                          <span>Recommended: {data.recommended_min}-{data.recommended_max}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Visual Charts for Bloom's */}
                <div className="charts-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-lg)' }}>
                  <BloomDistributionChart bloomAnalysis={optimizationResults.optimization.bloom_analysis} />
                  <BloomBalanceChart bloomAnalysis={optimizationResults.optimization.bloom_analysis} />
                </div>
              </>
            )}

            {/* CO-PO-PSO Mapping Matrix */}
            {optimizationResults.optimization?.co_po_mapping && (
              <>
                {/* Visual Heatmap Chart */}
                <COPOHeatmap mapping={optimizationResults.optimization.co_po_mapping} />

                {/* Original detailed table */}
                <div className="card">
                  <div className="card-header">
                    <h3 className="card-title">🎯 CO-PO-PSO Mapping Matrix (Detailed)</h3>
                    <p className="card-subtitle">Affinity Level: 1-Slight, 2-Moderate, 3-Substantial</p>
                  </div>
                  <div className="mapping-container">
                    <div className="table-wrapper">
                      <table className="mapping-table">
                        <thead>
                          <tr>
                            <th rowSpan="2">CO No</th>
                            <th colSpan="9">Program Outcomes (POs)</th>
                            <th colSpan="4">PSOs</th>
                            <th rowSpan="2">BTL</th>
                          </tr>
                          <tr>
                            {['PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'PO9',
                              'PSO1', 'PSO2', 'PSO3', 'PSO4'].map(po => (
                                <th key={po}>{po}</th>
                              ))}
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(optimizationResults.optimization.co_po_mapping).map(([co, poData]) => {
                            // Get Bloom's level from syllabus data
                            const coIndex = parseInt(co.replace('CO', '')) - 1;
                            const bloomLevel = optimizationResults.syllabus?.learning_outcomes?.[coIndex]?.bloom_level || 'AP';
                            const btl = bloomLevel.substring(0, 2).toUpperCase();

                            return (
                              <tr key={co}>
                                <td className="co-cell">{co}</td>
                                {['PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'PO9',
                                  'PSO1', 'PSO2', 'PSO3', 'PSO4'].map(po => {
                                    const value = poData[po] || 0;
                                    return (
                                      <td key={po} className={`affinity-${value}`}>
                                        {value > 0 ? value : '-'}
                                      </td>
                                    );
                                  })}
                                <td className="btl-cell">{btl}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Rebalancing Suggestions */}
            {optimizationResults.optimization?.rebalancing_suggestions && optimizationResults.optimization.rebalancing_suggestions.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">⚖️ Rebalancing Suggestions</h3>
                </div>
                <ul className="suggestions-list">
                  {optimizationResults.optimization.rebalancing_suggestions.map((suggestion, idx) => (
                    <li key={idx} className="suggestion-item">
                      <span className="suggestion-icon">💡</span>
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Modern Topics */}
            {optimizationResults.optimization?.modern_topics && optimizationResults.optimization.modern_topics.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">🚀 Modern Topics to Consider</h3>
                </div>
                <div className="topics-grid">
                  {optimizationResults.optimization.modern_topics.map((topic, idx) => (
                    <div key={idx} className="topic-badge">
                      {topic}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sequence Optimization */}
            {optimizationResults.optimization?.sequence_optimization && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">📚 Unit Sequencing</h3>
                </div>
                <div
                  className="sequence-content markdown-content"
                  dangerouslySetInnerHTML={{
                    __html: simpleMarkdown(optimizationResults.optimization.sequence_optimization.optimization_suggestions)
                  }}
                />
              </div>
            )}

            {/* Lesson Plan Analysis */}
            {optimizationResults.optimization?.lesson_plan_analysis && optimizationResults.optimization.lesson_plan_analysis.total_lessons > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">📝 Lesson Plan Analysis</h3>
                  <p className="card-subtitle">
                    {optimizationResults.optimization.lesson_plan_analysis.total_lessons} lessons identified across{' '}
                    {optimizationResults.optimization.lesson_plan_analysis.lesson_distribution?.lessons_per_unit ?
                      Object.keys(optimizationResults.optimization.lesson_plan_analysis.lesson_distribution.lessons_per_unit).length : '?'} units
                  </p>
                </div>
                <div className="lesson-analysis">
                  {optimizationResults.optimization.lesson_plan_analysis.gaps?.length > 0 && (
                    <div className="gaps-section">
                      <h4>Issues Found:</h4>
                      {optimizationResults.optimization.lesson_plan_analysis.gaps.map((gap, idx) => (
                        <div key={idx} className={`gap-item severity-${gap.severity}`}>
                          <span className="gap-icon">{gap.severity === 'high' ? '⚠️' : 'ℹ️'}</span>
                          <span>{gap.description}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="stats-grid">
                    <div className="stat-card">
                      <div className="stat-value">{optimizationResults.optimization.lesson_plan_analysis.total_planned_hours}</div>
                      <div className="stat-label">Total Hours</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">{optimizationResults.optimization.lesson_plan_analysis.average_hours_per_lesson.toFixed(1)}</div>
                      <div className="stat-label">Avg Hours/Lesson</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Redundancy Detection */}
            {optimizationResults.optimization?.redundancies && optimizationResults.optimization.redundancies.enabled && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">🔄 Content Redundancies</h3>
                  <p className="card-subtitle">
                    {optimizationResults.optimization.redundancies.total_redundancies} potential redundancies detected
                  </p>
                </div>
                <div className="redundancy-analysis">
                  {optimizationResults.optimization.redundancies.total_redundancies === 0 ? (
                    <div className="no-redundancies">
                      <span className="success-icon">✅</span>
                      <p>No significant redundancies detected. Content appears well-structured.</p>
                    </div>
                  ) : (
                    <>
                      {optimizationResults.optimization.redundancies.duplicate_topics?.length > 0 && (
                        <div className="redundancy-section">
                          <h4>🔁 Duplicate Topics:</h4>
                          {optimizationResults.optimization.redundancies.duplicate_topics.map((dup, idx) => (
                            <div key={idx} className={`redundancy-item severity-${dup.severity}`}>
                              <div className="redundancy-match">
                                <div className="match-item">
                                  <strong>{dup.unit1}</strong>
                                  <p>"{dup.topic1}"</p>
                                </div>
                                <div className="similarity-badge">{(dup.similarity * 100).toFixed(0)}% similar</div>
                                <div className="match-item">
                                  <strong>{dup.unit2}</strong>
                                  <p>"{dup.topic2}"</p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {optimizationResults.optimization.redundancies.similar_outcomes?.length > 0 && (
                        <div className="redundancy-section">
                          <h4>🎯 Similar Outcomes:</h4>
                          {optimizationResults.optimization.redundancies.similar_outcomes.map((sim, idx) => (
                            <div key={idx} className={`redundancy-item severity-${sim.severity}`}>
                              <div className="redundancy-match">
                                <div className="match-item">
                                  <strong>{sim.outcome1}</strong>
                                  <p>"{sim.text1}"</p>
                                </div>
                                <div className="similarity-badge">{(sim.similarity * 100).toFixed(0)}% similar</div>
                                <div className="match-item">
                                  <strong>{sim.outcome2}</strong>
                                  <p>"{sim.text2}"</p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Objectives Optimization */}
            {optimizationResults.optimization?.objectives_optimization?.status === 'success' && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">🎯 Objectives Enhancement</h3>
                </div>
                <div style={{ padding: '1rem' }}>
                  {optimizationResults.optimization.objectives_optimization.optimized_objectives.map((o, i) => (
                    <div key={i} style={{ marginBottom: '1rem', padding: '0.5rem', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                      <div>
                        <strong>Objective {i + 1}</strong>
                        <span style={{ float: 'right', color: 'var(--primary)' }}>{o.smart_score}/100</span>
                      </div>
                      <div style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>Original: {o.original}</div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--success)', marginTop: '0.25rem' }}>Enhanced: {o.optimized}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Reference Suggestions */}
            {optimizationResults.optimization?.reference_suggestions?.status === 'success' && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">📚 Reference Recommendations</h3>
                </div>
                <div style={{ padding: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                  {Object.entries(optimizationResults.optimization.reference_suggestions.suggestions || {}).map(([cat, refs]) => (
                    refs && refs.length > 0 && (
                      <div key={cat}>
                        <h4 style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>{cat.replace(/_/g, ' ')}</h4>
                        {refs.slice(0, 3).map((r, i) => (
                          <div key={i} style={{ fontSize: '0.85rem', marginBottom: '0.3rem' }}>• {r.title}</div>
                        ))}
                      </div>
                    )
                  ))}
                </div>
              </div>
            )}

            {/* Compliance Status */}
            {(optimizationResults.optimization?.nep_2020_compliance || optimizationResults.optimization?.accreditation_compliance) && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">🏅 Compliance Status</h3>
                </div>
                <div style={{ padding: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', textAlign: 'center' }}>
                  {optimizationResults.optimization.nep_2020_compliance?.status === 'success' && (
                    <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                      <div style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>🇮🇳 NEP 2020</div>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)', margin: '0.5rem 0' }}>
                        {optimizationResults.optimization.nep_2020_compliance.compliance_percentage}%
                      </div>
                      <div style={{ fontSize: '0.85rem' }}>{optimizationResults.optimization.nep_2020_compliance.compliance_level}</div>
                    </div>
                  )}
                  {optimizationResults.optimization.accreditation_compliance?.nba && (
                    <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                      <div style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>NBA</div>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)', margin: '0.5rem 0' }}>
                        {optimizationResults.optimization.accreditation_compliance.nba.compliance_percentage}%
                      </div>
                      <div style={{ fontSize: '0.85rem' }}>{optimizationResults.optimization.accreditation_compliance.nba.compliance_level}</div>
                    </div>
                  )}
                  {optimizationResults.optimization.accreditation_compliance?.naac && (
                    <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                      <div style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>NAAC</div>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)', margin: '0.5rem 0' }}>
                        {optimizationResults.optimization.accreditation_compliance.naac.compliance_percentage}%
                      </div>
                      <div style={{ fontSize: '0.85rem' }}>{optimizationResults.optimization.accreditation_compliance.naac.compliance_level}</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>

      <style>{`
        .upload-card {
          text-align: center;
          padding: var(--spacing-2xl);
        }

        .upload-content {
          max-width: 500px;
          margin: 0 auto;
        }

        .upload-icon {
          font-size: 5rem;
          margin-bottom: var(--spacing-lg);
        }

        .optimization-results {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);
        }

        .bloom-distribution {
          padding: var(--spacing-md);
        }

        .distribution-item {
          padding: var(--spacing-md);
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-md);
        }

        .level-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-sm);
        }

        .level-name {
          font-weight: 700;
          font-size: 1.125rem;
        }

        .status-badge {
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-sm);
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .status-badge.optimal {
          background: hsla(142, 71%, 45%, 0.15);
          color: var(--success);
        }

        .status-badge.below {
          background: hsla(45, 100%, 50%, 0.15);
          color: hsl(45, 100%, 35%);
        }

        .status-badge.above {
          background: hsla(0, 84%, 60%, 0.15);
          color: var(--error);
        }

        [data-theme="dark"] .status-badge.optimal {
          background: hsla(142, 71%, 45%, 0.25);
          color: hsl(142, 71%, 65%);
        }

        [data-theme="dark"] .status-badge.below {
          background: hsla(45, 100%, 50%, 0.25);
          color: hsl(45, 100%, 65%);
        }

        [data-theme="dark"] .status-badge.above {
          background: hsla(0, 84%, 60%, 0.25);
          color: hsl(0, 84%, 70%);
        }

        .level-stats {
          display: flex;
          justify-content: space-between;
          color: var(--text-secondary);
          font-size: 0.875rem;
        }

        /* CO-PO Mapping Table Styles */
        .card-subtitle {
          margin-top: var(--spacing-xs);
          font-size: 0.875rem;
          color: var(--text-secondary);
          font-style: italic;
        }

        .mapping-container {
          padding: var(--spacing-md);
          overflow-x: auto;
        }

        .table-wrapper {
          min-width: 900px;
        }

        .mapping-table {
          width: 100%;
          border-collapse: collapse;
          border: 2px solid var(--border-color);
          font-size: 0.9rem;
        }

        .mapping-table th,
        .mapping-table td {
          padding: 0.75rem;
          text-align: center;
          border: 1px solid var(--border-color);
        }

        .mapping-table thead {
          background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
        }

        .mapping-table thead th {
          font-weight: 700;
          color: var(--text-primary);
          font-size: 0.875rem;
        }

        .mapping-table tbody tr:nth-child(even) {
          background: var(--bg-secondary);
        }

        .mapping-table tbody tr:hover {
          background: var(--bg-hover);
        }

        .co-cell {
          font-weight: 700;
          background: var(--bg-secondary);
          color: var(--primary);
        }

        .btl-cell {
          font-weight: 700;
          background: var(--bg-secondary);
          color: var(--accent);
        }

        /* Affinity Level Colors */
        .affinity-0 {
          color: var(--text-disabled);
        }

        .affinity-1 {
          background: hsla(210, 100%, 50%, 0.1);
          color: hsl(210, 80%, 50%);
          font-weight: 600;
        }

        .affinity-2 {
          background: hsla(45, 100%, 50%, 0.15);
          color: hsl(45, 100%, 40%);
          font-weight: 700;
        }

        .affinity-3 {
          background: hsla(142, 71%, 45%, 0.15);
          color: hsl(142, 71%, 35%);
          font-weight: 700;
        }

        [data-theme="dark"] .affinity-1 {
            color: hsl(210, 80%, 70%);
            background: hsla(210, 100%, 50%, 0.25);
        }

        [data-theme="dark"] .affinity-2 {
            color: hsl(45, 100%, 65%);
            background: hsla(45, 100%, 50%, 0.25);
        }

        [data-theme="dark"] .affinity-3 {
            color: hsl(142, 71%, 65%);
            background: hsla(142, 71%, 45%, 0.25);
        }

        .suggestions-list {
          list-style: none;
          padding: var(--spacing-md);
        }

        .suggestion-item {
          display: flex;
          gap: var(--spacing-sm);
          padding: var(--spacing-md);
          margin-bottom: var(--spacing-sm);
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
          border-left: 4px solid var(--primary);
        }

        .suggestion-icon {
          font-size: 1.25rem;
        }

        .topics-grid {
          display: flex;
          flex-wrap: wrap;
          gap: var(--spacing-sm);
          padding: var(--spacing-md);
        }

        .topic-badge {
          padding: var(--spacing-sm) var(--spacing-md);
          background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
          color: var(--primary);
          border-radius: var(--radius-md);
          font-weight: 600;
          font-size: 0.875rem;
          border: 1px solid var(--border-color);
        }

        .sequence-content {
          padding: var(--spacing-md);
          line-height: 1.8;
        }

        /* Markdown content styles for AI-generated text */
        .markdown-content h2, .markdown-content h3, .markdown-content h4 {
          margin-top: var(--spacing-md);
          margin-bottom: var(--spacing-sm);
          color: var(--text-primary);
        }
        .markdown-content h2 { font-size: 1.25rem; }
        .markdown-content h3 { font-size: 1.1rem; }
        .markdown-content h4 { font-size: 1rem; }
        .markdown-content strong { color: var(--primary); }
        .markdown-content ul, .markdown-content ol {
          margin: var(--spacing-sm) 0;
          padding-left: var(--spacing-lg);
        }
        .markdown-content li {
          margin-bottom: var(--spacing-xs);
        }
        .markdown-content p {
          margin-bottom: var(--spacing-sm);
        }

        /* Lesson Plan Analysis Styles */
        .lesson-analysis {
          padding: var(--spacing-md);
        }

        .gaps-section {
          margin-bottom: var(--spacing-lg);
        }

        .gaps-section h4 {
          font-size: 0.9rem;
          font-weight: 700;
          margin-bottom: var(--spacing-sm);
          color: var(--text-primary);
        }

        .gap-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm) var(--spacing-md);
          margin-bottom: var(--spacing-xs);
          border-radius: var(--radius-md);
          background: var(--bg-secondary);
        }

        .gap-item.severity-high {
          border-left: 4px solid var(--error);
        }

        .gap-item.severity-medium {
          border-left: 4px solid hsl(45, 100%, 50%);
        }

        .gap-icon {
          font-size: 1.25rem;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: var(--spacing-md);
          margin-top: var(--spacing-md);
        }

        .stat-card {
          background: var(--bg-secondary);
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          text-align: center;
        }

        .stat-value {
          font-size: 2rem;
          font-weight: 700;
          color: var(--primary);
        }

        .stat-label {
          font-size: 0.875rem;
          color: var(--text-secondary);
          margin-top: var(--spacing-xs);
        }

        /* Redundancy Analysis Styles */
        .redundancy-analysis {
          padding: var(--spacing-md);
        }

        .no-redundancies {
          text-align: center;
          padding: var(--spacing-xl);
        }

        .success-icon {
          font-size: 3rem;
          display: block;
          margin-bottom: var(--spacing-md);
        }

        .redundancy-section {
          margin-bottom: var(--spacing-lg);
        }

        .redundancy-section h4 {
          font-size: 0.9rem;
          font-weight: 700;
          margin-bottom: var(--spacing-md);
          color: var(--text-primary);
        }

        .redundancy-item {
          margin-bottom: var(--spacing-md);
          padding: var(--spacing-md);
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
        }

        .redundancy-item.severity-high {
          border-left: 4px solid var(--error);
        }

        .redundancy-item.severity-moderate {
          border-left: 4px solid hsl(45, 100%, 50%);
        }

        .redundancy-match {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
        }

        .match-item {
          flex: 1;
          padding: var(--spacing-sm);
          background: var(--bg-primary);
          border-radius: var(--radius-sm);
        }

        .match-item strong {
          display: block;
          color: var(--primary);
          margin-bottom: var(--spacing-xs);
          font-size: 0.875rem;
        }

        .match-item p {
          margin: 0;
          color: var(--text-secondary);
          font-size: 0.875rem;
          font-style: italic;
        }

        .similarity-badge {
          padding: var(--spacing-xs) var(--spacing-sm);
          background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
          color: var(--primary);
          border-radius: var(--radius-full);
          font-weight: 700;
          font-size: 0.875rem;
          white-space: nowrap;
          border: 1px solid var(--border-color);
        }
      `}</style>
    </div>
  );
}

export default OptimizePage;
