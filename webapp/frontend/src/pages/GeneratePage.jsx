import React, { useState } from 'react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';

function GeneratePage() {
    const { generatedSyllabus, setGeneratedSyllabus } = useSyllabus();

    const [formData, setFormData] = useState({
        course_title: '',
        course_code: '',
        credits: '3-0-0',
        program_outcomes: ['PO1', 'PO2', 'PO3'],
        keywords: '',
        domain: 'engineering',
        num_units: 5,
        num_outcomes: 5,
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setGeneratedSyllabus(null);

        try {
            // Parse keywords
            const keywords = formData.keywords.split(',').map(k => k.trim()).filter(k => k);

            const response = await apiService.generateSyllabus({
                ...formData,
                keywords,
            });

            setGeneratedSyllabus(response.syllabus);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to generate syllabus');
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async () => {
        if (!generatedSyllabus) return;

        try {
            await apiService.exportPDF(generatedSyllabus);
        } catch (err) {
            setError('Failed to export PDF');
        }
    };

    return (
        <div className="generate-page">
            <div className="container">
                <div className="page-header">
                    <h1 className="page-title">Generate Syllabus</h1>
                    <p className="page-subtitle">
                        Create a complete syllabus using AI from minimal inputs
                    </p>
                </div>

                <div className="content-grid">
                    {/* Form Section */}
                    <div className="form-section">
                        <div className="card">
                            <div className="card-header">
                                <h2 className="card-title">Course Details</h2>
                                <p className="card-subtitle">Provide basic information about your course</p>
                            </div>

                            <form onSubmit={handleSubmit}>
                                <div className="form-group">
                                    <label className="form-label">Course Title *</label>
                                    <input
                                        type="text"
                                        name="course_title"
                                        className="form-input"
                                        value={formData.course_title}
                                        onChange={handleChange}
                                        placeholder="e.g., Machine Learning"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Course Code *</label>
                                    <input
                                        type="text"
                                        name="course_code"
                                        className="form-input"
                                        value={formData.course_code}
                                        onChange={handleChange}
                                        placeholder="e.g., CS401"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Credits (L-T-P) *</label>
                                    <input
                                        type="text"
                                        name="credits"
                                        className="form-input"
                                        value={formData.credits}
                                        onChange={handleChange}
                                        placeholder="e.g., 3-0-2"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Keywords (comma-separated) *</label>
                                    <textarea
                                        name="keywords"
                                        className="form-textarea"
                                        value={formData.keywords}
                                        onChange={handleChange}
                                        placeholder="e.g., neural networks, deep learning, classification"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Domain</label>
                                    <select
                                        name="domain"
                                        className="form-select"
                                        value={formData.domain}
                                        onChange={handleChange}
                                    >
                                        <option value="engineering">Engineering</option>
                                        <option value="management">Management</option>
                                        <option value="science">Science</option>
                                        <option value="humanities">Humanities</option>
                                    </select>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label className="form-label">Number of Units</label>
                                        <input
                                            type="number"
                                            name="num_units"
                                            className="form-input"
                                            value={formData.num_units}
                                            onChange={handleChange}
                                            min="3"
                                            max="8"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Number of Outcomes</label>
                                        <input
                                            type="number"
                                            name="num_outcomes"
                                            className="form-input"
                                            value={formData.num_outcomes}
                                            onChange={handleChange}
                                            min="4"
                                            max="8"
                                        />
                                    </div>
                                </div>

                                <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                                    {loading ? (
                                        <>
                                            <span className="spinner"></span>
                                            Generating...
                                        </>
                                    ) : (
                                        '✨ Generate Syllabus'
                                    )}
                                </button>
                            </form>
                        </div>
                    </div>

                    {/* Result Section */}
                    <div className="result-section">
                        {error && (
                            <div className="alert alert-error">
                                <strong>Error:</strong> {error}
                            </div>
                        )}

                        {generatedSyllabus && (
                            <div className="card result-card fade-in">
                                <div className="card-header">
                                    <h2 className="card-title">Generated Syllabus</h2>
                                    <button onClick={handleExport} className="btn btn-secondary">
                                        📄 Export PDF
                                    </button>
                                </div>

                                <div className="syllabus-content">
                                    <section className="syllabus-section">
                                        <h3>Course Information</h3>
                                        <p><strong>Title:</strong> {generatedSyllabus.course_title}</p>
                                        <p><strong>Code:</strong> {generatedSyllabus.course_code}</p>
                                        <p><strong>Credits:</strong> {generatedSyllabus.credits}</p>
                                    </section>

                                    {generatedSyllabus.overview && (
                                        <section className="syllabus-section">
                                            <h3>Course Overview</h3>
                                            <p>{generatedSyllabus.overview}</p>
                                        </section>
                                    )}

                                    {generatedSyllabus.learning_outcomes && (
                                        <section className="syllabus-section">
                                            <h3>Learning Outcomes</h3>
                                            <div className="outcomes-list">
                                                {generatedSyllabus.learning_outcomes.map((outcome, idx) => (
                                                    <div key={idx} className="outcome-item">
                                                        <span className="outcome-code">{outcome.code}</span>
                                                        <span className="outcome-text">{outcome.description}</span>
                                                        <span className={`badge badge-${getBloomColor(outcome.bloom_level)}`}>
                                                            {outcome.bloom_level}
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </section>
                                    )}

                                    {generatedSyllabus.units && (
                                        <section className="syllabus-section">
                                            <h3>Units</h3>
                                            {generatedSyllabus.units.map((unit, idx) => (
                                                <div key={idx} className="unit-card">
                                                    <h4>Unit {unit.unit_number}: {unit.title} ({unit.hours} hours)</h4>
                                                    <ul>
                                                        {unit.topics.map((topic, tidx) => (
                                                            <li key={tidx}>{topic}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            ))}
                                        </section>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <style>{`
        .page-header {
          text-align: center;
          margin-bottom: var(--spacing-2xl);
        }

        .page-title {
          font-size: 2.5rem;
          margin-bottom: var(--spacing-sm);
        }

        .page-subtitle {
          font-size: 1.125rem;
          color: var(--text-secondary);
        }

        .content-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--spacing-xl);
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--spacing-md);
        }

        .alert {
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-lg);
        }

        .alert-error {
          background: hsl(0, 84%, 95%);
          color: var(--error);
          border: 1px solid var(--error);
        }

        .result-card {
          max-height: 80vh;
          overflow-y: auto;
        }

        .syllabus-content {
          padding: var(--spacing-md);
        }

        .syllabus-section {
          margin-bottom: var(--spacing-xl);
        }

        .syllabus-section h3 {
          color: var(--primary);
          margin-bottom: var(--spacing-md);
          padding-bottom: var(--spacing-sm);
          border-bottom: 2px solid var(--primary);
        }

        .outcomes-list {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
        }

        .outcome-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm);
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
        }

        .outcome-code {
          font-weight: 700;
          color: var(--primary);
          min-width: 50px;
        }

        .outcome-text {
          flex: 1;
        }

        .unit-card {
          background: var(--bg-secondary);
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-md);
        }

        .unit-card h4 {
          color: var(--secondary);
          margin-bottom: var(--spacing-sm);
        }

        .unit-card ul {
          margin-left: var(--spacing-lg);
        }

        .unit-card li {
          margin-bottom: var(--spacing-xs);
        }

        @media (max-width: 1024px) {
          .content-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
        </div>
    );
}

function getBloomColor(level) {
    const colors = {
        remember: 'primary',
        understand: 'primary',
        apply: 'success',
        analyze: 'warning',
        evaluate: 'warning',
        create: 'error',
    };
    return colors[level] || 'primary';
}

export default GeneratePage;
