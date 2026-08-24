import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, Environment, Float } from '@react-three/drei';
import * as THREE from 'three';

type BloomLevel = 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';

const bloomOrder: BloomLevel[] = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'];
const bloomColors: Record<BloomLevel, string> = {
  remember: '#9ca3af',
  understand: '#60a5fa',
  apply: '#34d399',
  analyze: '#fbbf24',
  evaluate: '#f87171',
  create: '#c084fc'
};

interface Bar3DProps {
  position: [number, number, number];
  color: string;
  height: number;
  label: string;
  percentage: string;
}

const Bar3D: React.FC<Bar3DProps> = ({ position, color, height, label, percentage }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHover] = useState(false);
  
  useFrame((_state, delta) => {
    if (meshRef.current && meshRef.current.scale.y < height) {
      meshRef.current.scale.y += delta * Math.max((height - meshRef.current.scale.y) * 5, 0.1);
      meshRef.current.position.y = (meshRef.current.scale.y / 2) - 1.5;
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
        <meshPhysicalMaterial 
          color={color} 
          metalness={0.2}
          roughness={0.2}
          transmission={0.4} 
          thickness={1}
          emissive={hovered ? color : '#000'}
          emissiveIntensity={hovered ? 0.3 : 0}
        />
      </mesh>
      
      <Html position={[0, -2.5, 0]} center>
         <div style={{ color: 'white', fontFamily: 'var(--font-sans)', fontSize: '0.8rem', opacity: 0.8, textTransform: 'capitalize' }}>
           {label}
         </div>
      </Html>

      {hovered && (
        <Html position={[0, height > 0 ? height : 1, 0]} center>
           <div style={{ background: color, color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700, pointerEvents: 'none' }}>
              {percentage}%
           </div>
        </Html>
      )}
    </group>
  );
};

interface ThreeBloomChartProps {
  data: Record<string, number>;
}

const ThreeBloomChart: React.FC<ThreeBloomChartProps> = ({ data }) => {
  const chartData = bloomOrder.map(level => ({
    name: level,
    count: data[level] || 0
  }));
  const total = chartData.reduce((acc, curr) => acc + curr.count, 0) || 1;
  const maxCount = Math.max(...chartData.map(d => d.count), 0.1);
  
  const scaleRatio = 5 / maxCount;

  return (
    <div style={{ width: '100%', height: '400px', background: '#0f172a', borderRadius: '0.5rem', overflow: 'hidden', cursor: 'grab' }}>
      <Canvas camera={{ position: [0, 4, 12], fov: 45 }}>
        <color attach="background" args={['#0f172a']} />
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1} color="#ffffff" />
        <Environment preset="city" />

        <Float speed={1.5} rotationIntensity={0.1} floatIntensity={0.5}>
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
                 />
               )
            })}
          </group>
        </Float>
        
        <OrbitControls 
          enablePan={false}
          maxPolarAngle={Math.PI / 2}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  );
};

export default ThreeBloomChart;
