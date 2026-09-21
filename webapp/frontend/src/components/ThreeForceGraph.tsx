import React, { useState, useMemo, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Html, Environment, Line, Stars } from '@react-three/drei';
import { COPOMappingData } from '../types';

function getIsDark(): boolean {
  const attr = document.documentElement.getAttribute('data-theme');
  if (attr === 'dark') return true;
  if (attr === 'light') return false;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function getGraphBg(): string {
  return getIsDark() ? '#0f172a' : '#1e1b3a';
}

function getGraphBgCss(): string {
  return getIsDark() ? '#0f172a' : '#e8e0d0';
}

interface NodeInfoProps {
  title: string;
  isActive: boolean;
}

const NodeInfo: React.FC<NodeInfoProps> = ({ title, isActive }) => (
  <Html center style={{ pointerEvents: 'none', transition: 'all 0.2s', opacity: isActive ? 1 : 0.5 }}>
    <div style={{
      background: isActive ? 'rgba(67, 56, 202, 0.9)' : 'rgba(255, 255, 255, 0.1)',
      color: 'white',
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '0.75rem',
      fontWeight: isActive ? 700 : 400,
      fontFamily: 'var(--font-sans)',
      backdropFilter: 'blur(4px)',
      boxShadow: isActive ? '0 0 10px rgba(99,102,241,0.5)' : 'none'
    }}>
      {title}
    </div>
  </Html>
);

interface ConnectionLineProps {
  start: [number, number, number];
  end: [number, number, number];
  strength: number;
}

const ConnectionLine: React.FC<ConnectionLineProps> = ({ start, end, strength }) => {
  if (strength < 0.5) return null;

  const color = strength > 2.5 ? '#10b981' : strength > 1.5 ? '#60a5fa' : '#9ca3af';
  const width = strength * 1.5;

  return (
    <Line
      points={[start, end]}
      color={color}
      lineWidth={width}
      transparent
      opacity={strength > 2.5 ? 0.9 : 0.4}
      dashed={strength <= 1.5}
      dashSize={0.2}
      gapSize={0.2}
    />
  );
};

interface GraphNode {
  id: string;
  pos: [number, number, number];
  type: 'co' | 'po';
}

interface GraphEdge {
  start: [number, number, number];
  end: [number, number, number];
  strength: number;
}

interface ThreeForceGraphProps {
  mapping: COPOMappingData;
}

const ThreeForceGraph: React.FC<ThreeForceGraphProps> = ({ mapping }) => {
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [bg, setBg] = useState(getGraphBg);
  const [bgCss, setBgCss] = useState(getGraphBgCss);

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setBg(getGraphBg());
      setBgCss(getGraphBgCss());
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      if (!document.documentElement.getAttribute('data-theme')) {
        setBg(getGraphBg());
        setBgCss(getGraphBgCss());
      }
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  const matrix = mapping?.matrix ?? [];
  const numCOs = matrix.length;
  const numPOs = numCOs > 0 ? (matrix[0]?.po_scores?.length ?? 0) : 0;

  const coNodes: GraphNode[] = useMemo(() => {
    if (numCOs === 0) return [];
    return matrix.map((_row, i) => {
      const z = (i - (numCOs / 2)) * 1.5;
      const y = Math.sin((i / numCOs) * Math.PI) * 2;
      return { id: `CO${i + 1}`, pos: [-5, y, z] as [number, number, number], type: 'co' as const };
    });
  }, [matrix, numCOs]);

  const poNodes: GraphNode[] = useMemo(() => {
    if (numPOs === 0) return [];
    return Array.from({ length: numPOs }).map((_: unknown, j: number) => {
      const z = (j - (numPOs / 2)) * 1.2;
      const y = Math.sin((j / numPOs) * Math.PI) * -2;
      return { id: `PO${j + 1}`, pos: [5, y, z] as [number, number, number], type: 'po' as const };
    });
  }, [numPOs]);

  const edges: GraphEdge[] = useMemo(() => {
    if (numCOs === 0 || numPOs === 0) return [];
    const list: GraphEdge[] = [];
    matrix.forEach((row, coIdx: number) => {
      row.po_scores.forEach((score: number, poIdx: number) => {
        if (score > 0) {
          list.push({
            start: coNodes[coIdx].pos,
            end: poNodes[poIdx].pos,
            strength: score
          });
        }
      });
    });
    return list;
  }, [matrix, coNodes, poNodes, numCOs, numPOs]);

  if (!mapping || !mapping.matrix || mapping.matrix.length === 0) return null;

  return (
    <div style={{ width: '100%', height: '500px', background: bgCss, borderRadius: '0.5rem', overflow: 'hidden', cursor: 'grab', marginBottom: '2rem', transition: 'background 0.4s ease' }}>
      <Canvas camera={{ position: [0, 8, 12], fov: 45 }}>
        <color attach="background" args={[bg]} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[0, 10, 5]} intensity={1} />
        <Environment preset="city" />
        <Stars radius={50} depth={50} count={1000} factor={4} saturation={1} fade speed={1} />

        <group>
          {coNodes.map((node: GraphNode) => (
            <mesh
              key={node.id}
              position={node.pos}
              onPointerOver={() => setActiveNode(node.id)}
              onPointerOut={() => setActiveNode(null)}
              scale={activeNode === node.id ? 1.5 : 1}
            >
              <sphereGeometry args={[0.3, 32, 32]} />
              <meshStandardMaterial color="#6366f1" emissive="#6366f1" emissiveIntensity={activeNode === node.id ? 1 : 0.2} />
              <NodeInfo title={node.id} isActive={activeNode === node.id} />
            </mesh>
          ))}

          {poNodes.map((node: GraphNode) => (
            <mesh
              key={node.id}
              position={node.pos}
              onPointerOver={() => setActiveNode(node.id)}
              onPointerOut={() => setActiveNode(null)}
              scale={activeNode === node.id ? 1.5 : 1}
            >
              <sphereGeometry args={[0.4, 32, 32]} />
              <meshStandardMaterial color="#f59e0b" emissive="#f59e0b" emissiveIntensity={activeNode === node.id ? 1 : 0.2} />
              <NodeInfo title={node.id} isActive={activeNode === node.id} />
            </mesh>
          ))}

          {edges.map((edge: GraphEdge, idx: number) => (
            <ConnectionLine key={idx} start={edge.start} end={edge.end} strength={edge.strength} />
          ))}
        </group>

        <OrbitControls
          enablePan={false}
          autoRotate={!activeNode}
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  );
};

export default ThreeForceGraph;
