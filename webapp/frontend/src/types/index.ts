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

export interface BloomCoverage {
  level_counts: Record<string, number>;
  percentages: Record<string, number>;
  gaps: Array<{ level: string; current: number; recommended: string; issue: string; count?: number }>;
  total_outcomes: number;
}

export interface COPOMappingGaps {
  total_cos: number;
  mapped_cos: number;
  gaps: Array<{ type: string; co: string; description: string }>;
  coverage_percentage: number;
}

export interface AssessmentGaps {
  total_percentage: number;
  components: Record<string, number>;
  gaps: Array<{ type: string; description: string; component?: string; current_total?: number; expected_total?: number; current?: number }>;
  internal_total?: number;
  external_total?: number;
}

export interface ContentGaps {
  gaps: Array<{ type: string; component?: string; description: string; current_count?: number; recommended_min?: number; overlap?: number }>;
  total_units: number;
  total_hours: number;
  reference_count: number;
  total_topics?: number;
}

export interface StructuralIssues {
  type: string;
  severity: string;
  description: string;
}

export interface Recommendation {
  text: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
  related_to?: string;
}

export interface ContentQuality {
  depth_score: number;
  breadth_score: number;
  alignment_score: number;
  overall_score: number;
  issues: Array<{ type: string; severity: string; unit: string; description: string }>;
}

export interface LessonPlanAnalysis {
  status?: string;
  message?: string;
  units_without_hours: string[];
  units_without_methods: string[];
  gaps: Array<{ type: string; severity: string; description: string }>;
  lesson_distribution: {
    lessons_per_unit: Record<string, number>;
    total_lessons: number;
    average_per_unit: number;
  };
  total_units: number;
}

export interface RedundancyAnalysis {
  redundant_pairs: Array<{ unit_1: string; unit_2: string; similarity: number; severity: string; description: string }>;
  duplicate_outcomes: Array<{ outcome_1: string; outcome_2: string; similarity: number }>;
  overlap_score: number;
  unit_pairs_checked: number;
  total_redundancies: number;
}

export interface ComplianceResult {
  [key: string]: unknown;
}

export interface OutcomeValidation {
  outcomes: Array<{
    code: string;
    description: string;
    is_valid: boolean;
    measurability_score: number;
    bloom_level: string;
    issues: string[];
    suggestions: string[];
  }>;
  total_outcomes: number;
  valid_outcomes: number;
  issues_count: number;
  average_measurability: number;
}

export interface AnalysisResult {
  bloom_coverage: BloomCoverage;
  co_po_mapping_gaps: COPOMappingGaps;
  assessment_gaps: AssessmentGaps;
  content_gaps: ContentGaps;
  structural_issues: StructuralIssues[];
  lesson_plan_analysis: LessonPlanAnalysis;
  redundancies: RedundancyAnalysis;
  content_quality: ContentQuality;
  nep_2020_compliance: ComplianceResult;
  accreditation_compliance: { nba: ComplianceResult; naac: ComplianceResult };
  outcome_validation: OutcomeValidation;
  recommendations: Recommendation[];
  overall_quality_score: number;
  ai_analysis?: string;
  cached: boolean;
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

export interface UploadAndAnalyzeResponse {
  success: boolean;
  filename: string;
  data: SyllabusData;
  analysis: AnalysisResult;
  cached: boolean;
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
  chromadb?: string;
  chromadb_documents?: number;
  llm?: string;
}

// ---------------------------------------------------------------------------
// Component Prop Types
// ---------------------------------------------------------------------------

export interface FileUploaderProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
}
