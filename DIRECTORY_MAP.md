# Syllabus Optimizer - Comprehensive Directory Map

This document provides a **complete** reference of all project files with their descriptions and key functions.

---

## 📁 Root Directory Files

| File | Description |
|------|-------------|
| [README.md](file:///d:/Syllabus%20Optimizer/README.md) | Project overview and setup instructions |
| [CONTRIBUTING.md](file:///d:/Syllabus%20Optimizer/CONTRIBUTING.md) | Contribution guidelines |
| [requirements.txt](file:///d:/Syllabus%20Optimizer/requirements.txt) | Python dependencies |
| [get_openrouter_list.py](file:///d:/Syllabus%20Optimizer/get_openrouter_list.py) | Script to fetch available OpenRouter models |
| [free_models.json](file:///d:/Syllabus%20Optimizer/free_models.json) | Cached list of free AI models |
| [test_ml.py](file:///d:/Syllabus%20Optimizer/test_ml.py) | Test script for ML.pdf parsing |
| [test_validators.py](file:///d:/Syllabus%20Optimizer/test_validators.py) | Test script for NEP/accreditation validators |
| [test_openrouter_free.py](file:///d:/Syllabus%20Optimizer/test_openrouter_free.py) | Test script for free OpenRouter models |
| [start_app.bat](file:///d:/Syllabus%20Optimizer/start_app.bat) | Windows startup script for backend + frontend |

---

## 🤖 `src/ai/` - AI Model Integration

| File | Description | Key Functions |
|------|-------------|---------------|
| [base_model.py](file:///d:/Syllabus%20Optimizer/src/ai/base_model.py) | Abstract base class for AI models | `BaseAIModel.generate()`, `is_available()`, `get_model_info()` |
| [gemini_model.py](file:///d:/Syllabus%20Optimizer/src/ai/gemini_model.py) | Google Gemini integration (Free Tier) | `GeminiModel.generate()`, `is_available()` |
| [openrouter_model.py](file:///d:/Syllabus%20Optimizer/src/ai/openrouter_model.py) | OpenRouter API for multiple models | `OpenRouterModel.generate()` |
| [model_manager.py](file:///d:/Syllabus%20Optimizer/src/ai/model_manager.py) | Orchestrates model selection and fallbacks | `ModelManager.generate()`, `generate_json()`, `get_status()` |
| [prompt_library.py](file:///d:/Syllabus%20Optimizer/src/ai/prompt_library.py) | Centralized prompt templates for AI tasks | `get_unit_generation_prompt()`, `get_learning_outcome_prompt()` |

---

## 🔍 `src/analysis/` - Content Analysis

| File | Description | Key Functions |
|------|-------------|---------------|
| [syllabus_parser.py](file:///d:/Syllabus%20Optimizer/src/analysis/syllabus_parser.py) | Parses PDF, DOCX, TXT syllabi into structured data | `SyllabusParser.parse_file()`, `_extract_structure()`, `_extract_learning_outcomes()` |
| [content_analyzer.py](file:///d:/Syllabus%20Optimizer/src/analysis/content_analyzer.py) | Evaluates quality, depth, breadth | `ContentAnalyzer.analyze()`, `_assess_depth()`, `_assess_breadth()` |
| [gap_analyzer.py](file:///d:/Syllabus%20Optimizer/src/analysis/gap_analyzer.py) | Identifies gaps in Bloom's coverage, CO-PO mapping | `GapAnalyzer.analyze()`, `_analyze_bloom_coverage()`, `_generate_recommendations()` |
| [lesson_plan_extractor.py](file:///d:/Syllabus%20Optimizer/src/analysis/lesson_plan_extractor.py) | Extracts lesson structures from units | `LessonPlanExtractor.extract_lesson_plans()`, `_estimate_lesson_count()` |
| [outcome_extractor.py](file:///d:/Syllabus%20Optimizer/src/analysis/outcome_extractor.py) | Extracts and validates learning outcomes | `OutcomeExtractor.extract_outcomes()`, `validate_outcome()`, `generate_outcomes()` |
| [rag_analyzer.py](file:///d:/Syllabus%20Optimizer/src/analysis/rag_analyzer.py) | RAG-enhanced gap analysis with cited recommendations | `RAGAwareAnalyzer.analyze()`, `_get_rag_recommendations_parallel()` |
| [redundancy_detector.py](file:///d:/Syllabus%20Optimizer/src/analysis/redundancy_detector.py) | Detects duplicate topics using semantic similarity | `RedundancyDetector.detect_redundancies()`, `_compute_similarity()` |

---

## 📄 `src/export/` - Document Export

| File | Description | Key Functions |
|------|-------------|---------------|
| [pdf_exporter.py](file:///d:/Syllabus%20Optimizer/src/export/pdf_exporter.py) | Generates professional PDF reports (ReportLab) | `PDFExporter.export()`, `_create_analysis_section()`, `_generate_bloom_chart()` |
| [excel_exporter.py](file:///d:/Syllabus%20Optimizer/src/export/excel_exporter.py) | Exports to Excel with CO-PO-PSO mapping sheets | `ExcelExporter.export_complete_syllabus()`, `export_mapping_only()` |
| [latex_exporter.py](file:///d:/Syllabus%20Optimizer/src/export/latex_exporter.py) | LaTeX PDF export with math formula support (PyLaTeX) | `LaTeXExporter.export_pdf()`, `_add_co_po_mapping()` |
| [latex_template.py](file:///d:/Syllabus%20Optimizer/src/export/latex_template.py) | Standard LaTeX template with placeholders | `LaTeXExporter.export()`, `_fill_units()`, `_compile_pdf()` |

---

## 🌱 `src/generation/` - AI Course Generation

| File | Description | Key Functions |
|------|-------------|---------------|
| [syllabus_generator.py](file:///d:/Syllabus%20Optimizer/src/generation/syllabus_generator.py) | Generates complete syllabi from titles/keywords | `SyllabusGenerator.generate()`, `_generate_units()`, `_detect_domain()` |
| [chained_generator.py](file:///d:/Syllabus%20Optimizer/src/generation/chained_generator.py) | Staggered LLM chaining for consistency | `ChainedSyllabusGenerator.generate_staggered()`, `_generate_section()` |
| [section_prompts.py](file:///d:/Syllabus%20Optimizer/src/generation/section_prompts.py) | User prompts for each syllabus section | `SectionPrompts.get_overview_prompt()`, `get_units_prompt()`, `get_outcomes_prompt()` |
| [section_schemas.py](file:///d:/Syllabus%20Optimizer/src/generation/section_schemas.py) | Pydantic schemas for JSON validation | `OverviewSection`, `LearningOutcome`, `Unit`, `UnitsSection` |
| [bloom_distribution.py](file:///d:/Syllabus%20Optimizer/src/generation/bloom_distribution.py) | Bloom's Taxonomy distribution utilities | `get_bloom_distribution()`, `format_distribution_for_prompt()` |
| [rubric_generator.py](file:///d:/Syllabus%20Optimizer/src/generation/rubric_generator.py) | Generates assessment rubrics | `RubricGenerator.generate_rubrics()`, `generate_summary_table()` |
| [domain_templates.py](file:///d:/Syllabus%20Optimizer/src/generation/domain_templates.py) | Domain-specific context (ML, Web Dev, etc.) | `detect_domain()`, `get_domain_context()`, `get_domain_tools()` |
| [industry_data.py](file:///d:/Syllabus%20Optimizer/src/generation/industry_data.py) | Industry skills and job market data | `get_industry_skills()`, `get_industry_certifications()`, `format_industry_context()` |
| [instructional_strategy.py](file:///d:/Syllabus%20Optimizer/src/generation/instructional_strategy.py) | Recommends pedagogy and assessments | `InstructionalStrategyRecommender.recommend_strategies()` |
| [iterative_refiner.py](file:///d:/Syllabus%20Optimizer/src/generation/iterative_refiner.py) | Multi-pass critique and refinement | `IterativeRefiner.refine_learning_outcomes()`, `validate_and_refine_units()` |

---

## ⚙️ `src/optimization/` - Curriculum Enhancement

| File | Description | Key Functions |
|------|-------------|---------------|
| [content_optimizer.py](file:///d:/Syllabus%20Optimizer/src/optimization/content_optimizer.py) | AI-driven content optimization | `ContentOptimizer.optimize_full_syllabus()` |
| [bloom_mapper.py](file:///d:/Syllabus%20Optimizer/src/optimization/bloom_mapper.py) | Maps outcomes to Bloom's levels | `BloomMapper.map_outcome()`, `analyze_distribution()`, `suggest_activities()` |
| [objectives_optimizer.py](file:///d:/Syllabus%20Optimizer/src/optimization/objectives_optimizer.py) | Optimizes objectives using SMART criteria | `ObjectivesOptimizer.optimize_objectives()` |
| [reference_suggester.py](file:///d:/Syllabus%20Optimizer/src/optimization/reference_suggester.py) | Suggests textbooks and resources | `ReferenceSuggester.suggest_references()` |

---

## 🗺️ `src/mapping/` - Accreditation Mapping

| File | Description | Key Functions |
|------|-------------|---------------|
| [co_po_mapper.py](file:///d:/Syllabus%20Optimizer/src/mapping/co_po_mapper.py) | CO-PO-PSO correlation matrix | `COPOMapper.map_co_to_po()`, `generate_mapping_matrix()`, `validate_mapping()` |

---

## 📚 `src/rag/` - Knowledge Management (RAG)

| File | Description | Key Functions |
|------|-------------|---------------|
| [vector_store.py](file:///d:/Syllabus%20Optimizer/src/rag/vector_store.py) | ChromaDB vector store for embeddings | `VectorStore.add_documents()`, `query()` |
| [ingestion.py](file:///d:/Syllabus%20Optimizer/src/rag/ingestion.py) | Document ingestion into vector store | `DocumentIngestion.ingest_all()` |
| [retriever.py](file:///d:/Syllabus%20Optimizer/src/rag/retriever.py) | RAG query engine for context retrieval | `RAGEngine.query()`, `get_context()` |

---

## 🏢 `src/ibm/` - Local Storage

| File | Description | Key Functions |
|------|-------------|---------------|
| [local_storage.py](file:///d:/Syllabus%20Optimizer/src/ibm/local_storage.py) | Local filesystem storage (free alternative) | `LocalStorage.save_upload()`, `upload_file()`, `download_file()` |

---

## 🛠️ `src/utils/` - Utilities

| File | Description | Key Functions |
|------|-------------|---------------|
| [logging_utils.py](file:///d:/Syllabus%20Optimizer/src/utils/logging_utils.py) | Centralized logging setup | `setup_logger()` |
| [text_processing.py](file:///d:/Syllabus%20Optimizer/src/utils/text_processing.py) | Text processing and NLP utilities | `TextProcessor.extract_learning_outcomes()`, `classify_bloom_level()`, `extract_keywords()` |
| [mock_services.py](file:///d:/Syllabus%20Optimizer/src/utils/mock_services.py) | Mock services for testing | `MockContentOptimizer`, `MockBloomMapper`, `MockGapAnalyzer` |
| [exceptions.py](file:///d:/Syllabus%20Optimizer/src/utils/exceptions.py) | Custom exception classes | `SCDOException`, `ValidationException`, `AIUnavailableException` |
| [retry.py](file:///d:/Syllabus%20Optimizer/src/utils/retry.py) | Retry and circuit breaker utilities | `retry_with_backoff()`, `CircuitBreaker` |

---

## 🖥️ `webapp/backend/` - FastAPI Server

| File | Description | Key Endpoints |
|------|-------------|---------------|
| [main.py](file:///d:/Syllabus%20Optimizer/webapp/backend/main.py) | Main FastAPI application with all endpoints | `/api/upload`, `/api/analyze`, `/api/optimize`, `/api/generate`, `/api/map-outcomes`, `/api/export/*` |
| [app/main.py](file:///d:/Syllabus%20Optimizer/webapp/backend/app/main.py) | App factory with lifespan management | `lifespan()`, `app` |
| [app/dependencies.py](file:///d:/Syllabus%20Optimizer/webapp/backend/app/dependencies.py) | Dependency injection, auth, rate limiting | `verify_api_key()`, `rate_limit()`, `get_components()` |
| [app/schemas.py](file:///d:/Syllabus%20Optimizer/webapp/backend/app/schemas.py) | Pydantic request/response models | `GenerateRequest`, `OptimizeRequest`, `MapRequest` |
| [app/routers/](file:///d:/Syllabus%20Optimizer/webapp/backend/app/routers/) | API route handlers | `upload.py`, `analyze.py`, `generate.py`, `mapping.py`, `export.py`, `system.py`, `utils.py` |

---

## 🎨 `webapp/frontend/src/` - React UI

### Pages

| File | Description | Key Components |
|------|-------------|----------------|
| [App.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/App.tsx) | Root app with routing and navigation | `App`, Navbar |
| [LandingPage.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/pages/LandingPage.tsx) | Landing page with hero section | `LandingPage`, Feature cards |
| [AnalyzePage.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/pages/AnalyzePage.tsx) | Syllabus upload and analysis interface | `handleUpload()`, `handleExportPDF()` |
| [OptimizePage.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/pages/OptimizePage.tsx) | Side-by-side optimization comparison | `handleFileUpload()`, `handleExport()` |
| [GeneratePage.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/pages/GeneratePage.tsx) | Course generation wizard | `handleSubmit()`, `handleExportPDF()` |
| [MapOutcomesPage.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/pages/MapOutcomesPage.tsx) | CO-PO mapping interface | `handleMapOutcomes()` |
| [SpecsPage.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/pages/SpecsPage.tsx) | API documentation page | `SpecsPage` |

### Components

| File | Description |
|------|-------------|
| [COPOHeatmap.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/COPOHeatmap.tsx) | CO-PO mapping heatmap visualization |
| [ErrorBoundary.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/ErrorBoundary.tsx) | Error boundary for graceful failure |
| [FileUploader.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/FileUploader.tsx) | Drag-and-drop file upload component |
| [FlowDiagram.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/FlowDiagram.tsx) | Flow diagram visualization |
| [MarqueeTicker.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/MarqueeTicker.tsx) | Animated marquee ticker |
| [Navbar.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/Navbar.tsx) | Navigation bar |
| [SkeletonLoader.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/SkeletonLoader.tsx) | Skeleton loading placeholder |
| [ThreeBloomChart.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/ThreeBloomChart.tsx) | 3D Bloom's taxonomy chart |
| [ThreeForceGraph.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/components/ThreeForceGraph.tsx) | 3D force graph visualization |

### Context & Services

| File | Description | Key Functions |
|------|-------------|---------------|
| [SyllabusContext.tsx](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/context/SyllabusContext.tsx) | React Context for shared state | `useSyllabus()`, `SyllabusProvider` |
| [api.ts](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/services/api.ts) | Axios API client | `uploadSyllabus()`, `analyzeSyllabus()`, `optimizeSyllabus()`, `generateSyllabus()` |

### Styles

| File | Description |
|------|-------------|
| [index.css](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/index.css) | Global styles and CSS variables |
| [animations.css](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/animations.css) | Animation keyframes and transitions |
| [App.css](file:///d:/Syllabus%20Optimizer/webapp/frontend/src/App.css) | App-specific styles |

---

## ⚙️ `configs/` - Configuration Files

| File | Description |
|------|-------------|
| [accreditation.yaml](file:///d:/Syllabus%20Optimizer/configs/accreditation.yaml) | PO/PSO definitions for NBA/NAAC domains |
| [bloom_taxonomy.yaml](file:///d:/Syllabus%20Optimizer/configs/bloom_taxonomy.yaml) | Bloom's Taxonomy verbs and levels |
| [nep_2020.yaml](file:///d:/Syllabus%20Optimizer/configs/nep_2020.yaml) | NEP 2020 curriculum guidelines |
| [ai_models.yaml](file:///d:/Syllabus%20Optimizer/configs/ai_models.yaml) | AI model configurations |
| [verified_references.yaml](file:///d:/Syllabus%20Optimizer/configs/verified_references.yaml) | Verified reference books |

---

## 📖 `docs/` - Documentation

| File | Description |
|------|-------------|
| [SETUP.md](file:///d:/Syllabus%20Optimizer/docs/SETUP.md) | Detailed setup instructions |
| [architecture.md](file:///d:/Syllabus%20Optimizer/docs/architecture.md) | System architecture documentation |
| [Research_Paper.md](file:///d:/Syllabus%20Optimizer/docs/Research_Paper.md) | Research paper |
| [Viva_QA.md](file:///d:/Syllabus%20Optimizer/docs/Viva_QA.md) | Viva Q&A preparation |
| [Presentation_Script.md](file:///d:/Syllabus%20Optimizer/docs/Presentation_Script.md) | Presentation script |

---

## 📊 Summary Statistics

| Category | Count |
|----------|-------|
| **Python Files (src/)** | 50+ |
| **React/TS Files (webapp/)** | 20+ |
| **Configuration Files** | 5 |
| **Documentation Files** | 6 |
| **Total Lines of Code** | ~15,000+ |

---

> **Note:** All file links are clickable and will open directly in your editor.
