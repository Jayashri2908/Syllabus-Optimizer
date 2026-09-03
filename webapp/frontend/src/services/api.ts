import axios, { AxiosError } from 'axios';
import {
  SyllabusData,
  AnalysisResult,
  SystemHealth,
  UploadResponse,
  UploadAndAnalyzeResponse,
  AnalyzeResponse,
  OptimizeResponse,
  GenerateRequest,
  GenerateResponse,
  MapResponse,
} from '../types';
import toast from 'react-hot-toast';

const api = axios.create({
  baseURL: '/api'
});

// ---------------------------------------------------------------------------
// Global response interceptor — unified error handling
// ---------------------------------------------------------------------------
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    if (!error.response) {
      toast.error('Network error — is the backend running?');
      return Promise.reject(error);
    }

    const status = error.response.status;
    const detail = error.response.data?.detail;

    switch (status) {
      case 401:
        toast.error('Unauthorized — check your API key.');
        break;
      case 413:
        toast.error(detail || 'File too large.');
        break;
      case 429:
        toast.error('Rate limited — please wait a moment and try again.');
        break;
      case 503:
        toast.error(detail || 'Service unavailable — AI model may not be configured.');
        break;
      // 500s are handled per-call via catch blocks for custom messages
    }

    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

export const uploadSyllabus = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const uploadAndAnalyze = async (file: File): Promise<UploadAndAnalyzeResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post<UploadAndAnalyzeResponse>('/upload-and-analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const analyzeSyllabus = async (syllabusData: SyllabusData): Promise<AnalyzeResponse> => {
  const response = await api.post<AnalyzeResponse>('/analyze', syllabusData);
  return response.data;
};

export const optimizeSyllabus = async (
  syllabusData: SyllabusData,
  optimizationGoals: string[] = []
): Promise<OptimizeResponse> => {
  const response = await api.post<OptimizeResponse>('/optimize', {
    syllabus_data: syllabusData,
    optimization_goals: optimizationGoals
  });
  return response.data;
};

export const generateSyllabus = async (requestData: GenerateRequest): Promise<GenerateResponse> => {
  const response = await api.post<GenerateResponse>('/generate', requestData);
  return response.data;
};

export const mapOutcomes = async (requestData: {
  course_outcomes: Array<{ code?: string; description: string }>;
  domain?: string;
}): Promise<MapResponse> => {
  const response = await api.post<MapResponse>('/map-outcomes', requestData);
  return response.data;
};

export const exportPDF = async (
  syllabusData: SyllabusData,
  analysisData: AnalysisResult | null = null
): Promise<Blob> => {
  const response = await api.post('/export/pdf', {
    syllabus_data: syllabusData,
    analysis_data: analysisData
  }, { responseType: 'blob' });
  return response.data as Blob;
};

export const exportExcel = async (syllabusData: SyllabusData): Promise<Blob> => {
  const response = await api.post('/export/excel', {
    syllabus_data: syllabusData
  }, { responseType: 'blob' });
  return response.data as Blob;
};

export const exportWord = async (
  syllabusData: SyllabusData,
  analysisData: AnalysisResult | null = null
): Promise<Blob> => {
  const response = await api.post('/export/word', {
    syllabus_data: syllabusData,
    analysis_data: analysisData
  }, { responseType: 'blob' });
  return response.data as Blob;
};

export const getSystemHealth = async (): Promise<SystemHealth> => {
  const start = performance.now();
  let data: Partial<SystemHealth> = { status: 'offline' };
  try {
    const response = await api.get<SystemHealth>('/health');
    data = response.data;
  } catch {
    // Return offline payload on fail
  }
  const end = performance.now();
  return {
    ...data,
    status: data.status || 'offline',
    latency: Math.round(end - start)
  };
};

export default api;
