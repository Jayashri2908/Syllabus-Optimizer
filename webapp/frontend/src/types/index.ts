// =============================================================================
// SCDO — Shared TypeScript interfaces
// Matches FastAPI backend response shapes exactly
// =============================================================================

// ---------------------------------------------------------------------------
// Primitives & Building Blocks
// ---------------------------------------------------------------------------

export interface LearningOutcome {
  code: string;
  description: string;
  bloom_level: string;
}

export interface Unit {
  unit_number: number | string;
  title: string;
  topics: string[];
  hours?: number;
}

export interface BloomAnalysis {
  distribution: Record<string, number>;
  missing_levels: string[];
  recommendations: string[];
}

export interface References {
  textbooks?: string[];
  references?: string[];
  online_resources?: string[];
}

// ---------------------------------------------------------------------------
// Core Domain Models
// ---------------------------------------------------------------------------

export interface SyllabusData {
  course_title: string;
  course_code: string;
  credits: string;
  university_name?: string;
  faculty_name?: string;
  department?: string;
  program?: string;
  year?: string;
  semester?: string;
  course_type?: string;
  course_level?: string;
  domain?: string;
  overview?: string;
  units: Unit[];
  learning_outcomes: LearningOutcome[];
  references?: References | string[];
  program_outcomes?: string[];
  raw_text?: string;
  co_po_mapping?: COPOMappingData;
  bloom_analysis?: BloomAnalysis;
  [key: string]: unknown;  // allow extra backend fields without losing safety
}

export interface AnalysisResult {
  bloom_analysis?: BloomAnalysis;
  ai_analysis?: string;
  structural_analysis?: Record<string, unknown>;
  sequence_optimization?: Record<string, unknown> | string;
  [key: string]: unknown;
}

// ---------------------------------------------------------------------------
// CO-PO Mapping
// ---------------------------------------------------------------------------

export interface COPOMatrixEntry {
  co_id: string;
  description: string;
  po_scores: number[];
}

export interface COPOMappingData {
  matrix: COPOMatrixEntry[];
}

export interface COPOValidation {
  unmapped_cos: string[];
  po_coverage: number;
}

export interface COPOMapping {
  mapping: COPOMappingData;
  matrix?: string;
  validation: COPOValidation;
}

// ---------------------------------------------------------------------------
// API Request / Response shapes
// ---------------------------------------------------------------------------

export interface GenerateRequest {
  course_title: string;
  course_code: string;
  credits: string;
  university_name?: string;
  faculty_name?: string;
  department?: string;
  course_type?: string;
  semester?: string;
  program?: string;
  year?: string;
  course_level?: string;
  program_outcomes: string[];
  keywords: string[];
  unit_topics?: Array<Record<string, unknown>>;
  textbooks?: string[];
  references?: string[];
  online_resources?: string[];
  domain?: string;
  num_units?: number;
  num_outcomes?: number;
}

export interface UploadResponse {
  success: boolean;
  filename: string;
  data: SyllabusData;
}

export interface AnalyzeResponse {
  success: boolean;
  analysis: AnalysisResult;
}

export interface OptimizeResponse {
  success: boolean;
  original_syllabus: SyllabusData;
  optimized_syllabus: SyllabusData;
  optimization: {
    changes_summary: string[];
    bloom_distribution: Record<string, number>;
    rationale: string;
    industry_relevance_score: number;
    prerequisite_rationale: string;
    nep_2020_compliance: Record<string, unknown> | null;
    accreditation_compliance: Record<string, unknown> | null;
    co_po_mapping: COPOMappingData | null;
  };
}

export interface GenerateResponse {
  success: boolean;
  syllabus: SyllabusData;
}

export interface MapResponse {
  success: boolean;
  mapping: COPOMappingData;
  matrix: string;
  validation: COPOValidation;
}

export interface SystemHealth {
  status: string;
  service?: string;
  latency?: number;
}

// ---------------------------------------------------------------------------
// Component Prop Types
// ---------------------------------------------------------------------------

export interface FileUploaderProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
}
