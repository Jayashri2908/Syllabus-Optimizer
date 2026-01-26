import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart2, FileText, Zap, ArrowRight, CheckCircle, Shield } from 'lucide-react';
import { InfoTooltip } from '../components/Tooltip';
import ThreeBackground from '../components/ThreeBackground';

const FeatureCard = ({ icon: Icon, title, description, link, tooltip }) => (
  <Link to={link || '#'} className="card group hover:no-underline">
    <div className="module-card-header">
      <div className="icon-wrapper">
        <Icon size={24} />
      </div>
      {tooltip && <InfoTooltip text={tooltip} />}
    </div>
    <h3 className="module-title group-hover:text-brand transition-colors">
      {title}
      <ArrowRight size={16} className="arrow-icon" />
    </h3>
    <p className="text-subtle text-sm leading-relaxed">
      {description}
    </p>
  </Link>
);


const HomePage = () => {
  return (
    <div className="container animate-fade-in">
      {/* Professional Hero / Dashboard Header */}
      <div className="hero-section relative overflow-hidden">
        <ThreeBackground />
        <div className="hero-content">

          <h1 className="hero-title">
            Syllabus & Curriculum <br />
            <span style={{ color: 'var(--brand)' }}>Optimization Suite</span>
          </h1>
          <p className="hero-subtitle">
            Advanced AI-driven analysis for academic curriculum design.
            Ensure compliance, optimize learning outcomes, and generate
            comprehensive reports standard compliant formats.
          </p>

          <div className="flex gap-4">
            <Link to="/analyze" className="btn btn-primary">
              Start Analysis
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </div>


      {/* Main Action Grid */}
      <div className="modules-section">
        <div className="section-header">
          <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Core Modules</h2>
        </div>

        <div className="modules-grid">
          <FeatureCard
            icon={BarChart2}
            title="Deep Analysis"
            description="Upload syllabus documents for comprehensive gap analysis and compliance checking against university standards."
            link="/analyze"
            tooltip="Uses RAG architecture to analyze structural integrity"
          />

          <FeatureCard
            icon={FileText}
            title="Report Generation"
            description="Generate detailed PDF compliance reports and curriculum summaries for accreditation purposes."
            link="/generate"
            tooltip="Supports PDF and DOCX export updates"
          />

          <FeatureCard
            icon={Zap}
            title="AI Optimization"
            description="Leverage LLMs to suggest content improvements, bibliography updates, and outcome mappings."
            link="/optimize"
            tooltip="Powered by Gemini Pro + IBM Granite"
          />
        </div>
      </div>

      {/* Status Bar */}

    </div>
  );
};

export default HomePage;
