---
name: scdo-frontend
description: Frontend development skill for the SCDO (Syllabus & Curriculum Design Optimizer) React app. Use when working on any UI/UX changes, component creation, styling, animations, or page modifications in the webapp/frontend directory.
---

# SCDO Frontend Development

## Project Overview
SCDO is an AI-powered curriculum intelligence platform. The frontend is a React 19 + Vite 8 + TypeScript SPA with a custom glassmorphism design system, Three.js 3D visualizations, and Framer Motion animations.

## Tech Stack
- **Framework**: React 19 with TypeScript
- **Build**: Vite 8
- **Routing**: React Router v7 (lazy-loaded pages via `React.lazy`)
- **State**: React Context (`SyllabusContext`) with localStorage persistence
- **3D/Visuals**: Three.js via `@react-three/fiber` + `@react-three/drei`
- **Animations**: Framer Motion (already project-wide)
- **Icons**: Lucide React
- **Toasts**: react-hot-toast
- **HTTP**: Axios (configured in `src/services/api.ts`)
- **NO component library** — all UI is custom with the glassmorphism design system

## Directory Structure
```
webapp/frontend/src/
├── main.tsx              # Entry point (BrowserRouter + SyllabusProvider)
├── App.tsx               # Routes + Navbar + ErrorBoundary
├── index.css             # Design tokens (CSS custom properties), glassmorphism base, buttons
├── animations.css        # Keyframes (fadeIn, slideUp, pulseGlow, shimmer)
├── types/index.ts        # All TypeScript interfaces (matches FastAPI backend schemas)
├── context/SyllabusContext.tsx  # Global state: currentSyllabus, analysisResult, optimizedSyllabus, coPoMapping
├── services/api.ts       # Axios instance + all API functions (upload, analyze, generate, optimize, map, export, health)
├── components/
│   ├── Navbar.tsx         # Fixed top nav with theme toggle (light/dark/system) + mobile drawer
│   ├── FileUploader.tsx   # Drag-and-drop + click file upload (PDF/DOCX/TXT, 50MB max)
│   ├── TextCurtain.tsx    # Canvas-based mouse-reactive particle text animation (KEEP AS-IS on hero)
│   ├── FlowDiagram.tsx    # SVG pipeline diagram (Ingestion → Analyzer → ChromaDB/LLM → Export)
│   ├── MarqueeTicker.tsx  # Infinite scroll ticker strip
│   ├── ThreeBloomChart.tsx   # 3D bar chart for Bloom's Taxonomy distribution
│   ├── ThreeForceGraph.tsx   # 3D CO-PO force graph with spheres + connection lines
│   ├── COPOHeatmap.tsx       # CSS grid heatmap for CO-PO correlation matrix
│   ├── SkeletonLoader.tsx    # Shimmer skeleton placeholders
│   └── ErrorBoundary.tsx     # React error boundary wrapper
├── pages/
│   ├── LandingPage.tsx   # Hero + TextCurtain + features + workflow + FlowDiagram + footer
│   ├── AnalyzePage.tsx   # Upload → gap analysis dashboard (Bloom's, CO-PO, assessment, compliance)
│   ├── GeneratePage.tsx  # 3-step wizard → AI-generated syllabus with inline editing
│   ├── OptimizePage.tsx  # Upload → original vs optimized comparison
│   ├── MapOutcomesPage.tsx # JSON input → CO-PO heatmap + 3D force graph
│   └── SpecsPage.tsx     # System health dashboard + pipeline diagram + tech specs
```

## Design System (CSS Custom Properties)

### Theme Modes
- **Light** (default): parchment palette `--bg-parchment: #F5F0E8`, warm ivory glass
- **Dark** (`data-theme="dark"`): `--bg-parchment: #0f0f1a`, dark glass
- **System**: follows OS preference via `prefers-color-scheme` media query

### Key Tokens
- `--accent-indigo: #4338CA` (primary action color, light: `#6366F1`, dark mode: `#818cf8`)
- `--accent-amber: #D97706`, `--accent-emerald: #059669`, `--accent-rose: #E11D48`
- `--surface-glass: rgba(250, 247, 240, 0.7)` — glassmorphism panel background
- `--glass-bg: linear-gradient(145deg, rgba(255,255,255,0.9) 0%, rgba(250,247,240,0.5) 100%)`
- `--font-serif: 'Cormorant Garamond'` (headings), `--font-sans: 'Outfit'` (body), `--font-mono: 'JetBrains Mono'` (code/tags)

