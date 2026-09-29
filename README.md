# SCDO — Syllabus & Curriculum Design Optimizer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104+-green.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-18+-61DAFB.svg" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-5+-3178C6.svg" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/AI-OpenRouter%20%2B%20Gemini-purple.svg" alt="AI"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
</p>

<p align="center">
  <strong>AI-powered syllabus analysis, optimization, and generation</strong><br/>
  Using OpenRouter (Nvidia Nemotron) and Google Gemini — both free.
</p>

---

## ✨ Features

<p align="center">
<svg width="720" height="120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#6366f1"/>
      <stop offset="100%" style="stop-color:#8b5cf6"/>
    </linearGradient>
  </defs>
  <rect x="10" y="10" width="100" height="100" rx="12" fill="url(#g1)" opacity="0.15"/>
  <text x="60" y="55" text-anchor="middle" font-size="24">📄</text>
  <text x="60" y="80" text-anchor="middle" font-size="11" fill="#6366f1" font-weight="bold">Analyze</text>
  <rect x="130" y="10" width="100" height="100" rx="12" fill="url(#g1)" opacity="0.15"/>
  <text x="180" y="55" text-anchor="middle" font-size="24">🔍</text>
  <text x="180" y="80" text-anchor="middle" font-size="11" fill="#6366f1" font-weight="bold">Gap Analysis</text>
  <rect x="250" y="10" width="100" height="100" rx="12" fill="url(#g1)" opacity="0.15"/>
  <text x="300" y="55" text-anchor="middle" font-size="24">✨</text>
  <text x="300" y="80" text-anchor="middle" font-size="11" fill="#6366f1" font-weight="bold">Optimize</text>
  <rect x="370" y="10" width="100" height="100" rx="12" fill="url(#g1)" opacity="0.15"/>
  <text x="420" y="55" text-anchor="middle" font-size="24">🤖</text>
  <text x="420" y="80" text-anchor="middle" font-size="11" fill="#6366f1" font-weight="bold">Generate</text>
  <rect x="490" y="10" width="100" height="100" rx="12" fill="url(#g1)" opacity="0.15"/>
  <text x="540" y="55" text-anchor="middle" font-size="24">🗺️</text>
  <text x="540" y="80" text-anchor="middle" font-size="11" fill="#6366f1" font-weight="bold">CO-PO Map</text>
  <rect x="610" y="10" width="100" height="100" rx="12" fill="url(#g1)" opacity="0.15"/>
  <text x="660" y="55" text-anchor="middle" font-size="24">📦</text>
  <text x="660" y="80" text-anchor="middle" font-size="11" fill="#6366f1" font-weight="bold">Export</text>
</svg>
</p>

| Feature | Description |
|---------|-------------|
| 📄 **Syllabus Analysis** | Parse PDF/DOCX/TXT syllabi into structured data |
| 🔍 **Gap Analysis** | Bloom's taxonomy, CO-PO mapping, assessment gaps |
| ✨ **Content Optimization** | AI-powered suggestions for improvement |
| 🤖 **Syllabus Generation** | Complete syllabi from minimal inputs |
| 🗺️ **CO-PO Mapping** | LLM semantic mapping with rule-based fallback |
| 📦 **Multi-format Export** | PDF, Excel, LaTeX, Word, JSON |

---

## 🏗️ Architecture

