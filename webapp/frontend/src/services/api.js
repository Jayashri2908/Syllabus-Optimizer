import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// API Service Functions
export const apiService = {
    // Upload and parse syllabus
    uploadSyllabus: async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post('/api/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // Analyze syllabus
    analyzeSyllabus: async (syllabusData) => {
        const response = await api.post('/api/analyze', syllabusData);
        return response.data;
    },

    // Get optimization suggestions
    optimizeSyllabus: async (syllabusData, goals = []) => {
        const response = await api.post('/api/optimize', {
            syllabus_data: syllabusData,
            optimization_goals: goals,
        });
        return response.data;
    },

    // Generate new syllabus
    generateSyllabus: async (params) => {
        const response = await api.post('/api/generate', params);
        return response.data;
    },

    // Perform CO-PO mapping
    mapOutcomes: async (courseOutcomes, programOutcomes = null, domain = 'engineering') => {
        const response = await api.post('/api/map-outcomes', {
            course_outcomes: courseOutcomes,
            program_outcomes: programOutcomes,
            domain,
        });
        return response.data;
    },

    // Export to PDF
    exportPDF: async (syllabusData) => {
        const response = await api.post('/api/export/pdf', syllabusData, {
            responseType: 'blob',
        });

        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${syllabusData.course_code || 'syllabus'}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();

        return true;
    },

    // Extract outcomes from text
    extractOutcomes: async (text) => {
        const response = await api.post('/api/extract-outcomes', { text });
        return response.data;
    },

    // Validate outcome
    validateOutcome: async (outcome) => {
        const response = await api.post('/api/validate-outcome', { outcome });
        return response.data;
    },

    // Health check
    healthCheck: async () => {
        const response = await api.get('/api/health');
        return response.data;
    },
};

export default api;
