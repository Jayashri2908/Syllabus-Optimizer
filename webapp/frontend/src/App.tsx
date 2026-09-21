import React, { Suspense } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence, motion } from 'framer-motion';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import './components/SkeletonLoader.css';

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

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -12 }
};

const pageTransition = {
  type: 'tween' as const,
  ease: 'easeInOut' as const,
  duration: 0.25
};

const AnimatedPage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <motion.div
    variants={pageVariants}
    initial="initial"
    animate="animate"
    exit="exit"
    transition={pageTransition}
  >
    {children}
  </motion.div>
);

const App = () => {
  const location = useLocation();

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
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={<AnimatedPage><LandingPage /></AnimatedPage>} />
              <Route path="/analyze" element={<AnimatedPage><AnalyzePage /></AnimatedPage>} />
              <Route path="/generate" element={<AnimatedPage><GeneratePage /></AnimatedPage>} />
              <Route path="/optimize" element={<AnimatedPage><OptimizePage /></AnimatedPage>} />
              <Route path="/map-outcomes" element={<AnimatedPage><MapOutcomesPage /></AnimatedPage>} />
              <Route path="/specs" element={<AnimatedPage><SpecsPage /></AnimatedPage>} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AnimatePresence>
        </Suspense>
      </ErrorBoundary>
    </>
  );
};

export default App;