<p align="center">
<svg width="700" height="340" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="layer" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#6366f1;stop-opacity:0.1"/>
      <stop offset="100%" style="stop-color:#6366f1;stop-opacity:0.05"/>
    </linearGradient>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#6366f1"/>
    </marker>
  </defs>

  <!-- Frontend -->
  <rect x="50" y="10" width="600" height="60" rx="8" fill="url(#layer)" stroke="#6366f1" stroke-width="1.5"/>
  <text x="350" y="35" text-anchor="middle" font-size="13" fill="#6366f1" font-weight="bold">Frontend — React + TypeScript + Vite</text>
  <text x="350" y="55" text-anchor="middle" font-size="11" fill="#64748b">AnalyzePage · OptimizePage · GeneratePage · MapOutcomesPage</text>

  <!-- Arrow -->
  <line x1="350" y1="70" x2="350" y2="95" stroke="#6366f1" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- API Layer -->
  <rect x="50" y="100" width="600" height="60" rx="8" fill="url(#layer)" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="350" y="125" text-anchor="middle" font-size="13" fill="#8b5cf6" font-weight="bold">API Layer — FastAPI</text>
  <text x="350" y="145" text-anchor="middle" font-size="11" fill="#64748b">Upload · Analyze · Optimize · Generate · Map · Export · Health · Metrics</text>

  <!-- Arrow -->
  <line x1="350" y1="160" x2="350" y2="185" stroke="#8b5cf6" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Business Logic -->
  <rect x="50" y="190" width="600" height="60" rx="8" fill="url(#layer)" stroke="#0ea5e9" stroke-width="1.5"/>
  <text x="350" y="215" text-anchor="middle" font-size="13" fill="#0ea5e9" font-weight="bold">Business Logic</text>
  <text x="350" y="235" text-anchor="middle" font-size="11" fill="#64748b">Analysis · Optimization · Generation · Mapping · Validation</text>

  <!-- Arrow -->
  <line x1="350" y1="250" x2="350" y2="275" stroke="#0ea5e9" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Integration -->
  <rect x="50" y="280" width="600" height="60" rx="8" fill="url(#layer)" stroke="#10b981" stroke-width="1.5"/>
  <text x="350" y="305" text-anchor="middle" font-size="13" fill="#10b981" font-weight="bold">Integration Layer</text>
  <text x="350" y="325" text-anchor="middle" font-size="11" fill="#64748b">OpenRouter (Primary) · Gemini (Fallback) · ChromaDB (RAG) · PostgreSQL · Redis</text>
</svg>
</p>

---

## 🔄 Workflow

<p align="center">
<svg width="700" height="160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/>
    </marker>
  </defs>

  <rect x="20" y="40" width="100" height="80" rx="10" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="70" y="75" text-anchor="middle" font-size="20">📄</text>
  <text x="70" y="100" text-anchor="middle" font-size="11" fill="#475569" font-weight="bold">Upload</text>

  <line x1="120" y1="80" x2="155" y2="80" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arr2)"/>

  <rect x="160" y="40" width="100" height="80" rx="10" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="210" y="75" text-anchor="middle" font-size="20">🔍</text>
  <text x="210" y="100" text-anchor="middle" font-size="11" fill="#475569" font-weight="bold">Analyze</text>

  <line x1="260" y1="80" x2="295" y2="80" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arr2)"/>

  <rect x="300" y="40" width="100" height="80" rx="10" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="350" y="75" text-anchor="middle" font-size="20">✨</text>
  <text x="350" y="100" text-anchor="middle" font-size="11" fill="#475569" font-weight="bold">Optimize</text>

  <line x1="400" y1="80" x2="435" y2="80" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arr2)"/>

  <rect x="440" y="40" width="100" height="80" rx="10" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="490" y="75" text-anchor="middle" font-size="20">🗺️</text>
  <text x="490" y="100" text-anchor="middle" font-size="11" fill="#475569" font-weight="bold">Map CO-PO</text>

  <line x1="540" y1="80" x2="575" y2="80" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arr2)"/>

  <rect x="580" y="40" width="100" height="80" rx="10" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="630" y="75" text-anchor="middle" font-size="20">📦</text>
  <text x="630" y="100" text-anchor="middle" font-size="11" fill="#475569" font-weight="bold">Export</text>
