import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Box, MeshWobbleMaterial, Float } from '@react-three/drei';

function AnimatedLogo() {
    const meshRef = useRef();

    useFrame((state) => {
        const { clock } = state;
        if (meshRef.current) {
            meshRef.current.rotation.x = Math.sin(clock.getElapsedTime()) * 0.3;
            meshRef.current.rotation.y = clock.getElapsedTime() * 0.8;
            meshRef.current.rotation.z = Math.cos(clock.getElapsedTime() * 0.5) * 0.2;
        }
    });

    return (
        <Float speed={5} rotationIntensity={2} floatIntensity={2}>
            <Box ref={meshRef} args={[1, 1, 1]} scale={2.5}>
                <MeshWobbleMaterial
                    color="#f97316"
                    factor={0.4}
                    speed={2}
                    roughness={0}
                    metalness={1}
                />
            </Box>
        </Float>
    );
}

const Logo3D = () => {
    return (
        <div style={{ width: '40px', height: '40px' }}>
            <Canvas camera={{ position: [0, 0, 4], fov: 50 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <spotLight position={[-10, 10, 10]} angle={0.15} penumbra={1} intensity={1} color="#f97316" />
                <AnimatedLogo />
            </Canvas>
        </div>
    );
};

export default Logo3D;
