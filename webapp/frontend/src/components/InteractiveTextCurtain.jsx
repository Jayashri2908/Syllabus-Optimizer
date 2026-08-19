import React, { useRef, useEffect, useCallback } from 'react';

/**
 * Particle — a single character in the text curtain.
 * Plain JS class (not a React component) holding position, velocity,
 * spring anchor and the character to render.
 */
class Particle {
    constructor(x, y, character, friction, spring) {
        this.x = x;
        this.y = y;
        this.baseX = x;
        this.baseY = y;
        this.vx = 0;
        this.vy = 0;
        this.character = character;
        this.friction = friction;
        this.spring = spring;
    }

    /**
     * Apply mouse repulsion + spring snap-back physics.
     * @param {number} mouseX - mouse x relative to canvas
     * @param {number} mouseY - mouse y relative to canvas
     * @param {number} mouseRadius - radius of repulsion influence
     * @param {number} repulsionForce - strength of the repulsion
     */
    update(mouseX, mouseY, mouseRadius, repulsionForce) {
        const dx = mouseX - this.x;
        const dy = mouseY - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Repulsion away from the mouse when within radius
        if (distance < mouseRadius && distance > 0) {
            const force = (mouseRadius - distance) / mouseRadius;
            const angle = Math.atan2(dy, dx);
            this.vx -= Math.cos(angle) * force * repulsionForce;
            this.vy -= Math.sin(angle) * force * repulsionForce;
        }

        // Spring force pulling back toward the base position
        this.vx += (this.baseX - this.x) * this.spring;
        this.vy += (this.baseY - this.y) * this.spring;

        // Friction to dampen motion
        this.vx *= this.friction;
        this.vy *= this.friction;

        this.x += this.vx;
        this.y += this.vy;
    }

    /**
     * Draw the character at its current position.
     * @param {CanvasRenderingContext2D} ctx
     */
    draw(ctx) {
        ctx.fillText(this.character, this.x, this.y);
    }
}

const InteractiveTextCurtain = ({
    characters = "ANALYZE OPTIMIZE GENERATE SYLLABUS CURRICULUM OUTCOMES BLOOM TAXONOMY MAPPING COMPLIANCE ACCREDITATION NEP 2020 COURSE PROGRAM LEARNING ASSESSMENT",
    fontSize = 12,
    spacingX = 18,
    spacingY = 18,
    mouseRadius = 80,
    repulsionForce = 5,
    friction = 0.85,
    spring = 0.05,
    color = '#8b7e6f',       // Warm muted text color
    className = '',
    style = {},
    opacity = 0.35,          // Subtle background opacity
}) => {
    const wrapperRef = useRef(null);
    const canvasRef = useRef(null);
    const particlesRef = useRef([]);
    const mouseRef = useRef({ x: -9999, y: -9999 });
    const animationRef = useRef(null);
    const resizeObserverRef = useRef(null);

    // Keep latest props available to the animation loop without re-creating it
    const propsRef = useRef({ fontSize, spacingX, spacingY, mouseRadius, repulsionForce, friction, spring, color, opacity });
    propsRef.current = { fontSize, spacingX, spacingY, mouseRadius, repulsionForce, friction, spring, color, opacity };

    /**
     * Build the particle grid, centered in the canvas.
     */
    const initParticles = useCallback((width, height) => {
        const { fontSize: fs, spacingX: sx, spacingY: sy } = propsRef.current;
        const chars = characters.split('');
        if (chars.length === 0) return [];

        const cols = Math.max(1, Math.floor(width / sx));
        const rows = Math.max(1, Math.floor(height / sy));

        const gridWidth = (cols - 1) * sx;
        const gridHeight = (rows - 1) * sy;
        const offsetX = (width - gridWidth) / 2;
        const offsetY = (height - gridHeight) / 2;

        const particles = [];
        let index = 0;
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = offsetX + col * sx;
                const y = offsetY + row * sy;
                particles.push(new Particle(x, y, chars[index % chars.length], friction, spring));
                index++;
            }
        }
        return particles;
    }, [characters, friction, spring]);

    /**
     * Resize the canvas to match its parent and rebuild the grid.
     */
    const resize = useCallback(() => {
        const canvas = canvasRef.current;
        const wrapper = wrapperRef.current;
        if (!canvas || !wrapper) return;

        const { width, height } = wrapper.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        canvas.width = Math.max(1, Math.round(width * dpr));
        canvas.height = Math.max(1, Math.round(height * dpr));
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;

        const ctx = canvas.getContext('2d');
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        particlesRef.current = initParticles(width, height);
    }, [initParticles]);

    /**
     * Draw a single static frame (used for reduced-motion users).
     */
    const drawStatic = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const { fontSize: fs, color: c, opacity: o } = propsRef.current;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = `${fs}px monospace`;
        ctx.fillStyle = c;
        ctx.globalAlpha = o;
        for (const particle of particlesRef.current) {
            particle.draw(ctx);
        }
        ctx.globalAlpha = 1;
    }, []);

    /**
     * Animation loop — update physics and render every frame.
     */
    const animate = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const { fontSize: fs, color: c, opacity: o, mouseRadius: mr, repulsionForce: rf } = propsRef.current;
        const { x: mouseX, y: mouseY } = mouseRef.current;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = `${fs}px monospace`;
        ctx.fillStyle = c;
        ctx.globalAlpha = o;

        for (const particle of particlesRef.current) {
            particle.update(mouseX, mouseY, mr, rf);
            particle.draw(ctx);
        }

        ctx.globalAlpha = 1;
        animationRef.current = requestAnimationFrame(animate);
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;
        const wrapper = wrapperRef.current;
        if (!canvas || !wrapper) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Mouse tracking relative to the canvas
        const handleMouseMove = (event) => {
            const rect = canvas.getBoundingClientRect();
            mouseRef.current = {
                x: event.clientX - rect.left,
                y: event.clientY - rect.top,
            };
        };

        // On mouseout, push the mouse far away so particles settle back
        const handleMouseLeave = () => {
            mouseRef.current = { x: -9999, y: -9999 };
        };

        // ResizeObserver on the wrapper handles container size changes
        resizeObserverRef.current = new ResizeObserver(() => {
            resize();
            if (prefersReducedMotion) {
                drawStatic();
            }
        });

        resizeObserverRef.current.observe(wrapper);
        window.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('mouseleave', handleMouseLeave);

        resize();

        if (prefersReducedMotion) {
            // Static render — no animation, no interaction
            drawStatic();
        } else {
            animationRef.current = requestAnimationFrame(animate);
        }

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
                animationRef.current = null;
            }
            if (resizeObserverRef.current) {
                resizeObserverRef.current.disconnect();
                resizeObserverRef.current = null;
            }
            window.removeEventListener('mousemove', handleMouseMove);
            canvas.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, [animate, drawStatic, resize]);

    return (
        <div
            ref={wrapperRef}
            className={className}
            style={{ position: 'relative', overflow: 'hidden', ...style }}
        >
            <canvas
                ref={canvasRef}
                style={{
                    position: 'absolute',
                    inset: 0,
                    width: '100%',
                    height: '100%',
                    pointerEvents: 'none',
                }}
            />
        </div>
    );
};

export default InteractiveTextCurtain;