import React from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart2, FileText, Zap, ArrowRight, CheckCircle, Shield,
  Download, Upload, Layers
} from 'lucide-react';
import { InfoTooltip } from '../components/Tooltip';
import InteractiveTextCurtain from '../components/InteractiveTextCurtain';

/* ─── Enhanced Feature Card ─── */
const FeatureCard = ({
  icon: Icon,
  title,
  description,
  link,
  tooltip,
  tint = 'indigo',
  className = '',
}) => {
  const tintMap = {
    indigo: {
      gradient: 'from-[#efe8de]/60 via-[#faf7f2] to-[#efe8de]/40',
      iconBg: 'bg-[#efe8de]',
      iconColor: 'text-[#3d2e1f]',
      accent: 'text-[#3d2e1f]',
    },
    orange: {
      gradient: 'from-[#fbe9e7]/60 via-[#faf7f2] to-[#fff3e0]/40',
      iconBg: 'bg-[#fbe9e7]',
      iconColor: 'text-[#d32f2f]',
      accent: 'text-[#d32f2f]',
    },
    emerald: {
      gradient: 'from-[#f1f8e9]/60 via-[#faf7f2] to-[#e8f5e9]/40',
      iconBg: 'bg-[#e8f5e9]',
      iconColor: 'text-[#2e7d32]',
      accent: 'text-[#2e7d32]',
    },
    violet: {
      gradient: 'from-[#efe8de]/60 via-[#faf7f2] to-[#fbe9e7]/40',
      iconBg: 'bg-[#efe8de]',
      iconColor: 'text-[#5c4033]',
      accent: 'text-[#5c4033]',
    },
  };
  const t = tintMap[tint] || tintMap.indigo;

  return (
    <Link
      to={link || '#'}
      className={`card glass-panel group hover:no-underline relative overflow-hidden flex flex-col ${className}`}
      style={{ background: undefined }}
    >
      {/* Tinted gradient overlay */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${t.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none`}
      />

      <div className="module-card-header relative z-10">
        <div
          className={`w-12 h-12 rounded-xl flex items-center justify-center ${t.iconBg} shadow-sm group-hover:scale-110 transition-transform duration-300`}
        >
          <Icon size={24} className={t.iconColor} />
        </div>
        {tooltip && <InfoTooltip text={tooltip} />}
      </div>

      <div className="relative z-10 mt-4 flex-1 flex flex-col">
        <h3 className="text-lg font-bold text-primary group-hover:text-brand transition-colors mb-2 flex items-center gap-2">
          {title}
          <ArrowRight
            size={16}
            className="opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300"
          />
        </h3>
        <p className="text-secondary text-sm leading-relaxed text-balance flex-1">
          {description}
        </p>
        <span
          className={`inline-flex items-center gap-1 mt-4 text-sm font-semibold ${t.accent} group-hover:gap-2 transition-all duration-300`}
        >
          Learn more <ArrowRight size={14} />
        </span>
      </div>
    </Link>
  );
};

/* ─── Floating stat badge used in the hero ─── */
const StatBadge = ({ children, className = '' }) => (
  <span
    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold
      bg-white/70 backdrop-blur-md border border-white/40 shadow-sm
      text-primary/80 transition-transform duration-300 hover:scale-105 ${className}`}
  >
    {children}
  </span>
);

/* ─── Page ─── */
const HomePage = () => {
  return (
    <div className="container animate-fade-in relative z-10">
      {/* ═══════════════════ HERO ═══════════════════ */}
      <div className="hero-section relative overflow-hidden min-h-[60vh] flex items-center justify-center">
        <InteractiveTextCurtain 
          characters="SYLLABUS CURRICULUM OPTIMIZE ANALYZE GENERATE OUTCOMES BLOOM MAPPING COMPLIANCE NEP 2020 ACCREDITATION COURSE PROGRAM LEARNING ASSESSMENT"
          opacity={0.25}
          color="#8b7e6f"
          fontSize={13}
          spacingX={20}
          spacingY={20}
        />

        <div className="hero-content relative z-10 max-w-3xl text-center px-6">
          {/* Floating stat badges */}
          <div className="flex flex-wrap justify-center gap-3 mb-8">
            <StatBadge>
              <Shield size={14} className="text-[#d32f2f]" />
              50+ Accreditation Standards
            </StatBadge>
            <StatBadge>
              <Zap size={14} className="text-[#e65100]" />
              AI-Powered Analysis
            </StatBadge>
            <StatBadge>
              <CheckCircle size={14} className="text-[#2e7d32]" />
              NEP 2020 Compliant
            </StatBadge>
          </div>

          <h1 className="hero-title tracking-tight mb-6 text-5xl sm:text-6xl lg:text-7xl font-serif">
            Syllabus <span className="text-gradient">&amp;</span> Curriculum
            <br />
            <span className="text-gradient">Optimization</span>
          </h1>

          <p className="hero-subtitle text-lg font-medium text-secondary mb-10 max-w-2xl mx-auto">
            Advanced AI-driven analysis for academic curriculum design.
            Optimize learning outcomes, ensure compliance, and generate
            accreditation-ready reports in seconds.
          </p>

          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              to="/analyze"
              className="btn btn-primary px-10 py-4 text-lg font-semibold shadow-lg hover:shadow-brand/25 transition-all hover:-translate-y-1 group"
            >
              Start Analysis
              <span className="inline-flex items-center gap-1 group-hover:translate-x-1 transition-transform duration-300">
                <ArrowRight size={20} className="group-hover:animate-pulse" />
              </span>
            </Link>
          </div>
        </div>
      </div>

      {/* ═══════════════════ CORE MODULES — BENTO ═══════════════════ */}
      <div className="modules-section pb-16">
        <div className="section-header mb-8">
          <h2 className="text-2xl font-bold text-primary flex items-center gap-2">
            <Zap className="text-[#d32f2f]" size={24} />
            Core Modules
          </h2>
        </div>

        <div className="bento-grid">
          <FeatureCard
            icon={Zap}
            title="AI Optimization"
            description="Leverage Gemini Pro &amp; IBM Granite to suggest content improvements, align outcomes with Bloom's taxonomy, and auto-generate CO-PO mappings — all in one click."
            link="/optimize"
            tooltip="Powered by Gemini Pro + IBM Granite"
            tint="orange"
            className="md:col-span-2 md:row-span-2"
          />

          <FeatureCard
            icon={BarChart2}
            title="Deep Analysis Engine"
            description="Upload syllabi for comprehensive gap analysis, structural integrity checks, and outcome alignment scoring using RAG-based architecture."
            link="/analyze"
            tooltip="Uses RAG architecture"
            tint="indigo"
          />

          <FeatureCard
            icon={FileText}
            title="Report Generation"
            description="One-click PDF &amp; DOCX compliance reports, curriculum summaries, and accreditation-ready documentation with custom branding."
            link="/generate"
            tooltip="Supports PDF and DOCX export"
            tint="emerald"
          />

          <FeatureCard
            icon={Layers}
            title="CO-PO Mapping"
            description="Automatically map Course Outcomes to Programme Outcomes with visual correlation matrices. Identify weak links and ensure full NBA/NAAC coverage."
            link="/analyze"
            tooltip="Outcome-Outcome correlation"
            tint="violet"
          />
        </div>
      </div>

      {/* ═══════════════════ TRUST / STATS STRIP ═══════════════════ */}
      <section className="pb-20">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-0 py-8 px-4 rounded-2xl bg-gradient-to-r from-[#efe8de]/30 via-[#faf7f2] to-[#efe8de]/30 border border-[#d4c8b8] shadow-sm">
          {[
            { icon: Shield, label: 'NBA & NAAC Compliant' },
            { icon: CheckCircle, label: 'NEP 2020 Ready' },
            { icon: Zap, label: 'Multi-AI Engine' },
            { icon: FileText, label: 'Instant Reports' },
          ].map(({ icon: I, label }, i, arr) => (
            <React.Fragment key={label}>
              <div className="flex items-center gap-2.5 text-sm font-medium text-[#5c5446]">
                <I size={18} className="text-[#8b7e6f]" />
                {label}
              </div>
              {i < arr.length - 1 && (
                <span className="hidden sm:block h-5 w-px bg-[#d4c8b8] mx-6" />
              )}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* ═══════════════════ HOW IT WORKS ═══════════════════ */}
      <section className="pb-20">
        <div className="text-center mb-12">
          <h2 className="text-2xl font-bold text-primary mb-2">How It Works</h2>
          <p className="text-secondary text-sm max-w-md mx-auto">
            Three simple steps to transform your curriculum.
          </p>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-center gap-0 md:gap-0">
          {[
            { num: 1, icon: Upload, title: 'Upload Syllabus', desc: 'Drag & drop your PDF or DOCX syllabus file' },
            { num: 2, icon: Zap, title: 'AI Analysis', desc: 'Our multi-AI engine parses & evaluates every outcome' },
            { num: 3, icon: Download, title: 'Export Reports', desc: 'Download accreditation-ready reports instantly' },
          ].map((step, i, arr) => (
            <React.Fragment key={step.num}>
              <div className="flex flex-col items-center text-center w-64 px-4">
                {/* Numbered circle */}
                <div className="relative mb-4">
                  <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#3d2e1f] to-[#5c4033] shadow-lg flex items-center justify-center text-white font-bold text-lg">
                    {step.num}
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-white shadow flex items-center justify-center">
                    <step.icon size={16} className="text-[#d32f2f]" />
                  </div>
                </div>
                <h3 className="font-bold text-primary mb-1">{step.title}</h3>
                <p className="text-xs text-secondary leading-relaxed">{step.desc}</p>
              </div>
              {/* Connector line */}
              {i < arr.length - 1 && (
                <div className="hidden md:flex items-center w-16 -mt-6">
                  <div className="w-full h-px bg-gradient-to-r from-[#8b7e6f] to-[#d4c8b8]" />
                  <ArrowRight size={14} className="text-[#8b7e6f] -ml-1" />
                </div>
              )}
              {/* Mobile down arrow */}
              {i < arr.length - 1 && (
                <div className="flex md:hidden my-3">
                  <ArrowRight size={18} className="text-[#8b7e6f] rotate-90" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* ═══════════════════ FINAL CTA BANNER ═══════════════════ */}
      <section className="pb-20">
        <div
          className="relative overflow-hidden rounded-2xl px-8 py-14 text-center"
          style={{
            background: 'linear-gradient(135deg, #3d2e1f 0%, #5c4033 40%, #d32f2f 100%)',
          }}
        >
          {/* Decorative circles */}
          <div className="absolute -top-10 -left-10 w-40 h-40 rounded-full bg-white/5 pointer-events-none" />
          <div className="absolute -bottom-8 -right-8 w-32 h-32 rounded-full bg-white/5 pointer-events-none" />

          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-3 relative z-10">
            Ready to optimize your curriculum?
          </h2>
          <p className="text-[#efe8de] mb-8 max-w-lg mx-auto relative z-10">
            Join institutions already using SCDO to streamline accreditation, map outcomes, and build better syllabi — powered by AI.
          </p>
          <Link
            to="/analyze"
            className="btn inline-flex items-center gap-2 px-10 py-4 text-lg font-semibold rounded-xl bg-white text-[#3d2e1f] shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all relative z-10"
          >
            Get Started
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
