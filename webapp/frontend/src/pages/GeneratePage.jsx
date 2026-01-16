// Cache bust: 2026-01-10T23:31:00 - React must parse topic objects properly
import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { FileEdit, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';

function GeneratePage() {
    const { generatedSyllabus, setGeneratedSyllabus } = useSyllabus();

    // Collapsible sections
    const [expandedSections, setExpandedSections] = useState({
        institution: true,
        course: true,
        content: false,
        references: false,
        settings: false
    });

    const [formData, setFormData] = useState({
        // Institution Details
        university_name: 'Vishwakarma University, Pune',
        faculty_name: 'Faculty of Science and Technology',
        department: 'Computer Science',

        // Course Details
        course_title: '',
        course_code: '',
        course_type: 'DSC',  // DSC, GEC, SEC, etc.
        credits: '3-1-0',
        lecture_hours: '3',
        tutorial_hours: '1',
        practical_hours: '0',
        program: '',
        semester: 'I',
        year: '2024-25',
        course_level: 'intermediate',

        // Content
        program_outcomes: ['PO1', 'PO2', 'PO3', 'PO4', 'PO5'],
        keywords: '',
        unit_topics: [],
        num_units: 5,
        num_outcomes: 5,

        // References
        textbooks: '',
        references: '',
        online_resources: '',

        // Settings
        domain: 'engineering',
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const toggleSection = (section) => {
        setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setGeneratedSyllabus(null);

        const loadingToast = toast.loading('🎨 Generating syllabus with AI...');

        try {
            const keywords = formData.keywords.split(',').map(k => k.trim()).filter(k => k);
            const textbooks = formData.textbooks.split(',').map(t => t.trim()).filter(t => t);
            const references = formData.references.split(',').map(r => r.trim()).filter(r => r);
            const online_resources = formData.online_resources.split(',').map(o => o.trim()).filter(o => o);

            const response = await apiService.generateSyllabus({
                ...formData,
                credits: `${formData.lecture_hours}-${formData.tutorial_hours}-${formData.practical_hours}`,
                keywords,
                textbooks,
                references,
                online_resources,
            });

            setGeneratedSyllabus(response.syllabus);
            toast.success('✅ Syllabus generated successfully!', { id: loadingToast });
        } catch (err) {
            const errorMsg = err.response?.data?.detail || 'Failed to generate syllabus';
            setError(errorMsg);
            toast.error(`❌ ${errorMsg}`, { id: loadingToast });
        } finally {
            setLoading(false);
        }
    };

    const handleExportPDF = async () => {
        if (!generatedSyllabus) return;
        const loadingToast = toast.loading('📄 Exporting PDF...');
        try {
            await apiService.exportPDF({
                ...generatedSyllabus,
                university_name: formData.university_name,
                faculty_name: formData.faculty_name,
                department: formData.department,
            });
            toast.success('✅ PDF downloaded successfully!', { id: loadingToast });
        } catch (err) {
            toast.error('❌ Failed to export PDF', { id: loadingToast });
        }
    };

    const handleExportWord = async () => {
        if (!generatedSyllabus) return;
        const loadingToast = toast.loading('📝 Exporting Word document...');
        try {
            await apiService.exportWord({
                ...generatedSyllabus,
                university_name: formData.university_name,
                faculty_name: formData.faculty_name,
                department: formData.department,
            });
            toast.success('✅ Word document downloaded successfully!', { id: loadingToast });
        } catch (err) {
            toast.error('❌ Failed to export Word', { id: loadingToast });
        }
    };

    const handleExportLatexPDF = async () => {
        if (!generatedSyllabus) return;
        const loadingToast = toast.loading('📐 Exporting LaTeX PDF...');
        try {
            const exportData = {
                ...generatedSyllabus,
                university_name: formData.university_name,
                faculty_name: formData.faculty_name,
                department: formData.department,
            };

            const response = await fetch('http://localhost:8000/api/export/latex-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ syllabus_data: exportData })
            });

            if (!response.ok) throw new Error('Export failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${exportData.course_code || 'syllabus'}_latex.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            toast.success('✅ LaTeX PDF downloaded successfully!', { id: loadingToast });
        } catch (err) {
            toast.error('❌ Failed to export LaTeX PDF', { id: loadingToast });
        }
    };

    const SectionHeader = ({ title, section, icon }) => (
        <div className="section-header" onClick={() => toggleSection(section)}>
            <div className="section-title">
                <span className="section-icon">{icon}</span>
                <h3>{title}</h3>
            </div>
            {expandedSections[section] ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>
    );

    return (
        <div className="generate-page">
            <div className="container">
                <div className="page-header">
                    <h1 className="page-title">📚 Generate Syllabus [TEST-v3]</h1>
                    <p className="page-subtitle">
                        Create a professional academic syllabus using AI
                    </p>
                </div>

                <div className="main-content">
                    {/* Form Section */}
                    <div className="form-container">
                        <form onSubmit={handleSubmit}>

                            {/* Institution Details */}
                            <div className="form-section-card">
                                <SectionHeader title="Institution Details" section="institution" icon="🏛️" />
                                {expandedSections.institution && (
                                    <div className="section-content">
                                        <div className="form-row">
                                            <div className="form-group">
                                                <label>University Name</label>
                                                <input
                                                    type="text"
                                                    name="university_name"
                                                    value={formData.university_name}
                                                    onChange={handleChange}
                                                    placeholder="e.g., Vishwakarma University, Pune"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label>Faculty/School</label>
                                                <input
                                                    type="text"
                                                    name="faculty_name"
                                                    value={formData.faculty_name}
                                                    onChange={handleChange}
                                                    placeholder="e.g., Faculty of Science and Technology"
                                                />
                                            </div>
                                        </div>
                                        <div className="form-row">
                                            <div className="form-group">
                                                <label>Department</label>
                                                <input
                                                    type="text"
                                                    name="department"
                                                    value={formData.department}
                                                    onChange={handleChange}
                                                    placeholder="e.g., Computer Science"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label>Program</label>
                                                <input
                                                    type="text"
                                                    name="program"
                                                    value={formData.program}
                                                    onChange={handleChange}
                                                    placeholder="e.g., M.Sc Computer Science"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Course Details */}
                            <div className="form-section-card">
                                <SectionHeader title="Course Details" section="course" icon="📖" />
                                {expandedSections.course && (
                                    <div className="section-content">
                                        <div className="form-row">
                                            <div className="form-group flex-2">
                                                <label>Course Title *</label>
                                                <input
                                                    type="text"
                                                    name="course_title"
                                                    value={formData.course_title}
                                                    onChange={handleChange}
                                                    placeholder="e.g., Design and Analysis of Algorithms"
                                                    required
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label>Course Code *</label>
                                                <input
                                                    type="text"
                                                    name="course_code"
                                                    value={formData.course_code}
                                                    onChange={handleChange}
                                                    placeholder="e.g., MSCCS24101"
                                                    required
                                                />
                                            </div>
                                        </div>

                                        <div className="form-row">
                                            <div className="form-group">
                                                <label>Course Type</label>
                                                <select name="course_type" value={formData.course_type} onChange={handleChange}>
                                                    <option value="DSC">DSC - Discipline Specific Core</option>
                                                    <option value="DSE">DSE - Discipline Specific Elective</option>
                                                    <option value="GEC">GEC - Generic Elective Core</option>
                                                    <option value="SEC">SEC - Skill Enhancement Course</option>
                                                    <option value="AEC">AEC - Ability Enhancement Course</option>
                                                    <option value="VAC">VAC - Value Added Course</option>
                                                </select>
                                            </div>
                                            <div className="form-group">
                                                <label>Semester</label>
                                                <select name="semester" value={formData.semester} onChange={handleChange}>
                                                    <option value="I">Semester I</option>
                                                    <option value="II">Semester II</option>
                                                    <option value="III">Semester III</option>
                                                    <option value="IV">Semester IV</option>
                                                    <option value="V">Semester V</option>
                                                    <option value="VI">Semester VI</option>
                                                    <option value="VII">Semester VII</option>
                                                    <option value="VIII">Semester VIII</option>
                                                </select>
                                            </div>
                                            <div className="form-group">
                                                <label>Academic Year</label>
                                                <input
                                                    type="text"
                                                    name="year"
                                                    value={formData.year}
                                                    onChange={handleChange}
                                                    placeholder="e.g., 2024-25"
                                                />
                                            </div>
                                        </div>

                                        <div className="form-row">
                                            <div className="form-group">
                                                <label>Lecture (L)</label>
                                                <input
                                                    type="number"
                                                    name="lecture_hours"
                                                    value={formData.lecture_hours}
                                                    onChange={handleChange}
                                                    min="0" max="6"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label>Tutorial (T)</label>
                                                <input
                                                    type="number"
                                                    name="tutorial_hours"
                                                    value={formData.tutorial_hours}
                                                    onChange={handleChange}
                                                    min="0" max="6"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label>Practical (P)</label>
                                                <input
                                                    type="number"
                                                    name="practical_hours"
                                                    value={formData.practical_hours}
                                                    onChange={handleChange}
                                                    min="0" max="6"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label>Course Level</label>
                                                <select name="course_level" value={formData.course_level} onChange={handleChange}>
                                                    <option value="introductory">Introductory</option>
                                                    <option value="intermediate">Intermediate</option>
                                                    <option value="advanced">Advanced</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Course Content */}
                            <div className="form-section-card">
                                <SectionHeader title="Course Content" section="content" icon="📝" />
                                {expandedSections.content && (
                                    <div className="section-content">
                                        <div className="form-group">
                                            <label>Keywords / Topics *</label>
                                            <textarea
                                                name="keywords"
                                                value={formData.keywords}
                                                onChange={handleChange}
                                                placeholder="Enter comma-separated keywords (e.g., algorithms, complexity, sorting, graphs)"
                                                rows={2}
                                                required
                                            />
                                        </div>

                                        <div className="form-row">
                                            <div className="form-group">
                                                <label>Number of Units</label>
                                                <input
                                                    type="number"
                                                    name="num_units"
                                                    value={formData.num_units}
                                                    onChange={handleChange}
                                                    min="3" max="8"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label>Number of COs</label>
                                                <input
                                                    type="number"
                                                    name="num_outcomes"
                                                    value={formData.num_outcomes}
                                                    onChange={handleChange}
                                                    min="3" max="8"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label>Domain</label>
                                                <select name="domain" value={formData.domain} onChange={handleChange}>
                                                    <option value="engineering">Engineering</option>
                                                    <option value="science">Science</option>
                                                    <option value="management">Management</option>
                                                    <option value="humanities">Humanities</option>
                                                </select>
                                            </div>
                                        </div>

                                        <div className="unit-topics-grid">
                                            <label>Unit-wise Topics (Optional)</label>
                                            {Array.from({ length: formData.num_units }, (_, i) => (
                                                <div key={i} className="unit-input">
                                                    <span className="unit-badge">U{i + 1}</span>
                                                    <input
                                                        type="text"
                                                        placeholder={`Unit ${i + 1} topics (comma-separated)`}
                                                        value={formData.unit_topics[i]?.topics?.join(', ') || ''}
                                                        onChange={(e) => {
                                                            const topics = e.target.value.split(',').map(t => t.trim()).filter(t => t);
                                                            const newUnitTopics = [...formData.unit_topics];
                                                            newUnitTopics[i] = { unit_number: i + 1, topics };
                                                            setFormData(prev => ({ ...prev, unit_topics: newUnitTopics }));
                                                        }}
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* References */}
                            <div className="form-section-card">
                                <SectionHeader title="References & Textbooks" section="references" icon="📚" />
                                {expandedSections.references && (
                                    <div className="section-content">
                                        <p className="hint">Leave empty to auto-generate references</p>
                                        <div className="form-group">
                                            <label>Textbooks</label>
                                            <textarea
                                                name="textbooks"
                                                value={formData.textbooks}
                                                onChange={handleChange}
                                                placeholder="e.g., Introduction to Algorithms by Cormen, Data Structures by Aho"
                                                rows={2}
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Reference Books</label>
                                            <textarea
                                                name="references"
                                                value={formData.references}
                                                onChange={handleChange}
                                                placeholder="Additional reference materials"
                                                rows={2}
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Online Resources</label>
                                            <textarea
                                                name="online_resources"
                                                value={formData.online_resources}
                                                onChange={handleChange}
                                                placeholder="e.g., Coursera ML Course, MIT OCW"
                                                rows={2}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Submit Button */}
                            <button type="submit" className="submit-btn" disabled={loading}>
                                {loading ? (
                                    <><span className="spinner"></span> Generating...</>
                                ) : (
                                    '✨ Generate Syllabus'
                                )}
                            </button>
                        </form>
                    </div>

                    {/* Result Section */}
                    <div className="result-container">
                        {error && (
                            <div className="error-box">
                                <strong>Error:</strong> {error}
                            </div>
                        )}

                        {!generatedSyllabus && !error && (
                            <div className="empty-state">
                                <div className="empty-icon">📄</div>
                                <h3>No Syllabus Generated</h3>
                                <p>Fill in the form and click "Generate Syllabus" to create your course syllabus.</p>
                            </div>
                        )}

                        {generatedSyllabus && (
                            <div className="result-card">
                                <div className="result-header">
                                    <h2>Generated Syllabus</h2>
                                    <div className="export-btns">
                                        <button onClick={handleExportPDF} className="export-btn pdf">
                                            <FileText size={16} /> PDF
                                        </button>
                                        <button onClick={handleExportLatexPDF} className="export-btn latex">
                                            📐 LaTeX PDF
                                        </button>
                                        <button onClick={handleExportWord} className="export-btn word">
                                            <FileEdit size={16} /> Word
                                        </button>
                                    </div>
                                </div>

                                <div className="syllabus-preview">
                                    {/* Course Header */}
                                    <div className="preview-section header-section">
                                        <h3>{generatedSyllabus.course_code}: {generatedSyllabus.course_title}</h3>
                                        <div className="meta-grid">
                                            <span><strong>Credits:</strong> {generatedSyllabus.credits}</span>
                                            {generatedSyllabus.program && <span><strong>Program:</strong> {generatedSyllabus.program}</span>}
                                            {generatedSyllabus.course_level && (
                                                <span className={`level-badge ${generatedSyllabus.course_level}`}>
                                                    {generatedSyllabus.course_level}
                                                </span>
                                            )}
                                        </div>
                                    </div>

                                    {/* Overview */}
                                    {generatedSyllabus.overview && (
                                        <div className="preview-section">
                                            <h4>Course Description</h4>
                                            <p>{generatedSyllabus.overview}</p>
                                        </div>
                                    )}

                                    {/* Course Outcomes */}
                                    {generatedSyllabus.learning_outcomes && (
                                        <div className="preview-section">
                                            <h4>Course Outcomes</h4>
                                            <table className="co-table">
                                                <thead>
                                                    <tr>
                                                        <th>CO</th>
                                                        <th>Statement</th>
                                                        <th>BTL</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {generatedSyllabus.learning_outcomes.map((co, idx) => (
                                                        <tr key={idx}>
                                                            <td>{co.code}</td>
                                                            <td>{co.description}</td>
                                                            <td className="btl">{co.bloom_level}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    )}

                                    {/* Units */}
                                    {generatedSyllabus.units && (
                                        <div className="preview-section">
                                            <h4>Course Content <span style={{ fontSize: '0.7em', color: '#888' }}>(v2.1)</span></h4>
                                            {console.log('DEBUG: units type:', typeof generatedSyllabus.units, 'first unit topics type:', typeof generatedSyllabus.units[0]?.topics)}
                                            {generatedSyllabus.units.map((unit, idx) => {
                                                // Helper to parse a single topic if it's a string
                                                const parseTopic = (topic) => {
                                                    if (!topic) return { topic: '' };
                                                    if (typeof topic === 'object') return topic;
                                                    if (typeof topic === 'string') {
                                                        try {
                                                            // Try to parse Python dict format (single quotes -> double quotes)
                                                            return JSON.parse(topic.replace(/'/g, '"'));
                                                        } catch (e) {
                                                            return { topic: topic }; // Just use string as topic name
                                                        }
                                                    }
                                                    return { topic: String(topic) };
                                                };

                                                // Helper to safely extract topic content
                                                const getTopicName = (topic) => {
                                                    const t = parseTopic(topic);
                                                    return t?.topic || '';
                                                };
                                                const getTopicDesc = (topic) => {
                                                    const t = parseTopic(topic);
                                                    return t?.description || null;
                                                };
                                                const getSubtopics = (topic) => {
                                                    const t = parseTopic(topic);
                                                    return Array.isArray(t?.subtopics) ? t.subtopics : [];
                                                };
                                                const getKeyConcepts = (topic) => {
                                                    const t = parseTopic(topic);
                                                    return Array.isArray(t?.key_concepts) ? t.key_concepts : [];
                                                };

                                                // Get topics array (handle string or array)
                                                let topicsArray = unit.topics || [];
                                                if (typeof topicsArray === 'string') {
                                                    try {
                                                        topicsArray = JSON.parse(topicsArray.replace(/'/g, '"'));
                                                    } catch (e) {
                                                        topicsArray = [{ topic: topicsArray }];
                                                    }
                                                }

                                                return (
                                                    <div key={idx} className="unit-block">
                                                        <div className="unit-header">
                                                            <span className="unit-num">Unit {unit.unit_number}</span>
                                                            <span className="unit-title">{unit.title}</span>
                                                            <span className="unit-hours">{unit.hours} Hrs</span>
                                                        </div>
                                                        {unit.overview && (
                                                            <p className="unit-overview">{unit.overview}</p>
                                                        )}
                                                        <div className="topic-list-detailed">
                                                            {Array.isArray(topicsArray) && topicsArray.map((topic, tidx) => (
                                                                <div key={tidx} className="topic-item">
                                                                    <div className="topic-name">
                                                                        {getTopicName(topic)}
                                                                    </div>
                                                                    {getTopicDesc(topic) && (
                                                                        <p className="topic-description">{getTopicDesc(topic)}</p>
                                                                    )}
                                                                    {getSubtopics(topic).length > 0 && (
                                                                        <ul className="subtopic-list">
                                                                            {getSubtopics(topic).map((st, stidx) => (
                                                                                <li key={stidx}>{st}</li>
                                                                            ))}
                                                                        </ul>
                                                                    )}
                                                                    {getKeyConcepts(topic).length > 0 && (
                                                                        <div className="key-concepts">
                                                                            <strong>Key Concepts:</strong> {getKeyConcepts(topic).join(', ')}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            ))}
                                                        </div>
                                                        {unit.learning_activities && unit.learning_activities.length > 0 && (
                                                            <div className="learning-activities">
                                                                <strong>Learning Activities:</strong>
                                                                <ul>
                                                                    {unit.learning_activities.map((act, aidx) => (
                                                                        <li key={aidx}>{act}</li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}

                                    {/* References */}
                                    {generatedSyllabus.references && (
                                        <div className="preview-section">
                                            <h4>References</h4>
                                            {generatedSyllabus.references.textbooks?.length > 0 && (
                                                <div className="ref-group">
                                                    <strong>Textbooks:</strong>
                                                    <ol>
                                                        {generatedSyllabus.references.textbooks.map((book, idx) => (
                                                            <li key={idx}>{book}</li>
                                                        ))}
                                                    </ol>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* CO-PO Mapping */}
                                    {generatedSyllabus.copo_summary && (
                                        <div className="preview-section copo">
                                            <h4>CO-PO Mapping</h4>
                                            <p>{generatedSyllabus.copo_summary}</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <style>{`
                .generate-page {
                    padding: 2rem 0;
                    min-height: 100vh;
                    background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
                    transition: background var(--transition-base);
                }

                .container {
                    max-width: none;
                    margin: 0;
                    padding: 0 1.5rem;
                    width: 100%;
                }

                .page-header {
                    text-align: center;
                    margin-bottom: 2rem;
                }

                .page-title {
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: var(--text-primary);
                    margin-bottom: 0.5rem;
                }

                .page-subtitle {
                    color: var(--text-secondary);
                    font-size: 1.1rem;
                }

                .main-content {
                    display: grid;
                    grid-template-columns: 65% 1fr;
                    gap: 1.5rem;
                    align-items: start;
                }

                /* Form Styles */
                .form-container {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }

                .form-section-card {
                    background: var(--bg-primary);
                    border-radius: 12px;
                    box-shadow: var(--shadow-md);
                    overflow: hidden;
                    border: 1px solid var(--border);
                    transition: background var(--transition-base), border-color var(--transition-base);
                }

                .section-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem 1.25rem;
                    background: var(--bg-secondary);
                    cursor: pointer;
                    border-bottom: 1px solid var(--border);
                    transition: background 0.2s;
                    color: var(--text-primary);
                }

                .section-header:hover {
                    background: var(--bg-hover);
                }

                .section-title {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }

                .section-title h3 {
                    font-size: 1rem;
                    font-weight: 600;
                    color: var(--text-primary);
                    margin: 0;
                }

                .section-icon {
                    font-size: 1.25rem;
                }

                .section-content {
                    padding: 1.25rem;
                }

                .form-row {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 1rem;
                }

                .form-row .form-group {
                    flex: 1;
                }

                .form-row .form-group.flex-2 {
                    flex: 2;
                }

                .form-group {
                    margin-bottom: 0.75rem;
                }

                .form-group label {
                    display: block;
                    font-size: 0.85rem;
                    font-weight: 500;
                    color: var(--text-secondary);
                    margin-bottom: 0.35rem;
                }

                .form-group input,
                .form-group select,
                .form-group textarea {
                    width: 100%;
                    padding: 0.6rem 0.75rem;
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    font-size: 0.9rem;
                    transition: border-color 0.2s, box-shadow 0.2s;
                    background: var(--bg-primary);
                    color: var(--text-primary);
                }

                .form-group input:focus,
                .form-group select:focus,
                .form-group textarea:focus {
                    outline: none;
                    border-color: var(--primary);
                    box-shadow: 0 0 0 3px hsla(220, 90%, 56%, 0.15);
                }

                .hint {
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                    margin-bottom: 1rem;
                }

                .unit-topics-grid {
                    margin-top: 1rem;
                }

                .unit-topics-grid label {
                    display: block;
                    font-size: 0.85rem;
                    font-weight: 500;
                    color: var(--text-secondary);
                    margin-bottom: 0.5rem;
                }

                .unit-input {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 0.5rem;
                }

                .unit-badge {
                    background: var(--primary);
                    color: white;
                    padding: 0.35rem 0.6rem;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 600;
                }

                .unit-input input {
                    flex: 1;
                    padding: 0.5rem 0.75rem;
                    border: 1px solid var(--border);
                    border-radius: 6px;
                    background: var(--bg-primary);
                    color: var(--text-primary);
                }

                .submit-btn {
                    width: 100%;
                    padding: 1rem;
                    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                    color: white;
                    font-size: 1.1rem;
                    font-weight: 600;
                    border: none;
                    border-radius: 12px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0.5rem;
                    transition: transform 0.2s, box-shadow 0.2s;
                }

                .submit-btn:hover:not(:disabled) {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 20px hsla(220, 90%, 56%, 0.3);
                }

                .submit-btn:disabled {
                    opacity: 0.7;
                    cursor: not-allowed;
                }

                .spinner {
                    width: 20px;
                    height: 20px;
                    border: 2px solid rgba(255,255,255,0.3);
                    border-top-color: white;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }

                /* Result Styles */
                .result-container {
                    position: sticky;
                    top: 1rem;
                }

                .empty-state {
                    background: var(--bg-primary);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    box-shadow: var(--shadow-md);
                    font-size: 0.9rem;
                    border: 1px solid var(--border);
                }

                .empty-icon {
                    font-size: 2.5rem;
                    margin-bottom: 0.5rem;
                }

                .empty-state h3 {
                    color: var(--text-primary);
                    margin-bottom: 0.5rem;
                }

                .empty-state p {
                    color: var(--text-secondary);
                }

                .error-box {
                    background: hsla(0, 84%, 60%, 0.1);
                    border: 1px solid hsla(0, 84%, 60%, 0.3);
                    color: var(--error);
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                }

                .result-card {
                    background: var(--bg-primary);
                    border-radius: 12px;
                    box-shadow: var(--shadow-md);
                    overflow: hidden;
                    border: 1px solid var(--border);
                }

                .result-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem 1.25rem;
                    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                    color: white;
                }

                .result-header h2 {
                    font-size: 1.1rem;
                    font-weight: 600;
                    margin: 0;
                }

                .export-btns {
                    display: flex;
                    gap: 0.5rem;
                }

                .export-btn {
                    display: flex;
                    align-items: center;
                    gap: 0.35rem;
                    padding: 0.5rem 0.75rem;
                    border: none;
                    border-radius: 6px;
                    font-size: 0.85rem;
                    font-weight: 500;
                    cursor: pointer;
                    transition: opacity 0.2s;
                }

                .export-btn.pdf {
                    background: var(--error);
                    color: white;
                }

                .export-btn.word {
                    background: hsl(217, 91%, 60%);
                    color: white;
                }

                .syllabus-preview {
                    padding: 1.25rem;
                    max-height: 70vh;
                    overflow-y: auto;
                    color: var(--text-primary);
                }

                .preview-section {
                    margin-bottom: 1.5rem;
                    padding-bottom: 1rem;
                    border-bottom: 1px solid var(--border);
                }

                .preview-section:last-child {
                    border-bottom: none;
                    margin-bottom: 0;
                }

                .preview-section h4 {
                    font-size: 0.9rem;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 0.75rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .header-section h3 {
                    font-size: 1.2rem;
                    color: var(--text-primary);
                    margin-bottom: 0.5rem;
                }

                .meta-grid {
                    display: flex;
                    gap: 1rem;
                    flex-wrap: wrap;
                    font-size: 0.85rem;
                    color: var(--text-secondary);
                }

                .level-badge {
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 500;
                    text-transform: capitalize;
                }

                .level-badge.introductory { background: hsla(160, 84%, 39%, 0.15); color: hsla(160, 84%, 39%, 1); }
                .level-badge.intermediate { background: hsla(217, 91%, 60%, 0.15); color: hsla(217, 91%, 60%, 1); }
                .level-badge.advanced { background: hsla(28, 100%, 50%, 0.15); color: hsla(28, 100%, 50%, 1); }

                [data-theme="dark"] .level-badge.introductory { background: hsla(160, 84%, 39%, 0.25); color: hsla(160, 84%, 70%, 1); }
                [data-theme="dark"] .level-badge.intermediate { background: hsla(217, 91%, 60%, 0.25); color: hsla(217, 91%, 80%, 1); }
                [data-theme="dark"] .level-badge.advanced { background: hsla(28, 100%, 50%, 0.25); color: hsla(28, 100%, 70%, 1); }

                .co-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.85rem;
                }

                .co-table th, .co-table td {
                    padding: 0.5rem;
                    border: 1px solid var(--border);
                    text-align: left;
                    color: var(--text-primary);
                }

                .co-table th {
                    background: var(--bg-secondary);
                    font-weight: 600;
                    color: var(--text-secondary);
                }

                .co-table .btl {
                    text-transform: capitalize;
                    color: var(--primary);
                    font-weight: 500;
                }

                .unit-block {
                    background: var(--bg-secondary);
                    border-radius: 8px;
                    padding: 0.75rem;
                    margin-bottom: 0.75rem;
                }

                .unit-header {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    margin-bottom: 0.5rem;
                }

                .unit-num {
                    background: var(--primary);
                    color: white;
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 600;
                }

                .unit-title {
                    flex: 1;
                    font-weight: 600;
                    color: var(--text-primary);
                }

                .unit-hours {
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                }

                .topic-list {
                    margin: 0;
                    padding-left: 1.5rem;
                    font-size: 0.85rem;
                    color: var(--text-secondary);
                }

                .topic-list li {
                    margin-bottom: 0.25rem;
                }

                /* Detailed topic styles */
                .unit-overview {
                    font-style: italic;
                    color: var(--text-secondary);
                    font-size: 0.85rem;
                    margin: 0.5rem 0 0.75rem 0;
                    padding: 0.5rem;
                    background: var(--bg-tertiary);
                    border-radius: 4px;
                    border-left: 3px solid var(--primary);
                }

                .topic-list-detailed {
                    margin-top: 0.5rem;
                }

                .topic-item {
                    margin-bottom: 0.75rem;
                    padding: 0.5rem;
                    background: var(--bg-primary);
                    border-radius: 6px;
                    border-left: 2px solid var(--primary);
                }

                .topic-name {
                    font-weight: 600;
                    color: var(--text-primary);
                    font-size: 0.9rem;
                    margin-bottom: 0.25rem;
                }

                .topic-description {
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                    margin: 0.25rem 0;
                    line-height: 1.5;
                }

                .subtopic-list {
                    margin: 0.25rem 0 0.25rem 1rem;
                    padding-left: 0.5rem;
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                }

                .subtopic-list li {
                    margin-bottom: 0.15rem;
                }

                .key-concepts {
                    font-size: 0.75rem;
                    color: var(--accent);
                    margin-top: 0.25rem;
                }

                .learning-activities {
                    margin-top: 0.5rem;
                    padding-top: 0.5rem;
                    border-top: 1px dashed var(--border);
                    font-size: 0.8rem;
                }

                .learning-activities ul {
                    margin: 0.25rem 0 0 1rem;
                    padding-left: 0.5rem;
                    color: var(--text-secondary);
                }

                .ref-group {
                    margin-bottom: 0.75rem;
                }

                .ref-group ol {
                    margin: 0.5rem 0 0 1.5rem;
                    font-size: 0.85rem;
                    color: var(--text-secondary);
                }

                .copo {
                    background: linear-gradient(135deg, hsla(250, 84%, 90%, 0.5) 0%, hsla(260, 84%, 90%, 0.5) 100%);
                    padding: 1rem;
                    border-radius: 8px;
                }

                [data-theme="dark"] .copo {
                    background: linear-gradient(135deg, hsla(250, 44%, 20%, 0.5) 0%, hsla(260, 44%, 20%, 0.5) 100%);
                }

                .copo p {
                    font-style: italic;
                    color: var(--primary);
                }

                @media (max-width: 1024px) {
                    .main-content {
                        grid-template-columns: 1fr;
                    }

                    .result-container {
                        position: static;
                    }
                }

                @media (max-width: 640px) {
                    .form-row {
                        flex-direction: column;
                    }

                    .page-title {
                        font-size: 1.75rem;
                    }
                }
            `}</style>
        </div>
    );
}

export default GeneratePage;
