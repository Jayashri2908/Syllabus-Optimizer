import React, { useState } from 'react';
import { Upload, Download, FileText, CheckCircle, AlertTriangle, Zap, BarChart2, PieChart, Layers, Target, BookOpen, Shield, RefreshCw, Lightbulb, ArrowRight, Layout } from 'lucide-react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';
import { BloomDistributionChart, BloomBalanceChart, COPOHeatmap } from '../components/Charts';
import '../components/Charts.css';

// Simple markdown to HTML converter for AI-generated content
const simpleMarkdown = (text) => {
  if (!text) return '';

  // Clean up special Unicode characters that don't render well
  text = text
    .replace(/■/g, '•')  // Replace black squares with bullets
    .replace(/□/g, '○')  // Replace white squares with circles
    .replace(/▪/g, '•')  // Replace small black squares
    .replace(/►/g, '→');  // Replace arrows

  return text
    // Headers
    .replace(/^### (.+)$/gm, '<h4 class="font-bold text-sm uppercase text-[#2a1f14] mt-4 mb-2">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="font-bold text-base text-primary mt-6 mb-3">$1</h3>')
    .replace(/^# (.+)$/gm, '<h2 class="font-bold text-lg text-primary mt-8 mb-4">$1</h2>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-bold text-primary">$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em class="italic text-[#5c5446]">$1</em>')
    // Bullet points
    .replace(/^[•●○] (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
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

      // Get optimization suggestions - returns full response with new structure
      const optResponse = await apiService.optimizeSyllabus(syllabusData);

      setOptimizationResults(optResponse);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to optimize syllabus');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      // Send syllabus data and optimization results separately
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          syllabus_data: optimizationResults.optimized_syllabus,
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

      a.download = `${optimizationResults.optimized_syllabus?.course_code || 'syllabus'}_optimized.${ext}`;
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
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#fbe9e7] text-[#d32f2f] rounded-full text-xs font-semibold mb-4">
          <Zap size={14} />
          <span>AI-Powered Optimization</span>
        </div>
        <h1 className="page-title font-serif">Optimize Syllabus</h1>
        <p className="page-subtitle">
          Get intelligent suggestions to enhance your curriculum structure and content
        </p>
      </div>

      {!optimizationResults ? (
        <div className="mb-12">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-5 gap-12 items-center">
              {/* Left Column: Upload Card */}
              <div className="lg:col-span-3">
                <div className="card text-center p-10 hover:shadow-xl transition-all duration-300 border-dashed border-2 border-[#d4c8b8]/60 bg-[#faf7f2]/50 backdrop-blur-sm">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-[#fbe9e7] text-[#d32f2f] rounded-full mb-6">
                    <Zap size={40} />
                  </div>
                  <h3 className="text-xl font-bold text-[#2a1f14] mb-2">Upload Syllabus for Optimization</h3>
                  <p className="text-[#5c5446] mb-8 max-w-sm mx-auto">Get comprehensive AI insights, gap analysis, and modernize your curriculum in seconds.</p>

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

              {/* Right Column: Key Benefits */}
              <div className="lg:col-span-2 space-y-6">
                <div>
                  <h3 className="text-2xl font-extrabold text-primary font-serif mb-2">Why Optimize?</h3>
                  <p className="text-subtle">Engineered to elevate educational standards through intelligent curriculum refinement.</p>
                </div>

                <div className="space-y-4">
                  {[
                    { icon: Target, title: 'Gap Analysis', desc: 'Identify missing core concepts and industry-relevant topics.' },
                    { icon: Lightbulb, title: 'AI Modernization', desc: 'Update outdated terminology and introduce emerging concepts.' },
                    { icon: Shield, title: 'Compliance Check', desc: 'Ensure alignment with NEP 2020 and accreditation standards.' }
                  ].map((feature, idx) => (
                    <div key={idx} className="flex gap-4 p-4 rounded-xl bg-[#faf7f2] border border-[#d4c8b8] shadow-sm hover:shadow-md transition-all">
                      <div className="p-2 bg-[#fbe9e7] text-[#d32f2f] rounded-lg shrink-0">
                        <feature.icon size={20} />
                      </div>
                      <div>
                        <h4 className="font-bold text-primary text-sm">{feature.title}</h4>
                        <p className="text-xs text-subtle leading-relaxed">{feature.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="p-4 rounded-xl bg-[#3d2e1f] text-white shadow-lg overflow-hidden relative">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -translate-x-8 -translate-y-8"></div>
                  <div className="relative z-10 flex items-center gap-4">
                    <div className="p-2 bg-white/20 rounded-lg">
                      <Zap size={20} />
                    </div>
                    <div>
                      <p className="text-xs font-bold uppercase tracking-wider opacity-80">Pro Tip</p>
                      <p className="text-sm font-medium">Large documents take longer to process but provide deeper insights.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-8 animate-bouncy-reveal">
          {/* Export Buttons */}
          {/* Export Buttons */}
          <div className="flex justify-end gap-3 sticky top-4 z-50">
            <button
              onClick={() => handleExport('pdf')}
              className="btn bg-white border border-[#d4c8b8] text-[#3d2e1f] shadow-sm hover:shadow-md hover:border-[#d32f2f]/40 hover:text-[#d32f2f] transition-all text-sm flex items-center gap-2 rounded-lg px-4 py-2.5"
            >
              <Download size={16} className="" />
              Export PDF
            </button>
            <button
              onClick={() => handleExport('word')}
              className="btn bg-white border border-[#d4c8b8] text-[#3d2e1f] shadow-sm hover:shadow-md hover:border-[#5c4033]/40 hover:text-[#5c4033] transition-all text-sm flex items-center gap-2 rounded-lg px-4 py-2.5"
            >
              <FileText size={16} className="" />
              Export Word
            </button>
          </div>

          {/* Optimization Summary & Rationale */}
          {/* Optimization Summary & Rationale */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="card bg-white border border-[#d4c8b8] shadow-sm rounded-xl p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-[#fbe9e7] rounded-full translate-x-8 -translate-y-8 opacity-50"></div>
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-[#fbe9e7] text-[#d32f2f] rounded-lg">
                    <Zap size={20} />
                  </div>
                  <h3 className="font-bold text-lg text-[#2a1f14] font-serif">Optimization Rationale</h3>
                </div>
                <p className="text-[#5c5446] leading-relaxed text-sm">
                  {optimizationResults.optimization?.rationale || "The syllabus has been optimized for better learning outcomes and industry alignment."}
                </p>
              </div>
            </div>

            <div className="card bg-white border border-[#a5d6a7] shadow-sm rounded-xl p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-[#e8f5e9] rounded-full translate-x-8 -translate-y-8 opacity-50"></div>
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-[#e8f5e9] text-[#2e7d32] rounded-lg">
                    <CheckCircle size={20} />
                  </div>
                  <h3 className="font-bold text-lg text-[#2a1f14] font-serif">Key Improvements</h3>
                </div>
                <ul className="space-y-3">
                  {optimizationResults.optimization?.changes_summary?.map((change, idx) => (
                    <li key={idx} className="flex gap-3 text-sm text-[#5c5446] bg-[#efe8de]/30 p-2 rounded-lg border border-[#d4c8b8]">
                      <div className="mt-1 shrink-0">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#2e7d32] mt-1.5"></div>
                      </div>
                      {typeof change === 'object' ? (
                        <div className="flex flex-col w-full">
                          <span className="font-semibold text-[#2a1f14] mb-0.5">{change.aspect}</span>
                          <span className="text-[#5c5446] text-xs mb-1.5">{change.impact}</span>
                          {change.original && change.optimized && (
                            <div className="grid grid-cols-2 gap-2 text-[10px] items-center bg-[#faf7f2] p-1.5 rounded border border-[#d4c8b8]/50">
                              <div className="text-[#c62828] line-through opacity-80 truncate" title={change.original}>{change.original}</div>
                              <div className="text-[#2e7d32] font-medium truncate" title={change.optimized}>{change.optimized}</div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <span>{change}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Side-by-Side Comparison */}
          {/* Side-by-Side Comparison */}
          <div className="space-y-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-[#fbe9e7] text-[#d32f2f] rounded-lg">
                <Layout size={24} />
              </div>
              <div>
                <h3 className="font-bold text-xl text-[#2a1f14] font-serif">Side-by-Side Comparison</h3>
                <p className="text-sm text-[#5c5446]">Review the transformation from original to optimized curriculum</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {/* Original Syllabus */}
              <div className="flex flex-col h-full">
                <div className="flex items-center justify-between px-5 py-3 bg-[#efe8de]/50 rounded-t-xl border-x border-t border-[#d4c8b8]">
                  <span className="font-bold text-[#5c5446] uppercase text-xs tracking-wider flex items-center gap-2">
                    <Layers size={14} /> Original
                  </span>
                  <span className="bg-[#d4c8b8] text-[#5c5446] px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide">Baseline</span>
                </div>
                <SyllabusView syllabus={optimizationResults.original_syllabus} />
              </div>

              {/* Optimized Syllabus */}
              <div className="flex flex-col h-full relative">
                <div className="absolute -top-3 -right-3 z-20">
                  <span className="flex h-6 w-6 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-6 w-6 bg-brand"></span>
                  </span>
                </div>

                <div className="flex items-center justify-between px-5 py-3 bg-[#3d2e1f] rounded-t-xl border-x border-t border-[#3d2e1f] shadow-md z-10">
                  <span className="font-bold text-white uppercase text-xs tracking-wider flex items-center gap-2">
                    <Zap size={14} className="fill-current" /> Optimized
                  </span>
                  <span className="bg-white/20 text-white px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide backdrop-blur-sm">AI Enhanced</span>
                </div>
                <SyllabusView syllabus={optimizationResults.optimized_syllabus} isOptimized={true} />
              </div>
            </div>
          </div>



          {/* Bloom's Analysis */}
          {optimizationResults.optimization?.bloom_distribution && (
            <div className="card">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-[#d4c8b8]">
                <PieChart className="text-brand" size={24} />
                <h3 className="font-bold text-lg text-[#2a1f14] font-serif">Bloom's Taxonomy Analysis</h3>
              </div>
              <div className="grid md:grid-cols-2 gap-8 items-center">
                <div className="space-y-4">
                  <p className="text-sm text-[#5c5446]">
                    Distribution of cognitive levels in the optimized syllabus:
                  </p>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(optimizationResults.optimization.bloom_distribution).map(([level, value]) => (
                      <div key={level} className="p-3 bg-[#efe8de]/30 rounded border border-[#d4c8b8]">
                        <div className="text-[10px] font-bold text-[#8b7e6f] uppercase">{level}</div>
                        <div className="text-lg font-bold text-[#d32f2f]">{value}%</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="h-64">
                  {/* Simplified chart or message if data is basic */}
                  <BloomDistributionChart data={optimizationResults.optimization.bloom_distribution} />
                </div>
              </div>
            </div>
          )}

          {/* CO-PO Mapping */}
          {optimizationResults.optimization?.co_po_mapping && (
            <div className="card border border-[#d4c8b8] shadow-sm rounded-xl overflow-hidden p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-[#efe8de] text-[#5c4033] rounded-lg">
                  <Target size={20} />
                </div>
                <h3 className="font-bold text-lg text-[#2a1f14] font-serif">CO-PO Mapping Matrix (Optimized)</h3>
              </div>
              <div className="h-[400px] w-full">
                <COPOHeatmap mapping={optimizationResults.optimization.co_po_mapping} />
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

// Helper Components for Side-by-Side Comparison
const SyllabusView = ({ syllabus, isOptimized = false }) => {
  if (!syllabus) return <div className="card text-center p-8 text-[#8b7e6f]">No data available</div>;

  return (
    <div className={`card ${isOptimized ? 'border-2 border-[#d32f2f]/20 bg-white shadow-xl shadow-[#d32f2f]/5' : 'border border-[#d4c8b8] bg-white shadow-sm'} rounded-b-xl rounded-t-none h-[600px] overflow-y-auto custom-scrollbar p-6 transition-all duration-300`}>
      <div className="space-y-8">
        {/* Header */}
          <div className="pb-4 border-b border-[#d4c8b8]">
          <div className="flex justify-between items-start">
            <div>
              <h4 className={`text-xs font-bold uppercase tracking-wider ${isOptimized ? 'text-[#d32f2f]' : 'text-[#5c5446]'} mb-1`}>
                {syllabus.course_code || "CODE"}
              </h4>
              <h2 className="text-xl font-bold text-[#2a1f14] leading-tight">{syllabus.course_title || "Course Title"}</h2>
            </div>
            {syllabus.credits && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-[#efe8de] text-[#3d2e1f] border border-[#d4c8b8]">
                Credits: {syllabus.credits}
              </span>
            )}
          </div>
        </div>

        {/* Outcomes */}
        <div>
          <h4 className="flex items-center gap-2 text-xs font-bold text-[#8b7e6f] uppercase tracking-wider mb-4">
            <Target size={14} /> Learning Outcomes
          </h4>
          <div className="space-y-3">
            {syllabus.learning_outcomes?.map((co, idx) => (
              <div key={idx} className={`p-3 rounded-lg border text-sm group transition-colors ${isOptimized ? 'bg-[#fbe9e7]/30 border-[#d32f2f]/20 hover:border-[#d32f2f]/40' : 'bg-[#efe8de]/30 border-[#d4c8b8] hover:border-[#8b7e6f]'}`}>
                <div className="flex gap-2">
                  <span className={`font-bold mt-0.5 text-xs ${isOptimized ? 'text-[#d32f2f]' : 'text-[#5c5446]'}`}>{co.code || `CO${idx + 1}`}</span>
                  <div className="flex-1">
                    <p className="text-[#5c5446] leading-relaxed text-sm">{co.description}</p>
                    {co.bloom_level && (
                      <div className="mt-2 text-right">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide ${isOptimized ? 'bg-[#fbe9e7] text-[#d32f2f]' : 'bg-[#d4c8b8] text-[#5c5446]'}`}>
                          {co.bloom_level}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Units */}
        <div>
          <h4 className="flex items-center gap-2 text-xs font-bold text-[#8b7e6f] uppercase tracking-wider mb-4">
            <Layers size={14} /> Course Content
          </h4>
          <div className="space-y-4">
            {syllabus.units?.map((unit, idx) => (
              <div key={idx} className="bg-[#faf7f2] rounded-lg border border-[#d4c8b8] shadow-sm overflow-hidden group hover:shadow-md transition-shadow">
                <div className="bg-[#efe8de]/50 px-4 py-2 border-b border-[#d4c8b8] flex justify-between items-center">
                  <span className="font-bold text-xs text-[#5c5446] uppercase tracking-wide">Unit {unit.unit_number || idx + 1}</span>
                  {unit.hours && <span className="text-[10px] font-bold text-[#d32f2f] bg-[#fbe9e7] px-2 py-0.5 rounded-full">{unit.hours} Hours</span>}
                </div>
                <div className="p-4">
                  <h5 className="font-bold text-[#2a1f14] mb-3 text-sm leading-snug">{unit.title}</h5>
                  <ul className="space-y-2">
                    {unit.topics?.map((topic, tIdx) => (
                      <li key={tIdx} className="text-xs text-[#5c5446] flex items-start gap-2.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#8b7e6f] mt-1.5 shrink-0 group-hover:bg-[#d32f2f] transition-colors"></span>
                        <span className="leading-relaxed">{typeof topic === 'string' ? topic : (topic.name || topic.topic || JSON.stringify(topic))}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}

          </div>

          {/* Textbooks & References */}
          {(syllabus.textbooks?.length > 0 || syllabus.references?.length > 0 || syllabus.reference_books?.length > 0) && (
            <div className="space-y-6 pt-4 border-t border-[#d4c8b8]">
              {syllabus.textbooks?.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 text-xs font-bold text-[#8b7e6f] uppercase tracking-wider mb-3">
                    <BookOpen size={14} /> Textbooks
                  </h4>
                  <ul className="space-y-2">
                    {syllabus.textbooks.map((book, idx) => (
                      <li key={idx} className="bg-[#efe8de]/30 border border-[#d4c8b8] p-3 rounded-lg text-sm text-[#5c5446] leading-relaxed flex gap-2">
                        <span className="text-[#8b7e6f] font-bold text-xs mt-0.5">{idx + 1}.</span>
                        <span>{book}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {(syllabus.references?.length > 0 || syllabus.reference_books?.length > 0) && (
                <div>
                  <h4 className="flex items-center gap-2 text-xs font-bold text-[#8b7e6f] uppercase tracking-wider mb-3">
                    <BookOpen size={14} /> References
                  </h4>
                  <ul className="space-y-2">
                    {(syllabus.references || syllabus.reference_books).map((ref, idx) => (
                      <li key={idx} className="bg-[#efe8de]/30 border border-[#d4c8b8] p-3 rounded-lg text-sm text-[#5c5446] leading-relaxed flex gap-2">
                        <span className="text-[#8b7e6f] font-bold text-xs mt-0.5">{idx + 1}.</span>
                        <span>{ref}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default OptimizePage;
