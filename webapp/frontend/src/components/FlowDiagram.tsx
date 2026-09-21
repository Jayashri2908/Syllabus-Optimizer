import React from 'react';
import { motion } from 'framer-motion';
import { FileScan, Database, Cpu, PieChart, Download } from 'lucide-react';
import './FlowDiagram.css';

const FlowDiagram = () => {
  const width = 900;
  const height = 400;

  const nodes = {
    upload: {
      id: 'upload',
      label: 'Ingestion Engine',
      icon: <FileScan size={24} />,
      x: 100,
      y: 200
    },
    analyzer: {
      id: 'analyzer',
      label: 'Gap Analyzer',
      icon: <PieChart size={24} />,
      x: 350,
      y: 200
    },
    chroma: {
      id: 'chroma',
      label: 'ChromaDB',
      icon: <Database size={24} />,
      x: 600,
      y: 100
    },
    llm: {
      id: 'llm',
      label: 'OpenRouter AI',
      icon: <Cpu size={24} />,
      x: 600,
      y: 300
    },
    export: {
      id: 'export',
      label: 'Exporter',
      icon: <Download size={24} />,
      x: 820,
      y: 200
    }
  };

  const drawPath = (startId: string, endId: string) => {
    const s = nodes[startId as keyof typeof nodes];
    const e = nodes[endId as keyof typeof nodes];

    const sx = s.x + 80;
    const sy = s.y;
    const ex = e.x - 80;
    const ey = e.y;

    return `M ${sx} ${sy} C ${sx + 40} ${sy}, ${ex - 40} ${ey}, ${ex} ${ey}`;
  };

  const connections = [
    { id: 'c1', path: drawPath('upload', 'analyzer') },
    { id: 'c2', path: drawPath('analyzer', 'chroma') },
    { id: 'c3', path: drawPath('analyzer', 'llm') },
    { id: 'c4', path: drawPath('chroma', 'llm') },
    { id: 'c5', path: drawPath('llm', 'export') },
  ];

  return (
    <div className="svg-diagram-wrapper">
      <div className="svg-canvas-container glass">
        <svg viewBox={`0 0 ${width} ${height}`} className="main-svg" preserveAspectRatio="xMidYMid meet">
          <defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="8" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <linearGradient id="glassGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="rgba(255,255,255,0.8)" className="glass-stop-light" />
              <stop offset="100%" stopColor="rgba(255,255,255,0.2)" className="glass-stop-dark" />
            </linearGradient>
            <linearGradient id="glassGradientDark" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="rgba(30,30,50,0.9)" />
              <stop offset="100%" stopColor="rgba(20,20,34,0.6)" />
            </linearGradient>
          </defs>

          {connections.map((conn) => (
            <g key={conn.id}>
              <path
                d={conn.path}
                className="connection-track"
              />
              <motion.path
                d={conn.path}
                className="connection-flow"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  duration: 2,
                  ease: "easeInOut",
                  repeat: Infinity,
                  repeatType: "loop",
                  repeatDelay: 0.5
                }}
              />
            </g>
          ))}

          {Object.values(nodes).map((node) => (
            <g key={node.id} className="svg-node" transform={`translate(${node.x}, ${node.y})`}>
              <rect
                x="-75" y="-35" width="150" height="70" rx="16"
                fill="url(#glassGradient)"
                stroke="var(--accent-indigo-light)" strokeWidth="2"
                filter="url(#glow)"
                className="glass-rect"
                style={{ opacity: 0.85 }}
              />

              <foreignObject x="-75" y="-35" width="150" height="70">
                <div className="node-content">
                  {node.icon}
                  <span className="node-label">{node.label}</span>
                </div>
              </foreignObject>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
};

export default FlowDiagram;
