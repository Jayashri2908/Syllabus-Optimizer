import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { SyllabusData, AnalysisResult, COPOMapping } from '../types';

interface SyllabusContextType {
  currentSyllabus: SyllabusData | null;
  setCurrentSyllabus: React.Dispatch<React.SetStateAction<SyllabusData | null>>;
  analysisResult: AnalysisResult | null;
  setAnalysisResult: React.Dispatch<React.SetStateAction<AnalysisResult | null>>;
  optimizedSyllabus: SyllabusData | null;
  setOptimizedSyllabus: React.Dispatch<React.SetStateAction<SyllabusData | null>>;
  coPoMapping: COPOMapping | null;
  setCoPoMapping: React.Dispatch<React.SetStateAction<COPOMapping | null>>;
}

const SyllabusContext = createContext<SyllabusContextType | undefined>(undefined);

export const useSyllabus = (): SyllabusContextType => {
  const context = useContext(SyllabusContext);
  if (!context) {
    throw new Error('useSyllabus must be used within a SyllabusProvider');
  }
  return context;
};

const getSavedState = <T,>(key: string, defaultValue: T): T => {
  try {
    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : defaultValue;
  } catch (e) {
    return defaultValue;
  }
};

export const SyllabusProvider = ({ children }: { children: ReactNode }) => {
  const [currentSyllabus, setCurrentSyllabus] = useState<SyllabusData | null>(() => getSavedState<SyllabusData | null>('scdo_currentSyllabus', null));
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(() => getSavedState<AnalysisResult | null>('scdo_analysisResult', null));
  const [optimizedSyllabus, setOptimizedSyllabus] = useState<SyllabusData | null>(() => getSavedState<SyllabusData | null>('scdo_optimizedSyllabus', null));
  const [coPoMapping, setCoPoMapping] = useState<COPOMapping | null>(() => getSavedState<COPOMapping | null>('scdo_coPoMapping', null));

  useEffect(() => {
    if (currentSyllabus) localStorage.setItem('scdo_currentSyllabus', JSON.stringify(currentSyllabus));
    else localStorage.removeItem('scdo_currentSyllabus');
  }, [currentSyllabus]);

  useEffect(() => {
    if (analysisResult) localStorage.setItem('scdo_analysisResult', JSON.stringify(analysisResult));
    else localStorage.removeItem('scdo_analysisResult');
  }, [analysisResult]);

  useEffect(() => {
    if (optimizedSyllabus) localStorage.setItem('scdo_optimizedSyllabus', JSON.stringify(optimizedSyllabus));
    else localStorage.removeItem('scdo_optimizedSyllabus');
  }, [optimizedSyllabus]);

  useEffect(() => {
    if (coPoMapping) localStorage.setItem('scdo_coPoMapping', JSON.stringify(coPoMapping));
    else localStorage.removeItem('scdo_coPoMapping');
  }, [coPoMapping]);

  const value = {
    currentSyllabus,
    setCurrentSyllabus,
    analysisResult,
    setAnalysisResult,
    optimizedSyllabus,
    setOptimizedSyllabus,
    coPoMapping,
    setCoPoMapping
  };

  return (
    <SyllabusContext.Provider value={value}>
      {children}
    </SyllabusContext.Provider>
  );
};
