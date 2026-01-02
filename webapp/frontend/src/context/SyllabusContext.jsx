import React, { createContext, useState, useContext } from 'react';

const SyllabusContext = createContext();

export const useSyllabus = () => useContext(SyllabusContext);

export const SyllabusProvider = ({ children }) => {
    // Shared State
    const [generatedSyllabus, setGeneratedSyllabus] = useState(null);
    const [optimizationResults, setOptimizationResults] = useState(null);
    const [analysisResults, setAnalysisResults] = useState(null);

    // File uploads persistence
    const [analyzeFile, setAnalyzeFile] = useState(null);
    const [optimizeFile, setOptimizeFile] = useState(null);

    const value = {
        generatedSyllabus,
        setGeneratedSyllabus,
        optimizationResults,
        setOptimizationResults,
        analysisResults,
        setAnalysisResults,
        analyzeFile,
        setAnalyzeFile,
        optimizeFile,
        setOptimizeFile
    };

    return (
        <SyllabusContext.Provider value={value}>
            {children}
        </SyllabusContext.Provider>
    );
};
