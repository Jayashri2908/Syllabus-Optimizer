import React, { useState, useMemo } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { uploadAndAnalyze, exportPDF } from '../services/api';
import FileUploader from '../components/FileUploader';
import ThreeBloomChart from '../components/ThreeBloomChart';
import { ShieldAlert, CheckCircle, Download, AlertCircle, TrendingUp, BarChart3, BookOpen, Map as MapIcon, Calendar, RefreshCw, ListChecks, ChevronDown, ChevronUp, Zap, FileText, Target, Award, Lightbulb, AlertTriangle, Sparkles, Filter } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import './AnalyzePage.css';

interface CollapsibleCardProps {
  title: string;
  icon: React.ReactNode;
  defaultOpen?: boolean;
  badge?: string;
  badgeColor?: string;
  children: React.ReactNode;
}

const CollapsibleCard: React.FC<CollapsibleCardProps> = ({ title, icon, defaultOpen = true, badge, badgeColor, children }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="glass-card collapsible-card">
      <div className="collapsible-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="collapsible-title">
          {icon}
          <h3>{title}</h3>
          {badge && <span className="collapsible-badge" style={{ background: badgeColor || 'rgba(67,56,202,0.1)', color: badgeColor ? '#fff' : 'var(--accent-indigo)' }}>{badge}</span>}
        </div>
        {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </div>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            className="collapsible-body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

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
  recommendation: { text: string; priority: 'high' | 'medium' | 'low'; category: string; related_to?: string };
}

const categoryIcons: Record<string, React.ReactNode> = {
  bloom_taxonomy: <BarChart3 size={14} />,
  accreditation: <Award size={14} />,
  assessment: <Target size={14} />,
  content: <BookOpen size={14} />,
  structure: <AlertTriangle size={14} />,
  outcome_quality: <Lightbulb size={14} />,
  lesson_plan: <Calendar size={14} />,
  rag_insight: <Sparkles size={14} />,
};

const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const priorityColors = {
    high: 'var(--accent-rose)',
    medium: 'var(--accent-amber)',
    low: 'var(--accent-blue)'
  };
  return (
    <div className="recommendation-card" style={{ borderLeftColor: priorityColors[recommendation.priority] }}>
      <div className="recommendation-header">
        <span className={`priority-badge priority-${recommendation.priority}`}>{recommendation.priority}</span>
        <span className="category">
          {categoryIcons[recommendation.category] || <Zap size={14} />} {recommendation.category.replace(/_/g, ' ')}
        </span>
      </div>
      <p className="recommendation-text">{recommendation.text}</p>
    </div>
  );
};

type TabId = 'overview' | 'bloom' | 'compliance' | 'recommendations';
type PriorityFilter = 'all' | 'high' | 'medium' | 'low';

