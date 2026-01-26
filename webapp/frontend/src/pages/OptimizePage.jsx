import React, { useState } from 'react';
import { Upload, Download, FileText, CheckCircle, AlertTriangle, Zap, BarChart2, PieChart, Layers, Target, BookOpen, Shield, RefreshCw, Lightbulb, ArrowRight, Layout } from 'lucide-react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';
import { BloomDistributionChart, BloomBalanceChart, COPOHeatmap } from '../components/Charts';
import '../components/Charts.css';

// Simple markdown to HTML converter for AI-generated content
const simpleMarkdown = (text) => {
  if (!text) return '';
  return text
    // Headers
    .replace(/^### (.+)$/gm, '<h4 class="font-bold text-sm uppercase text-gray-800 mt-4 mb-2">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="font-bold text-base text-primary mt-6 mb-3">$1</h3>')
    .replace(/^# (.+)$/gm, '<h2 class="font-bold text-lg text-primary mt-8 mb-4">$1</h2>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-bold text-primary">$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em class="italic text-gray-600">$1</em>')
    // Bullet points
    .replace(/^\* (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    // Numbered lists  
    .replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal">$1</li>')
    // Line breaks
    .replace(/\n\n/g, '</p><p class="mb-3">')
    .replace(/\n/g, '<br/>')
    // Wrap in paragraph
    .replace(/^/, '<p class="mb-3">')
    .replace(/$/, '</p>')
    // Fix list items (wrap consecutive li in ul)
    .replace(/(<li.*<\/li>(<br\/>)?)+/g, '<ul class="space-y-1 my-2">$&</ul>')
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
      // Send syllabus data and optimization results separately
      const response = await fetch(`http://localhost:8000/api/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          syllabus_data: optimizationResults.syllabus,
          analysis_data: optimizationResults.optimization  // Pass full optimization as analysis_data
        })
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

      a.download = `${optimizationResults.syllabus?.course_code || 'syllabus'}_optimized.${ext}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(`Export failed: ${err.message}`);
    }
  };

  return (
    <div className="container py-8 animate-bouncy-reveal">
      <div className="page-header">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-semibold mb-4">
          <Zap size={14} />
          <span>AI-Powered Optimization</span>
        </div>
        <h1 className="page-title">Optimize Syllabus</h1>
        <p className="page-subtitle">
          Get intelligent suggestions to enhance your curriculum structure and content
        </p>
      </div>

      {!optimizationResults ? (
        <div className="max-w-xl mx-auto">
          <div className="card text-center p-8 hover:shadow-lg transition-shadow border-dashed border-2 border-indigo-100">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-indigo-50 text-indigo-600 rounded-full mb-6">
              <Zap size={40} />
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Upload Syllabus for Optimization</h3>
            <p className="text-gray-500 mb-8 max-w-sm mx-auto">Get comprehensive AI insights, gap analysis, and modernize your curriculum in seconds.</p>

            <input
              type="file"
              id="optimize-upload"
              accept=".pdf,.docx,.txt"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />

            <label htmlFor="optimize-upload" className="btn btn-primary btn-lg w-full max-w-xs mx-auto flex items-center justify-center gap-2 cursor-pointer shadow-lg hover:translate-y-[-2px] transition-transform">
              {loading ? (
                <>
                  <RefreshCw className="animate-spin" size={20} />
                  Processing...
                </>
              ) : (
                <>
                  <Upload size={20} />
                  Choose Syllabus File
                </>
              )}
            </label>
          </div>
        </div>
      ) : (
        <div className="space-y-8 animate-bouncy-reveal">
          {/* Export Buttons */}
          <div className="flex justify-end gap-3 sticky top-4 z-50">
            <button
              onClick={() => handleExport('pdf')}
              className="btn btn-white shadow-md text-sm flex items-center gap-2"
            >
              <Download size={16} className="text-red-500" />
              Export PDF
            </button>
            <button
              onClick={() => handleExport('word')}
              className="btn btn-white shadow-md text-sm flex items-center gap-2"
            >
              <FileText size={16} className="text-blue-500" />
              Export Word
            </button>
          </div>

          {/* Bloom's Analysis */}
          {optimizationResults.optimization?.bloom_analysis && (
            <div className="space-y-6">
              <div className="card">
                <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
                  <PieChart className="text-brand animate-pulse" size={24} />
                  <h3 className="font-bold text-lg text-gray-800">Bloom's Taxonomy Distribution</h3>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  {Object.entries(optimizationResults.optimization.bloom_analysis.comparison).map(([level, data]) => (
                    <div key={level} className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-bold capitalize text-primary">{level}</span>
                        <span className={`badge ${data.status === 'optimal' ? 'badge-success' :
                          data.status === 'below' ? 'badge-warning' : 'badge-error'
                          }`}>
                          {data.status}
                        </span>
                      </div>
                      <div className="flex justify-between text-xs text-gray-500 mt-3">
                        <div>
                          <span className="block font-bold text-lg text-gray-800">{data.current.toFixed(1)}%</span>
                          <span>Current</span>
                        </div>
                        <div className="text-right">
                          <span className="block font-bold text-lg text-gray-400">{data.recommended_min}-{data.recommended_max}%</span>
                          <span>Target</span>
                        </div>
                      </div>

                      {/* Progress Bar for visual feedback */}
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                        <div
                          className={`h-1.5 rounded-full ${data.status === 'optimal' ? 'bg-emerald-500' :
                            data.status === 'below' ? 'bg-amber-400' : 'bg-red-400'
                            }`}
                          style={{ width: `${Math.min(data.current, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Visual Charts for Bloom's */}
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="h-80">
                    <BloomDistributionChart bloomAnalysis={optimizationResults.optimization.bloom_analysis} />
                  </div>
                  <div className="h-80">
                    <BloomBalanceChart bloomAnalysis={optimizationResults.optimization.bloom_analysis} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* CO-PO-PSO Mapping Matrix */}
          {optimizationResults.optimization?.co_po_mapping && (
            <div className="space-y-6">
              {/* Visual Heatmap Chart */}
              <div className="card">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="text-brand" size={24} />
                  <h3 className="font-bold text-lg text-gray-800">CO-PO Mapping Heatmap</h3>
                </div>
                <div className="h-96">
                  <COPOHeatmap mapping={optimizationResults.optimization.co_po_mapping} />
                </div>
              </div>

              {/* Original detailed table */}
              <div className="card overflow-hidden">
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <Layers className="text-brand" size={24} />
                    <h3 className="font-bold text-lg text-gray-800">Detailed Mapping Matrix</h3>
                  </div>
                  <p className="text-xs font-medium text-subtle bg-slate-50 px-3 py-1 rounded-full">
                    Affinity: 1-Slight, 2-Moderate, 3-Substantial
                  </p>
                </div>

                <div className="overflow-x-auto text-sm">
                  <table className="w-full border-collapse border border-slate-200">
                    <thead>
                      <tr className="bg-slate-50 text-gray-600">
                        <th className="border border-slate-200 p-2 text-center" rowSpan="2">CO No</th>
                        <th className="border border-slate-200 p-2 text-center font-bold text-primary" colSpan="9">Program Outcomes (POs)</th>
                        <th className="border border-slate-200 p-2 text-center font-bold text-primary" colSpan="4">PSOs</th>
                        <th className="border border-slate-200 p-2 text-center" rowSpan="2">BTL</th>
                      </tr>
                      <tr className="bg-slate-50 text-gray-500 text-xs uppercase cursor-default">
                        {['PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'PO9',
                          'PSO1', 'PSO2', 'PSO3', 'PSO4'].map(po => (
                            <th key={po} className="border border-slate-200 p-2 font-semibold">{po}</th>
                          ))}
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(optimizationResults.optimization.co_po_mapping).map(([co, poData], idx) => {
                        // Get Bloom's level from syllabus data
                        const coIndex = parseInt(co.replace('CO', '')) - 1;
                        const bloomLevel = optimizationResults.syllabus?.learning_outcomes?.[coIndex]?.bloom_level || 'AP';
                        const btl = bloomLevel.substring(0, 2).toUpperCase();

                        return (
                          <tr key={co} className="hover:bg-slate-50 transition-colors">
                            <td className="border border-slate-200 p-2 font-bold text-primary text-center bg-slate-50/50">{co}</td>
                            {['PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'PO9',
                              'PSO1', 'PSO2', 'PSO3', 'PSO4'].map(po => {
                                const value = poData[po] || 0;
                                let bgClass = '';
                                let textClass = 'text-gray-300';
                                if (value === 1) { bgClass = 'bg-blue-50'; textClass = 'text-blue-600 font-semibold'; }
                                if (value === 2) { bgClass = 'bg-indigo-50'; textClass = 'text-indigo-600 font-bold'; }
                                if (value === 3) { bgClass = 'bg-emerald-50'; textClass = 'text-emerald-700 font-extrabold'; }

                                return (
                                  <td key={po} className={`border border-slate-200 p-2 text-center ${bgClass} ${textClass}`}>
                                    {value > 0 ? value : '-'}
                                  </td>
                                );
                              })}
                            <td className="border border-slate-200 p-2 text-center text-xs font-bold text-gray-500 bg-slate-50/50">{btl}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Rebalancing Suggestions */}
          {optimizationResults.optimization?.rebalancing_suggestions && optimizationResults.optimization.rebalancing_suggestions.length > 0 && (
            <div className="card border-l-4 border-l-amber-400">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="text-amber-500" size={24} />
                <h3 className="font-bold text-lg text-gray-800">Rebalancing Suggestions</h3>
              </div>
              <ul className="space-y-3">
                {optimizationResults.optimization.rebalancing_suggestions.map((suggestion, idx) => (
                  <li key={idx} className="flex gap-3 text-gray-700 bg-amber-50/50 p-3 rounded-md border border-amber-100/50">
                    <ArrowRight size={18} className="text-amber-500 mt-0.5 shrink-0" />
                    <span className="text-sm">{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Modern Topics */}
          {optimizationResults.optimization?.modern_topics && optimizationResults.optimization.modern_topics.length > 0 && (
            <div className="card bg-gradient-to-br from-indigo-50 to-white">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="text-indigo-600" size={24} />
                <h3 className="font-bold text-lg text-gray-800">Modern Topics to Consider</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {optimizationResults.optimization.modern_topics.map((topic, idx) => (
                  <span key={idx} className="badge bg-white text-indigo-700 border border-indigo-200 shadow-sm px-3 py-1.5 text-sm">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Sequence Optimization */}
          {optimizationResults.optimization?.sequence_optimization && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4 pb-4 border-b border-gray-100">
                <Layout className="text-brand" size={24} />
                <h3 className="font-bold text-lg text-gray-800">Unit Sequencing Analysis</h3>
              </div>
              <div
                className="prose prose-sm max-w-none text-gray-600"
                dangerouslySetInnerHTML={{
                  __html: simpleMarkdown(optimizationResults.optimization.sequence_optimization.optimization_suggestions)
                }}
              />
            </div>
          )}

          {/* AI Analysis (shown when structured parsing was incomplete) */}
          {optimizationResults.optimization?.ai_analysis && (
            <div className="card border-2 border-indigo-100 bg-indigo-50/30">
              <div className="flex items-center gap-2 mb-4 pb-4 border-b border-indigo-100">
                <div className="p-2 bg-indigo-100 rounded-lg text-indigo-600">
                  <Zap size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-lg text-gray-800">AI-Powered Syllabus Analysis</h3>
                  <p className="text-xs text-indigo-600 font-medium uppercase tracking-wide">Deep Insight Report</p>
                </div>
              </div>
              <div
                className="prose prose-sm max-w-none text-gray-700"
                dangerouslySetInnerHTML={{
                  __html: simpleMarkdown(optimizationResults.optimization.ai_analysis)
                }}
              />
            </div>
          )}

          {/* Lesson Plan Analysis */}
          {optimizationResults.optimization?.lesson_plan_analysis && optimizationResults.optimization.lesson_plan_analysis.total_lessons > 0 && (
            <div className="card">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <BookOpen className="text-brand" size={24} />
                  <h3 className="font-bold text-lg text-gray-800">Lesson Plan Analysis</h3>
                </div>
                <div className="text-sm font-medium text-gray-500">
                  {optimizationResults.optimization.lesson_plan_analysis.total_lessons} lessons detected
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-6 mb-6">
                <div className="bg-slate-50 p-4 rounded-lg text-center border border-slate-100">
                  <div className="text-3xl font-bold text-primary">{optimizationResults.optimization.lesson_plan_analysis.total_planned_hours}</div>
                  <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-1">Total Hours</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg text-center border border-slate-100">
                  <div className="text-3xl font-bold text-indigo-600">{optimizationResults.optimization.lesson_plan_analysis.average_hours_per_lesson.toFixed(1)}</div>
                  <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-1">Avg Hrs/Lesson</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg text-center border border-slate-100">
                  {Object.keys(optimizationResults.optimization.lesson_plan_analysis.lesson_distribution?.lessons_per_unit || {}).length > 0 ? (
                    <div className="text-3xl font-bold text-emerald-600">{Object.keys(optimizationResults.optimization.lesson_plan_analysis.lesson_distribution.lessons_per_unit).length}</div>
                  ) : (
                    <div className="text-3xl font-bold text-gray-400">-</div>
                  )}
                  <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-1">Units Covered</div>
                </div>
              </div>

              {optimizationResults.optimization.lesson_plan_analysis.gaps?.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-bold text-sm text-gray-500 uppercase tracking-wider mb-2">Identified Issues</h4>
                  {optimizationResults.optimization.lesson_plan_analysis.gaps.map((gap, idx) => (
                    <div key={idx} className={`p-3 rounded-lg flex items-start gap-3 text-sm border-l-4 ${gap.severity === 'high' ? 'bg-red-50 text-red-800 border-red-500' : 'bg-blue-50 text-blue-800 border-blue-500'}`}>
                      {gap.severity === 'high' ? <AlertTriangle size={18} className="shrink-0 mt-0.5 text-red-600" /> : <div className="mt-0.5 font-bold text-blue-600">i</div>}
                      <div>
                        {gap.description}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Redundancy Detection */}
          {optimizationResults.optimization?.redundancies && optimizationResults.optimization.redundancies.enabled && (
            <div className="card">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <RefreshCw className="text-brand" size={24} />
                  <h3 className="font-bold text-lg text-gray-800">Content Redundancy Check</h3>
                </div>
                <div className="text-sm font-medium text-gray-500">
                  {optimizationResults.optimization.redundancies.total_redundancies} issues found
                </div>
              </div>

              {optimizationResults.optimization.redundancies.total_redundancies === 0 ? (
                <div className="text-center py-12 bg-green-50 rounded-lg border border-green-100">
                  <CheckCircle className="mx-auto text-green-500 mb-4" size={48} />
                  <h4 className="font-bold text-green-800 text-lg">No Redundancies Detected</h4>
                  <p className="text-green-600 text-sm mt-1">Your syllabus content appears efficient and unique.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {optimizationResults.optimization.redundancies.duplicate_topics?.length > 0 && (
                    <div>
                      <h4 className="font-bold text-sm text-gray-500 uppercase tracking-wider mb-3">Duplicate Topics</h4>
                      <div className="space-y-3">
                        {optimizationResults.optimization.redundancies.duplicate_topics.map((dup, idx) => (
                          <div key={idx} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                            <div className="flex items-center justify-between gap-4 mb-2">
                              <div className="badge badge-warning text-xs">{(dup.similarity * 100).toFixed(0)}% Similarity</div>
                            </div>
                            <div className="flex items-center gap-4 text-sm">
                              <div className="flex-1">
                                <div className="font-bold text-xs text-gray-500 uppercase mb-1">{dup.unit1}</div>
                                <div className="font-medium text-gray-800 bg-white p-2 rounded border border-gray-100">{dup.topic1}</div>
                              </div>
                              <RefreshCw size={16} className="text-gray-400" />
                              <div className="flex-1">
                                <div className="font-bold text-xs text-gray-500 uppercase mb-1">{dup.unit2}</div>
                                <div className="font-medium text-gray-800 bg-white p-2 rounded border border-gray-100">{dup.topic2}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {optimizationResults.optimization.redundancies.similar_outcomes?.length > 0 && (
                    <div>
                      <h4 className="font-bold text-sm text-gray-500 uppercase tracking-wider mb-3">Similar Outcomes</h4>
                      <div className="space-y-3">
                        {optimizationResults.optimization.redundancies.similar_outcomes.map((sim, idx) => (
                          <div key={idx} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                            <div className="flex items-center justify-between gap-4 mb-2">
                              <div className="badge badge-warning text-xs">{(sim.similarity * 100).toFixed(0)}% Similarity</div>
                            </div>
                            <div className="flex flex-col gap-3 text-sm">
                              <div className="bg-white p-3 rounded border border-gray-100">
                                <span className="font-bold text-indigo-600 text-xs mr-2">{sim.outcome1}</span>
                                <span className="text-gray-700">{sim.text1}</span>
                              </div>
                              <div className="bg-white p-3 rounded border border-gray-100">
                                <span className="font-bold text-indigo-600 text-xs mr-2">{sim.outcome2}</span>
                                <span className="text-gray-700">{sim.text2}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Objectives Optimization */}
          {optimizationResults.optimization?.objectives_optimization?.status === 'success' && (
            <div className="card">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
                <Target className="text-brand" size={24} />
                <h3 className="font-bold text-lg text-gray-800">Objectives Enhancement</h3>
              </div>
              <div className="space-y-4">
                {optimizationResults.optimization.objectives_optimization.optimized_objectives.map((o, i) => (
                  <div key={i} className="p-4 bg-slate-50 rounded-lg border border-slate-100 transition-colors hover:border-indigo-100">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-bold text-sm text-indigo-900 uppercase">Objective {i + 1}</span>
                      <div className="flex items-center gap-1 text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-100">
                        <Zap size={10} />
                        Score: {o.smart_score}/100
                      </div>
                    </div>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-xs font-semibold text-gray-400 mb-1">Original</div>
                        <p className="text-gray-500 italic">{o.original}</p>
                      </div>
                      <div className="bg-white p-3 rounded border border-indigo-50 shadow-sm relative overflow-hidden">
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-indigo-400"></div>
                        <div className="text-xs font-semibold text-indigo-400 mb-1 flex items-center gap-1">
                          <Zap size={10} /> AI Enhanced
                        </div>
                        <p className="text-gray-800 font-medium">{o.optimized}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reference Suggestions */}
          {optimizationResults.optimization?.reference_suggestions?.status === 'success' && (
            <div className="card">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
                <BookOpen className="text-brand" size={24} />
                <h3 className="font-bold text-lg text-gray-800">Reference Recommendations</h3>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                {Object.entries(optimizationResults.optimization.reference_suggestions.suggestions || {}).map(([cat, refs]) => (
                  refs && refs.length > 0 && (
                    <div key={cat} className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                      <h4 className="font-bold text-sm text-gray-700 capitalize mb-3 pb-2 border-b border-slate-200">{cat.replace(/_/g, ' ')}</h4>
                      <ul className="space-y-2">
                        {refs.slice(0, 3).map((r, i) => (
                          <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-indigo-400 mt-1.5 text-[8px] shrink-0">●</span>
                            <div>
                              <span className="font-medium text-gray-800 block">{r.title}</span>
                              {r.author && <span className="text-xs text-gray-400">{r.author}</span>}
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )
                ))}
              </div>
            </div>
          )}

          {/* Compliance Status */}
          {(optimizationResults.optimization?.nep_2020_compliance || optimizationResults.optimization?.accreditation_compliance) && (
            <div className="card">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
                <Shield className="text-brand" size={24} />
                <h3 className="font-bold text-lg text-gray-800">Compliance & Accreditation</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {optimizationResults.optimization.nep_2020_compliance?.status === 'success' && (
                  <div className="bg-gradient-to-br from-orange-50 to-white p-6 rounded-xl border border-orange-100 text-center relative overflow-hidden group hover:shadow-md transition-shadow">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                      <Shield size={60} className="text-orange-500" />
                    </div>
                    <div className="font-bold text-orange-900 mb-2">NEP 2020</div>
                    <div className="text-4xl font-extrabold text-orange-600 mb-2">
                      {optimizationResults.optimization.nep_2020_compliance.compliance_percentage}%
                    </div>
                    <div className="text-xs font-bold uppercase tracking-wider text-orange-400">{optimizationResults.optimization.nep_2020_compliance.compliance_level}</div>
                  </div>
                )}
                {optimizationResults.optimization.accreditation_compliance?.nba && (
                  <div className="bg-gradient-to-br from-blue-50 to-white p-6 rounded-xl border border-blue-100 text-center relative overflow-hidden group hover:shadow-md transition-shadow">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                      <Shield size={60} className="text-blue-500" />
                    </div>
                    <div className="font-bold text-blue-900 mb-2">NBA</div>
                    <div className="text-4xl font-extrabold text-blue-600 mb-2">
                      {optimizationResults.optimization.accreditation_compliance.nba.compliance_percentage}%
                    </div>
                    <div className="text-xs font-bold uppercase tracking-wider text-blue-400">{optimizationResults.optimization.accreditation_compliance.nba.compliance_level}</div>
                  </div>
                )}
                {optimizationResults.optimization.accreditation_compliance?.naac && (
                  <div className="bg-gradient-to-br from-emerald-50 to-white p-6 rounded-xl border border-emerald-100 text-center relative overflow-hidden group hover:shadow-md transition-shadow">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                      <Shield size={60} className="text-emerald-500" />
                    </div>
                    <div className="font-bold text-emerald-900 mb-2">NAAC</div>
                    <div className="text-4xl font-extrabold text-emerald-600 mb-2">
                      {optimizationResults.optimization.accreditation_compliance.naac.compliance_percentage}%
                    </div>
                    <div className="text-xs font-bold uppercase tracking-wider text-emerald-400">{optimizationResults.optimization.accreditation_compliance.naac.compliance_level}</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="alert alert-error mt-4 flex items-center gap-2">
          <AlertTriangle size={18} />
          <span><strong>Error:</strong> {error}</span>
        </div>
      )}
    </div>
  );
}

export default OptimizePage;