</svg>
</p>

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Jayashri2908/Syllabus-Optimizer.git
cd Syllabus-Optimizer
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | Primary AI — [openrouter.ai](https://openrouter.ai) |
| `GEMINI_API_KEY` | ❌ | Fallback AI — [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `API_KEY` | Prod only | API authentication key |
| `ENV` | ❌ | `development` / `staging` / `production` |

### 3. Run

```bash
# Backend
cd webapp/backend && python main.py

# Frontend (new terminal)
cd webapp/frontend && npm install && npm run dev
```

<p align="center">
<svg width="400" height="50" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="170" height="30" rx="6" fill="#6366f1"/>
  <text x="95" y="30" text-anchor="middle" font-size="12" fill="white">API: localhost:8000</text>
  <rect x="200" y="10" width="170" height="30" rx="6" fill="#8b5cf6"/>
  <text x="285" y="30" text-anchor="middle" font-size="12" fill="white">Docs: localhost:8000/docs</text>
</svg>
</p>

---

## 📡 API Endpoints

<p align="center">
<svg width="600" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="580" height="180" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
  <text x="300" y="35" text-anchor="middle" font-size="13" fill="#475569" font-weight="bold">REST API — 12 Endpoints</text>

  <rect x="30" y="50" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="40" y="69" font-size="11" fill="#166534" font-family="monospace">POST /api/upload</text>
  <rect x="210" y="50" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="220" y="69" font-size="11" fill="#166534" font-family="monospace">POST /api/analyze</text>
  <rect x="390" y="50" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="400" y="69" font-size="11" fill="#166534" font-family="monospace">POST /api/optimize</text>

  <rect x="30" y="85" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="40" y="104" font-size="11" fill="#166534" font-family="monospace">POST /api/generate</text>
  <rect x="210" y="85" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="220" y="104" font-size="11" fill="#166534" font-family="monospace">POST /api/map-outcomes</text>
  <rect x="390" y="85" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="400" y="104" font-size="11" fill="#166534" font-family="monospace">POST /api/export/pdf</text>

  <rect x="30" y="120" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="40" y="139" font-size="11" fill="#166534" font-family="monospace">POST /api/export/excel</text>
  <rect x="210" y="120" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="220" y="139" font-size="11" fill="#166534" font-family="monospace">POST /api/export/word</text>
  <rect x="390" y="120" width="170" height="28" rx="4" fill="#dcfce7"/>
  <text x="400" y="139" font-size="11" fill="#166534" font-family="monospace">POST /api/export/latex</text>

  <rect x="30" y="155" width="170" height="28" rx="4" fill="#dbeafe"/>
  <text x="40" y="174" font-size="11" fill="#1e40af" font-family="monospace">GET /api/health</text>
  <rect x="210" y="155" width="170" height="28" rx="4" fill="#dbeafe"/>
  <text x="220" y="174" font-size="11" fill="#1e40af" font-family="monospace">GET /api/metrics</text>
  <rect x="390" y="155" width="170" height="28" rx="4" fill="#dbeafe"/>
  <text x="400" y="174" font-size="11" fill="#1e40af" font-family="monospace">POST /api/extract-outcomes</text>
</svg>
</p>

---

## 🏛️ Accreditation Standards

<p align="center">
<svg width="500" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="100" height="60" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="70" y="45" text-anchor="middle" font-size="11" fill="#92400e" font-weight="bold">NBA</text>
  <text x="70" y="65" text-anchor="middle" font-size="9" fill="#92400e">India</text>

  <rect x="140" y="20" width="100" height="60" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="190" y="45" text-anchor="middle" font-size="11" fill="#92400e" font-weight="bold">NAAC</text>
  <text x="190" y="65" text-anchor="middle" font-size="9" fill="#92400e">India</text>

  <rect x="260" y="20" width="100" height="60" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="310" y="45" text-anchor="middle" font-size="11" fill="#92400e" font-weight="bold">NEP 2020</text>
  <text x="310" y="65" text-anchor="middle" font-size="9" fill="#92400e">India</text>

  <rect x="380" y="20" width="100" height="60" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="430" y="45" text-anchor="middle" font-size="11" fill="#92400e" font-weight="bold">ABET</text>
  <text x="430" y="65" text-anchor="middle" font-size="9" fill="#92400e">International</text>
</svg>
</p>

---

## 🧪 Development

```bash
# Run tests
pytest tests/ -v --cov=src

# Code quality
black src/ webapp/backend/ tests/
flake8 src/ webapp/backend/ tests/
mypy src/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

---

## 📁 Project Structure

```
SCDO/
├── src/
│   ├── ai/              # OpenRouter + Gemini integration
│   ├── analysis/        # Parser, gap analyzer, RAG
│   ├── optimization/    # Bloom mapper, content optimizer
│   ├── generation/      # Syllabus generator, chained generation
│   ├── mapping/         # CO-PO mapper
│   ├── export/          # PDF, Excel, LaTeX, JSON exporters
│   ├── rag/             # ChromaDB vector store
│   ├── validation/      # NEP 2020, accreditation validators
│   ├── collaboration/   # Sharing, version history
│   ├── notifications/   # Email + in-app notifications
│   ├── tasks/           # Celery background tasks
│   ├── models/          # SQLAlchemy models
│   └── utils/           # Cache, metrics, retry, exceptions
├── webapp/
│   ├── backend/         # FastAPI server
│   └── frontend/        # React + TypeScript + Vite
├── configs/             # YAML configurations
├── tests/               # Unit + integration tests
└── docs/                # Documentation
```

---

## 📄 License

This project is developed for academic purposes.

---

<p align="center">
  <strong>Built with ❤️ using OpenRouter, Gemini, FastAPI & React</strong>
</p>
