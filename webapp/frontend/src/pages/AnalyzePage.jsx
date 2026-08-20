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
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/export/pdf`, {
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
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#fbe9e7] text-[#d32f2f] rounded-full text-xs font-semibold mb-4">
          <BarChart2 size={14} />
          <span>Deep Content Analysis</span>
        </div>
        <h1 className="page-title font-serif">Analyze Syllabus</h1>
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
            <div className="card mb-6 bg-[#efe8de]/30 border-[#d4c8b8]">
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
                        <div className="flex-1 h-2 bg-[#d4c8b8] rounded-full overflow-hidden">
                          <div className="h-full bg-[#5c4033] rounded-full" style={{ width: `${(value / 25) * 100}%` }}></div>
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
            {['overview', 'content', 'structure', 'compliance', 'recommendations'].map(tab => (
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
                  <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d4c8b8]">
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
                  <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d4c8b8]">
                    <h3 className="font-bold text-lg flex items-center gap-2">
                      <Layers size={20} className="text-brand" />
                      CO-PO Mapping Status
                    </h3>
                    <InfoTooltip text="Alignment of Course Outcomes with Program Outcomes." />
                  </div>
                  <div className="grid grid-cols-3 gap-4 py-4 text-center">
                    <div className="p-4 bg-[#efe8de]/30 rounded-lg">
                      <div className="text-2xl font-bold text-primary mb-1">{analysis.co_po_mapping_gaps?.total_cos || 0}</div>
                      <div className="text-xs font-semibold text-subtle uppercase">Total COs</div>
                    </div>
                    <div className="p-4 bg-[#efe8de]/30 rounded-lg">
                      <div className="text-2xl font-bold text-[#d32f2f] mb-1">{analysis.co_po_mapping_gaps?.mapped_cos || 0}</div>
                      <div className="text-xs font-semibold text-subtle uppercase">Mapped</div>
                    </div>
                    <div className="p-4 bg-[#efe8de]/30 rounded-lg">
                      <div className="text-2xl font-bold text-[#2e7d32] mb-1">{(analysis.co_po_mapping_gaps?.coverage_percentage || 0).toFixed(0)}%</div>
                      <div className="text-xs font-semibold text-subtle uppercase">Coverage</div>
                    </div>
                  </div>

                  {/* Modern Topics */}
                  {analysis.content_quality?.modern_topics && (
                    <div className="mt-6 pt-6 border-t border-[#d4c8b8]">
                      <h4 className="font-bold text-sm mb-3 text-subtle uppercase tracking-wider">Modern Topics Detection</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.content_quality.modern_topics.detected?.map((topic, idx) => (
                          <span key={idx} className="badge badge-success bg-[#e8f5e9] text-[#2e7d32] border border-[#a5d6a7]">
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
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d4c8b8]">
                      <h3 className="font-bold text-lg flex items-center gap-2">
                        <FileText size={20} className="text-brand" />
                        Content Depth Analysis
                      </h3>
                      <div className="text-sm text-subtle font-medium bg-[#efe8de]/30 px-3 py-1 rounded-full">
                        Total Topics: {analysis.content_quality.content_depth.total_topics}
                      </div>
                    </div>
                    <div className="grid md:grid-cols-4 gap-4">
                      {Object.entries(analysis.content_quality.content_depth.depth_distribution || {}).map(([level, count]) => (
                        <div key={level} className="p-4 rounded-lg bg-[#efe8de]/30 border border-[#d4c8b8] text-center">
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
                    <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#d4c8b8]">
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
                          <div className="w-16 font-bold text-sm text-subtle">Unit {item.unit_number}</div>
                          <div className="flex-1 bg-[#efe8de] h-8 rounded-md overflow-hidden relative group">
                            <div className="absolute inset-y-0 left-0 bg-[#5c4033] rounded-md flex items-center px-2 text-xs font-bold text-white transition-all group-hover:bg-[#3d2e1f]" style={{ width: `${Math.max(item.percentage, 5)}%` }}>
                              {item.hours}h
                            </div>
                          </div>
                          <div className="w-20 text-right text-xs text-subtle font-medium">
                            {typeof item.percentage === 'number' ? item.percentage.toFixed(1) : item.percentage}%
                          </div>
                          {item.topic_count !== undefined && (
                            <div className="w-20 text-xs text-subtle">{item.topic_count} topics</div>
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="mt-6 pt-4 border-t border-[#d4c8b8] flex justify-between text-sm text-subtle">
                      <span>Total: <span className="font-bold text-primary">{analysis.content_quality.hours_distribution.total_hours}h</span></span>
                      <span>Avg: <span className="font-bold text-primary">{analysis.content_quality.hours_distribution.average_hours}h/unit</span></span>
                      {analysis.content_quality.hours_distribution.average_hours_per_topic !== undefined && (
                        <span>Avg/Topic: <span className="font-bold text-primary">{analysis.content_quality.hours_distribution.average_hours_per_topic}h</span></span>
                      )}
                    </div>
                  </div>
                )}

                {/* Unit Theory Analysis */}
                {analysis.content_quality?.unit_analysis && (
                  <div className="card">
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d4c8b8]">
                      <h3 className="font-bold text-lg flex items-center gap-2">
                        <Layers size={20} className="text-brand" />
                        Unit Content Analysis
                      </h3>
                      <div className="text-sm text-subtle bg-[#efe8de]/30 px-3 py-1 rounded-full">
                        {analysis.content_quality.unit_analysis.summary}
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div className="p-4 bg-[#fbe9e7] rounded-lg border border-[#d32f2f]/20 text-center">
                        <div className="text-2xl font-bold text-[#d32f2f]">{analysis.content_quality.unit_analysis.theory_ratio}%</div>
                        <div className="text-xs font-semibold text-[#d32f2f] uppercase">Theory Content</div>
                      </div>
                      <div className="p-4 bg-[#e8f5e9] rounded-lg border border-[#a5d6a7] text-center">
                        <div className="text-2xl font-bold text-[#2e7d32]">{analysis.content_quality.unit_analysis.practical_ratio}%</div>
                        <div className="text-xs font-semibold text-[#2e7d32] uppercase">Practical Content</div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      {analysis.content_quality.unit_analysis.units?.map((unit, idx) => (
                        <div key={idx} className="p-4 bg-[#efe8de]/30 rounded-lg border border-[#d4c8b8]">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold">Unit {unit.unit_number}: {unit.title}</span>
                            <span className="text-sm text-subtle">{unit.hours}h | {unit.total_topics} topics</span>
                          </div>
                          <div className="flex items-center gap-2 mb-2">
                            <div className="flex-1 bg-[#d4c8b8] h-2 rounded-full overflow-hidden">
                              <div className="h-full bg-[#d32f2f]" style={{ width: `${unit.theory_percentage}%` }}></div>
                            </div>
                            <span className="text-xs text-subtle w-16">{unit.theory_percentage}% theory</span>
                          </div>
                          {unit.key_concepts?.length > 0 && (
                            <div className="text-xs text-subtle">
                              <span className="font-medium">Key concepts:</span> {unit.key_concepts.join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Redundancies */}
                {analysis.redundancies?.redundant_topics?.length > 0 && (
                  <div className="card border-[#d32f2f]/20">
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d32f2f]/20">
                      <h3 className="font-bold text-lg flex items-center gap-2 text-[#d32f2f]">
                        <AlertTriangle size={20} />
                        Redundancies Detected
                      </h3>
                    </div>
                    <div className="grid gap-3">
                      {analysis.redundancies.redundant_topics.slice(0, 5).map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-[#fbe9e7] rounded-lg border border-[#d32f2f]/20 text-sm">
                          <div className="flex items-center gap-3">
                            <span className="font-semibold text-[#3d2e1f]">{item.topic1?.substring(0, 30)}...</span>
                            <span className="text-[#8b7e6f]">↔</span>
                            <span className="font-semibold text-[#3d2e1f]">{item.topic2?.substring(0, 30)}...</span>
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
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#d4c8b8]">
                  <h3 className="font-bold text-lg flex items-center gap-2">
                    <Shield size={20} className="text-brand" />
                    Structural Integrity
                  </h3>
                </div>

                <div className="grid grid-cols-3 gap-6 mb-8 text-center text-sm">
                  <div className="p-4 bg-[#efe8de]/30 border border-[#d4c8b8] rounded-lg">
                    <div className="font-bold text-3xl text-primary mb-1">{analysis.content_gaps?.total_units || 0}</div>
                    <div className="uppercase tracking-wider text-xs text-subtle font-semibold">Units Found</div>
                  </div>
                  <div className="p-4 bg-[#efe8de]/30 border border-[#d4c8b8] rounded-lg">
                    <div className="font-bold text-3xl text-primary mb-1">{analysis.content_gaps?.total_hours || 0}</div>
                    <div className="uppercase tracking-wider text-xs text-subtle font-semibold">Total Hours</div>
                  </div>
                  <div className="p-4 bg-[#efe8de]/30 border border-[#d4c8b8] rounded-lg">
                    <div className="font-bold text-3xl text-primary mb-1">{analysis.content_gaps?.reference_count || 0}</div>
                    <div className="uppercase tracking-wider text-xs text-subtle font-semibold">References</div>
                  </div>
                </div>

                {analysis.structural_issues?.length > 0 ? (
                  <div className="space-y-3">
                    <h4 className="font-bold text-sm text-subtle uppercase tracking-wider mb-2">Identified Issues</h4>
                    {analysis.structural_issues.map((issue, idx) => (
                      <div key={idx} className={`p-4 rounded-lg flex items-start gap-3 text-sm ${issue.severity === 'high' ? 'bg-[#fbe9e7] text-[#c62828] border-[#d32f2f]/20' : 'bg-[#fff3e0] text-[#e65100] border-[#e65100]/20'} border`}>
                        {issue.severity === 'high' ? <AlertTriangle size={18} className="shrink-0 mt-0.5" /> : <InfoTooltip size={18} className="shrink-0 mt-0.5" />}
                        <div>
                          <span className="font-bold uppercase text-xs block mb-1 opacity-75">{issue.severity} Severity</span>
                          {issue.description}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center bg-[#e8f5e9] rounded-lg border border-[#a5d6a7] text-[#2e7d32]">
                    <CheckCircle size={32} className="mx-auto mb-3 text-[#2e7d32]" />
                    <h4 className="font-bold text-lg">No Structural Issues Found</h4>
                    <p className="text-sm opacity-80">The syllabus structure appears to be sound and compliant.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'compliance' && (
              <div className="grid gap-6">
                {/* NEP 2020 Compliance */}
                <div className="card">
                  <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d4c8b8]">
                    <h3 className="font-bold text-lg flex items-center gap-2">
                      <Shield size={20} className="text-brand" />
                      NEP 2020 Compliance
                    </h3>
                    {analysis.nep_2020_compliance?.compliance_score !== undefined && (
                      <span className={`badge ${analysis.nep_2020_compliance.compliance_score >= 70 ? 'badge-success' : analysis.nep_2020_compliance.compliance_score >= 50 ? 'badge-warning' : 'badge-error'}`}>
                        {analysis.nep_2020_compliance.compliance_score}% Compliant
                      </span>
                    )}
                  </div>

                  {analysis.nep_2020_compliance?.checks && (
                    <div className="space-y-3">
                      {Object.entries(analysis.nep_2020_compliance.checks).map(([key, check]) => (
                        <div key={key} className={`p-4 rounded-lg border ${check.passed ? 'bg-[#e8f5e9] border-[#a5d6a7]' : 'bg-[#fff3e0] border-[#e65100]/20'}`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium capitalize">{key.replace(/_/g, ' ')}</span>
                            {check.passed ? (
                              <CheckCircle size={16} className="text-[#2e7d32]" />
                            ) : (
                              <AlertTriangle size={16} className="text-[#e65100]" />
                            )}
                          </div>
                          {check.details && <p className="text-sm text-subtle">{check.details}</p>}
                        </div>
                      ))}
                    </div>
                  )}

                  {analysis.nep_2020_compliance?.recommendations?.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-[#d4c8b8]">
                      <h4 className="font-semibold text-sm mb-2 text-subtle">NEP 2020 Recommendations</h4>
                      <ul className="list-disc ml-5 space-y-1 text-sm">
                        {analysis.nep_2020_compliance.recommendations.slice(0, 5).map((rec, idx) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* NBA/NAAC Accreditation */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* NBA Compliance */}
                  <div className="card">
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d4c8b8]">
                      <h3 className="font-bold text-lg">NBA Compliance</h3>
                      {analysis.accreditation_compliance?.nba?.compliance_score !== undefined && (
                        <span className={`badge ${analysis.accreditation_compliance.nba.compliance_score >= 70 ? 'badge-success' : 'badge-warning'}`}>
                          {analysis.accreditation_compliance.nba.compliance_score}%
                        </span>
                      )}
                    </div>
                    <div className="space-y-2 text-sm">
                      {analysis.accreditation_compliance?.nba?.checks && Object.entries(analysis.accreditation_compliance.nba.checks).slice(0, 4).map(([key, check]) => (
                        <div key={key} className="flex items-center justify-between py-2 border-b border-[#d4c8b8]/50">
                          <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                          {check.passed ? (
                            <CheckCircle size={14} className="text-[#2e7d32]" />
                          ) : (
                            <AlertTriangle size={14} className="text-[#e65100]" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* NAAC Compliance */}
                  <div className="card">
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d4c8b8]">
                      <h3 className="font-bold text-lg">NAAC Compliance</h3>
                      {analysis.accreditation_compliance?.naac?.compliance_score !== undefined && (
                        <span className={`badge ${analysis.accreditation_compliance.naac.compliance_score >= 70 ? 'badge-success' : 'badge-warning'}`}>
                          {analysis.accreditation_compliance.naac.compliance_score}%
                        </span>
                      )}
                    </div>
                    <div className="space-y-2 text-sm">
                      {analysis.accreditation_compliance?.naac?.checks && Object.entries(analysis.accreditation_compliance.naac.checks).slice(0, 4).map(([key, check]) => (
                        <div key={key} className="flex items-center justify-between py-2 border-b border-[#d4c8b8]/50">
                          <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                          {check.passed ? (
                            <CheckCircle size={14} className="text-[#2e7d32]" />
                          ) : (
                            <AlertTriangle size={14} className="text-[#e65100]" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="card">
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#d4c8b8]">
                  <h3 className="font-bold text-lg flex items-center gap-2">
                    <CheckCircle size={20} className="text-brand" />
                    AI Recommendations
                  </h3>
                  <div className="text-sm text-subtle">
                    {analysis.recommendations?.length || 0} Suggestions
                  </div>
                </div>
                <ul className="space-y-3">
                  {analysis.recommendations?.map((rec, idx) => {
                    // Support both string and object format
                    const text = typeof rec === 'string' ? rec : rec.text;
                    const priority = typeof rec === 'object' ? rec.priority : null;
                    const priorityColors = {
                      high: 'bg-[#fbe9e7] text-[#c62828] border-[#d32f2f]/20',
                      medium: 'bg-[#fff3e0] text-[#e65100] border-[#e65100]/20',
                      low: 'bg-[#fbe9e7] text-[#d32f2f] border-[#d4c8b8]'
                    };

                    return (
                      <li key={idx} className="flex gap-4 p-4 rounded-lg bg-[#efe8de]/30 border border-[#d4c8b8] group hover:border-brand-light hover:bg-white hover:shadow-sm transition-all">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-brand-light text-brand flex items-center justify-center font-bold text-xs mt-0.5">{idx + 1}</span>
                        <div className="flex-1">
                          <span className="text-sm text-primary leading-relaxed">{text}</span>
                        </div>
                        {priority && (
                          <span className={`flex-shrink-0 text-xs font-semibold px-2 py-1 rounded border ${priorityColors[priority] || ''}`}>
                            {priority.toUpperCase()}
                          </span>
                        )}
                      </li>
                    );
                  })}
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
