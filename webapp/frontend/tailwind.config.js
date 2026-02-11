/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', '-apple-system', 'sans-serif'],
            },
            colors: {
                // Corporate Palette - Warm & Vibrant Sunset
                primary: {
                    DEFAULT: '#1e1b4b',
                    light: '#312e81',
                    dark: '#0f172a',
                },
                brand: {
                    DEFAULT: '#f97316',
                    hover: '#ea580c',
                    light: '#fff7ed',
                    subtle: '#fffaf5',
                },
                // Neutral/Surface - Warmer
                bg: {
                    body: '#fdfcfc',
                    surface: '#f4f4f5',
                    elevated: '#ffffff',
                },
                // Functional
                success: {
                    DEFAULT: '#059669',
                    bg: '#ecfdf5',
                },
                warning: {
                    DEFAULT: '#fbbf24',
                    bg: '#fffbeb',
                },
                error: {
                    DEFAULT: '#e11d48',
                    bg: '#fff1f2',
                },
                border: {
                    DEFAULT: '#e2e8f0',
                    light: '#f1f5f9',
                    focus: '#cbd5e1',
                },
                text: {
                    primary: '#1e293b',
                    secondary: '#475569',
                    tertiary: '#64748b',
                    subtle: '#94a3b8',
                }
            },
            borderRadius: {
                xl: '0.75rem',
                '2xl': '1rem',
                '3xl': '1.5rem',
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out forwards',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                }
            }
        },
    },
    plugins: [],
}
