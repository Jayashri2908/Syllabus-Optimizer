import React, { useState, ChangeEvent, FormEvent } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { generateSyllabus, exportPDF } from '../services/api';
import { SyllabusData, LearningOutcome, GenerateRequest } from '../types';
import SkeletonLoader from '../components/SkeletonLoader';
import { ChevronRight, Activity, Download, Edit2, Save, Cpu, FlaskConical, Palette, Briefcase, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import './GeneratePage.css';

interface FormData {
  course_title: string;
  course_code: string;
  credits: string;
  university_name: string;
  department: string;
  keywords: string;
  domain: string;
  program_outcomes: string[];
}

interface DomainPreset {
  id: string;
  label: string;
  icon: React.ReactNode;
  domain: string;
  keywords: string[];
  color: string;
}

const domainPresets: DomainPreset[] = [
  {
    id: 'engineering',
    label: 'Engineering',
    icon: <Cpu size={20} />,
    domain: 'engineering',
    keywords: ['algorithms', 'systems design', 'optimization', 'modeling'],
    color: 'var(--accent-indigo)'
  },
  {
    id: 'science',
    label: 'Basic Sciences',
    icon: <FlaskConical size={20} />,
    domain: 'science',
    keywords: ['hypothesis', 'experimentation', 'analysis', 'theory'],
    color: 'var(--accent-emerald)'
  },
  {
    id: 'arts',
    label: 'Arts & Humanities',
    icon: <Palette size={20} />,
    domain: 'arts',
    keywords: ['critical thinking', 'interpretation', 'creative expression', 'discourse'],
    color: 'var(--accent-amber)'
  },
  {
    id: 'business',
    label: 'Business',
    icon: <Briefcase size={20} />,
    domain: 'business',
    keywords: ['strategy', 'decision making', 'analytics', 'leadership'],
    color: 'var(--accent-rose)'
  }
];

const GeneratePage: React.FC = () => {
  const { setCurrentSyllabus } = useSyllabus();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [generatedData, setGeneratedData] = useState<SyllabusData | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [activePreset, setActivePreset] = useState<string>('engineering');

  const [formData, setFormData] = useState<FormData>({
    course_title: '',
    course_code: '',
    credits: '3-0-0',
    university_name: '',
    department: '',
    keywords: '',
    domain: 'engineering',
    program_outcomes: ['PO1', 'PO2', 'PO3']
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>): void => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const applyPreset = (preset: DomainPreset): void => {
    setActivePreset(preset.id);
    setFormData({
      ...formData,
      domain: preset.domain,
      keywords: preset.keywords.join(', ')
    });
  };

  const handleSubmit = async (e?: FormEvent): Promise<void> => {
    if (e) e.preventDefault();
    setIsLoading(true);
    const keywordsList = formData.keywords.split(',').map(k => k.trim()).filter(k => k);
    const reqData: GenerateRequest = {
      ...formData,
      keywords: keywordsList,
    };

    const t = toast.loading('Initializing LLM and structuring blueprint...');
    try {
      const res = await generateSyllabus(reqData);
      setGeneratedData(res.syllabus);
      setCurrentSyllabus(res.syllabus);
      setStep(3);
      toast.success('Curriculum Successfully Generated!', { id: t });
    } catch {
      toast.error('Generation failed. Check API configurations.', { id: t });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportPDF = async (): Promise<void> => {
    if (!generatedData) return;
    const t = toast.loading('Exporting to PDF...');
    try {
      const blob = await exportPDF(generatedData);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${generatedData.course_code || 'generated'}_syllabus.pdf`;
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Exported successfully!', { id: t });
    } catch {
      toast.error('Export failed.', { id: t });
    }
  };

  const handleOutcomeChange = (index: number, field: keyof LearningOutcome, value: string): void => {
    if (!generatedData) return;
    const updated = { ...generatedData };
    const outcomes = [...(updated.learning_outcomes || [])];
    outcomes[index] = { ...outcomes[index], [field]: value };
    updated.learning_outcomes = outcomes;
    setGeneratedData(updated);
  };

  const handleUnitChange = (index: number, field: string, value: string): void => {
    if (!generatedData) return;
    const updated = { ...generatedData };
    const units = [...(updated.units || [])];
    if (field === 'topics') {
      units[index] = { ...units[index], topics: value.split(',').map(t => t.trim()) };
    } else {
      units[index] = { ...units[index], [field]: value };
    }
    updated.units = units;
    setGeneratedData(updated);
  };

  const toggleEdit = (): void => {
    if (isEditing && generatedData) {
      setCurrentSyllabus(generatedData);
      toast.success('Changes saved to syllabus.');
    }
    setIsEditing(!isEditing);
  };

  const getBloomDistribution = (): Record<string, number> => {
    if (!generatedData?.learning_outcomes) return {};
    const dist: Record<string, number> = {};
    generatedData.learning_outcomes.forEach(co => {
      const level = co.bloom_level || 'unspecified';
      dist[level] = (dist[level] || 0) + 1;
    });
    return dist;
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <h1>Bloom-Aware AI Generation</h1>
        <p>Use domain detection and minimal variables to draft logically sequenced educational frameworks.</p>
      </div>

      <div className="generate-wizard glass-card">
        <div className="wizard-progress">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
            <span className="step-num">1</span> Course Info
          </div>
          <div className="progress-line"><div className="progress-line-fill" style={{ width: step >= 2 ? '100%' : '0%' }} /></div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
            <span className="step-num">2</span> Content Drivers
          </div>
          <div className="progress-line"><div className="progress-line-fill" style={{ width: step >= 3 ? '100%' : '0%' }} /></div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
            <span className="step-num">3</span> AI Blueprint
          </div>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="step1" className="wizard-step" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} transition={{ duration: 0.2 }}>
              <h3>Course Identity</h3>
              <div className="form-grid mt-4">
                <div className="form-group">
                  <label>Course Title</label>
                  <input name="course_title" value={formData.course_title} onChange={handleChange} placeholder="e.g. Deep Learning and Neural Interfaces" />
                </div>
                <div className="form-group">
                  <label>Course Code</label>
                  <input name="course_code" value={formData.course_code} onChange={handleChange} placeholder="e.g. CS401" />
                </div>
                <div className="form-group">
                  <label>Credits (L-T-P)</label>
                  <input name="credits" value={formData.credits} onChange={handleChange} placeholder="3-0-0" />
                </div>
                <div className="form-group">
                  <label>University (Optional)</label>
                  <input name="university_name" value={formData.university_name} onChange={handleChange} placeholder="e.g. MIT" />
                </div>
              </div>
              <div className="wizard-actions">
                <button className="btn-primary" onClick={() => setStep(2)} disabled={!formData.course_title}>
                  Next Step <ChevronRight size={18} />
                </button>
              </div>
            </motion.div>
          )}

          {step === 2 && !isLoading && (
            <motion.div key="step2" className="wizard-step" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} transition={{ duration: 0.2 }}>
              <h3>Content Drivers</h3>
              <p className="step-subtitle">Choose a domain preset or customize manually</p>

              <div className="preset-grid mt-4">
                {domainPresets.map(preset => (
                  <button
                    key={preset.id}
                    className={`preset-card ${activePreset === preset.id ? 'preset-active' : ''}`}
                    onClick={() => applyPreset(preset)}
                  >
                    <div className="preset-icon" style={{ color: preset.color }}>{preset.icon}</div>
                    <span className="preset-label">{preset.label}</span>
                    <span className="preset-check">{activePreset === preset.id && <Sparkles size={14} />}</span>
                  </button>
                ))}
              </div>

              <div className="form-grid mt-4">
                <div className="form-group full-width">
                  <label>Target Domain</label>
                  <select name="domain" value={formData.domain} onChange={handleChange}>
                    <option value="engineering">Engineering</option>
                    <option value="arts">Arts & Humanities</option>
                    <option value="science">Basic Sciences</option>
                    <option value="business">Business & Management</option>
                  </select>
                </div>
                <div className="form-group full-width">
                  <label>Core Keywords (Comma separated)</label>
                  <textarea
                    name="keywords"
                    value={formData.keywords}
                    onChange={handleChange}
                    placeholder="e.g. backpropagation, transformers, PyTorch, natural language processing"
                    rows={3}
                  />
                  {formData.keywords && (
                    <div className="keyword-chips">
                      {formData.keywords.split(',').map((k, i) => k.trim() && (
                        <span key={i} className="keyword-chip">{k.trim()}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="wizard-actions between mt-4">
                <button className="btn-secondary" onClick={() => setStep(1)}>Back</button>
                <button className="btn-primary" onClick={() => handleSubmit()} disabled={!formData.keywords}>
                  <Activity size={18} /> Generate Blueprint
                </button>
              </div>
            </motion.div>
          )}

          {step === 2 && isLoading && (
            <motion.div key="loading" className="wizard-step text-center py-8" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <h3 className="mb-4 text-indigo">Drafting Curriculum...</h3>
              <div className="max-w-2xl mx-auto text-left">
                <SkeletonLoader count={2} />
                <br />
                <SkeletonLoader type="card" count={2} />
              </div>
            </motion.div>
          )}

          {step === 3 && generatedData && (
            <motion.div key="step3" className="wizard-step" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} transition={{ duration: 0.2 }}>
              <div className="results-header">
                <div>
                  <h2 style={{ color: 'var(--accent-indigo)' }}>Generation Complete</h2>
                  <p>Review or refine your AI drafted syllabus structure</p>
                </div>
                <div className="actions">
                  <button
                    className={isEditing ? 'btn-primary' : 'btn-secondary'}
                    onClick={toggleEdit}
                    style={isEditing ? { backgroundColor: 'var(--accent-emerald)' } : {}}
                  >
                    {isEditing ? <><Save size={18} /> Save Changes</> : <><Edit2 size={18} /> Edit Content</>}
                  </button>
                  <button className="btn-primary" onClick={handleExportPDF}><Download size={18} /> Export PDF</button>
                </div>
              </div>

              <div className="gen-results-layout mt-4">
                <div className="gen-main-col">
                  <h3>
                    {isEditing ? (
                      <input
                        className="inline-input w-full font-serif text-2xl"
                        value={generatedData.course_title}
                        onChange={e => setGeneratedData({ ...generatedData, course_title: e.target.value })}
                      />
                    ) : (
                      `${generatedData.course_title} (${generatedData.course_code})`
                    )}
                  </h3>

                  <div className="mt-4">
                    <h4>Course Outcomes</h4>
                    <div className="co-grid">
                      {generatedData.learning_outcomes?.map((co, idx) => (
                        <div key={idx} className="glass-card co-card">
                          <div className="co-card-top">
                            <strong className="co-code">{co.code || `CO${idx + 1}`}</strong>
                            <span className="mono-tag">{co.bloom_level}</span>
                          </div>
                          {isEditing ? (
                            <input
                              className="inline-input co-edit-input"
                              value={co.description}
                              onChange={(e) => handleOutcomeChange(idx, 'description', e.target.value)}
                            />
                          ) : (
                            <p className="co-desc">{co.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-4">
                    <h4>Curriculum Units</h4>
                    <div className="units-grid">
                      {generatedData.units?.map((unit, idx) => (
                        <div key={idx} className="glass-card unit-card">
                          {isEditing ? (
                            <div className="unit-edit">
                              <div className="unit-edit-header">
                                <strong>Unit {unit.unit_number || idx + 1}:</strong>
                                <input
                                  className="inline-input flex-1"
                                  value={unit.title}
                                  onChange={(e) => handleUnitChange(idx, 'title', e.target.value)}
                                />
                              </div>
                              <textarea
                                className="inline-input w-full"
                                value={unit.topics ? unit.topics.join(', ') : ''}
                                onChange={(e) => handleUnitChange(idx, 'topics', e.target.value)}
                                rows={2}
                              />
                            </div>
                          ) : (
                            <>
                              <div className="unit-card-header">
                                <span className="unit-num">Unit {unit.unit_number}</span>
                                <strong>{unit.title}</strong>
                              </div>
                              <div className="topic-tags">
                                {unit.topics?.map((topic, ti) => (
                                  <span key={ti} className="topic-tag">{topic}</span>
                                ))}
                              </div>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="gen-side-col">
                  <div className="glass-card gen-meta-card">
                    <h4>Quick Stats</h4>
                    <div className="meta-rows">
                      <div className="meta-row">
                        <span>Code</span>
                        <strong>{generatedData.course_code}</strong>
                      </div>
                      <div className="meta-row">
                        <span>Credits</span>
                        <strong>{generatedData.credits}</strong>
                      </div>
                      <div className="meta-row">
                        <span>Outcomes</span>
                        <strong>{generatedData.learning_outcomes?.length ?? 0}</strong>
                      </div>
                      <div className="meta-row">
                        <span>Units</span>
                        <strong>{generatedData.units?.length ?? 0}</strong>
                      </div>
                      <div className="meta-row">
                        <span>Domain</span>
                        <strong style={{ textTransform: 'capitalize' }}>{generatedData.domain || formData.domain}</strong>
                      </div>
                    </div>
                  </div>

                  <div className="glass-card gen-meta-card">
                    <h4>Bloom's Distribution</h4>
                    <div className="bloom-mini-bars">
                      {Object.entries(getBloomDistribution()).map(([level, count]) => (
                        <div key={level} className="bloom-mini-row">
                          <span className="bloom-mini-label">{level}</span>
                          <div className="bloom-mini-bar-bg">
                            <div
                              className="bloom-mini-bar-fill"
                              style={{ width: `${(count / Math.max(...Object.values(getBloomDistribution()), 1)) * 100}%` }}
                            />
                          </div>
                          <span className="bloom-mini-count">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default GeneratePage;
