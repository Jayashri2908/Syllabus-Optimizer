import React, { useRef, useState, useEffect, useMemo, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';

type BloomLevel = 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';

const bloomOrder: BloomLevel[] = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'];
const bloomColors: Record<BloomLevel, string> = {
  remember: '#94a3b8',
  understand: '#60a5fa',
  apply: '#34d399',
  analyze: '#fbbf24',
  evaluate: '#f87171',
  create: '#c084fc'
};

/* ── Theme-aware background helper ─────────────────────────────────── */
function getChartBackground(): string {
  const attr = document.documentElement.getAttribute('data-theme');
  if (attr === 'dark') return 'linear-gradient(180deg, #0f172a 0%, #1e1b3a 100%)';
  if (attr === 'light') return 'linear-gradient(180deg, #e8e0d0 0%, #ddd6c8 100%)';
  // system — ask the OS
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'linear-gradient(180deg, #0f172a 0%, #1e1b3a 100%)';
  }
  return 'linear-gradient(180deg, #e8e0d0 0%, #ddd6c8 100%)';
}

function getSceneBg(): string {
  const attr = document.documentElement.getAttribute('data-theme');
  if (attr === 'dark') return '#0f172a';
  if (attr === 'light') return '#e8e0d0';
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) return '#0f172a';
  return '#e8e0d0';
}

function getIsDark(): boolean {
  const attr = document.documentElement.getAttribute('data-theme');
  if (attr === 'dark') return true;
  if (attr === 'light') return false;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

/* ── Bar3D component ───────────────────────────────────────────────── */
interface Bar3DProps {
  position: [number, number, number];
  color: string;
  height: number;
  label: string;
  percentage: string;
  onDone: () => void;
  isDark: boolean;
}

const Bar3D: React.FC<Bar3DProps> = ({ position, color, height, label, percentage, onDone, isDark }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHover] = useState(false);
  const doneRef = useRef(false);

  useFrame((_state, delta) => {
    if (doneRef.current || !meshRef.current) return;
    if (meshRef.current.scale.y < height) {
      const remaining = height - meshRef.current.scale.y;
      const step = delta * Math.max(remaining * 5, 0.1);
      meshRef.current.scale.y = Math.min(meshRef.current.scale.y + step, height);
      meshRef.current.position.y = (meshRef.current.scale.y / 2) - 1.5;
    } else {
      doneRef.current = true;
      onDone();
    }
  });

  return (
    <group position={[position[0], 0, position[2]]}>
      <mesh
        ref={meshRef}
        position={[0, -1.5, 0]}
        scale={[1, 0.1, 1]}
        onPointerOver={() => setHover(true)}
        onPointerOut={() => setHover(false)}
      >
        <boxGeometry args={[1.5, 1, 1.5]} />
        <meshStandardMaterial
          color={color}
          metalness={0.15}
          roughness={0.45}
          emissive={hovered ? color : '#000'}
          emissiveIntensity={hovered ? 0.35 : 0}
        />
      </mesh>

      <Html position={[0, -2.5, 0]} center>
        <div style={{
          color: isDark ? 'rgba(255,255,255,0.8)' : 'rgba(30,30,46,0.7)',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.8rem',
          textTransform: 'capitalize'
        }}>
          {label}
        </div>
      </Html>

      {hovered && (
        <Html position={[0, height > 0 ? height : 1, 0]} center>
          <div style={{
            background: color,
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 700,
            pointerEvents: 'none'
          }}>
            {percentage}%
          </div>
        </Html>
      )}
    </group>
  );
};

/* ── Animation orchestrator — invalidates canvas only while animating ── */
const AnimationDriver: React.FC = () => {
  const { invalidate } = useThree();
  const frameCount = useRef(0);

  useFrame(() => {
    // Keep canvas alive for ~120 frames (~2 seconds) for the bar grow-in
    if (frameCount.current < 120) {
      invalidate();
      frameCount.current++;
    }
  });

  return null;
};

/* ── Main Chart Component ──────────────────────────────────────────── */
interface ThreeBloomChartProps {
  data: Record<string, number>;
}

const ThreeBloomChart: React.FC<ThreeBloomChartProps> = ({ data }) => {
  const [bg, setBg] = useState(getChartBackground);
  const [sceneBg, setSceneBg] = useState(getSceneBg);
  const [isDark, setIsDark] = useState(getIsDark);

  // Watch for data-theme changes on <html>
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setBg(getChartBackground());
      setSceneBg(getSceneBg());
      setIsDark(getIsDark());
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });
    return () => observer.disconnect();
  }, []);

  // Also listen for OS preference changes when in system mode
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      // Only update if in system mode
      if (!document.documentElement.getAttribute('data-theme')) {
        setBg(getChartBackground());
        setSceneBg(getSceneBg());
        setIsDark(getIsDark());
      }
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  const chartData = useMemo(() => bloomOrder.map(level => ({
    name: level,
    count: data[level] || 0
  })), [data]);

  const total = chartData.reduce((acc, curr) => acc + curr.count, 0) || 1;
  const maxCount = Math.max(...chartData.map(d => d.count), 0.1);
  const scaleRatio = 5 / maxCount;

  // No-op callback — we use AnimationDriver instead of per-bar invalidate
  const handleBarDone = useCallback(() => {}, []);

  return (
    <div style={{
      width: '100%',
      height: '400px',
      background: bg,
      borderRadius: '0.5rem',
      overflow: 'hidden',
      cursor: 'grab',
      transition: 'background 0.4s ease'
    }}>
      <Canvas
        camera={{ position: [0, 4, 12], fov: 45 }}
        frameloop="demand"
      >
        <color attach="background" args={[sceneBg]} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[8, 10, 5]} intensity={1.2} color="#ffffff" />
        <pointLight position={[-6, 6, 4]} intensity={0.6} color="#a5b4fc" />

        <group position={[-5, 0, 0]}>
          {chartData.map((item, i) => {
            const barHeight = (item.count * scaleRatio) + 0.1;
            const perc = ((item.count / total) * 100).toFixed(1);
            return (
              <Bar3D
                key={item.name}
                position={[i * 2, 0, 0]}
                height={barHeight}
                color={bloomColors[item.name]}
                label={item.name}
                percentage={perc}
                onDone={handleBarDone}
                isDark={isDark}
              />
            );
          })}
        </group>

        <OrbitControls
          enablePan={false}
          maxPolarAngle={Math.PI / 2}
        />

        <AnimationDriver />
      </Canvas>
    </div>
  );
};

export default ThreeBloomChart;
