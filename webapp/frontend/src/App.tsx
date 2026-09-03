import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import './components/SkeletonLoader.css'; // Global skeleton styles

// Lazy Loaded Pages
const LandingPage = React.lazy(() => import('./pages/LandingPage'));
const AnalyzePage = React.lazy(() => import('./pages/AnalyzePage'));
const GeneratePage = React.lazy(() => import('./pages/GeneratePage'));
const OptimizePage = React.lazy(() => import('./pages/OptimizePage'));
const MapOutcomesPage = React.lazy(() => import('./pages/MapOutcomesPage'));
const SpecsPage = React.lazy(() => import('./pages/SpecsPage'));

const PageFallback = () => (
  <div className="page-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
    <div className="spinner-small" style={{ width: 40, height: 40, borderColor: 'rgba(67, 56, 202, 0.2)', borderLeftColor: 'var(--accent-indigo)' }}></div>
  </div>
);

const App = () => {
  return (
    <>
      <Toaster position="bottom-right" toastOptions={{
        style: {
          background: 'var(--surface-glass)',
          color: 'var(--text-primary)',
          backdropFilter: 'blur(10px)',
          border: '1px solid var(--border-subtle)',
          fontFamily: 'var(--font-sans)',
        }
      }} />
      <Navbar />
      <ErrorBoundary>
        <Suspense fallback={<PageFallback />}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/optimize" element={<OptimizePage />} />
            <Route path="/map-outcomes" element={<MapOutcomesPage />} />
            <Route path="/specs" element={<SpecsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </>
  );
};

export default App;
