import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowRight, Eye, EyeOff, Mail, Lock, User, Sparkles, CheckCircle2, GraduationCap, BookOpen, Users } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AuthPage = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        email: ''
    });
    const [errors, setErrors] = useState({});
    const [generalError, setGeneralError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [focusedField, setFocusedField] = useState(null);
    const [showPassword, setShowPassword] = useState(false);

    const { login, signup, user } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        if (user) {
            const from = location.state?.from?.pathname || '/';
            navigate(from, { replace: true });
        }
    }, [user, navigate, location]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }
        setGeneralError(null);
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.username.trim()) newErrors.username = "Username is required";
        if (!formData.password) newErrors.password = "Password is required";
        if (!isLogin) {
            if (!formData.email.trim()) newErrors.email = "Email is required";
            else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = "Email is invalid";
            if (formData.password.length < 8) newErrors.password = "Password must be at least 8 characters";
        }
        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setGeneralError(null);
        const newErrors = validate();
        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }
        setLoading(true);
        try {
            if (isLogin) {
                await login({ identifier: formData.username, password: formData.password });
            } else {
                await signup({ username: formData.username, email: formData.email, password: formData.password });
            }
        } catch (err) {
            setGeneralError(err.message || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    const toggleMode = () => {
        setIsLogin(!isLogin);
        setGeneralError(null);
        setErrors({});
        setFormData({ username: '', password: '', email: '' });
    };

    const features = [
        { icon: GraduationCap, text: "AI-Powered Curriculum Design" },
        { icon: BookOpen, text: "Smart Syllabus Optimization" },
        { icon: Users, text: "Trusted by 10,000+ Educators" }
    ];

    return (
        <div className="min-h-screen w-full flex font-sans overflow-hidden">

            {/* LEFT PANEL - Animated Gradient Hero */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1 }}
                className="hidden lg:flex w-[50%] relative flex-col justify-between p-12 overflow-hidden"
                style={{
                    background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4c1d95 70%, #7c3aed 100%)'
                }}
            >
                {/* Animated Mesh Gradient Overlay */}
                <div className="absolute inset-0 opacity-30">
                    <div
                        className="absolute inset-0"
                        style={{
                            background: 'radial-gradient(circle at 20% 80%, rgba(249, 115, 22, 0.4) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.4) 0%, transparent 50%), radial-gradient(circle at 40% 40%, rgba(236, 72, 153, 0.3) 0%, transparent 40%)',
                            animation: 'pulse 8s ease-in-out infinite'
                        }}
                    />
                </div>

                {/* Floating Particles Effect */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    {[...Array(6)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="absolute w-2 h-2 bg-white/20 rounded-full"
                            initial={{
                                x: Math.random() * 100 + '%',
                                y: '100%',
                                opacity: 0.3
                            }}
                            animate={{
                                y: '-10%',
                                opacity: [0.3, 0.8, 0.3]
                            }}
                            transition={{
                                duration: 8 + Math.random() * 4,
                                repeat: Infinity,
                                delay: i * 1.5,
                                ease: 'linear'
                            }}
                        />
                    ))}
                </div>

                {/* Top Gradient Fade */}
                <div className="absolute top-0 left-0 w-full h-40 bg-gradient-to-b from-[#1e1b4b]/80 to-transparent z-10" />
                <div className="absolute bottom-0 left-0 w-full h-40 bg-gradient-to-t from-[#1e1b4b]/80 to-transparent z-10" />

                {/* Logo */}
                <div className="relative z-20">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center shadow-lg shadow-orange-500/30">
                            <span className="text-white font-black text-lg">S</span>
                        </div>
                        <div>
                            <span className="text-white font-bold text-xl tracking-tight">SCDO</span>
                            <span className="text-orange-400 font-black text-xl">.</span>
                        </div>
                    </div>
                </div>

                {/* Main Content */}
                <div className="relative z-20 flex flex-col justify-center flex-1 py-12">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3, duration: 0.8 }}
                        className="space-y-8"
                    >
                        {/* Badge */}
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 backdrop-blur-sm">
                            <Sparkles size={14} className="text-orange-400" />
                            <span className="text-orange-200 text-xs font-semibold uppercase tracking-wider">
                                AI-Powered Education
                            </span>
                        </div>

                        {/* Headline */}
                        <h1 className="text-5xl xl:text-6xl font-black text-white leading-[1.1] tracking-tight">
                            Design Better
                            <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-pink-400 to-violet-400">
                                Curricula, Faster.
                            </span>
                        </h1>

                        {/* Subheadline */}
                        <p className="text-lg text-indigo-200/80 leading-relaxed max-w-md">
                            Join thousands of educators transforming their teaching with AI-powered syllabus optimization.
                        </p>

                        {/* Features */}
                        <div className="space-y-4 pt-4">
                            {features.map((feature, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.5 + i * 0.1 }}
                                    className="flex items-center gap-3"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                                        <feature.icon size={16} className="text-orange-400" />
                                    </div>
                                    <span className="text-white/90 text-sm font-medium">{feature.text}</span>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                </div>

                {/* Footer */}
                <div className="relative z-20 text-indigo-300/50 text-xs font-medium">
                    © 2025 SCDO Inc. • Empowering Educators Worldwide
                </div>
            </motion.div>

            {/* RIGHT PANEL - Form */}
            <div className="w-full lg:w-[50%] relative flex items-center justify-center p-6 md:p-12 bg-slate-50">

                {/* Subtle Pattern Background */}
                <div
                    className="absolute inset-0 opacity-[0.03]"
                    style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
                    }}
                />

                {/* Form Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="w-full max-w-[440px] relative z-10"
                >
                    {/* Mobile Logo */}
                    <div className="lg:hidden flex justify-center mb-8">
                        <div className="flex items-center gap-2">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center">
                                <span className="text-white font-black text-lg">S</span>
                            </div>
                            <span className="text-slate-800 font-bold text-xl">SCDO<span className="text-orange-500">.</span></span>
                        </div>
                    </div>

                    {/* Card Container */}
                    <div className="bg-white rounded-3xl shadow-2xl shadow-slate-200/50 p-8 md:p-10 border border-slate-100">

                        {/* Header */}
                        <div className="text-center mb-8">
                            <motion.h2
                                key={isLogin ? "login" : "signup"}
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="text-2xl md:text-3xl font-bold text-slate-900 mb-2"
                            >
                                {isLogin ? 'Welcome back' : 'Create your account'}
                            </motion.h2>
                            <p className="text-slate-500 text-sm">
                                {isLogin
                                    ? 'Enter your credentials to access your account'
                                    : 'Start your journey with SCDO today'}
                            </p>
                        </div>


                        {/* Error Message */}
                        <AnimatePresence>
                            {generalError && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="mb-4 p-3 rounded-xl bg-red-50 border border-red-100 flex items-center gap-2"
                                >
                                    <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                                    <span className="text-red-600 text-sm font-medium">{generalError}</span>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Form */}
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={isLogin ? "login-form" : "signup-form"}
                                    initial={{ opacity: 0, x: 10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -10 }}
                                    transition={{ duration: 0.2 }}
                                    className="space-y-4"
                                >
                                    {/* Username/Email Field */}
                                    <div className="mb-5">
                                        <label className="block text-sm font-semibold text-slate-700 mb-2">
                                            {isLogin ? 'Email or Username' : 'Username'}
                                        </label>
                                        <div className="relative">
                                            <input
                                                name="username"
                                                type="text"
                                                value={formData.username}
                                                onChange={handleChange}
                                                onFocus={() => setFocusedField('username')}
                                                onBlur={() => setFocusedField(null)}
                                                placeholder={isLogin ? "Enter your email or username" : "Choose a username"}
                                                className={`w-full px-4 py-3.5 rounded-xl border-2 bg-slate-50/50 text-slate-900 placeholder:text-slate-400 text-sm font-medium transition-all duration-200 outline-none ${errors.username
                                                    ? 'border-red-300 focus:border-red-400 focus:bg-red-50/30'
                                                    : 'border-slate-200 focus:border-orange-400 focus:bg-white focus:shadow-lg focus:shadow-orange-500/10'
                                                    }`}
                                            />
                                        </div>
                                        {errors.username && (
                                            <p className="text-xs text-red-500 font-medium mt-1">{errors.username}</p>
                                        )}
                                    </div>

                                    {/* Email Field (Signup only) */}
                                    {!isLogin && (
                                        <div className="mb-5">
                                            <label className="block text-sm font-semibold text-slate-700 mb-2">Email Address</label>
                                            <div className="relative">
                                                <input
                                                    name="email"
                                                    type="email"
                                                    value={formData.email}
                                                    onChange={handleChange}
                                                    onFocus={() => setFocusedField('email')}
                                                    onBlur={() => setFocusedField(null)}
                                                    placeholder="you@institution.edu"
                                                    className={`w-full px-4 py-3.5 rounded-xl border-2 bg-slate-50/50 text-slate-900 placeholder:text-slate-400 text-sm font-medium transition-all duration-200 outline-none ${errors.email
                                                        ? 'border-red-300 focus:border-red-400 focus:bg-red-50/30'
                                                        : 'border-slate-200 focus:border-orange-400 focus:bg-white focus:shadow-lg focus:shadow-orange-500/10'
                                                        }`}
                                                />
                                            </div>
                                            {errors.email && (
                                                <p className="text-xs text-red-500 font-medium mt-1">{errors.email}</p>
                                            )}
                                        </div>
                                    )}

                                    {/* Password Field */}
                                    <div className="mb-5">
                                        <div className="flex justify-between items-center mb-2">
                                            <label className="block text-sm font-semibold text-slate-700">Password</label>
                                            {isLogin && (
                                                <button type="button" className="text-xs font-semibold text-orange-500 hover:text-orange-600 transition-colors">
                                                    Forgot password?
                                                </button>
                                            )}
                                        </div>
                                        <div className="relative">
                                            <input
                                                name="password"
                                                type={showPassword ? 'text' : 'password'}
                                                value={formData.password}
                                                onChange={handleChange}
                                                onFocus={() => setFocusedField('password')}
                                                onBlur={() => setFocusedField(null)}
                                                placeholder="••••••••"
                                                className={`w-full px-4 pr-12 py-3.5 rounded-xl border-2 bg-slate-50/50 text-slate-900 placeholder:text-slate-400 text-sm font-medium transition-all duration-200 outline-none ${errors.password
                                                    ? 'border-red-300 focus:border-red-400 focus:bg-red-50/30'
                                                    : 'border-slate-200 focus:border-orange-400 focus:bg-white focus:shadow-lg focus:shadow-orange-500/10'
                                                    }`}
                                            />
                                            <button
                                                type="button"
                                                onClick={() => setShowPassword(!showPassword)}
                                                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                                            >
                                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                            </button>
                                        </div>
                                        {errors.password && (
                                            <p className="text-xs text-red-500 font-medium mt-1">{errors.password}</p>
                                        )}
                                    </div>
                                </motion.div>
                            </AnimatePresence>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full mt-6 py-4 px-6 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-bold text-sm shadow-lg shadow-orange-500/30 hover:shadow-orange-500/40 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 flex items-center justify-center gap-2 group disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                <span>{loading ? 'Please wait...' : (isLogin ? 'Sign in' : 'Create account')}</span>
                                {!loading && <ArrowRight size={18} className="group-hover:translate-x-0.5 transition-transform" />}
                            </button>
                        </form>

                        {/* Toggle Mode */}
                        <div className="mt-8 pt-6 border-t border-slate-100 text-center">
                            <p className="text-slate-500 text-sm">
                                {isLogin ? "Don't have an account?" : "Already have an account?"}
                                <button
                                    onClick={toggleMode}
                                    className="ml-2 font-bold text-orange-500 hover:text-orange-600 transition-colors"
                                >
                                    {isLogin ? 'Sign up free' : 'Sign in'}
                                </button>
                            </p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default AuthPage;
