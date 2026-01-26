import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

function KnowledgeNetwork() {
    const pointsRef = useRef();
    const linesRef = useRef();

    const count = 40;
    const [positions, lineIndices] = useMemo(() => {
        const pos = new Float32Array(count * 3);
        const indices = [];
        for (let i = 0; i < count; i++) {
            pos[i * 3] = (Math.random() - 0.5) * 10;
            pos[i * 3 + 1] = (Math.random() - 0.5) * 10;
            pos[i * 3 + 2] = (Math.random() - 0.5) * 10;
        }

        // Connect nodes that are close to each other to form a "network"
        for (let i = 0; i < count; i++) {
            let connections = 0;
            for (let j = i + 1; j < count; j++) {
                const dx = pos[i * 3] - pos[j * 3];
                const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
                const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
                if (dist < 4 && connections < 3) {
                    indices.push(i, j);
                    connections++;
                }
            }
        }

        return [pos, new Uint16Array(indices)];
    }, [count]);

    useFrame((state) => {
        const time = state.clock.getElapsedTime();
        if (pointsRef.current) {
            pointsRef.current.rotation.y = time * 0.05;
            pointsRef.current.rotation.x = time * 0.03;
        }
        if (linesRef.current) {
            linesRef.current.rotation.y = time * 0.05;
            linesRef.current.rotation.x = time * 0.03;
        }
    });

    return (
        <group>
            <Points ref={pointsRef} positions={positions} stride={3}>
                <PointMaterial
                    transparent
                    color="#ea580c"
                    size={0.4}
                    sizeAttenuation={true}
                    depthWrite={false}
                />
            </Points>
            <lineSegments ref={linesRef}>
                <bufferGeometry>
                    <bufferAttribute
                        attach="attributes-position"
                        count={positions.length / 3}
                        array={positions}
                        itemSize={3}
                    />
                    <bufferAttribute
                        attach="index"
                        count={lineIndices.length}
                        array={lineIndices}
                        itemSize={1}
                    />
                </bufferGeometry>
                <lineBasicMaterial
                    color="#4338ca"
                    transparent
                    opacity={0.6}
                />
            </lineSegments>
        </group>
    );
}

const ThreeBackground = () => {
    return (
        <div style={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: '60%',
            height: '100%',
            zIndex: -1,
            pointerEvents: 'none',
            opacity: 0.7,
            maskImage: 'linear-gradient(to left, rgba(0,0,0,1), rgba(0,0,0,0))',
            WebkitMaskImage: 'linear-gradient(to left, rgba(0,0,0,1), rgba(0,0,0,0))'
        }}>
            <Canvas camera={{ position: [0, 0, 10], fov: 60 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} color="#f97316" intensity={1} />
                <Float speed={1} rotationIntensity={0.2} floatIntensity={0.5}>
                    <KnowledgeNetwork />
                </Float>
            </Canvas>
        </div>
    );
};

export default ThreeBackground;
