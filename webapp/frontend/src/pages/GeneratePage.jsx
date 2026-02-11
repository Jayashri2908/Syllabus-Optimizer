// Cache bust: 2026-01-10T23:31:00 - React must parse topic objects properly
import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { FileEdit, FileText, ChevronDown, ChevronUp, BookOpen, Layers, Settings, School, Download, Wand2 } from 'lucide-react';
import { apiService } from '../services/api';
import { useSyllabus } from '../context/SyllabusContext';

function GeneratePage() {
    const { generatedSyllabus, setGeneratedSyllabus } = useSyllabus();

    // Collapsible sections
    const [expandedSections, setExpandedSections] = useState({
        institution: true,
        course: true,
        content: true,
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
        cie_marks: '60',
        ese_marks: '40',

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

        const loadingToast = toast.loading('Generating syllabus with AI...');

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
            toast.success('Syllabus generated successfully', { id: loadingToast });
        } catch (err) {
            const errorMsg = err.response?.data?.detail || 'Failed to generate syllabus';
            setError(errorMsg);
            toast.error(`Generation failed: ${errorMsg}`, { id: loadingToast });
        } finally {
            setLoading(false);
        }
    };

    const handleExportPDF = async () => {
        if (!generatedSyllabus) return;
        const loadingToast = toast.loading('Exporting PDF...');
        try {
            await apiService.exportPDF({
                ...generatedSyllabus,
                university_name: formData.university_name,
                faculty_name: formData.faculty_name,
                department: formData.department,
            });
            toast.success('PDF downloaded successfully', { id: loadingToast });
        } catch (err) {
            toast.error('Failed to export PDF', { id: loadingToast });
        }
    };

    const handleExportWord = async () => {
        if (!generatedSyllabus) return;
        const loadingToast = toast.loading('Exporting Word document...');
        try {
            await apiService.exportWord({
                ...generatedSyllabus,
                university_name: formData.university_name,
                faculty_name: formData.faculty_name,
                department: formData.department,
            });
            toast.success('Word document downloaded successfully', { id: loadingToast });
        } catch (err) {
            toast.error('Failed to export Word', { id: loadingToast });
        }
    };

    const SectionHeader = ({ title, section, icon: Icon }) => (
        <div
            className="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-50 transition-colors border-b border-gray-100"
            onClick={() => toggleSection(section)}
        >
            <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-50 text-brand rounded-lg">
                    <Icon size={20} />
                </div>
                <h3 className="font-bold text-gray-800">{title}</h3>
            </div>
            {expandedSections[section] ? <ChevronUp size={20} className="text-gray-400" /> : <ChevronDown size={20} className="text-gray-400" />}
        </div>
    );

    return (
        <div className="container py-8 animate-fade-in">
            <div className="page-header">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-semibold mb-4">
                    <Wand2 size={14} />
                    <span>AI Content Generation</span>
                </div>
                <h1 className="page-title">Generate Syllabus</h1>
                <p className="page-subtitle">
                    Create a professional academic syllabus using AI
                </p>
            </div>

            <div className="flex flex-col lg:flex-row gap-8 items-start">
                {/* Form Section */}
                <div className="w-full lg:w-3/5 space-y-6">
                    <form onSubmit={handleSubmit}>
                        {/* Institution Details */}
                        <div className="card mb-6 p-0 overflow-hidden">
                            <SectionHeader title="Institution Details" section="institution" icon={School} />
                            {expandedSections.institution && (
                                <div className="p-6 space-y-4">
                                    <div className="grid md:grid-cols-2 gap-4">
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
                                    <div className="grid md:grid-cols-2 gap-4">
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
                        <div className="card mb-6 p-0 overflow-hidden">
                            <SectionHeader title="Course Details" section="course" icon={BookOpen} />
                            {expandedSections.course && (
                                <div className="p-6 space-y-4">
                                    <div className="grid md:grid-cols-2 gap-4">
                                        <div className="form-group md:col-span-2">
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
                                    </div>

                                    <div className="grid md:grid-cols-3 gap-4">
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
                                        <div className="form-group">
                                            <label>Course Level</label>
                                            <select name="course_level" value={formData.course_level} onChange={handleChange}>
                                                <option value="introductory">Introductory</option>
                                                <option value="intermediate">Intermediate</option>
                                                <option value="advanced">Advanced</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                                        <h4 className="text-xs font-bold uppercase text-subtle mb-3">Credits Structure (L-T-P)</h4>
                                        <div className="grid grid-cols-3 gap-4">
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
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="form-group">
                                            <label>CIE Marks</label>
                                            <input
                                                type="number"
                                                name="cie_marks"
                                                value={formData.cie_marks}
                                                onChange={handleChange}
                                                min="0" max="100"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>ESE Marks</label>
                                            <input
                                                type="number"
                                                name="ese_marks"
                                                value={formData.ese_marks}
                                                onChange={handleChange}
                                                min="0" max="100"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Total Marks</label>
                                            <div className="p-3 bg-slate-100 rounded-md text-center font-bold text-primary border border-slate-200">
                                                {parseInt(formData.cie_marks || 0) + parseInt(formData.ese_marks || 0)}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Course Content */}
                        <div className="card mb-6 p-0 overflow-hidden">
                            <SectionHeader title="Course Content" section="content" icon={Layers} />
                            {expandedSections.content && (
                                <div className="p-6 space-y-4">
                                    <div className="form-group">
                                        <label>Keywords / Topics (AI Context) *</label>
                                        <textarea
                                            name="keywords"
                                            value={formData.keywords}
                                            onChange={handleChange}
                                            placeholder="Enter comma-separated keywords (e.g., algorithms, complexity, sorting, graphs, divide and conquer)"
                                            rows={3}
                                            required
                                        />
                                        <p className="text-xs text-subtle mt-1">These keywords guide the AI in generating relevant content.</p>
                                    </div>

                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="form-group">
                                            <label>No. of Units</label>
                                            <input
                                                type="number"
                                                name="num_units"
                                                value={formData.num_units}
                                                onChange={handleChange}
                                                min="3" max="8"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>No. of COs</label>
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

                                    <div className="border-t border-gray-100 pt-4 mt-4">
                                        <label className="block text-sm font-bold text-gray-700 mb-3">Unit-wise Topics (Optional Customization)</label>
                                        <div className="space-y-3">
                                            {Array.from({ length: formData.num_units }, (_, i) => (
                                                <div key={i} className="flex gap-3 items-center">
                                                    <span className="shrink-0 w-8 h-8 rounded bg-primary text-white flex items-center justify-center font-bold text-xs">U{i + 1}</span>
                                                    <input
                                                        className="flex-1 text-sm form-input"
                                                        type="text"
                                                        placeholder={`Specific topics for Unit ${i + 1}...`}
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
                                </div>
                            )}
                        </div>

                        {/* References */}
                        <div className="card mb-6 p-0 overflow-hidden">
                            <SectionHeader title="References & Textbooks" section="references" icon={BookOpen} />
                            {expandedSections.references && (
                                <div className="p-6 space-y-4">
                                    <div className="bg-yellow-50 p-3 rounded-md border border-yellow-100 text-sm text-yellow-800 mb-2">
                                        Leave these fields empty to let AI suggest the best books and resources.
                                    </div>
                                    <div className="form-group">
                                        <label>Textbooks</label>
                                        <textarea
                                            name="textbooks"
                                            value={formData.textbooks}
                                            onChange={handleChange}
                                            placeholder="e.g., Introduction to Algorithms by Cormen..."
                                            rows={2}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Reference Books</label>
                                        <textarea
                                            name="references"
                                            value={formData.references}
                                            onChange={handleChange}
                                            placeholder="Additional reference materials..."
                                            rows={2}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Online Resources</label>
                                        <textarea
                                            name="online_resources"
                                            value={formData.online_resources}
                                            onChange={handleChange}
                                            placeholder="e.g., Coursera ML Course, MIT OCW..."
                                            rows={2}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Submit Button */}
                        <button type="submit" className="btn btn-primary w-full py-4 text-lg shadow-lg" disabled={loading}>
                            {loading ? (
                                <><Wand2 className="animate-spin mr-2" /> Generating Syllabus...</>
                            ) : (
                                <><Wand2 className="mr-2" /> Generate Syllabus with AI</>
                            )}
                        </button>
                    </form>
                </div>

                {/* Result Section */}
                <div className="w-full lg:w-2/5">
                    <div className="sticky top-6">
                        {error && (
                            <div className="alert alert-error mb-4">
                                <strong>Error:</strong> {error}
                            </div>
                        )}

                        {!generatedSyllabus && !error && (
                            <div className="card p-8 text-center bg-slate-50 border-dashed border-2">
                                <FileText size={48} className="mx-auto text-slate-300 mb-4" />
                                <h3 className="text-lg font-bold text-gray-500 mb-2">Ready to Generate</h3>
                                <p className="text-sm text-gray-400">
                                    Fill in the details on the left and click "Generate" to see your AI-crafted syllabus here.
                                </p>
                            </div>
                        )}

                        {generatedSyllabus && (
                            <>
                                <div className="flex justify-end gap-3 mb-4 animate-fade-in">
                                    <button
                                        onClick={handleExportPDF}
                                        className="btn bg-white border border-gray-200 text-gray-700 shadow-sm hover:shadow-md hover:border-red-200 hover:text-red-600 transition-all text-sm flex items-center gap-2 rounded-lg px-4 py-2.5"
                                    >
                                        <Download size={16} />
                                        Export PDF
                                    </button>
                                    <button
                                        onClick={handleExportWord}
                                        className="btn bg-white border border-gray-200 text-gray-700 shadow-sm hover:shadow-md hover:border-blue-200 hover:text-blue-600 transition-all text-sm flex items-center gap-2 rounded-lg px-4 py-2.5"
                                    >
                                        <FileText size={16} />
                                        Export Word
                                    </button>
                                </div>
                                <div className="card p-0 overflow-hidden animate-fade-in shadow-xl border-indigo-100">
                                    <div className="bg-gradient-to-r from-primary to-primary-light p-4 text-white flex justify-between items-center">
                                        <h2 className="font-bold text-lg">Syllabus Preview</h2>
                                        <div className="flex gap-2">
                                            <button onClick={handleExportPDF} className="p-2 bg-white/20 hover:bg-white/30 rounded text-white transition-colors" title="Export PDF">
                                                <Download size={18} />
                                            </button>
                                            <button onClick={handleExportWord} className="p-2 bg-white/20 hover:bg-white/30 rounded text-white transition-colors" title="Export Word">
                                                <FileEdit size={18} />
                                            </button>
                                        </div>
                                    </div>

                                    <div className="p-6 max-h-[80vh] overflow-y-auto custom-scrollbar">
                                        {/* Header Info */}
                                        <div className="mb-6 pb-6 border-b border-gray-100">
                                            <h3 className="text-xl font-bold text-primary mb-2 line-clamp-2">{generatedSyllabus.course_title}</h3>
                                            <div className="flex flex-wrap gap-2 text-xs font-semibold text-subtle uppercase tracking-wider">
                                                <span className="bg-slate-100 px-2 py-1 rounded">{generatedSyllabus.course_code}</span>
                                                <span className="bg-slate-100 px-2 py-1 rounded">{generatedSyllabus.credits} Credits</span>
                                                <span className="bg-indigo-50 text-indigo-700 px-2 py-1 rounded">{generatedSyllabus.course_level}</span>
                                            </div>
                                        </div>

                                        {/* Description */}
                                        {generatedSyllabus.overview && (
                                            <div className="mb-6">
                                                <h4 className="text-sm font-bold text-gray-900 uppercase mb-2">Course Description</h4>
                                                <p className="text-sm text-gray-600 leading-relaxed">{generatedSyllabus.overview}</p>
                                            </div>
                                        )}

                                        {/* Outcomes */}
                                        {generatedSyllabus.learning_outcomes && (
                                            <div className="mb-6">
                                                <h4 className="text-sm font-bold text-gray-900 uppercase mb-2">Course Outcomes</h4>
                                                <div className="space-y-2">
                                                    {generatedSyllabus.learning_outcomes.map((co, idx) => (
                                                        <div key={idx} className="text-sm border-l-2 border-indigo-200 pl-3 py-1">
                                                            <span className="font-bold text-indigo-700 mr-2">{co.code}:</span>
                                                            <span className="text-gray-700">{co.description}</span>
                                                            <span className="ml-2 text-xs bg-gray-100 px-1 rounded text-gray-500">({co.bloom_level})</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Units Content */}
                                        {generatedSyllabus.units && (
                                            <div className="mb-6">
                                                <h4 className="text-sm font-bold text-gray-900 uppercase mb-3">Course Content</h4>
                                                <div className="space-y-4">
                                                    {generatedSyllabus.units.map((unit, idx) => {
                                                        // Helper to parse topic strings if needed (same logic as before)
                                                        let topicsArray = unit.topics || [];
                                                        if (typeof topicsArray === 'string') {
                                                            try {
                                                                topicsArray = JSON.parse(topicsArray.replace(/'/g, '"'));
                                                            } catch (e) {
                                                                topicsArray = [{ topic: topicsArray }];
                                                            }
                                                        }

                                                        return (
                                                            <div key={idx} className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                                                                <div className="flex justify-between items-start mb-2">
                                                                    <h5 className="font-bold text-sm text-primary">Unit {unit.unit_number}: {unit.title}</h5>
                                                                    <span className="text-xs bg-white px-2 py-0.5 rounded border border-gray-200 whitespace-nowrap">{unit.hours} Hrs</span>
                                                                </div>
                                                                <ul className="list-disc list-inside text-xs text-gray-600 space-y-1 ml-1">
                                                                    {Array.isArray(topicsArray) && topicsArray.slice(0, 4).map((t, i) => (
                                                                        <li key={i} className="line-clamp-1">{typeof t === 'string' ? t : (t.topic || 'Topic')}</li>
                                                                    ))}
                                                                    {Array.isArray(topicsArray) && topicsArray.length > 4 && (
                                                                        <li className="italic text-gray-400">and {topicsArray.length - 4} more...</li>
                                                                    )}
                                                                </ul>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )}

                                        {/* References */}
                                        {generatedSyllabus.references?.textbooks && (
                                            <div className="mb-6">
                                                <h4 className="text-sm font-bold text-gray-900 uppercase mb-2">Textbooks</h4>
                                                <ul className="text-xs text-gray-600 list-decimal list-inside space-y-1">
                                                    {generatedSyllabus.references.textbooks.slice(0, 3).map((book, i) => (
                                                        <li key={i}>{book}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default GeneratePage;
