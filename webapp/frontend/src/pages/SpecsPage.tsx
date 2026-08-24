import React, { useState, useEffect } from 'react';
import { getSystemHealth } from '../services/api';
import { SystemHealth } from '../types';
import FlowDiagram from '../components/FlowDiagram';
import { Server, Database, Activity, Cpu, Hexagon } from 'lucide-react';
import './SpecsPage.css';

const SpecsPage = () => {
  const [healthData, setHealthData] = useState<SystemHealth>({
    status: 'checking...',
    latency: 0,
    service: 'Connecting...'
  });

  useEffect(() => {
    let active = true;
    const checkHealth = async () => {
      const data = await getSystemHealth();
      if (active) setHealthData(data);
    };
    checkHealth();
    
    // Poll every 10 seconds for real-time heartbeat effect
    const interval = setInterval(checkHealth, 10000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const isOnline = healthData.status === 'healthy';

  return (
    <div className="page-container animate-fade-in" style={{ maxWidth: '1200px' }}>
      <div className="page-header">
        <h1>Architecture & Specs</h1>
        <p>Real-time system telemetry and processing pipeline diagrams.</p>
      </div>

      {/* KPI Dashboard */}
      <div className="kpi-grid mb-4">
        {/* API Health */}
        <div className="kpi-card glass-card">
          <div className="kpi-icon"><Server size={24} className="text-secondary" /></div>
          <div className="kpi-content">
            <span className="kpi-label">API Gateway</span>
            <div className={`status-indicator ${isOnline ? 'online' : 'offline'}`}>
               <span className="dot"></span> {isOnline ? 'Connected' : 'Offline'}
            </div>
          </div>
        </div>

        {/* Latency */}
        <div className="kpi-card glass-card">
          <div className="kpi-icon"><Activity size={24} className={isOnline ? 'text-emerald' : 'text-amber'} /></div>
          <div className="kpi-content">
            <span className="kpi-label">Gateway Latency</span>
            <div className="kpi-value">
              {healthData.latency ? `${healthData.latency} ms` : '--'}
            </div>
          </div>
        </div>

        {/* Vector DB (Inferred from health or static as part of the unified backend) */}
        <div className="kpi-card glass-card">
          <div className="kpi-icon"><Database size={24} className="text-indigo" /></div>
          <div className="kpi-content">
            <span className="kpi-label">Vector Store (ChromaDB)</span>
            <div className={`status-indicator ${isOnline ? 'online' : 'offline'}`}>
               <span className="dot"></span> {isOnline ? 'Active' : 'Unreachable'}
            </div>
          </div>
        </div>
        
        {/* LLM Engine */}
        <div className="kpi-card glass-card">
          <div className="kpi-icon"><Cpu size={24} className="text-amber" /></div>
          <div className="kpi-content">
            <span className="kpi-label">Primary LLM</span>
            <div className="kpi-value small">IBM Granite via OpenRouter</div>
          </div>
        </div>
      </div>

      {/* Interactive Flow */}
      <div className="mt-4">
        <FlowDiagram />
      </div>

      {/* Tech Stack Specs */}
      <div className="specs-grid mt-4">
         <div className="glass-card tech-spec-card p-6">
            <div className="spec-card-header">
              <div className="icon-wrapper bg-indigo-light">
                <Hexagon size={20} />
              </div>
              <h3>Frontend Engine</h3>
            </div>
            
            <div className="spec-stats-grid">
              <div className="stat-item">
                <span className="stat-label">Framework</span>
                <span className="stat-value">React 18 + Vite</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Aesthetics</span>
                <span className="stat-value">Glassmorphism UI</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Routing</span>
                <span className="stat-value">Lazy Load & Suspense</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Rendering</span>
                <span className="stat-value">WebGL + Three.js</span>
              </div>
            </div>
         </div>

         <div className="glass-card tech-spec-card p-6">
            <div className="spec-card-header">
              <div className="icon-wrapper bg-emerald">
                <Database size={20} />
              </div>
              <h3>Backend Pipeline</h3>
            </div>

            <div className="spec-stats-grid">
              <div className="stat-item">
                <span className="stat-label">Framework</span>
                <span className="stat-value">FastAPI (Py 3.12)</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Extraction</span>
                <span className="stat-value">Heuristic PDF Chunking</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Vector Store</span>
                <span className="stat-value">ChromaDB Embeddings</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Gen Core</span>
                <span className="stat-value">Instructor JSON Schema</span>
              </div>
            </div>
         </div>
      </div>
    </div>
  );
};

export default SpecsPage;
