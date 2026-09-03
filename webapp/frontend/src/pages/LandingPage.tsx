import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSyllabus } from '../context/SyllabusContext';
import { uploadAndAnalyze } from '../services/api';
import { FileScan, PenTool, Lightbulb, ArrowRight, ShieldCheck, UploadCloud } from 'lucide-react';
import TextCurtain from '../components/TextCurtain';
import MarqueeTicker from '../components/MarqueeTicker';
import FlowDiagram from '../components/FlowDiagram';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const { setCurrentSyllabus, setAnalysisResult } = useSyllabus();
  
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setIsDragActive(true);
  };
  const handleDragLeave = () => setIsDragActive(false);
  
  const handleDrop = async (e: React.DragEvent<HTMLDivElement>): Promise<void> => {
    e.preventDefault();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processDrop(e.dataTransfer.files[0]);
    }
  };

  const processDrop = async (file: File): Promise<void> => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.docx') && !file.name.endsWith('.pdf') && !file.name.endsWith('.txt')) {
      toast.error('Invalid format. Please use PDF, DOCX, or TXT.');
      return;
    }

    // Client-side file size check (50 MB)
    const MAX_SIZE = 50 * 1024 * 1024;
    if (file.size > MAX_SIZE) {
      toast.error(`File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum: 50 MB.`);
      return;
    }

    setIsUploading(true);
    const t = toast.loading('Initiating Fast-Track analysis...');
    
    try {
      // Single combined request — upload + parse + analyze in one round-trip
      const res = await uploadAndAnalyze(file);
      setCurrentSyllabus(res.data);
      setAnalysisResult(res.analysis);
      toast.success(res.cached ? 'Analysis complete (cached)!' : 'Analysis complete!', { id: t });

      navigate('/analyze');
    } catch {
      toast.error('Upload failed. Please try again.', { id: t });
      setIsUploading(false);
    }
  };

  // Framer Motion Variants
  const cardVariants = {
    offscreen: { y: 50, opacity: 0 },
    onscreen: { y: 0, opacity: 1, transition: { type: "spring" as const, bounce: 0.4, duration: 0.8 } }
  };

  return (
    <div className="landing-container animate-fade-in">
      <section className="hero-section">
        {/* Left Side: Content */}
        <div className="hero-content">
          <div className="badge animate-slide-up stagger-1">
            <ShieldCheck size={16} /> NEP 2020 & NBA Aligned
          </div>
          <h1 className="hero-title animate-slide-up stagger-2">
            Redesigning<br/>Academic<br/>Excellence
          </h1>
          <p className="hero-subtitle animate-slide-up stagger-3">
            AI-powered curriculum intelligence. Analyze gaps, generate rigorous syllabi, and map outcomes automatically.
          </p>
          
          <div className="hero-actions animate-slide-up stagger-4">
             {/* Fast Track Upload Box */}
             <div 
               className={`hero-dropzone ${isDragActive ? 'active' : ''} ${isUploading ? 'uploading' : ''}`}
               onDragOver={handleDragOver}
               onDragLeave={handleDragLeave}
               onDrop={handleDrop}
             >
                {isUploading ? (
                  <div className="flex items-center gap-2">
                     <span className="spinner-small" style={{ borderColor: 'rgba(67,56,202,0.3)', borderLeftColor: 'var(--accent-indigo)' }}></span>
                     <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>Accelerating to Analyzer...</span>
                  </div>
                ) : (
                  <>
                     <UploadCloud size={20} className="text-indigo" />
                     <div>
                       <strong>Drag & Drop Syllabus</strong>
                       <p>Instant RAG analysis (PDF, DOCX)</p>
                     </div>
                  </>
                )}
             </div>
             
             {!isUploading && (
                <button onClick={() => navigate('/analyze')} className="btn-secondary" style={{ height: 'max-content', padding: '1rem', alignSelf: 'center' }}>
                  Explore Tools <ArrowRight size={18} />
                </button>
             )}
          </div>
        </div>

        {/* Right Side: Text Curtain */}
        <div className="hero-visual animate-fade-in stagger-5">
          <div className="visual-roof"></div>
          <div className="canvas-wrapper">
            <TextCurtain 
               cols={20}
               rows={22}
            />
          </div>
        </div>
      </section>

      <MarqueeTicker />

      {/* NEW: Problem Statement / Intro */}
      <section className="intro-section text-center mb-4">
         <motion.h2 
           initial={{ opacity: 0, y: 20 }}
           whileInView={{ opacity: 1, y: 0 }}
           viewport={{ once: true }}
         >
           Automate Pedagogical Compliance
         </motion.h2>
         <motion.p 
           className="intro-subtitle"
           initial={{ opacity: 0, y: 20 }}
           whileInView={{ opacity: 1, y: 0 }}
           viewport={{ once: true }}
           transition={{ delay: 0.2 }}
         >
           Stop losing hours to manual syllabus formatting. SCDO ingests your raw curriculum, 
           identifies critical Bloom's Taxonomy gaps, and utilizes an AI pipeline to auto-generate 
           NBA-compliant Course Outcomes and unit topics instantly.
         </motion.p>
      </section>

      {/* Feature Cards below fold using framer-motion */}
      <section className="features-section">
         <motion.div 
           className="feature-card glass-card"
           initial="offscreen"
           whileInView="onscreen"
           viewport={{ once: true, margin: "-50px" }}
           variants={cardVariants}
         >
           <div className="feature-icon bg-indigo-light"><FileScan size={24} /></div>
           <h3>Analyze</h3>
           <p>Upload any syllabus for instant Bloom's Taxonomy gap analysis and CO-PO mapping detection.</p>
           <button onClick={() => navigate('/analyze')} className="feature-link" style={{background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-indigo)'}}>Try Tool <ArrowRight size={14}/></button>
         </motion.div>

         <motion.div 
           className="feature-card glass-card"
           initial="offscreen"
           whileInView="onscreen"
           viewport={{ once: true, margin: "-50px" }}
           variants={cardVariants}
           transition={{ delay: 0.2 }}
         >
           <div className="feature-icon bg-amber"><PenTool size={24} /></div>
           <h3>Generate</h3>
           <p>Draft logically sequenced educational frameworks perfectly aligned with modern domains.</p>
           <button onClick={() => navigate('/generate')} className="feature-link" style={{background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-amber)'}}>Try Tool <ArrowRight size={14}/></button>
         </motion.div>

         <motion.div 
           className="feature-card glass-card"
           initial="offscreen"
           whileInView="onscreen"
           viewport={{ once: true, margin: "-50px" }}
           variants={cardVariants}
           transition={{ delay: 0.4 }}
         >
           <div className="feature-icon bg-emerald"><Lightbulb size={24} /></div>
           <h3>Optimize</h3>
           <p>RAG-grounded refactoring of your curriculum referencing actual Educational Quality Guidelines.</p>
           <button onClick={() => navigate('/optimize')} className="feature-link" style={{background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-emerald)'}}>Try Tool <ArrowRight size={14}/></button>
         </motion.div>
      </section>

      {/* NEW: How It Works Workflow */}
      <section className="workflow-section">
         <div className="text-center mb-4">
           <h2>How The Optimizer Works</h2>
           <p className="text-secondary">A transparent 4-step pipeline to secure curriculum alignment.</p>
         </div>

         <div className="workflow-grid">
           {[
             { step: "01", title: "Ingestion", desc: "Drag & Drop your legacy PDF or DOCX syllabus. Our engine extracts the raw text natively." },
             { step: "02", title: "Gap Analysis", desc: "The platform evaluates your cognitive levels, mapping semantic gaps across Bloom's Taxonomy." },
              { step: "03", title: "RAG Generation", desc: "Using ChromaDB and OpenRouter AI, missing topics and outcomes are generated to meet standards." },
             { step: "04", title: "Refactoring", desc: "Export a finalized, beautifully formatted syllabus document, complete with CO-PO matrices." }
           ].map((item, i) => (
             <motion.div 
               key={i} 
               className="workflow-step glass-card"
               initial={{ opacity: 0, x: -30 }}
               whileInView={{ opacity: 1, x: 0 }}
               viewport={{ once: true, margin: "-100px" }}
               transition={{ delay: i * 0.15 }}
             >
               <h1 className="step-number">{item.step}</h1>
               <h4>{item.title}</h4>
               <p>{item.desc}</p>
             </motion.div>
           ))}
         </div>
      </section>

      {/* NEW: 3D Architecture Visual */}
      <section className="architecture-section" style={{ minHeight: '600px', paddingBottom: '2rem' }}>
         <motion.div 
           className="text-center mb-4"
           initial={{ opacity: 0, y: 30 }}
           whileInView={{ opacity: 1, y: 0 }}
           viewport={{ once: true, margin: "-100px" }}
         >
           <h2>Powered by Retrieval-Augmented Generation</h2>
           <p className="text-secondary mb-4">Explore the multi-stage neural pipeline executing your optimizations.</p>
         </motion.div>

         <div className="flow-diagram-container" style={{ width: '100%', position: 'relative', zIndex: 5 }}>
           <FlowDiagram />
         </div>
      </section>

      <footer className="landing-footer" style={{ position: 'relative', zIndex: 10, marginTop: '2rem' }}>
        <p>Powered by OpenRouter and Google Gemini</p>
      </footer>
    </div>
  );
};

export default LandingPage;