const AnalyzePage: React.FC = () => {
  const { currentSyllabus, setCurrentSyllabus, analysisResult, setAnalysisResult } = useSyllabus();
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>('all');

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
      const message = err instanceof Error ? err.message : 'An error occurred during analysis.';
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
      toast.error('Failed to export PDF', { id: t });
    }
  };

  const missingBloomLevels = (['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'] as const).filter(
    k => !(k in (analysisResult?.bloom_coverage?.level_counts ?? {})) || (analysisResult?.bloom_coverage?.level_counts?.[k] ?? 0) === 0
  );

  const filteredRecommendations = useMemo(() => {
    if (!analysisResult?.recommendations) return [];
    if (priorityFilter === 'all') return analysisResult.recommendations;
    return analysisResult.recommendations.filter(r => r.priority === priorityFilter);
  }, [analysisResult?.recommendations, priorityFilter]);

  const positiveFindings = useMemo(() => {
    if (!analysisResult) return [];
    const findings: string[] = [];

    if (analysisResult.bloom_coverage?.gaps?.length === 0 && (analysisResult.bloom_coverage?.total_outcomes ?? 0) > 0) {
      findings.push("Good Bloom's taxonomy distribution across cognitive levels");
    }
    if ((analysisResult.co_po_mapping_gaps?.coverage_percentage ?? 0) >= 80) {
      findings.push(`Strong CO-PO mapping coverage (${analysisResult.co_po_mapping_gaps!.coverage_percentage!.toFixed(0)}%)`);
    }
    if (analysisResult.assessment_gaps?.total_percentage === 100 && (analysisResult.assessment_gaps?.gaps?.length ?? 0) === 0) {
      findings.push("Assessment components properly total 100%");
    }
    if ((analysisResult.content_gaps?.reference_count ?? 0) >= 5) {
      findings.push(`Good reference materials (${analysisResult.content_gaps!.reference_count} references)`);
    }
    if ((analysisResult.structural_issues?.length ?? 0) === 0) {
      findings.push("No structural issues detected");
    }
    if ((analysisResult.redundancies?.total_redundancies ?? 0) === 0) {
      findings.push("No significant content redundancies");
    }
    if ((analysisResult.outcome_validation?.average_measurability ?? 0) >= 0.7) {
      findings.push(`High outcome measurability (${(analysisResult.outcome_validation!.average_measurability * 100).toFixed(0)}%)`);
    }
    if ((analysisResult.content_quality?.overall_score ?? 0) >= 0.7) {
      findings.push(`Good overall content quality (${(analysisResult.content_quality!.overall_score * 100).toFixed(0)}%)`);
    }

    return findings;
  }, [analysisResult]);

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
  const scoreColor = score >= 70 ? 'var(--accent-emerald)' : score >= 40 ? 'var(--accent-amber)' : 'var(--accent-rose)';
  const nepPct = Math.round((analysisResult?.nep_2020_compliance?.compliance_percentage as number) ?? 0);
  const nbaPct = Math.round((analysisResult?.accreditation_compliance?.nba?.compliance_percentage as number) ?? 0);
  const naacPct = Math.round((analysisResult?.accreditation_compliance?.naac?.compliance_percentage as number) ?? 0);

  const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <Target size={16} /> },
    { id: 'bloom', label: "Bloom's", icon: <BarChart3 size={16} /> },
    { id: 'compliance', label: 'Compliance', icon: <ShieldAlert size={16} /> },
    { id: 'recommendations', label: 'Actions', icon: <ListChecks size={16} /> },
  ];

  const nbaRecommendations = (analysisResult?.accreditation_compliance?.nba?.recommendations ?? []) as string[];
  const naacRecommendations = (analysisResult?.accreditation_compliance?.naac?.recommendations ?? []) as string[];

  const nepChecks = (analysisResult?.nep_2020_compliance?.detailed_checks ?? {}) as Record<string, { compliant: boolean; message: string; score: number }>;
  const nbaChecks = (analysisResult?.accreditation_compliance?.nba?.checks ?? {}) as Record<string, { compliant: boolean; message: string; score: number }>;
  const naacChecks = (analysisResult?.accreditation_compliance?.naac?.checks ?? {}) as Record<string, { compliant: boolean; message: string; score: number }>;

  const coPOMapping = currentSyllabus.co_po_mapping?.matrix ?? [];
  const poSet = new Set<string>();
  coPOMapping.forEach(entry => {
    entry.po_scores.forEach((_, idx) => {
      if (entry.po_scores[idx] > 0) poSet.add(`PO${idx + 1}`);
    });
  });

  const contentQualityIssues = (analysisResult?.content_quality?.issues ?? []) as Array<{ type: string; severity: string; unit: string; description: string }>;
  const duplicateOutcomes = (analysisResult?.redundancies?.duplicate_outcomes ?? []) as Array<{ outcome_1: string; outcome_2: string; similarity: number }>;
  const lessonDistribution = analysisResult?.lesson_plan_analysis?.lesson_distribution?.lessons_per_unit ?? {};

  return (
    <div className="analyze-page animate-fade-in">
      <div className="analyze-page-header">
        <div>
          <h1>{currentSyllabus.course_code}: {currentSyllabus.course_title}</h1>
          <p>Comprehensive syllabus analysis with Bloom's Taxonomy, CO-PO mapping, and quality assessment</p>
        </div>
        <div className="analyze-actions-header">
          <button className="btn-secondary" onClick={() => { setCurrentSyllabus(null); setAnalysisResult(null); }}>
            <RefreshCw size={16} /> Clear
          </button>
          <button className="btn-primary" onClick={handleExport}><Download size={18} /> Export Report</button>
        </div>
      </div>

      <div className="score-banner">
        <div className="score-ring-container">
          <svg className="score-ring" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="52" fill="none" stroke="var(--border-subtle)" strokeWidth="8" />
            <circle
              cx="60" cy="60" r="52" fill="none"
              stroke={scoreColor}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${(score / 100) * 327} 327`}
              transform="rotate(-90 60 60)"
              className="score-ring-fill"
            />
          </svg>
          <div className="score-ring-label">
            <span className="score-ring-value" style={{ color: scoreColor }}>{score}</span>
            <span className="score-ring-pct">%</span>
          </div>
        </div>
        <div className="score-banner-stats">
          <div className="banner-stat">
            <BookOpen size={18} />
            <div>
              <strong>{totalUnits}</strong> Units
            </div>
          </div>
          <div className="banner-stat">
            <FileText size={18} />
            <div>
              <strong>{totalOutcomes}</strong> Outcomes
            </div>
          </div>
          <div className="banner-stat">
            <Zap size={18} />
            <div>
              <strong>{analysisResult?.content_gaps?.reference_count ?? 0}</strong> References
            </div>
          </div>
          <div className="banner-stat">
            <Target size={18} />
            <div>
              <strong style={{ color: scoreColor }}>{score >= 70 ? 'Good' : score >= 40 ? 'Needs Work' : 'Critical'}</strong> Quality
            </div>
          </div>
        </div>
      </div>

      <div className="analyze-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`analyze-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div key="overview" className="tab-content" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <div className="overview-grid">
              <CollapsibleCard title="CO-PO Mapping Coverage" icon={<MapIcon size={20} />} badge={`${analysisResult?.co_po_mapping_gaps?.coverage_percentage?.toFixed(0) ?? 0}%`}>
                <div className="coverage-stat">
                  <div className="coverage-value">{analysisResult?.co_po_mapping_gaps?.coverage_percentage?.toFixed(0) ?? 0}%</div>
                  <p>{analysisResult?.co_po_mapping_gaps?.mapped_cos ?? 0} / {analysisResult?.co_po_mapping_gaps?.total_cos ?? 0} course outcomes mapped</p>
                </div>
                {coPOMapping.length > 0 && (
                  <div className="co-po-heatmap">
                    <h4>PO Coverage Heatmap</h4>
                    <div className="heatmap-grid">
                      {Array.from({ length: 12 }, (_, i) => `PO${i + 1}`).map(po => (
                        <div key={po} className={`heatmap-cell ${poSet.has(po) ? 'mapped' : 'unmapped'}`}>
                          {po}
                        </div>
                      ))}
                    </div>
                    <p className="heatmap-legend">
                      <span className="heatmap-cell mapped">Mapped</span>
                      <span className="heatmap-cell unmapped">Unmapped</span>
                    </p>
                  </div>
                )}
                {(analysisResult?.co_po_mapping_gaps?.gaps?.length ?? 0) > 0 && (
                  <div className="gap-list">
                    {analysisResult!.co_po_mapping_gaps!.gaps!.slice(0, 3).map((gap, i) => (
                      <GapBadge key={i} type={gap.type} severity="medium" description={gap.description} />
                    ))}
                  </div>
                )}
              </CollapsibleCard>

              <CollapsibleCard title="Assessment Pattern" icon={<Calendar size={20} />}>
                <div className="assessment-stats">
                  <div className="total-bar">
                    <span>Total: {analysisResult?.assessment_gaps?.total_percentage ?? 0}%</span>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${(analysisResult?.assessment_gaps?.total_percentage ?? 0)}%` }}></div>
                    </div>
                  </div>
                  <div className="components">
                    {Object.entries(analysisResult?.assessment_gaps?.components ?? {}).map(([key, val]) => (
                      <span key={key} className="component-badge">{key}: {val}%</span>
                    ))}
                  </div>
                  {(analysisResult?.assessment_gaps?.internal_total !== undefined || analysisResult?.assessment_gaps?.external_total !== undefined) && (
                    <div className="assessment-balance">
                      <span>IA: {analysisResult?.assessment_gaps?.internal_total ?? 0}%</span>
                      <span>ESE: {analysisResult?.assessment_gaps?.external_total ?? 0}%</span>
                    </div>
                  )}
                </div>
              </CollapsibleCard>

              <CollapsibleCard title="Content & Structure" icon={<BookOpen size={20} />}>
                <div className="content-stats">
                  <span><strong>{totalUnits}</strong> units &bull; <strong>{totalOutcomes}</strong> outcomes &bull; <strong>{analysisResult?.content_gaps?.reference_count ?? 0}</strong> references &bull; <strong>{analysisResult?.content_gaps?.total_topics ?? 0}</strong> topics</span>
                </div>
                {(analysisResult?.content_gaps?.gaps?.length ?? 0) > 0 && (
                  <div className="gap-list">
                    {analysisResult!.content_gaps!.gaps!.map((gap, i) => (
                      <GapBadge key={i} type={gap.type} severity="medium" description={gap.description} />
                    ))}
                  </div>
                )}
              </CollapsibleCard>

              <CollapsibleCard title="Content Quality" icon={<Sparkles size={20} />} badge={`${Math.round((analysisResult?.content_quality?.overall_score ?? 0) * 100)}%`}>
                <div className="quality-scores">
                  <div className="quality-score-item">
                    <span>Depth</span>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${(analysisResult?.content_quality?.depth_score ?? 0) * 100}%` }}></div>
                    </div>
                    <strong>{Math.round((analysisResult?.content_quality?.depth_score ?? 0) * 100)}%</strong>
                  </div>
                  <div className="quality-score-item">
                    <span>Breadth</span>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${(analysisResult?.content_quality?.breadth_score ?? 0) * 100}%` }}></div>
                    </div>
                    <strong>{Math.round((analysisResult?.content_quality?.breadth_score ?? 0) * 100)}%</strong>
                  </div>
                  <div className="quality-score-item">
                    <span>Alignment</span>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${(analysisResult?.content_quality?.alignment_score ?? 0) * 100}%` }}></div>
                    </div>
                    <strong>{Math.round((analysisResult?.content_quality?.alignment_score ?? 0) * 100)}%</strong>
                  </div>
                </div>
                {contentQualityIssues.length > 0 && (
                  <div className="gap-list">
                    {contentQualityIssues.map((issue, i) => (
                      <GapBadge key={i} type={issue.type} severity={issue.severity} description={`${issue.unit}: ${issue.description}`} />
                    ))}
                  </div>
                )}
              </CollapsibleCard>

              <CollapsibleCard title="Structural Issues" icon={<AlertCircle size={20} />} badge={`${analysisResult?.structural_issues?.length ?? 0}`}>
                {(analysisResult?.structural_issues?.length ?? 0) > 0 ? (
                  <div className="issue-list">
                    {analysisResult!.structural_issues!.map((issue, i) => (
                      <GapBadge key={i} type={issue.type} severity={issue.severity} description={issue.description} />
                    ))}
                  </div>
                ) : (
                  <div className="issue-ok"><CheckCircle size={16} /> No structural issues detected</div>
                )}
              </CollapsibleCard>

              <CollapsibleCard title="Redundancies" icon={<TrendingUp size={20} />} defaultOpen={false}>
                <div className="redundancy-stats">
                  <span><strong>{analysisResult?.redundancies?.total_redundancies ?? 0}</strong> redundancies detected</span>
                  <span className="overlap-score">Overlap score: {Math.round((analysisResult?.redundancies?.overlap_score ?? 0) * 100)}%</span>
                </div>
                {(analysisResult?.redundancies?.total_redundancies ?? 0) > 0 ? (
                  <div className="redundancy-list">
                    {analysisResult!.redundancies!.redundant_pairs?.slice(0, 3).map((pair, i) => (
                      <GapBadge key={i} type="overlap" severity={pair.severity} description={pair.description} />
                    ))}
                    {duplicateOutcomes.length > 0 && (
                      <div className="duplicate-outcomes">
                        <h4>Duplicate Outcomes</h4>
                        {duplicateOutcomes.map((dup, i) => (
                          <div key={i} className="duplicate-outcome">
                            <span className="similarity">{Math.round(dup.similarity * 100)}% similar</span>
                            <p>"{dup.outcome_1}"</p>
                            <p>"{dup.outcome_2}"</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="issue-ok"><CheckCircle size={16} /> No significant content overlaps</div>
                )}
              </CollapsibleCard>

              <CollapsibleCard title="Lesson Plan Analysis" icon={<Calendar size={20} />} defaultOpen={false}>
                {analysisResult?.lesson_plan_analysis?.status === 'no_units' ? (
                  <p>No units found</p>
                ) : (
                  <div className="lesson-stats">
                    <div className="lesson-row">
                      <span>{analysisResult?.lesson_plan_analysis?.units_without_hours?.length ?? 0}</span>
                      <span>units missing hours allocation</span>
                    </div>
                    {(analysisResult?.lesson_plan_analysis?.units_without_methods?.length ?? 0) > 0 && (
                      <div className="lesson-warning">
                        <ShieldAlert size={16} /> {analysisResult!.lesson_plan_analysis!.units_without_methods!.length} units without teaching methods
                      </div>
                    )}
                    {analysisResult?.lesson_plan_analysis?.lesson_distribution?.total_lessons && (
                      <div className="lesson-dist">
                        <p>Average: {analysisResult.lesson_plan_analysis.lesson_distribution.average_per_unit} lessons/unit</p>
                        {Object.keys(lessonDistribution).length > 0 && (
                          <table className="lesson-table">
                            <thead>
                              <tr><th>Unit</th><th>Lessons</th></tr>
                            </thead>
                            <tbody>
                              {Object.entries(lessonDistribution).map(([unit, count]) => (
                                <tr key={unit}>
                                  <td>Unit {unit}</td>
                                  <td>{count}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </CollapsibleCard>

              {positiveFindings.length > 0 && (
                <CollapsibleCard title="What's Good" icon={<Award size={20} />} badge={positiveFindings.length} badgeColor="rgba(5,150,105,0.9)" defaultOpen={true}>
                  <div className="positive-findings">
                    {positiveFindings.map((finding, i) => (
                      <div key={i} className="positive-finding">
                        <CheckCircle size={14} /> {finding}
                      </div>
                    ))}
                  </div>
                </CollapsibleCard>
              )}
            </div>
          </motion.div>
        )}

        {activeTab === 'bloom' && (
          <motion.div key="bloom" className="tab-content" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <CollapsibleCard title="Bloom's Taxonomy Distribution" icon={<BarChart3 size={20} />} defaultOpen={true}>
              <div className="bloom-content">
                <div className="bloom-chart">
                  <ThreeBloomChart data={Object.fromEntries(
                    (['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'] as const).map(
                      k => [k, analysisResult?.bloom_coverage?.level_counts?.[k] ?? 0]
                    )
                  )} />
                </div>
                <div className="bloom-counts">
                  {(['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'] as const).map(level => (
                    <div key={level} className="bloom-count-item">
                      <span className="bloom-level-name">{level}</span>
                      <span className="bloom-level-count">{analysisResult?.bloom_coverage?.level_counts?.[level] ?? 0} outcomes</span>
                      <span className="bloom-level-pct">({((analysisResult?.bloom_coverage?.percentages?.[level] ?? 0)).toFixed(1)}%)</span>
                    </div>
                  ))}
                </div>
                {(analysisResult?.bloom_coverage?.gaps?.length ?? 0) > 0 && (
                  <div className="bloom-gaps">
                    <h4>Distribution Gaps</h4>
                    {analysisResult!.bloom_coverage!.gaps!.map((gap, i) => (
                      <div key={i} className={`gap-item gap-${gap.issue}`}>
                        <strong>{gap.level}</strong>: {gap.current.toFixed(1)}% (recommended: {gap.recommended})
                        {gap.issue === 'unknown_level' && <span className="gap-count">({gap.count} outcomes)</span>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CollapsibleCard>

            <CollapsibleCard
              title="Missing Cognitive Levels"
              icon={<ShieldAlert size={20} />}
              badge={missingBloomLevels.length > 0 ? `${missingBloomLevels.length} missing` : 'Complete'}
              badgeColor={missingBloomLevels.length > 0 ? 'rgba(217,119,6,0.9)' : 'rgba(5,150,105,0.9)'}
              defaultOpen={true}
            >
              {missingBloomLevels.length > 0 ? (
                <div className="gap-warning">
                  <ShieldAlert size={20} className="text-amber" />
                  <div>
                    <strong>Missing Cognitive Levels</strong>
                    <p>Syllabus lacks outcomes at: {missingBloomLevels.join(', ')}</p>
                  </div>
                </div>
              ) : (
                <div className="gap-ok"><CheckCircle size={16} /> All Bloom's levels represented</div>
              )}
            </CollapsibleCard>

            <CollapsibleCard title="Outcome Validation" icon={<ListChecks size={20} />} defaultOpen={false}>
              {analysisResult?.outcome_validation ? (
                <div className="outcome-validation">
                  <div className="validation-stats">
                    <span className="stat-pair"><strong>{analysisResult.outcome_validation.valid_outcomes}</strong> / {analysisResult.outcome_validation.total_outcomes} valid</span>
                    <span className="stat-pair">Avg measurability: <strong>{Math.round(analysisResult.outcome_validation.average_measurability * 100)}%</strong></span>
                  </div>
                  {analysisResult.outcome_validation.outcomes.filter(o => !o.is_valid).map((outcome, i) => (
                    <div key={i} className="outcome-issue">
                      <div className="outcome-header">
                        <span className="outcome-code">{outcome.code}</span>
                        <span className="gap-severity gap-severity-high">needs improvement</span>
                      </div>
                      <p className="outcome-desc">{outcome.description}</p>
                      {outcome.issues.length > 0 && (
                        <ul className="outcome-issues-list">
                          {outcome.issues.map((issue, j) => (<li key={j}>{issue}</li>))}
                        </ul>
                      )}
                      {outcome.suggestions.length > 0 && (
                        <div className="outcome-suggestions">
                          {outcome.suggestions.map((suggestion, j) => (
                            <p key={j} className="outcome-suggestion">{suggestion}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted">No outcome validation data available.</p>
              )}
            </CollapsibleCard>
          </motion.div>
        )}

        {activeTab === 'compliance' && (
          <motion.div key="compliance" className="tab-content" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <div className="compliance-grid">
              <CollapsibleCard title="NEP 2020 Compliance" icon={<FileText size={20} />} badge={`${nepPct}%`} defaultOpen={true}>
                {analysisResult?.nep_2020_compliance ? (
                  <div className="compliance-section">
                    <div className="compliance-header">
                      <span className="compliance-pct">{nepPct}%</span>
                      <span className={`compliance-level ${nepPct >= 70 ? 'level-good' : 'level-needs-work'}`}>
                        {(analysisResult.nep_2020_compliance.compliance_level as string) ?? 'Unknown'}
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${nepPct}%` }}></div>
                    </div>
                    {Object.keys(nepChecks).length > 0 && (
                      <div className="criteria-breakdown">
                        <h4>Criteria Breakdown</h4>
                        {Object.entries(nepChecks).map(([key, check]) => (
                          <div key={key} className={`criterion-item ${check.compliant ? 'pass' : 'fail'}`}>
                            <span className="criterion-status">{check.compliant ? '✓' : '✗'}</span>
                            <span className="criterion-name">{key.replace(/_/g, ' ')}</span>
                            <span className="criterion-score">{Math.round(check.score)}%</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-muted">NEP 2020 compliance data unavailable.</p>
                )}
              </CollapsibleCard>

              <CollapsibleCard title="Accreditation (NBA/NAAC)" icon={<ShieldAlert size={20} />} defaultOpen={true}>
                <div className="accreditation-grid">
                  <div className="accred-item">
                    <span className="accred-label">NBA</span>
                    <span className="accred-pct">{nbaPct}%</span>
                  </div>
                  <div className="accred-item">
                    <span className="accred-label">NAAC</span>
                    <span className="accred-pct">{naacPct}%</span>
                  </div>
                </div>
                {Object.keys(nbaChecks).length > 0 && (
                  <div className="criteria-breakdown">
                    <h4>NBA Criteria</h4>
                    {Object.entries(nbaChecks).map(([key, check]) => (
                      <div key={key} className={`criterion-item ${check.compliant ? 'pass' : 'fail'}`}>
                        <span className="criterion-status">{check.compliant ? '✓' : '✗'}</span>
                        <span className="criterion-name">{key.replace(/_/g, ' ')}</span>
                        <span className="criterion-score">{Math.round(check.score)}%</span>
                      </div>
                    ))}
                  </div>
                )}
                {Object.keys(naacChecks).length > 0 && (
                  <div className="criteria-breakdown">
                    <h4>NAAC Criteria</h4>
                    {Object.entries(naacChecks).map(([key, check]) => (
                      <div key={key} className={`criterion-item ${check.compliant ? 'pass' : 'fail'}`}>
                        <span className="criterion-status">{check.compliant ? '✓' : '✗'}</span>
                        <span className="criterion-name">{key.replace(/_/g, ' ')}</span>
                        <span className="criterion-score">{Math.round(check.score)}%</span>
                      </div>
                    ))}
                  </div>
                )}
                {nbaRecommendations.length > 0 && (
                  <div className="accred-recs">
                    <h4>NBA Recommendations</h4>
                    {nbaRecommendations.map((r: string, i: number) => (
                      <p key={i} className="accred-rec">{r}</p>
                    ))}
                  </div>
                )}
                {naacRecommendations.length > 0 && (
                  <div className="accred-recs">
                    <h4>NAAC Recommendations</h4>
                    {naacRecommendations.map((r: string, i: number) => (
                      <p key={i} className="accred-rec">{r}</p>
                    ))}
                  </div>
                )}
              </CollapsibleCard>

              <CollapsibleCard title="RAG Grounded Insights" icon={<Zap size={20} />} defaultOpen={true}>
                {analysisResult?.ai_analysis ? (
                  <div className="ai-insight">
                    <CheckCircle size={16} /> {analysisResult.ai_analysis}
                  </div>
                ) : (
                  <p className="text-muted">RAG insights unavailable - using rule-based analysis.</p>
                )}
              </CollapsibleCard>
            </div>
          </motion.div>
        )}

        {activeTab === 'recommendations' && (
          <motion.div key="recommendations" className="tab-content" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <div className="recommendations-filter">
              <Filter size={16} />
              <span>Filter by priority:</span>
              {(['all', 'high', 'medium', 'low'] as const).map(p => (
                <button
                  key={p}
                  className={`filter-btn ${priorityFilter === p ? 'active' : ''}`}
                  onClick={() => setPriorityFilter(p)}
                >
                  {p}
                </button>
              ))}
            </div>
            {filteredRecommendations.length > 0 ? (
              <div className="recommendations-list">
                {filteredRecommendations.map((rec, i) => (
                  <RecommendationCard key={i} recommendation={rec} />
                ))}
              </div>
            ) : (
              <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
                <CheckCircle size={32} style={{ color: 'var(--accent-emerald)', marginBottom: '0.5rem' }} />
                <h3 style={{ fontFamily: 'var(--font-sans)', fontSize: '1.1rem' }}>No Recommendations Needed</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Your syllabus appears to meet all quality standards.</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AnalyzePage;
