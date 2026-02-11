import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart2, FileText, Zap, ArrowRight, CheckCircle, Shield } from 'lucide-react';
import { InfoTooltip } from '../components/Tooltip';

import ThreeBackground from '../components/ThreeBackground';
import SCDOLogo from '../components/SCDOLogo';

const FeatureCard = ({ icon: Icon, title, description, link, tooltip, className = "" }) => (
  <Link to={link || '#'} className={`card glass-panel group hover:no-underline relative overflow-hidden ${className}`}>


    <div className="module-card-header relative z-10">
      <div className="icon-wrapper bg-gradient-to-br from-white to-surface shadow-sm group-hover:scale-110 transition-transform duration-300">
        <Icon size={24} className="text-brand" />
      </div>
      {tooltip && <InfoTooltip text={tooltip} />}
    </div>

    <div className="relative z-10 mt-4">
      <h3 className="text-lg font-bold text-primary group-hover:text-brand transition-colors mb-2 flex items-center gap-2">
        {title}
        <ArrowRight size={16} className="opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" />
      </h3>
      <p className="text-secondary text-sm leading-relaxed text-balance">
        {description}
      </p>
    </div>
  </Link>
);


const HomePage = () => {
  return (
    <div className="container animate-fade-in relative z-10">


      {/* Professional Hero / Dashboard Header */}
      <div className="hero-section relative overflow-hidden min-h-[55vh] flex items-center justify-center">
        <ThreeBackground />

        <div className="hero-content relative z-10 max-w-3xl text-center px-6">


          <h1 className="hero-title tracking-tight mb-6 text-5xl sm:text-6xl">
            Syllabus <span className="text-gradient">&</span> Curriculum <br />
            <span className="text-gradient">Optimization</span>
          </h1>

          <p className="hero-subtitle text-lg font-medium text-secondary mb-8 max-w-2xl mx-auto">
            Advanced AI-driven analysis for academic curriculum design.
            Optimize learning outcomes, ensure compliance, and generate
            accreditation-ready reports in seconds.
          </p>

          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/analyze" className="btn btn-primary px-8 py-3 text-lg shadow-lg hover:shadow-brand/20 transition-all hover:-translate-y-1">
              Start Analysis
              <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </div>


      {/* Main Action Grid - Bento Style */}
      <div className="modules-section pb-20">
        <div className="section-header mb-8">
          <h2 className="text-2xl font-bold text-primary flex items-center gap-2">
            <Zap className="text-brand" size={24} />
            Core Modules
          </h2>
        </div>

        <div className="bento-grid">
          {/* Main Optimization Card - Spans 2 cols on tablet+ */}
          <FeatureCard
            icon={Zap}
            title="AI Optimization"
            description="Leverage LLMs to suggest content improvements and outcome mappings. Powered by Gemini Pro + IBM Granite for superior results."
            link="/optimize"
            tooltip="Powered by Gemini Pro + IBM Granite"
            className="md:col-span-2 md:row-span-2 bg-gradient-to-br from-white to-orange-50/30"
          />

          <FeatureCard
            icon={BarChart2}
            title="Deep Analysis Engine"
            description="Upload syllabus documents for comprehensive gap analysis and structural integrity checks."
            link="/analyze"
            tooltip="Uses RAG architecture"
          />

          <FeatureCard
            icon={FileText}
            title="Report Generation"
            description="One-click PDF compliance reports and curriculum summaries."
            link="/generate"
            tooltip="Supports PDF and DOCX export updates"
          />


        </div>
      </div>

    </div>
  );
};

export default HomePage;
