import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import InteractiveTextCurtain from '../components/InteractiveTextCurtain';
import { useAuth } from '../context/AuthContext';
import { ArrowRight, User, Lock, Mail, AlertCircle, CheckCircle } from 'lucide-react';

const AuthPage = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        email: ''
    });
    const [error, setError] = useState(null);
    const { login, signup, user } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    // Redirect if already logged in
    useEffect(() => {
        if (user) {
            const from = location.state?.from?.pathname || '/';
            navigate(from, { replace: true });
        }
    }, [user, navigate, location]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError(null); // Clear error on typing
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            if (isLogin) {
                await login({
                    identifier: formData.username,
                    password: formData.password
                });
            } else {
                await signup({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password
                });
            }
        } catch (err) {
            setError(err.message || 'Authentication failed');
        }
    };

    const toggleMode = () => {
        setIsLogin(!isLogin);
        setError(null);
        setFormData({ username: '', password: '', email: '' });
    };

    return (
        <div className="h-screen w-full flex relative overflow-hidden bg-[#f5efe6] font-sans">
            {/* Background Layers - Warm earthy tones */}
            <div className="absolute inset-0 bg-gradient-to-br from-[#efe8de]/30 via-[#faf7f2] to-[#fbe9e7]/30 animate-gradient-xy"></div>

            {/* Text Curtain Layer */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                <InteractiveTextCurtain 
                    characters="SYLLABUS CURRICULUM OPTIMIZE ANALYZE GENERATE OUTCOMES BLOOM COMPLIANCE NEP 2020 ACCREDITATION COURSE LEARNING ASSESSMENT"
                    opacity={0.2}
                    color="#8b7e6f"
                    fontSize={12}
                    spacingX={16}
                    spacingY={16}
                />
            </div>

            <div className="relative z-10 w-full h-full flex flex-col md:flex-row shadow-2xl">
                {/* Left Side: Brand & Visuals (Desktop only) */}
                <div className="hidden md:flex md:w-[55%] flex-col justify-center px-16 lg:px-32 bg-[#faf7f2]/10 backdrop-blur-sm border-r border-[#d4c8b8]/30">
                    <div className="space-y-8 animate-fade-in-up">
                        <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-[#fbe9e7]/80 backdrop-blur-md border border-[#d32f2f]/20 shadow-sm mb-4">
                            <span className="w-2 h-2 rounded-full bg-[#d32f2f] animate-pulse"></span>
                            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#d32f2f]">SCDO Enterprise</span>
                        </div>

                        <h1 className="text-7xl lg:text-8xl font-black tracking-tighter leading-[0.85] font-serif">
                            <span className="text-[#2a1f14]">Optimizing</span><br />
                            <span className="text-gradient">Curriculum.</span>
                        </h1>

                        <p className="text-xl text-[#5c5446] font-medium max-w-lg leading-relaxed">
                            A professional suite for educators to analyze, generate, and bridge the gap between academia and industry.
                        </p>

                        <div className="flex items-center gap-12 pt-6">
                            <div className="flex flex-col">
                                <span className="text-3xl font-black text-[#2a1f14]">100%</span>
                                <span className="text-[10px] font-bold text-[#8b7e6f] uppercase tracking-widest">Compliance</span>
                            </div>
                            <div className="w-px h-12 bg-[#d4c8b8]"></div>
                            <div className="flex flex-col">
                                <span className="text-3xl font-black text-[#2a1f14]">AI</span>
                                <span className="text-[10px] font-bold text-[#8b7e6f] uppercase tracking-widest">Orchestrated</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Side: Auth Form - Optimized for Modern SaaS Layout */}
                <div className="w-full md:w-[45%] flex items-center justify-center p-4 sm:p-6 md:p-8 lg:p-16 h-full bg-[#faf7f2]/20 backdrop-blur-lg">
                    <div className="w-full max-w-[720px] animate-fade-in stagger-2">
                        {/* Mobile/Small Screen Logo */}
                        <div className="md:hidden flex flex-col items-center mb-8">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#3d2e1f] to-[#d32f2f] flex items-center justify-center text-white shadow-xl mb-4">
                                <span className="text-2xl font-black">S</span>
                            </div>
                            <h2 className="text-4xl font-black text-gradient tracking-tighter">SCDO</h2>
                        </div>

                        {/* Form Card */}
                        <div className="glass-panel rounded-xl p-8 sm:p-12 md:p-14 lg:p-16 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.12)] border border-[#d4c8b8]/60 relative overflow-hidden animate-scale-in">
                            {/* Subtle light effect */}
                            <div className="absolute -top-40 -right-40 w-80 h-80 bg-[#d32f2f]/10 blur-[120px] rounded-full"></div>
                            <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-[#e65100]/10 blur-[120px] rounded-full"></div>

                            <div className="relative mb-12">
                                <h2 className="text-5xl sm:text-5xl md:text-6xl font-black text-[#2a1f14] tracking-tight mb-4 font-serif">
                                    {isLogin ? 'Welcome Back' : 'Create Account'}
                                </h2>
                                <p className="text-[#5c5446] font-semibold text-lg md:text-xl leading-relaxed">
                                    {isLogin
                                        ? 'Access your curriculum dashboard'
                                        : 'Join the next generation of curriculum design'}
                                </p>
                            </div>

                            {error && (
                                <div className="mb-8 bg-rose-50 border border-rose-100 text-rose-600 px-6 py-4 rounded-2xl text-base font-bold flex items-center gap-3 animate-shake">
                                    <AlertCircle size={20} className="shrink-0" />
                                    <span>{error}</span>
                                </div>
                            )}

                            <form onSubmit={handleSubmit} className="space-y-9">
                                <div className="space-y-3 group animate-fade-in-up stagger-1">
                                    <label className="text-xs font-black text-[#8b7e6f] uppercase tracking-[0.2em] ml-3">
                                        {isLogin ? 'Identifier' : 'Username'}
                                    </label>
                                    <div className="relative">
                                        <div className="absolute left-6 top-1/2 -translate-y-1/2 text-[#8b7e6f] group-focus-within:text-[#d32f2f] transition-colors duration-300">
                                            <User size={28} strokeWidth={2.5} />
                                        </div>
                                        <input
                                            type="text"
                                            name="username"
                                            value={formData.username}
                                            onChange={handleChange}
                                            placeholder={isLogin ? "Username or email" : "Choose username"}
                                            className="form-input !pl-20 !py-6 !text-lg !rounded-2xl !bg-white/40 !border-[#d4c8b8]/80 focus:!bg-white focus:!border-[#d32f2f] focus:!ring-[#d32f2f]/10 text-lg font-bold"
                                            required
                                        />
                                    </div>
                                </div>

                                {!isLogin && (
                                    <div className="space-y-3 group animate-fade-in-up stagger-2">
                                        <label className="text-xs font-black text-[#8b7e6f] uppercase tracking-[0.2em] ml-3">
                                            Email
                                        </label>
                                        <div className="relative">
                                            <div className="absolute left-6 top-1/2 -translate-y-1/2 text-[#8b7e6f] group-focus-within:text-[#d32f2f] transition-colors duration-300">
                                                <Mail size={28} strokeWidth={2.5} />
                                            </div>
                                            <input
                                                type="email"
                                                name="email"
                                                value={formData.email}
                                                onChange={handleChange}
                                                placeholder="email@university.edu"
                                                className="form-input !pl-20 !py-6 !text-lg !rounded-2xl !bg-white/40 !border-[#d4c8b8]/80 focus:!bg-white focus:!border-[#d32f2f] focus:!ring-[#d32f2f]/10 text-lg font-bold"
                                                required
                                            />
                                        </div>
                                    </div>
                                )}

                                <div className="space-y-3 group animate-fade-in-up stagger-3">
                                    <div className="flex items-center justify-between mx-3">
                                        <label className="text-xs font-black text-[#8b7e6f] uppercase tracking-[0.2em]">
                                            Password
                                        </label>
                                        {isLogin && (
                                            <a href="#" className="text-xs font-black text-[#d32f2f] hover:text-[#b71c1c] transition-colors">
                                                FORGOT?
                                            </a>
                                        )}
                                    </div>
                                    <div className="relative">
                                        <div className="absolute left-6 top-1/2 -translate-y-1/2 text-[#8b7e6f] group-focus-within:text-[#d32f2f] transition-colors duration-300">
                                            <Lock size={28} strokeWidth={2.5} />
                                        </div>
                                        <input
                                            type="password"
                                            name="password"
                                            value={formData.password}
                                            onChange={handleChange}
                                            placeholder="••••••••"
                                            className="form-input !pl-20 !py-6 !text-lg !rounded-2xl !bg-white/40 !border-[#d4c8b8]/80 focus:!bg-white focus:!border-[#d32f2f] focus:!ring-[#d32f2f]/10 text-lg font-bold"
                                            required
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    className="w-full bg-[#3d2e1f] hover:bg-[#2a1f14] text-white font-black text-lg py-6 rounded-xl shadow-xl hover:shadow-2xl hover:-translate-y-1 active:translate-y-0 transition-all duration-500 flex items-center justify-center gap-3 mt-10 group overflow-hidden relative"
                                >
                                    <span className="relative z-10 text-lg">{isLogin ? 'Sign In' : 'Get Started'}</span>
                                    <ArrowRight size={26} strokeWidth={3} className="relative z-10 group-hover:translate-x-2 transition-transform duration-300" />
                                    <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                                </button>
                            </form>

                            <div className="mt-12 pt-10 border-t border-[#d4c8b8] flex items-center justify-center text-base font-bold animate-fade-in-up stagger-4">
                                <span className="text-[#8b7e6f]">
                                    {isLogin ? "DON'T HAVE AN ACCOUNT?" : "ALREADY A MEMBER?"}
                                </span>
                                <button
                                    onClick={toggleMode}
                                    className="ml-4 text-[#d32f2f] hover:text-[#b71c1c] transition-all duration-300 border-b-2 border-[#d32f2f]/30 hover:border-[#d32f2f] font-black hover:scale-105"
                                >
                                    {isLogin ? 'SIGN UP' : 'SIGN IN'}
                                </button>
                            </div>
                        </div>

                        {/* Security Footer - Enhanced */}
                        <div className="mt-8 flex justify-center items-center gap-8 opacity-50 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-500">
                            <div className="flex items-center gap-3">
                                <Lock size={16} className="text-[#8b7e6f]" />
                                <span className="text-[11px] font-black text-[#8b7e6f] uppercase tracking-[0.25em]">Secure System</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <CheckCircle size={16} className="text-[#8b7e6f]" />
                                <span className="text-[11px] font-black text-[#8b7e6f] uppercase tracking-[0.25em]">Verified</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuthPage;
