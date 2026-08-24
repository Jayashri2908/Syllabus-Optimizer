import React, { useState, ChangeEvent, FormEvent } from 'react';
import { useSyllabus } from '../context/SyllabusContext';
import { generateSyllabus, exportPDF } from '../services/api';
import { SyllabusData, LearningOutcome, GenerateRequest } from '../types';
import SkeletonLoader from '../components/SkeletonLoader';
import { PenTool, ChevronRight, Activity, Download, Edit2, Save } from 'lucide-react';
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

const GeneratePage: React.FC = () => {
  const { setCurrentSyllabus } = useSyllabus();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [generatedData, setGeneratedData] = useState<SyllabusData | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  
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
    setFormData({...formData, [e.target.name]: e.target.value});
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
      toast.error("Generation failed. Check API configurations.", { id: t });
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
      toast.success('Exported successfully!', { id: t });
    } catch {
      toast.error('Export failed.', { id: t });
    }
  };

  const handleOutcomeChange = (index: number, field: keyof LearningOutcome, value: string): void => {
    if (!generatedData) return;
    const updated = {...generatedData};
    const outcomes = [...(updated.learning_outcomes || [])];
    outcomes[index] = { ...outcomes[index], [field]: value };
    updated.learning_outcomes = outcomes;
    setGeneratedData(updated);
  };

  const handleUnitChange = (index: number, field: string, value: string): void => {
    if (!generatedData) return;
    const updated = {...generatedData};
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
      toast.success("Changes saved to syllabus.");
    }
    setIsEditing(!isEditing);
  };

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <h1>Bloom-Aware AI Generation</h1>
        <p>Use domain detection and minimal variables to draft logically sequenced educational frameworks.</p>
      </div>

      <div className="generate-wizard glass-card">
        <div className="wizard-progress">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>1. Course Info</div>
          <div className="progress-line"></div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>2. Content Drivers</div>
          <div className="progress-line"></div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>3. AI Blueprint</div>
        </div>

        {step === 1 && (
          <div className="wizard-step animate-slide-up">
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
                Next Step <ChevronRight size={18}/>
              </button>
            </div>
          </div>
        )}

        {step === 2 && !isLoading && (
          <div className="wizard-step animate-slide-up">
            <h3>Content Drivers</h3>
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
              </div>
            </div>
            
            <div className="wizard-actions between mt-4">
              <button className="btn-secondary" onClick={() => setStep(1)}>Back</button>
              <button className="btn-primary" onClick={() => handleSubmit()} disabled={!formData.keywords}>
                <Activity size={18}/> Generate Blueprint
              </button>
            </div>
          </div>
        )}

        {step === 2 && isLoading && (
          <div className="wizard-step text-center py-8">
            <h3 className="mb-4 text-indigo">Drafting Curriculum...</h3>
            <div className="max-w-2xl mx-auto text-left">
               <SkeletonLoader count={2} />
               <br/>
               <SkeletonLoader type="card" count={2} />
            </div>
          </div>
        )}

        {step === 3 && generatedData && (
          <div className="wizard-step animate-slide-up">
            <div className="results-header">
              <div>
                <h2 style={{color: 'var(--accent-indigo)'}}>Generation Complete</h2>
                <p>Review or refine your AI drafted syllabus structure</p>
              </div>
              <div className="actions">
                <button 
                  className={isEditing ? "btn-primary" : "btn-secondary"} 
                  onClick={toggleEdit}
                  style={isEditing ? { backgroundColor: 'var(--accent-emerald)' } : {}}
                >
                  {isEditing ? <><Save size={18}/> Save Changes</> : <><Edit2 size={18}/> Edit Content</>}
                </button>
                <button className="btn-primary" onClick={handleExportPDF}><Download size={18}/> Export PDF</button>
              </div>
            </div>

            <div className="syllabus-preview mt-4">
              <h3>
                {isEditing ? (
                  <input 
                    className="inline-input w-full font-serif text-2xl" 
                    value={generatedData.course_title} 
                    onChange={e => setGeneratedData({...generatedData, course_title: e.target.value})}
                  />
                ) : (
                  `${generatedData.course_title} (${generatedData.course_code})`
                )}
              </h3>
              
              <div className="mt-4">
                <h4>Course Outcomes</h4>
                <div style={{ display: 'grid', gap: '0.5rem', marginTop: '0.5rem' }}>
                  {generatedData.learning_outcomes?.map((co, idx) => (
                    <div key={idx} className="glass-card" style={{ padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                       <strong>{co.code || `CO${idx+1}`}:</strong> 
                       {isEditing ? (
                          <input 
                            className="inline-input flex-1" 
                            value={co.description} 
                            onChange={(e) => handleOutcomeChange(idx, 'description', e.target.value)}
                          />
                       ) : (
                         <span style={{flex: 1}}>{co.description}</span>
                       )}
                       <span className="mono-tag" style={{flexShrink: 0}}>{co.bloom_level}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4">
                <h4>Curriculum Units</h4>
                <div style={{ display: 'grid', gap: '1rem', marginTop: '0.5rem' }}>
                  {generatedData.units?.map((unit, idx) => (
                    <div key={idx} className="glass-card" style={{ padding: '1rem' }}>
                       {isEditing ? (
                         <div className="flex flex-col gap-2">
                           <div className="flex gap-2">
                             <strong>Unit {unit.unit_number || idx+1}:</strong>
                             <input 
                               className="inline-input flex-1 font-bold" 
                               value={unit.title} 
                               onChange={(e) => handleUnitChange(idx, 'title', e.target.value)}
                             />
                           </div>
                           <textarea 
                             className="inline-input w-full text-sm text-secondary" 
                             value={unit.topics ? unit.topics.join(', ') : ''} 
                             onChange={(e) => handleUnitChange(idx, 'topics', e.target.value)}
                             rows={2}
                           />
                         </div>
                       ) : (
                         <>
                           <strong>Unit {unit.unit_number}: {unit.title}</strong>
                           <p className="text-sm text-secondary mt-2">{unit.topics?.join(', ')}</p>
                         </>
                       )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GeneratePage;
