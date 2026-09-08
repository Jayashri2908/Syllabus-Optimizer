import React, { useState } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { uploadAndAnalyze, exportPDF } from '../services/api';
import FileUploader from '../components/FileUploader';
import ThreeBloomChart from '../components/ThreeBloomChart';
import { ShieldAlert, CheckCircle, Download, AlertCircle, TrendingUp, BarChart3, BookOpen, Map as MapIcon, Calendar, RefreshCw, ListChecks } from 'lucide-react';
import toast from 'react-hot-toast';
import './AnalyzePage.css';

interface ScoreCardProps {
  title: string;
  value: number;
  max?: number;
  icon: React.ReactNode;
  color?: string;
}

const ScoreCard: React.FC<ScoreCardProps> = ({ title, value, icon, color = 'var(--accent-indigo)' }) => (
  <div className="score-card" style={{ borderBottomColor: color }}>
    <div className="score-icon" style={{ color }}>{icon}</div>
    <div className="score-content">
      <div className="score-value">{value}%</div>
      <div className="score-title">{title}</div>
    </div>
  </div>
);

interface GapBadgeProps {
  type: string;
  severity: string;
  description: string;
}

const GapBadge: React.FC<GapBadgeProps> = ({ type, severity, description }) => (
  <div className="gap-badge">
    <div className="gap-header">
      <AlertCircle size={14} className="gap-icon" />
      <span className="gap-type">{type}</span>
      <span className={`gap-severity gap-severity-${severity}`}>{severity}</span>
    </div>
    <p className="gap-desc">{description}</p>
  </div>
);

interface RecommendationCardProps {
  recommendation: { text: string; priority: 'high' | 'medium' | 'low'; category: string };
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const priorityColors = {
    high: 'var(--accent-red)',
    medium: 'var(--accent-yellow)',
    low: 'var(--accent-blue)'
  };
  
  return (
    <div className="recommendation-card" style={{ borderLeftColor: priorityColors[recommendation.priority] }}>
      <div className="recommendation-header">
        <span className={`priority-badge priority-${recommendation.priority}`}>{recommendation.priority}</span>
        <span className="category">{recommendation.category}</span>
      </div>
      <p className="recommendation-text">{recommendation.text}</p>
    </div>
  );
};

