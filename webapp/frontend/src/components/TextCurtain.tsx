import React, { useEffect, useRef, MutableRefObject } from 'react';

interface MouseState {
  x: number;
  y: number;
  radius: number;
}

// The physics object for each individual letter
class Particle {
  x: number;
  y: number;
  baseX: number;
  baseY: number;
  vx: number;
  vy: number;
  character: string;
  mouse: MutableRefObject<MouseState>;
  friction: number;
  spring: number;

  constructor(x: number, y: number, character: string, mouseRef: MutableRefObject<MouseState>) {
    this.x = x;
    this.y = y;
    this.baseX = x;
    this.baseY = y;
    this.vx = 0;
    this.vy = 0;
    this.character = character;
    this.mouse = mouseRef;
    
    // Physics properties
    this.friction = 0.85; 
    this.spring = 0.05;   
  }

  update(): void {
    const dx = this.mouse.current.x - this.x;
    const dy = this.mouse.current.y - this.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < 0.001) return;
    if (distance < this.mouse.current.radius) {
      const forceDirectionX = dx / distance;
      const forceDirectionY = dy / distance;
      const force = (this.mouse.current.radius - distance) / this.mouse.current.radius;
      
      const directionX = forceDirectionX * force * -5; 
      const directionY = forceDirectionY * force * -5;

      this.vx += directionX;
      this.vy += directionY;
    }

    const baseDx = this.baseX - this.x;
    const baseDy = this.baseY - this.y;
    
    this.vx += baseDx * this.spring;
    this.vy += baseDy * this.spring;

    this.vx *= this.friction;
    this.vy *= this.friction;
    
    this.x += this.vx;
    this.y += this.vy;
  }

  draw(ctx: CanvasRenderingContext2D): void {
    ctx.fillText(this.character, this.x, this.y);
  }
}

interface TextCurtainProps {
  words?: string[];
  cols?: number;
  rows?: number;
  spacingX?: number;
  spacingY?: number;
  particleColor?: string;
  font?: string;
}

const TextCurtain: React.FC<TextCurtainProps> = ({ 
  words = ["Bloom", "Analyze", "Create", "Evaluate", "CO", "PO", "NAAC", "NBA", "NEP2020", "ABET", "Curriculum", "Outcome", "Taxonomy", "Pedagogy", "Syllabus", "Design", "Optimization", "Cognitive", "Synthesize", "Assess"],
  cols = 20, 
  rows = 24, 
  spacingX = 64, 
  spacingY = 24,
  particleColor = '#5c5446',
  font = '14px "JetBrains Mono", monospace'
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef<MouseState>({ x: -1000, y: -1000, radius: 100 });
  const particlesRef = useRef<Particle[]>([]);
  const requestRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    let width = canvas.parentElement?.clientWidth || 800;
    let height = canvas.parentElement?.clientHeight || 600;
    
    // Handle DPI for sharp text
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    const initParticles = (): void => {
      particlesRef.current = [];
      const startX = (width / 2) - ((cols * spacingX) / 2);
      const startY = (height / 2) - ((rows * spacingY) / 2);

      let wordIndex = 0;
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          const x = startX + (i * spacingX);
          const y = startY + (j * spacingY);
          
          const word = words[wordIndex % words.length];
          particlesRef.current.push(new Particle(x, y, word, mouseRef));
          wordIndex++;
        }
      }
    };

    const animate = (): void => {
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = particleColor;
      ctx.font = font;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      particlesRef.current.forEach(particle => {
        particle.update();
        particle.draw(ctx);
      });

      requestRef.current = requestAnimationFrame(animate);
    };

    const handleMouseMove = (e: MouseEvent): void => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current.x = e.clientX - rect.left;
      mouseRef.current.y = e.clientY - rect.top;
    };

    const handleMouseOut = (): void => {
      mouseRef.current.x = -1000;
      mouseRef.current.y = -1000;
    };

    const handleResize = (): void => {
      width = canvas.parentElement?.clientWidth || 800;
      height = canvas.parentElement?.clientHeight || 600;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      initParticles();
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseout', handleMouseOut);
    window.addEventListener('resize', handleResize);

    initParticles();
    animate();

    return () => {
      cancelAnimationFrame(requestRef.current);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseout', handleMouseOut);
      window.removeEventListener('resize', handleResize);
    };
  }, [words, cols, rows, spacingX, spacingY, particleColor, font]);

  return (
    <canvas 
      ref={canvasRef} 
      style={{ display: 'block', width: '100%', height: '100%' }}
    />
  );
};

export default TextCurtain;
