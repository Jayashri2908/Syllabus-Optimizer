import React, { useState } from 'react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';

function AnalyzePage() {
  // Global State
  const {
    analysisResults, setAnalysisResults,
    analyzeFile, setAnalyzeFile
  } = useSyllabus();

  // Local state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setAnalyzeFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!analyzeFile && !analysisResults) {
      setError('Please select a file');
      return;
    }

    if (analysisResults && !analyzeFile) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.uploadSyllabus(analyzeFile);
      const analysisResponse = await apiService.analyzeSyllabus(response.data);
      setAnalysisResults({
        syllabus: response.data,
        analysis: analysisResponse.analysis
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze syllabus');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async () => {
    if (!analysisResults) return;
    try {
      const response = await fetch('http://localhost:8000/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          syllabus_data: analysisResults.syllabus,
          analysis_data: analysisResults.analysis // Sending analysis data
        })
      });
      if (!response.ok) throw new Error('Export failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${analysisResults.syllabus?.course_code || 'syllabus'}_analysis.pdf`;
      a.click();
    } catch (err) {
      setError('Failed to export PDF');
    }
  };

  // Quality score color
  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  };

  const analysis = analysisResults?.analysis;
  const qualityScore = analysis?.content_quality?.quality_score;

  return (
    <div className="analyze-page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">📊 Analyze Syllabus</h1>
          <p className="page-subtitle">
            Comprehensive syllabus evaluation with actionable insights
          </p>
        </div>

        {/* Upload Section */}
        <div className="upload-section">
          <div className="card">
            <div className="upload-area">
              <div className="upload-icon">📤</div>
              <h3>Upload Syllabus</h3>
              <p className="text-muted">Supports PDF, DOCX, and TXT files</p>

              <input
                type="file"
                id="file-upload"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />

              <label htmlFor="file-upload" className="btn btn-secondary">
                {analyzeFile ? 'Change File' : 'Choose File'}
              </label>

              {analyzeFile && (
                <div className="file-info">
                  <span className="file-name">📄 {analyzeFile.name}</span>
                  <button onClick={handleUpload} className="btn btn-primary" disabled={loading}>
                    {loading ? 'Analyzing...' : 'Analyze'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className="alert alert-error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Analysis Results */}
        {analysis && (
          <div className="results-section fade-in">
            {/* Export Buttons */}
            <div className="export-bar">
              <button onClick={handleExportPDF} className="btn btn-secondary">
                📄 Export PDF Report
              </button>
            </div>

            {/* Quality Score Dashboard */}
            {qualityScore && (
              <div className="score-dashboard">
                <div className="score-circle" style={{ borderColor: getScoreColor(qualityScore.total_score) }}>
                  <div className="score-value">{qualityScore.total_score}</div>
                  <div className="score-max">/100</div>
                </div>
                <div className="score-details">
                  <h2>Quality Score: {qualityScore.grade}</h2>
                  <p className="score-status">{qualityScore.status}</p>
                  <div className="score-breakdown">
                    {Object.entries(qualityScore.breakdown || {}).map(([key, value]) => (
                      <div key={key} className="breakdown-item">
                        <span>{key.replace('_', ' ')}</span>
                        <div className="breakdown-bar">
                          <div
                            className="breakdown-fill"
                            style={{ width: `${(value / 25) * 100}%` }}
                          />
                        </div>
                        <span>{value}/25</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Tab Navigation */}
            <div className="tab-nav">
              {['overview', 'content', 'structure', 'recommendations'].map(tab => (
                <button
                  key={tab}
                  className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="tab-content">
              {activeTab === 'overview' && (
                <div className="results-grid">
                  {/* Bloom's Coverage */}
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">🎯 Bloom's Taxonomy Coverage</h3>
                    </div>
                    <div className="bloom-analysis">
                      {Object.entries(analysis.bloom_coverage?.percentages || {}).map(([level, percentage]) => (
                        <div key={level} className="bloom-item">
                          <div className="bloom-label">
                            <span>{level.charAt(0).toUpperCase() + level.slice(1)}</span>
                            <span className="bloom-percentage">{percentage.toFixed(1)}%</span>
                          </div>
                          <div className="bloom-bar">
                            <div className="bloom-fill" style={{ width: `${percentage}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* CO-PO Mapping */}
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">🔗 CO-PO Mapping Status</h3>
                    </div>
                    <div className="mapping-stats">
                      <div className="stat-item">
                        <div className="stat-value">{analysis.co_po_mapping_gaps?.total_cos || 0}</div>
                        <div className="stat-label">Total COs</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-value">{analysis.co_po_mapping_gaps?.mapped_cos || 0}</div>
                        <div className="stat-label">Mapped COs</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-value">{(analysis.co_po_mapping_gaps?.coverage_percentage || 0).toFixed(0)}%</div>
                        <div className="stat-label">Coverage</div>
                      </div>
                    </div>
                  </div>

                  {/* Assessment Pattern */}
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">📝 Assessment Pattern</h3>
                    </div>
                    <div className="assessment-info">
                      <p><strong>Total:</strong> {analysis.assessment_gaps?.total_percentage || 0}%</p>
                      {Object.entries(analysis.assessment_gaps?.components || {}).map(([component, value]) => (
                        <div key={component} className="assessment-item">
                          <span>{component.replace(/_/g, ' ')}</span>
                          <span className="badge badge-primary">{value}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Modern Topics */}
                  {analysis.content_quality?.modern_topics && (
                    <div className="card">
                      <div className="card-header">
                        <h3 className="card-title">🚀 Modern Topics Detected</h3>
                      </div>
                      <div className="modern-topics">
                        <div className="modernity-score">
                          Modernity Score: {analysis.content_quality.modern_topics.modernity_score?.toFixed(0)}%
                        </div>
                        <div className="topics-detected">
                          {analysis.content_quality.modern_topics.detected?.map((topic, idx) => (
                            <div key={idx} className="topic-tag detected">
                              ✓ {topic.category}
                            </div>
                          ))}
                        </div>
                        {analysis.content_quality.modern_topics.missing_suggestions?.length > 0 && (
                          <div className="missing-topics">
                            <p><strong>Consider adding:</strong></p>
                            {analysis.content_quality.modern_topics.missing_suggestions.map((topic, idx) => (
                              <span key={idx} className="topic-tag missing">{topic}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'content' && (
                <div className="results-grid">
                  {/* Content Depth */}
                  {analysis.content_quality?.content_depth && (
                    <div className="card">
                      <div className="card-header">
                        <h3 className="card-title">📚 Content Depth Analysis</h3>
                      </div>
                      <div className="depth-analysis">
                        <div className="depth-distribution">
                          {Object.entries(analysis.content_quality.content_depth.depth_distribution || {}).map(([level, count]) => (
                            <div key={level} className="depth-item">
                              <span className={`depth-badge ${level}`}>{level}</span>
                              <span className="depth-count">{count} units</span>
                            </div>
                          ))}
                        </div>
                        <p>Total Topics: {analysis.content_quality.content_depth.total_topics}</p>
                      </div>
                    </div>
                  )}

                  {/* Hours Distribution */}
                  {analysis.content_quality?.hours_distribution && (
                    <div className="card wide-card">
                      <div className="card-header">
                        <h3 className="card-title">⏰ Hours Distribution</h3>
                        {!analysis.content_quality.hours_distribution.is_balanced && (
                          <span className="badge badge-warning">Imbalanced</span>
                        )}
                      </div>
                      <div className="hours-chart">
                        {analysis.content_quality.hours_distribution.distribution?.map((item, idx) => (
                          <div key={idx} className="hours-bar-container">
                            <div className="hours-label">U{item.unit_number}</div>
                            <div className="hours-bar-wrapper">
                              <div
                                className="hours-bar"
                                style={{ width: `${item.percentage}%` }}
                              >
                                {item.hours}h
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="hours-summary">
                        Total: {analysis.content_quality.hours_distribution.total_hours}h |
                        Avg: {analysis.content_quality.hours_distribution.average_hours?.toFixed(1)}h/unit
                      </div>
                    </div>
                  )}

                  {/* Learning Progression */}
                  {analysis.content_quality?.learning_progression && (
                    <div className="card">
                      <div className="card-header">
                        <h3 className="card-title">📈 Learning Progression</h3>
                        {analysis.content_quality.learning_progression.is_proper_progression ? (
                          <span className="badge badge-success">✓ Proper</span>
                        ) : (
                          <span className="badge badge-warning">⚠ Issues</span>
                        )}
                      </div>
                      <div className="progression-flow">
                        {analysis.content_quality.learning_progression.progression?.map((item, idx) => (
                          <div key={idx} className={`progression-item ${item.level}`}>
                            <span className="prog-unit">U{item.unit_number}</span>
                            <span className="prog-level">{item.level}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Redundancies */}
                  {analysis.redundancies?.redundant_topics?.length > 0 && (
                    <div className="card">
                      <div className="card-header">
                        <h3 className="card-title">🔄 Redundancies Detected</h3>
                      </div>
                      <div className="redundancy-list">
                        {analysis.redundancies.redundant_topics.slice(0, 5).map((item, idx) => (
                          <div key={idx} className="redundancy-item">
                            <span className="similarity">{(item.similarity * 100).toFixed(0)}% similar</span>
                            <p>{item.topic1?.substring(0, 50)} ↔ {item.topic2?.substring(0, 50)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'structure' && (
                <div className="results-grid">
                  {/* Structural Issues */}
                  <div className="card wide-card">
                    <div className="card-header">
                      <h3 className="card-title">🏗️ Structural Analysis</h3>
                    </div>
                    <div className="structure-analysis">
                      <div className="structure-stats">
                        <div className="stat-box">
                          <span className="stat-num">{analysis.content_gaps?.total_units || 0}</span>
                          <span>Units</span>
                        </div>
                        <div className="stat-box">
                          <span className="stat-num">{analysis.content_gaps?.total_hours || 0}</span>
                          <span>Hours</span>
                        </div>
                        <div className="stat-box">
                          <span className="stat-num">{analysis.content_gaps?.reference_count || 0}</span>
                          <span>References</span>
                        </div>
                      </div>
                      {analysis.structural_issues?.length > 0 && (
                        <div className="issues-list">
                          <h4>Issues Found:</h4>
                          {analysis.structural_issues.map((issue, idx) => (
                            <div key={idx} className={`issue-item severity-${issue.severity}`}>
                              <span className="issue-badge">{issue.severity}</span>
                              {issue.description}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'recommendations' && (
                <div className="card recommendations-card">
                  <div className="card-header">
                    <h3 className="card-title">📋 Recommendations</h3>
                  </div>
                  <ul className="recommendations-list">
                    {analysis.recommendations?.map((rec, idx) => (
                      <li key={idx} className="recommendation-item">
                        <span className="rec-icon">✓</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style>{`
        .analyze-page {
          padding: 2rem 0;
          min-height: 100vh;
          background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
          transition: background var(--transition-base);
        }
        
        .container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 1.5rem;
        }
        
        .page-header {
          text-align: center;
          margin-bottom: 2rem;
        }
        
        .page-title {
          font-size: 2.5rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        
        .upload-section {
          margin-bottom: 2rem;
        }

        .upload-area {
          text-align: center;
          padding: 2rem;
        }

        .upload-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }

        .file-info {
          margin-top: 1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
        }

        .file-name {
          padding: 0.5rem 1rem;
          background: var(--bg-tertiary);
          border-radius: 8px;
          color: var(--text-primary);
        }

        .export-bar {
          display: flex;
          justify-content: flex-end;
          margin-bottom: 1.5rem;
          gap: 10px;
        }

        /* Score Dashboard */
        .score-dashboard {
          display: flex;
          align-items: center;
          gap: 2rem;
          background: var(--bg-primary);
          padding: 2rem;
          border-radius: 16px;
          margin-bottom: 1.5rem;
          box-shadow: var(--shadow-lg);
          border: 1px solid var(--border);
          transition: background var(--transition-base);
        }

        .score-circle {
          width: 140px;
          height: 140px;
          border-radius: 50%;
          border: 8px solid;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          background: var(--bg-primary);
        }

        .score-value {
          font-size: 3rem;
          font-weight: 700;
          line-height: 1;
          color: var(--text-primary);
        }

        .score-max {
          font-size: 1rem;
          color: var(--text-secondary);
        }

        .score-details {
          flex: 1;
        }

        .score-details h2 {
          margin: 0 0 0.5rem 0;
          font-size: 1.5rem;
          color: var(--text-primary);
        }

        .score-status {
          color: var(--text-secondary);
          margin-bottom: 1rem;
        }

        .score-breakdown {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .breakdown-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 0.9rem;
          color: var(--text-primary);
        }

        .breakdown-item span:first-child {
          width: 120px;
          text-transform: capitalize;
        }

        .breakdown-bar {
          flex: 1;
          height: 8px;
          background: var(--bg-tertiary);
          border-radius: 4px;
          overflow: hidden;
        }

        .breakdown-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--primary), var(--secondary));
          border-radius: 4px;
        }

        /* Tabs */
        .tab-nav {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
          background: var(--bg-primary);
          padding: 0.5rem;
          border-radius: 12px;
          border: 1px solid var(--border);
        }

        .tab-btn {
          padding: 0.75rem 1.5rem;
          border: none;
          background: transparent;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.2s;
          color: var(--text-secondary);
        }

        .tab-btn.active {
          background: linear-gradient(135deg, var(--primary), var(--secondary));
          color: white;
        }

        .tab-btn:hover:not(.active) {
          background: var(--bg-hover);
          color: var(--text-primary);
        }

        .results-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .card {
          background: var(--bg-primary);
          border-radius: 12px;
          box-shadow: var(--shadow-md);
          overflow: hidden;
          border: 1px solid var(--border);
          transition: background var(--transition-base), border-color var(--transition-base);
        }

        .wide-card {
          grid-column: 1 / -1;
        }

        .card-header {
          padding: 1rem 1.25rem;
          border-bottom: 1px solid var(--border);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .card-title {
          margin: 0;
          font-size: 1rem;
          font-weight: 600;
          color: var(--text-primary);
        }

        /* Bloom's Analysis */
        .bloom-analysis {
          padding: 1rem;
        }

        .bloom-item {
          margin-bottom: 0.75rem;
        }

        .bloom-label {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.25rem;
          font-weight: 500;
          font-size: 0.9rem;
          color: var(--text-primary);
        }

        .bloom-bar {
          height: 8px;
          background: var(--bg-tertiary);
          border-radius: 4px;
          overflow: hidden;
        }

        .bloom-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--primary), var(--secondary));
        }

        /* Stats */
        .mapping-stats {
          display: flex;
          justify-content: space-around;
          padding: 1.5rem;
        }

        .stat-item {
          text-align: center;
        }

        .stat-value {
          font-size: 2.5rem;
          font-weight: 700;
          color: var(--primary);
        }

        .stat-label {
          color: var(--text-secondary);
          font-size: 0.875rem;
        }

        /* Modern Topics */
        .modern-topics {
          padding: 1rem;
        }

        .modernity-score {
          font-weight: 600;
          margin-bottom: 1rem;
          color: var(--primary);
        }

        .topic-tag {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          margin: 0.25rem;
          font-size: 0.85rem;
        }

        .topic-tag.detected {
          background: hsla(142, 71%, 45%, 0.15);
          color: var(--success);
        }

        .topic-tag.missing {
          background: hsla(45, 100%, 51%, 0.15);
          color: hsl(45, 100%, 35%);
        }

        [data-theme="dark"] .topic-tag.detected {
          background: hsla(142, 71%, 45%, 0.25);
          color: hsl(142, 71%, 65%);
        }

        [data-theme="dark"] .topic-tag.missing {
          background: hsla(45, 100%, 51%, 0.25);
          color: hsl(45, 100%, 65%);
        }

        /* Hours Chart */
        .hours-chart {
          padding: 1rem;
        }

        .hours-bar-container {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.5rem;
        }

        .hours-label {
          width: 30px;
          font-weight: 600;
          font-size: 0.85rem;
          color: var(--text-primary);
        }

        .hours-bar-wrapper {
          flex: 1;
          background: var(--bg-tertiary);
          border-radius: 4px;
          height: 24px;
        }

        .hours-bar {
          height: 100%;
          background: linear-gradient(90deg, var(--primary), var(--secondary));
          border-radius: 4px;
          display: flex;
          align-items: center;
          padding-left: 0.5rem;
          color: white;
          font-size: 0.8rem;
          font-weight: 500;
          min-width: 40px;
        }

        .hours-summary {
          text-align: center;
          padding: 0.75rem;
          color: var(--text-secondary);
          font-size: 0.9rem;
        }

        /* Progression */
        .progression-flow {
          display: flex;
          gap: 0.5rem;
          padding: 1rem;
          flex-wrap: wrap;
        }

        .progression-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          font-size: 0.85rem;
        }

        .progression-item.introductory { background: hsla(210, 100%, 50%, 0.15); color: hsl(210, 80%, 50%); }
        .progression-item.intermediate { background: hsla(45, 100%, 50%, 0.15); color: hsl(45, 100%, 35%); }
        .progression-item.advanced { background: hsla(142, 71%, 45%, 0.15); color: hsl(142, 71%, 40%); }

        [data-theme="dark"] .progression-item.introductory { background: hsla(210, 100%, 50%, 0.25); color: hsl(210, 80%, 65%); }
        [data-theme="dark"] .progression-item.intermediate { background: hsla(45, 100%, 50%, 0.25); color: hsl(45, 100%, 65%); }
        [data-theme="dark"] .progression-item.advanced { background: hsla(142, 71%, 45%, 0.25); color: hsl(142, 71%, 65%); }

        /* Depth */
        .depth-distribution {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          padding: 1rem;
        }

        .depth-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .depth-analysis p {
          color: var(--text-secondary);
          padding: 0 1rem 1rem;
        }

        .depth-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .depth-badge.basic { background: hsla(0, 84%, 60%, 0.15); color: hsl(0, 84%, 50%); }
        .depth-badge.intermediate { background: hsla(45, 100%, 50%, 0.15); color: hsl(45, 100%, 35%); }
        .depth-badge.advanced { background: hsla(142, 71%, 45%, 0.15); color: hsl(142, 71%, 40%); }

        [data-theme="dark"] .depth-badge.basic { background: hsla(0, 84%, 60%, 0.25); color: hsl(0, 84%, 70%); }
        [data-theme="dark"] .depth-badge.intermediate { background: hsla(45, 100%, 50%, 0.25); color: hsl(45, 100%, 65%); }
        [data-theme="dark"] .depth-badge.advanced { background: hsla(142, 71%, 45%, 0.25); color: hsl(142, 71%, 65%); }

        .depth-count {
          color: var(--text-secondary);
          margin-left: 0.5rem;
        }

        /* Badges */
        .badge {
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .badge-primary { background: var(--primary); color: white; }
        .badge-success { background: var(--success); color: white; }
        .badge-warning { background: var(--warning); color: white; }

        /* Structure */
        .structure-stats {
          display: flex;
          gap: 2rem;
          padding: 1.5rem;
          justify-content: center;
        }

        .stat-box {
          text-align: center;
        }

        .stat-box span:last-child {
          color: var(--text-secondary);
          font-size: 0.875rem;
        }

        .stat-num {
          display: block;
          font-size: 2rem;
          font-weight: 700;
          color: var(--primary);
        }

        .structure-analysis {
          color: var(--text-primary);
        }

        .issues-list {
          padding: 1rem;
          border-top: 1px solid var(--border);
        }

        .issues-list h4 {
          color: var(--text-primary);
          margin-bottom: 0.75rem;
        }

        .issue-item {
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          border-radius: 8px;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          color: var(--text-primary);
        }

        .issue-item.severity-high { 
          background: hsla(0, 84%, 60%, 0.15); 
          border-left: 3px solid hsl(0, 84%, 60%);
        }
        .issue-item.severity-medium { 
          background: hsla(45, 100%, 50%, 0.15); 
          border-left: 3px solid hsl(45, 100%, 50%);
        }

        [data-theme="dark"] .issue-item.severity-high { 
          background: hsla(0, 84%, 60%, 0.2); 
        }
        [data-theme="dark"] .issue-item.severity-medium { 
          background: hsla(45, 100%, 50%, 0.2); 
        }

        .issue-badge {
          padding: 0.15rem 0.5rem;
          border-radius: 4px;
          font-size: 0.7rem;
          text-transform: uppercase;
          font-weight: 600;
          background: var(--bg-tertiary);
          color: var(--text-primary);
        }

        /* Recommendations */
        .recommendations-list {
          list-style: none;
          padding: 1rem;
          margin: 0;
        }

        .recommendation-item {
          display: flex;
          gap: 0.75rem;
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          background: var(--bg-secondary);
          border-radius: 8px;
          color: var(--text-primary);
          border-left: 3px solid var(--success);
        }

        .rec-icon {
          color: var(--success);
          font-weight: 700;
        }

        .assessment-info {
          padding: 1rem;
        }

        .assessment-item {
          display: flex;
          justify-content: space-between;
          padding: 0.5rem 0;
          border-bottom: 1px solid var(--border);
          text-transform: capitalize;
          color: var(--text-primary);
        }

        .alert {
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1rem;
        }

        .alert-error {
          background: hsla(0, 84%, 60%, 0.15);
          border: 1px solid hsl(0, 84%, 60%);
          color: var(--error);
        }

        [data-theme="dark"] .alert-error {
          background: hsla(0, 84%, 60%, 0.2);
        }

        .redundancy-list {
          padding: 1rem;
        }

        .redundancy-item {
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          background: var(--bg-secondary);
          border-radius: 8px;
        }

        .redundancy-item .similarity {
          font-size: 0.75rem;
          color: var(--primary);
          font-weight: 600;
        }

        .redundancy-item p {
          font-size: 0.875rem;
          color: var(--text-secondary);
          margin: 0.25rem 0 0;
        }

        .fade-in {
          animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

export default AnalyzePage;

