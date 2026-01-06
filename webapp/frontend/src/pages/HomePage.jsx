import React from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Sparkles } from 'lucide-react';

function HomePage() {
  const showToastDemo = () => {
    toast.success('✅ This is a success notification!', {
      icon: '🎉',
    });

    setTimeout(() => {
      toast('💡 Try the buttons below to test features!', {
        icon: '👋',
      });
    }, 1000);
  };

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content fade-in">
            <h1 className="hero-title">
              AI-Powered Syllabus <br />
              <span className="gradient-text">Design & Optimization</span>
            </h1>
            <p className="hero-subtitle">
              Transform your curriculum with intelligent analysis, optimization, and generation
              powered by IBM Granite AI
            </p>
            <div className="hero-actions">
              <Link to="/generate" className="btn btn-primary btn-lg">
                <Sparkles size={20} />
                Generate Syllabus
              </Link>
              <Link to="/analyze" className="btn btn-secondary btn-lg">
                Analyze Existing
              </Link>
            </div>
            <div className="hero-badge">
              <span className="badge badge-success">✅ 100% Free Tier</span>
              <span className="badge badge-primary">🚀 AI-Powered</span>
              <button
                onClick={showToastDemo}
                className="badge badge-warning"
                style={{ cursor: 'pointer', border: 'none' }}
              >
                🎨 Try New UI Features
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2 className="section-title text-center">Powerful Features</h2>
          <div className="features-grid">
            <FeatureCard
              icon="📊"
              title="Intelligent Analysis"
              description="Parse and analyze syllabi with AI. Identify gaps in Bloom's taxonomy, CO-PO mappings, and assessment patterns."
            />
            <FeatureCard
              icon="✨"
              title="AI Generation"
              description="Generate complete syllabi from minimal inputs using IBM Granite. Create measurable outcomes and structured content."
            />
            <FeatureCard
              icon="🎯"
              title="Smart Optimization"
              description="Get AI-powered suggestions for improving content, balancing workload, and modernizing topics."
            />
            <FeatureCard
              icon="🗺️"
              title="CO-PO Mapping"
              description="Automatic intelligent mapping of Course Outcomes to Program Outcomes with validation."
            />
            <FeatureCard
              icon="📄"
              title="Professional Export"
              description="Export beautiful PDF documents with formatted sections and mapping matrices."
            />
            <FeatureCard
              icon="🎓"
              title="Accreditation Ready"
              description="Aligned with NBA, NAAC, NEP 2020, and ABET standards for academic excellence."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="container">
          <div className="cta-card glass">
            <h2 className="cta-title">Ready to optimize your curriculum?</h2>
            <p className="cta-text">
              Start creating professional syllabi in minutes with AI assistance
            </p>
            <Link to="/generate" className="btn btn-primary btn-lg">
              Get Started Free
            </Link>
          </div>
        </div>
      </section>

      <style>{`
        .hero {
          padding: var(--spacing-2xl) 0;
          background: linear-gradient(135deg, 
            hsl(220, 90%, 98%) 0%, 
            hsl(280, 70%, 98%) 100%
          );
        }

        [data-theme="dark"] .hero {
          background: linear-gradient(135deg, 
            hsl(220, 20%, 12%) 0%, 
            hsl(280, 20%, 15%) 100%
          );
        }

        .hero-content {
          text-align: center;
          max-width: 800px;
          margin: 0 auto;
        }

        .hero-title {
          font-size: 3.5rem;
          margin-bottom: var(--spacing-lg);
          line-height: 1.1;
        }

        .gradient-text {
          background: linear-gradient(135deg, var(--primary), var(--secondary));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .hero-subtitle {
          font-size: 1.25rem;
          color: var(--text-secondary);
          margin-bottom: var(--spacing-xl);
        }

        .hero-actions {
          display: flex;
          gap: var(--spacing-md);
          justify-content: center;
          margin-bottom: var(--spacing-lg);
        }

        .hero-badge {
          display: flex;
          gap: var(--spacing-sm);
          justify-content: center;
        }

        .features {
          padding: var(--spacing-2xl) 0;
        }

        .section-title {
          font-size: 2.5rem;
          margin-bottom: var(--spacing-2xl);
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: var(--spacing-lg);
        }

        .cta {
          padding: var(--spacing-2xl) 0;
        }

        .cta-card {
          text-align: center;
          padding: var(--spacing-2xl);
          border-radius: var(--radius-xl);
        }

        .cta-title {
          font-size: 2rem;
          margin-bottom: var(--spacing-md);
        }

        .cta-text {
          font-size: 1.125rem;
          color: var(--text-secondary);
          margin-bottom: var(--spacing-xl);
        }

        @media (max-width: 768px) {
          .hero-title {
            font-size: 2.5rem;
          }
          .hero-actions {
            flex-direction: column;
          }
          .features-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="card feature-card">
      <div className="feature-icon">{icon}</div>
      <h3 className="feature-title">{title}</h3>
      <p className="feature-description">{description}</p>

      <style>{`
        .feature-card {
          text-align: center;
          transition: all var(--transition-base);
        }

        .feature-icon {
          font-size: 3rem;
          margin-bottom: var(--spacing-md);
        }

        .feature-title {
          font-size: 1.25rem;
          margin-bottom: var(--spacing-sm);
        }

        .feature-description {
          color: var(--text-secondary);
          font-size: 0.9375rem;
          line-height: 1.6;
        }
      `}</style>
    </div>
  );
}

export default HomePage;
