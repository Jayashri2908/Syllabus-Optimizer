import React, { useState } from 'react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';

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
            const response = await apiService.uploadSyllabus(file);

            // Get optimization suggestions
            const optResponse = await apiService.optimizeSyllabus(response.data);
            setOptimizationResults({
                syllabus: response.data,
                optimization: optResponse
            }); // Persist results
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to optimize syllabus');
        } finally {
            setLoading(false);
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
                        {/* Bloom's Analysis */}
                        {optimizationResults.optimization?.bloom_analysis && (
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
                                <div className="sequence-content">
                                    <p>{optimizationResults.optimization.sequence_optimization.optimization_suggestions}</p>
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
          background: hsl(142, 71%, 95%);
          color: var(--success);
        }

        .status-badge.below {
          background: hsl(45, 100%, 95%);
          color: hsl(45, 100%, 35%);
        }

        .status-badge.above {
          background: hsl(0, 84%, 95%);
          color: var(--error);
        }

        .level-stats {
          display: flex;
          justify-content: space-between;
          color: var(--text-secondary);
          font-size: 0.875rem;
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
          background: linear-gradient(135deg, var(--primary-light), hsl(280, 70%, 96%));
          color: var(--primary);
          border-radius: var(--radius-md);
          font-weight: 600;
          font-size: 0.875rem;
        }

        .sequence-content {
          padding: var(--spacing-md);
          white-space: pre-wrap;
          line-height: 1.8;
        }
      `}</style>
        </div>
    );
}

export default OptimizePage;
