import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import GeneratePage from './pages/GeneratePage';
import OptimizePage from './pages/OptimizePage';
import AuthPage from './pages/AuthPage';
import SCDOLogo from './components/SCDOLogo';

function App() {
  return (
    <AuthProvider>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

const AppContent = () => {
  const location = useLocation();
  const isAuthPage = location.pathname === '/auth';

  return (
    <div className="app">
      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#ffffff',
            color: '#0f172a',
            border: '1px solid #e2e8f0',
            borderRadius: '6px',
            fontFamily: 'Inter, sans-serif',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          },
          success: {
            iconTheme: {
              primary: '#15803d',
              secondary: 'white',
            },
          },
          error: {
            iconTheme: {
              primary: '#b91c1c',
              secondary: 'white',
            },
          },
        }}
      />

      {/* Navigation - Hidden on AuthPage */}
      {!isAuthPage && <Navbar />}

      {/* Main Content */}
      <main className={isAuthPage ? "" : "main-content"}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/generate" element={<GeneratePage />} />
          <Route path="/optimize" element={<OptimizePage />} />
          <Route path="/auth" element={<AuthPage />} />
        </Routes>
      </main>

      {/* Footer - Hidden on AuthPage */}
      {!isAuthPage && (
        <footer className="footer">
          <div className="container">
            <div className="flex flex-col items-center justify-center gap-4">
              <SCDOLogo size="sm" showText={false} className="opacity-50 hover:opacity-100 transition-opacity" />
              <div className="flex flex-col items-center">
                <p className="footer-text">
                  © 2025 SCDO Inc. All rights reserved.
                </p>
                <p className="text-xs text-subtle">
                  Enterprise Grade Syllabus Management System
                </p>
              </div>
            </div>
          </div>
        </footer>
      )}

      <style>{`
        .footer {
          background: white;
          border-top: 1px solid var(--border);
          padding: 2rem 0;
          margin-top: auto;
        }

        .footer-text {
          color: var(--text-secondary);
          font-size: 0.875rem;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};

export default App;
