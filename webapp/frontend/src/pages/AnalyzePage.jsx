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

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setAnalyzeFile(selectedFile); // Persist file
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!analyzeFile && !analysisResults) {
            setError('Please select a file');
            return;
        }

        if (analysisResults) {
            // If already analyzed, maybe confirm to re-analyze? 
            // For now, we assume if they clicked analyze again with a file selected they want to re-run
            if (!analyzeFile) return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await apiService.uploadSyllabus(analyzeFile);

            // Automatically analyze
            const analysisResponse = await apiService.analyzeSyllabus(response.data);
            setAnalysisResults({
                syllabus: response.data,
                analysis: analysisResponse.analysis
            }); // Persist
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to analyze syllabus');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="analyze-page">
            <div className="container">
                <div className="page-header">
                    <h1 className="page-title">Analyze Syllabus</h1>
                    <p className="page-subtitle">
                        Upload and analyze existing syllabi for gaps and improvements
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
                {analysisResults?.analysis && (
                    <div className="results-section fade-in">
                        <div className="results-grid">
                            {/* Bloom's Coverage */}
                            <div className="card">
                                <div className="card-header">
                                    <h3 className="card-title">Bloom's Taxonomy Coverage</h3>
                                </div>
                                <div className="bloom-analysis">
                                    {Object.entries(analysisResults.analysis.bloom_coverage.percentages).map(([level, percentage]) => (
                                        <div key={level} className="bloom-item">
                                            <div className="bloom-label">
                                                <span>{level.charAt(0).toUpperCase() + level.slice(1)}</span>
                                                <span className="bloom-percentage">{percentage.toFixed(1)}%</span>
                                            </div>
                                            <div className="bloom-bar">
                                                <div
                                                    className="bloom-fill"
                                                    style={{ width: `${percentage}%` }}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* CO-PO Mapping */}
                            <div className="card">
                                <div className="card-header">
                                    <h3 className="card-title">CO-PO Mapping Status</h3>
                                </div>
                                <div className="mapping-stats">
                                    <div className="stat-item">
                                        <div className="stat-value">{analysisResults.analysis.co_po_mapping_gaps.total_cos}</div>
                                        <div className="stat-label">Total COs</div>
                                    </div>
                                    <div className="stat-item">
                                        <div className="stat-value">{analysisResults.analysis.co_po_mapping_gaps.mapped_cos}</div>
                                        <div className="stat-label">Mapped COs</div>
                                    </div>
                                    <div className="stat-item">
                                        <div className="stat-value">{analysisResults.analysis.co_po_mapping_gaps.coverage_percentage.toFixed(0)}%</div>
                                        <div className="stat-label">Coverage</div>
                                    </div>
                                </div>
                            </div>

                            {/* Assessment Gaps */}
                            <div className="card">
                                <div className="card-header">
                                    <h3 className="card-title">Assessment Pattern</h3>
                                </div>
                                <div className="assessment-info">
                                    <p><strong>Total:</strong> {analysisResults.analysis.assessment_gaps.total_percentage}%</p>
                                    {Object.entries(analysisResults.analysis.assessment_gaps.components).map(([component, value]) => (
                                        <div key={component} className="assessment-item">
                                            <span>{component.replace(/_/g, ' ')}</span>
                                            <span className="badge badge-primary">{value}%</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Recommendations */}
                            <div className="card recommendations-card">
                                <div className="card-header">
                                    <h3 className="card-title">📋 Recommendations</h3>
                                </div>
                                <ul className="recommendations-list">
                                    {analysisResults.analysis.recommendations.map((rec, idx) => (
                                        <li key={idx} className="recommendation-item">
                                            <span className="rec-icon">✓</span>
                                            {rec}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <style>{`
        .upload-section {
          margin-bottom: var(--spacing-2xl);
        }

        .upload-area {
          text-align: center;
          padding: var(--spacing-2xl);
        }

        .upload-icon {
          font-size: 4rem;
          margin-bottom: var(--spacing-md);
        }

        .file-info {
          margin-top: var(--spacing-lg);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: var(--spacing-md);
        }

        .file-name {
          padding: var(--spacing-sm) var(--spacing-md);
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
        }

        .results-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: var(--spacing-lg);
        }

        .bloom-analysis {
          padding: var(--spacing-md);
        }

        .bloom-item {
          margin-bottom: var(--spacing-md);
        }

        .bloom-label {
          display: flex;
          justify-content: space-between;
          margin-bottom: var(--spacing-xs);
          font-weight: 600;
        }

        .bloom-bar {
          height: 8px;
          background: var(--bg-tertiary);
          border-radius: var(--radius-sm);
          overflow: hidden;
        }

        .bloom-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--primary), var(--secondary));
          transition: width var(--transition-base);
        }

        .mapping-stats {
          display: flex;
          justify-content: space-around;
          padding: var(--spacing-lg);
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

        .assessment-info {
          padding: var(--spacing-md);
        }

        .assessment-item {
          display: flex;
          justify-content: space-between;
          padding: var(--spacing-sm) 0;
          border-bottom: 1px solid var(--border);
        }

        .recommendations-card {
          grid-column: 1 / -1;
        }

        .recommendations-list {
          list-style: none;
          padding: var(--spacing-md);
        }

        .recommendation-item {
          display: flex;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm);
          margin-bottom: var(--spacing-sm);
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
        }

        .rec-icon {
          color: var(--success);
          font-weight: 700;
        }
      `}</style>
        </div>
    );
}

export default AnalyzePage;