const AnalyzePage: React.FC = () => {
  const { currentSyllabus, setCurrentSyllabus, analysisResult, setAnalysisResult } = useSyllabus();
  const [isLoading, setIsLoading] = useState(false);

  const handleUpload = async (file: File): Promise<void> => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.docx') && !file.name.endsWith('.pdf') && !file.name.endsWith('.txt')) {
      toast.error('Please upload a valid PDF, DOCX, or TXT file.');
      return;
    }

    setIsLoading(true);
    const loadingToast = toast.loading('Parsing syllabus and detecting gaps...');
    try {
      const res = await uploadAndAnalyze(file);
      setCurrentSyllabus(res.data);
      setAnalysisResult(res.analysis);
      
      toast.success(res.cached ? 'Analysis complete (cached)!' : 'Analysis complete!', { id: loadingToast });
    } catch (err: unknown) {
      console.error(err);
      const message = err instanceof Error ? err.message : "An error occurred during analysis.";
      toast.error(message, { id: loadingToast });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (): Promise<void> => {
    if (!currentSyllabus) return;
    const t = toast.loading('Generating PDF report...');
    try {
      const blob = await exportPDF(currentSyllabus, analysisResult);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentSyllabus.course_code || 'syllabus'}_analysis.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Downloaded!', { id: t });
    } catch {
      toast.error("Failed to export PDF", { id: t });
    }
  };

  const hasAnyGaps = (analysis: typeof analysisResult) => {
    if (!analysis) return false;
    return (
      (analysis.bloom_coverage?.gaps?.length ?? 0) > 0 ||
      (analysis.co_po_mapping_gaps?.gaps?.length ?? 0) > 0 ||
      (analysis.assessment_gaps?.gaps?.length ?? 0) > 0 ||
      (analysis.content_gaps?.gaps?.length ?? 0) > 0 ||
      (analysis.structural_issues?.length ?? 0) > 0 ||
      (analysis.lesson_plan_analysis?.gaps?.length ?? 0) > 0 ||
      (analysis.redundancies?.total_redundancies ?? 0) > 0 ||
      analysis.content_quality?.overall_score < 70
    );
  };

  if (!currentSyllabus || (!analysisResult && !isLoading)) {
    return (
      <div className="page-container animate-fade-in">
        <div className="page-header">
          <h1>Gap Analyzer</h1>
          <p>Upload a syllabus document to extract course outcomes and detect pedagogical gaps.</p>
        </div>
        <div className="upload-section">
          <FileUploader onUpload={handleUpload} isLoading={isLoading} />
        </div>
      </div>
    );
  }

  const score = analysisResult?.overall_quality_score ?? Math.round((analysisResult?.content_quality?.overall_score ?? 0.75) * 100);
  const totalUnits = currentSyllabus.units?.length ?? 0;
  const totalOutcomes = currentSyllabus.learning_outcomes?.length ?? 0;

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h1>{currentSyllabus.course_code}: {currentSyllabus.course_title}</h1>
          <p>Comprehensive syllabus analysis with Bloom's Taxonomy, CO-PO mapping, and quality assessment</p>
        </div>
        <div className="actions-header">
          <button 
            className="btn-secondary" 
            onClick={() => {
              setCurrentSyllabus(null);
              setAnalysisResult(null);
            }}
          >
            <RefreshCw size={16} /> Clear & Upload New
          </button>
          <button className="btn-primary" onClick={handleExport}><Download size={18}/> Export Report</button>
        </div>
      </div>

      {!analysisResult && isLoading ? (
        <div className="glass-card p-6 animate-slide-up">
          <p>Analyzing syllabus structure and detecting gaps...</p>
        </div>
      ) : (
        <>
          <div className="analysis-grid">
            <div className="glass-card p-6" style={{ gridColumn: '1 / -1' }}>
              <h3>Overall Quality Score</h3>
              <div className="score-overview">
                <div className="score-main" style={{ background: hasAnyGaps(analysisResult) ? 'linear-gradient(135deg, #fee2e2, #fee2e2)' : 'linear-gradient(135deg, #dcfce7, #dcfce7)' }}>
                  <div className="score-big">{score}%</div>
                  <div className="score-label">Overall Quality</div>
                </div>
                <div className="score-small">
                  <ScoreCard title="Depth" value={(analysisResult?.content_quality?.depth_score ?? 0) * 100} icon={<BookOpen size={18}/>} color="var(--accent-blue)" />
                  <ScoreCard title="Breadth" value={(analysisResult?.content_quality?.breadth_score ?? 0) * 100} icon={<BarChart3 size={18}/>} color="var(--accent-green)" />
                  <ScoreCard title="Alignment" value={(analysisResult?.content_quality?.alignment_score ?? 0) * 100} icon={<MapIcon size={18}/>} color="var(--accent-purple)" />
                </div>
              </div>
            </div>

            <div className="glass-card p-6 bloom-section" style={{ gridColumn: '1 / -1' }}>
              <h3>Bloom's Taxonomy Distribution</h3>
              <div className="bloom-content">
                <div className="bloom-chart">
                  <ThreeBloomChart data={Object.fromEntries(
                    (['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'] as const).map(
                      k => [k, analysisResult?.bloom_coverage?.level_counts?.[k] ?? 0]
                    )
                  )} />
                </div>
                {analysisResult?.bloom_coverage?.gaps?.length > 0 && (
                  <div className="bloom-gaps">
                    <h4>Distribution Gaps</h4>
                    {analysisResult.bloom_coverage.gaps.map((gap, i) => (
                      <div key={i} className={`gap-item gap-${gap.issue}`}>
                        <strong>{gap.level}</strong>: {gap.current.toFixed(1)}% (recommended: {gap.recommended})
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="glass-card p-6 gap-section">
              <h3><AlertCircle size={20}/> Bloom's Gaps</h3>
              {analysisResult?.bloom_coverage?.missing_levels?.length > 0 ? (
                <div className="gap-warning">
                  <ShieldAlert size={20} className="text-amber" />
                  <div>
                    <strong>Missing Cognitive Levels</strong>
                    <p>Syllabus lacks outcomes at: {analysisResult.bloom_coverage.missing_levels.join(', ')}</p>
                  </div>
                </div>
              ) : (
                <div className="gap-ok"><CheckCircle size={16}/> All Bloom's levels represented</div>
              )}
            </div>

            <div className="glass-card p-6">
              <h3><TrendingUp size={20}/> CO-PO Mapping Coverage</h3>
              <div className="coverage-stat">
                <div className="coverage-value">{analysisResult?.co_po_mapping_gaps?.coverage_percentage?.toFixed(0) ?? 0}%</div>
                <p>{analysisResult?.co_po_mapping_gaps?.mapped_cos ?? 0} / {analysisResult?.co_po_mapping_gaps?.total_cos ?? 0} course outcomes mapped</p>
              </div>
              {analysisResult?.co_po_mapping_gaps?.gaps?.length > 0 && (
                <div className="gap-list">
                  {analysisResult.co_po_mapping_gaps.gaps.slice(0, 3).map((gap, i) => (
                    <GapBadge key={i} type={gap.type} severity="medium" description={gap.description} />
                  ))}
                </div>
              )}
            </div>

            <div className="glass-card p-6">
              <h3><Calendar size={20}/> Assessment Pattern</h3>
              <div className="assessment-stats">
                <div className="total-bar">
                  <span>Total: {analysisResult?.assessment_gaps?.total_percentage ?? 0}%</span>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${(analysisResult?.assessment_gaps?.total_percentage ?? 0)}%` }}></div>
                  </div>
                </div>
                <div className="components">
                  {(analysisResult?.assessment_gaps?.components || {}).map(([key, val]) => (
                    <span key={key} className="component-badge">{key}: {val}%</span>
                  ))}
                </div>
              </div>
              {analysisResult?.assessment_gaps?.gaps?.length > 0 && (
                <div className="gap-list">
                  {analysisResult.assessment_gaps.gaps.map((gap, i) => (
                    <GapBadge key={i} type={gap.type} severity={gap.type === 'total_mismatch' ? 'high' : 'medium'} description={gap.description} />
                  ))}
                </div>
              )}
            </div>

            <div className="glass-card p-6">
              <h3><BookOpen size={20}/> Content & Structure</h3>
              <div className="content-stats">
                <span><strong>{totalUnits}</strong> units • <strong>{totalOutcomes}</strong> outcomes • <strong>{analysisResult?.content_gaps?.reference_count ?? 0}</strong> references</span>
              </div>
              {analysisResult?.content_gaps?.gaps?.length > 0 && (
                <div className="gap-list">
                  {analysisResult.content_gaps.gaps.map((gap, i) => (
                    <GapBadge key={i} type={gap.type} severity="medium" description={gap.description} />
                  ))}
                </div>
              )}
            </div>

            <div className="glass-card p-6">
              <h3><ListChecks size={20}/> Structural Issues</h3>
              {analysisResult?.structural_issues?.length > 0 ? (
                <div className="issue-list">
                  {analysisResult.structural_issues.map((issue, i) => (
                    <GapBadge key={i} type={issue.type} severity={issue.severity} description={issue.description} />
                  ))}
                </div>
              ) : (
                <div className="issue-ok"><CheckCircle size={16}/> No structural issues detected</div>
              )}
            </div>

            <div className="glass-card p-6">
              <h3>Redundancies</h3>
              <div className="redundancy-stats">
                <span><strong>{analysisResult?.redundancies?.total_redundancies ?? 0}</strong> redundancies detected</span>
                <span className="overlap-score">Overlap score: {Math.round((analysisResult?.redundancies?.overlap_score ?? 0) * 100)}%</span>
              </div>
              {analysisResult?.redundancies?.total_redundancies > 0 ? (
                <div className="redundancy-list">
                  {analysisResult.redundancies.redundant_pairs?.slice(0, 3).map((pair, i) => (
                    <GapBadge key={i} type="overlap" severity={pair.severity} description={pair.description} />
                  ))}
                </div>
              ) : (
                <div className="issue-ok"><CheckCircle size={16}/> No significant content overlaps</div>
              )}
            </div>

            <div className="glass-card p-6">
              <h3>Lesson Plan Analysis</h3>
              {analysisResult?.lesson_plan_analysis?.status === 'no_units' ? (
                <p>No units found</p>
              ) : (
                <div className="lesson-stats">
                  <div className="lesson-row">
                    <span>{analysisResult?.lesson_plan_analysis?.units_without_hours?.length ?? 0}</span>
                    <span>units missing hours allocation</span>
                  </div>
                  {analysisResult?.lesson_plan_analysis?.units_without_methods?.length > 0 && (
                    <div className="lesson-warning">
                      <ShieldAlert size={16}/> {analysisResult.lesson_plan_analysis.units_without_methods.length} units without teaching methods
                    </div>
                  )}
                  {analysisResult?.lesson_plan_analysis?.lesson_distribution?.total_lessons && (
                    <div className="lesson-dist">
                      <p>Average: {analysisResult.lesson_plan_analysis.lesson_distribution.average_per_unit} lessons/unit</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="glass-card p-6 full-width">
              <h3>RAG Grounded Insights</h3>
              {analysisResult?.ai_analysis ? (
                <div className="ai-insight">
                  <CheckCircle size={16}/> {analysisResult.ai_analysis}
                </div>
              ) : (
                <p className="text-muted">RAG insights unavailable - using rule-based analysis.</p>
              )}
            </div>

            {analysisResult?.recommendations?.length > 0 && (
              <div className="glass-card p-6 full-width">
                <h3><ListChecks size={20}/> Actionable Recommendations</h3>
                <div className="recommendations-list">
                  {analysisResult.recommendations.map((rec, i) => (
                    <RecommendationCard key={i} recommendation={rec} />
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default AnalyzePage;