### Component Patterns
- **Glass cards**: `.glass-card` class — frosted glass background, blur backdrop, hover lift + shine animation
- **Buttons**: `.btn-primary` (indigo bg, white text), `.btn-secondary` (transparent, bordered)
- **Tags**: `.mono-tag` — monospace pill badges for bloom levels, categories
- **Animations**: `.animate-fade-in`, `.animate-slide-up`, `.stagger-1` through `.stagger-5`

## API Layer
All API calls go through `src/services/api.ts` which uses an Axios instance with:
- Base URL: `/api` (proxied to FastAPI backend in dev via Vite config)
- Global error interceptor: handles 401, 413, 429, 503 with toast messages
- Key endpoints: `POST /upload`, `POST /upload-and-analyze`, `POST /analyze`, `POST /optimize`, `POST /generate`, `POST /map-outcomes`, `POST /export/pdf`, `GET /health`

## Important Rules
1. **NEVER modify TextCurtain.tsx** — it's the signature hero animation and must stay as-is
2. **All new pages must be lazy-loaded** in App.tsx via `React.lazy()`
3. **Use Framer Motion** for all animations (already a project dependency) — never use raw CSS @keyframes for component-level animations
4. **Theme-awareness is mandatory** — every new component must work in light, dark, and system modes. Use CSS custom properties, never hardcode colors. For Three.js scenes, read `data-theme` attribute or use `getIsDark()` pattern from ThreeBloomChart
5. **Follow the glassmorphism pattern** — new cards/panels use `.glass-card` or match its styling
6. **Keep the serif/sans font split** — headings use `--font-serif`, body uses `--font-sans`, code/tags use `--font-mono`
7. **No new UI libraries** — the project uses custom components only. If a complex UI element is needed (e.g., tabs, command palette), build it with the existing design system
8. **TypeScript is strict** — all components must be fully typed. Use interfaces from `types/index.ts` or extend them
9. **Toast notifications for all async operations** — use `toast.loading()` → `toast.success()` / `toast.error()` pattern
10. **File uploads**: Use the existing `FileUploader` component or match its validation (PDF/DOCX/TXT, 50MB max)

## Testing
- Lint: `cd webapp/frontend && npm run lint` (oxlint)
- Build check: `cd webapp/frontend && npm run build`
- No frontend test framework is currently configured

## Backend API (for reference)
- FastAPI backend at `webapp/backend/app/main.py`
- Routes in `webapp/backend/app/routers/`
- Run backend: `cd webapp/backend && python main.py` (port 8000)
- Run frontend: `cd webapp/frontend && npm run dev` (port 5173, proxies `/api` to 8000)

## Common Tasks
- **Adding a new page**: Create in `pages/`, add CSS file, lazy-import in `App.tsx`, add `<Route>`, add nav link in `Navbar.tsx`
- **Adding a new API endpoint**: Add function in `services/api.ts`, add types in `types/index.ts`
- **Creating a 3D visualization**: Use `@react-three/fiber` Canvas + drei helpers. Make theme-aware. Use `frameloop="demand"` for performance. Add OrbitControls for interactivity
- **Adding a new shared component**: Create in `components/`, use CSS file (not CSS modules), follow glassmorphism pattern

## Page Architecture Patterns

### AnalyzePage Pattern
- Uses `uploadAndAnalyze()` combined endpoint for fast-track
- Renders a grid of glass-card sections for each analysis dimension
- Score cards use `ScoreCard` sub-component with icon + value
- Gap badges use `GapBadge` with severity color coding
- All data comes from `AnalysisResult` type in `types/index.ts`

### GeneratePage Pattern
- 3-step wizard with `step` state (1→2→3)
- Step 1: Course identity fields
- Step 2: Domain + keywords (triggers generation)
- Step 3: Results with inline editing toggle
- Uses `generateSyllabus()` API call

### OptimizePage Pattern
- Upload → parse → optimize (two sequential API calls)
- Split-view comparison: original vs optimized
- Loading state shows skeleton placeholders in both columns

### MapOutcomesPage Pattern
- JSON textarea input for course outcomes
- Calls `mapOutcomes()` with parsed CO array
- Shows ThreeForceGraph + COPOHeatmap side by side
- Validation section below matrix

## Known Issues & Improvement Areas
- MapOutcomesPage uses raw JSON textarea — not user-friendly for non-developers
- OptimizePage only shows CO-level diff, not unit-level changes
- AnalyzePage is a flat wall of cards — needs tabbed/collapsible layout
- ThreeForceGraph has hardcoded `#0f172a` dark background regardless of theme
- FlowDiagram uses hardcoded light colors regardless of theme
- App.css contains unused Vite boilerplate
- Multiple inline styles throughout components that should be CSS classes
- No page transition animations between routes
- No empty/error state illustrations
