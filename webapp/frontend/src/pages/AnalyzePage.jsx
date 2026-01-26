import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertTriangle, BarChart2, PieChart, Clock, Layers, Shield, Download, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';
import { InfoTooltip } from '../components/Tooltip';

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
    if (score >= 80) return 'var(--success)';
    if (score >= 60) return 'var(--warning)';
    if (score >= 40) return '#f97316';
    return 'var(--error)';
  };

  const analysis = analysisResults?.analysis;
  const qualityScore = analysis?.content_quality?.quality_score;

  return (
    <div className="container animate-fade-in">
      <div className="page-header">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-semibold mb-4">
          <BarChart2 size={14} />
          <span>Deep Content Analysis</span>
        </div>
        <h1 className="page-title">Analyze Syllabus</h1>
        <p className="page-subtitle">
          Comprehensive syllabus evaluation with actionable insights
        </p>
      </div>

      {/* Upload Section */}
      <div className="mb-8">
        <div className="card">
          <div className="upload-area">
            <div className="upload-icon">
              <Upload size={48} />
            </div>
            <h3 className="text-lg font-bold mb-2">Upload Syllabus Document</h3>
            <p className="text-subtle mb-6">Supports PDF, DOCX, and TXT files</p>

            <input
              type="file"
              id="file-upload"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />

            <div className="flex justify-center gap-4 items-center">
              <label htmlFor="file-upload" className="btn btn-secondary">
                {analyzeFile ? 'Change File' : 'Choose File'}
              </label>

              {analyzeFile && (
                <button onClick={handleUpload} className="btn btn-primary" disabled={loading}>
                  {loading ? (
                    <>
                      <RefreshCw className="animate-spin" size={16} />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <BarChart2 size={16} />
                      Analyze
                    </>
                  )}
                </button>
              )}
            </div>

            {analyzeFile && (
              <div className="mt-4 text-sm text-brand font-medium flex items-center justify-center gap-2">
                <FileText size={16} /> {analyzeFile.name}
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error flex items-center gap-2">
          <AlertTriangle size={16} />
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Analysis Results */}
      {analysis && (
        <div className="animate-fade-in">
          {/* Export Buttons */}
          <div className="flex justify-end mb-6">
            <button onClick={handleExportPDF} className="btn btn-secondary">
              <Download size={16} />
              Export PDF Report
            </button>
          </div>

          {/* Quality Score Dashboard */}
          {qualityScore && (
            <div className="card mb-6 bg-slate-50 border-slate-200">
              <div className="flex flex-col md:flex-row items-center gap-8 p-4">
                <div className="relative flex items-center justify-center h-32 w-32 rounded-full border-8 bg-white" style={{ borderColor: getScoreColor(qualityScore.total_score) }}>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-primary">{qualityScore.total_score}</div>
                    <div className="text-xs text-subtle font-semibold">/ 100</div>
                  </div>
                </div>

                <div className="flex-1 w-full">
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-2xl font-bold">Quality Score: {qualityScore.grade}</h2>
                    <span className="badge badge-neutral">{qualityScore.status}</span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    {Object.entries(qualityScore.breakdown || {}).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-3 text-sm">
                        <span className="w-32 capitalize font-medium text-subtle">{key.replace(/_/g, ' ')}</span>
                        <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(value / 25) * 100}%` }}></div>
                        </div>
                        <span className="font-bold w-8 text-right">{value}</span>
                      </div>
                    ))}
                  </div>
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
          <div className="mb-12">
            {activeTab === 'overview' && (
              <div className="grid md:grid-cols-2 gap-6">
                {/* Bloom's Coverage */}
                <div className="card h-full">
                  <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100">
                    <h3 className="font-bold text-lg flex items-center gap-2">
                      <PieChart size={20} className="text-brand" />
                      Bloom's Taxonomy Coverage
                    </h3>
                    <InfoTooltip text="Distribution of cognitive levels across the syllabus using Bloom's Taxonomy." />
                  </div>
                  <div className="space-y-4">
                    {Object.entries(analysis.bloom_coverage?.percentages || {}).map(([level, percentage]) => (
                      <div key={level}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="font-medium capitalize">{level}</span>
                          <span className="font-bold text-primary">{percentage.toFixed(1)}%</span>
                        </div>
                        <div className="progress-container">
                          <div className="progress-fill" style={{ width: `${percentage}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* CO-PO Mapping */}
                <div className="card h-full">
                  <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100">
                    <h3 className="font-bold text-lg flex items-center gap-2">
                      <Layers size={20} className="text-brand" />
                      CO-PO Mapping Status
                    </h3>
                    <InfoTooltip text="Alignment of Course Outcomes with Program Outcomes." />
                  </div>
                  <div className="grid grid-cols-3 gap-4 py-4 text-center">
                    <div className="p-4 bg-slate-50 rounded-lg">
                      <div className="text-2xl font-bold text-primary mb-1">{analysis.co_po_mapping_gaps?.total_cos || 0}</div>
                      <div className="text-xs font-semibold text-subtle uppercase">Total COs</div>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-lg">
                      <div className="text-2xl font-bold text-indigo-600 mb-1">{analysis.co_po_mapping_gaps?.mapped_cos || 0}</div>
                      <div className="text-xs font-semibold text-subtle uppercase">Mapped</div>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-lg">
                      <div className="text-2xl font-bold text-emerald-600 mb-1">{(analysis.co_po_mapping_gaps?.coverage_percentage || 0).toFixed(0)}%</div>
                      <div className="text-xs font-semibold text-subtle uppercase">Coverage</div>
                    </div>
                  </div>

                  {/* Modern Topics */}
                  {analysis.content_quality?.modern_topics && (
                    <div className="mt-6 pt-6 border-t border-gray-100">
                      <h4 className="font-bold text-sm mb-3 text-subtle uppercase tracking-wider">Modern Topics Detection</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.content_quality.modern_topics.detected?.map((topic, idx) => (
                          <span key={idx} className="badge badge-success bg-emerald-50 text-emerald-700 border border-emerald-100">
                            {topic.category}
                          </span>
                        ))}
                        {analysis.content_quality.modern_topics.detected?.length === 0 && (
                          <span className="text-sm text-subtle italic">No modern topics specifically categorized.</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'content' && (
              <div className="grid gap-6">
                {/* Content Depth */}
                {analysis.content_quality?.content_depth && (
                  <div className="card">
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100">
                      <h3 className="font-bold text-lg flex items-center gap-2">
                        <FileText size={20} className="text-brand" />
                        Content Depth Analysis
                      </h3>
                      <div className="text-sm text-subtle font-medium bg-slate-50 px-3 py-1 rounded-full">
                        Total Topics: {analysis.content_quality.content_depth.total_topics}
                      </div>
                    </div>
                    <div className="grid md:grid-cols-4 gap-4">
                      {Object.entries(analysis.content_quality.content_depth.depth_distribution || {}).map(([level, count]) => (
                        <div key={level} className="p-4 rounded-lg bg-slate-50 border border-slate-100 text-center">
                          <div className="uppercase text-xs font-bold text-subtle mb-2 tracking-wider">{level}</div>
                          <div className="text-2xl font-bold text-primary">{count}</div>
                          <div className="text-xs text-subtle mt-1">units</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Hours Distribution */}
                {analysis.content_quality?.hours_distribution && (
                  <div className="card">
                    <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
                      <h3 className="font-bold text-lg flex items-center gap-2">
                        <Clock size={20} className="text-brand" />
                        Hours Distribution
                      </h3>
                      {!analysis.content_quality.hours_distribution.is_balanced && (
                        <span className="badge badge-warning">Imbalanced Structure</span>
                      )}
                    </div>

                    <div className="space-y-4">
                      {analysis.content_quality.hours_distribution.distribution?.map((item, idx) => (
                        <div key={idx} className="flex items-center gap-4">
                          <div className="w-12 font-bold text-sm text-subtle">Unit {item.unit_number}</div>
                          <div className="flex-1 bg-slate-100 h-8 rounded-md overflow-hidden relative group">
                            <div className="absolute inset-y-0 left-0 bg-indigo-500 rounded-md flex items-center px-2 text-xs font-bold text-white transition-all group-hover:bg-indigo-600" style={{ width: `${Math.max(item.percentage, 5)}%` }}>
                              {item.hours}h
                            </div>
                          </div>
                          <div className="w-12 text-right text-xs text-subtle font-medium">{item.percentage}%</div>
                        </div>
                      ))}
                    </div>
                    <div className="mt-6 pt-4 border-t border-gray-100 text-center text-sm text-subtle">
                      Total: <span className="font-bold text-primary">{analysis.content_quality.hours_distribution.total_hours}h</span> |
                      Avg: <span className="font-bold text-primary">{analysis.content_quality.hours_distribution.average_hours?.toFixed(1)}h/unit</span>
                    </div>
                  </div>
                )}

                {/* Redundancies */}
                {analysis.redundancies?.redundant_topics?.length > 0 && (
                  <div className="card border-orange-100">
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-orange-100">
                      <h3 className="font-bold text-lg flex items-center gap-2 text-orange-700">
                        <AlertTriangle size={20} />
                        Redundancies Detected
                      </h3>
                    </div>
                    <div className="grid gap-3">
                      {analysis.redundancies.redundant_topics.slice(0, 5).map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-100 text-sm">
                          <div className="flex items-center gap-3">
                            <span className="font-semibold text-orange-800">{item.topic1?.substring(0, 30)}...</span>
                            <span className="text-orange-400">↔</span>
                            <span className="font-semibold text-orange-800">{item.topic2?.substring(0, 30)}...</span>
                          </div>
                          <span className="badge badge-warning text-xs">{(item.similarity * 100).toFixed(0)}% Match</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'structure' && (
              <div className="card">
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
                  <h3 className="font-bold text-lg flex items-center gap-2">
                    <Shield size={20} className="text-brand" />
                    Structural Integrity
                  </h3>
                </div>

                <div className="grid grid-cols-3 gap-6 mb-8 text-center text-sm">
                  <div className="p-4 bg-slate-50 border border-slate-100 rounded-lg">
                    <div className="font-bold text-3xl text-primary mb-1">{analysis.content_gaps?.total_units || 0}</div>
                    <div className="uppercase tracking-wider text-xs text-subtle font-semibold">Units Found</div>
                  </div>
                  <div className="p-4 bg-slate-50 border border-slate-100 rounded-lg">
                    <div className="font-bold text-3xl text-primary mb-1">{analysis.content_gaps?.total_hours || 0}</div>
                    <div className="uppercase tracking-wider text-xs text-subtle font-semibold">Total Hours</div>
                  </div>
                  <div className="p-4 bg-slate-50 border border-slate-100 rounded-lg">
                    <div className="font-bold text-3xl text-primary mb-1">{analysis.content_gaps?.reference_count || 0}</div>
                    <div className="uppercase tracking-wider text-xs text-subtle font-semibold">References</div>
                  </div>
                </div>

                {analysis.structural_issues?.length > 0 ? (
                  <div className="space-y-3">
                    <h4 className="font-bold text-sm text-subtle uppercase tracking-wider mb-2">Identified Issues</h4>
                    {analysis.structural_issues.map((issue, idx) => (
                      <div key={idx} className={`p-4 rounded-lg flex items-start gap-3 text-sm ${issue.severity === 'high' ? 'bg-red-50 text-red-800 border-red-100' : 'bg-yellow-50 text-yellow-800 border-yellow-100'} border`}>
                        {issue.severity === 'high' ? <AlertTriangle size={18} className="shrink-0 mt-0.5" /> : <InfoTooltip size={18} className="shrink-0 mt-0.5" />}
                        <div>
                          <span className="font-bold uppercase text-xs block mb-1 opacity-75">{issue.severity} Severity</span>
                          {issue.description}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center bg-green-50 rounded-lg border border-green-100 text-green-800">
                    <CheckCircle size={32} className="mx-auto mb-3 text-green-600" />
                    <h4 className="font-bold text-lg">No Structural Issues Found</h4>
                    <p className="text-sm opacity-80">The syllabus structure appears to be sound and compliant.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="card">
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100">
                  <h3 className="font-bold text-lg flex items-center gap-2">
                    <CheckCircle size={20} className="text-brand" />
                    AI Recommendations
                  </h3>
                  <div className="text-sm text-subtle">
                    {analysis.recommendations?.length || 0} Suggestions
                  </div>
                </div>
                <ul className="space-y-3">
                  {analysis.recommendations?.map((rec, idx) => (
                    <li key={idx} className="flex gap-4 p-4 rounded-lg bg-slate-50 border border-slate-100 group hover:border-brand-light hover:bg-white hover:shadow-sm transition-all">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-brand-light text-brand flex items-center justify-center font-bold text-xs mt-0.5">{idx + 1}</span>
                      <span className="text-sm text-primary leading-relaxed">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyzePage;
