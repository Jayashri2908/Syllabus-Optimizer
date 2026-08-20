import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Menu, X, LayoutDashboard, FileText, Zap, BarChart2 } from 'lucide-react';
import SCDOLogo from './SCDOLogo';

const Navbar = () => {
    const { user, logout } = useAuth();
    const location = useLocation();
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    // Scroll detection — stronger shadow + more opaque background when scrolled
    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Close mobile menu on route change
    useEffect(() => {
        setIsMobileMenuOpen(false);
    }, [location.pathname]);

    const isActive = (path) => location.pathname === path;

    const navLinks = [
        { path: '/', label: 'Home', icon: LayoutDashboard },
        { path: '/analyze', label: 'Analyze', icon: BarChart2 },
        { path: '/generate', label: 'Generate', icon: FileText },
        { path: '/optimize', label: 'Optimize', icon: Zap },
    ];

    return (
        <nav
            className={`sticky top-4 mx-4 z-50 mb-6 transition-all duration-500 border rounded-2xl overflow-hidden ${
                isScrolled
                    ? 'bg-[#faf7f2]/95 backdrop-blur-xl shadow-xl border-[#d4c8b8]/40'
                    : 'bg-[#faf7f2]/80 backdrop-blur-xl shadow-sm border-[#d4c8b8]/30'
            }`}
            style={{ position: 'sticky' }}
        >
            {/* Gradient bottom border — indigo to brand, 1px */}
            <div
                className="absolute bottom-0 left-0 right-0 h-[1px] opacity-60"
                style={{
                    background: 'linear-gradient(90deg, #3d2e1f 0%, #d32f2f 50%, #3d2e1f 100%)',
                }}
            />

            <div className="container px-6 md:px-8 relative">
                <div className="flex items-center h-20">
                    {/* Logo + Tagline */}
                    <div className="flex items-center gap-3 shrink-0">
                        <Link to="/" className="hover:no-underline">
                            <SCDOLogo size="md" />
                        </Link>
                        {/* Dot separator + tagline */}
                        <span className="hidden lg:flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#8b7e6f]" />
                            <span className="text-xs font-medium tracking-wide text-[#8b7e6f] uppercase">
                                Curriculum Optimizer
                            </span>
                        </span>
                    </div>

                    {/* Desktop Navigation — centered */}
                    <div className="hidden md:flex items-center justify-center flex-1">
                        <div className="flex items-center gap-1 bg-[#efe8de]/40 rounded-2xl p-1.5 border border-[#d4c8b8]/40">
                            {navLinks.map((link) => {
                                const Icon = link.icon;
                                const active = isActive(link.path);
                                return (
                                    <Link
                                        key={link.path}
                                        to={link.path}
                                        className={`group relative flex items-center gap-2.5 px-5 h-11 rounded-xl text-sm font-semibold transition-all duration-300 ${
                                            active
                                                ? 'text-[var(--brand)]'
                                                : 'text-[#5c5446] hover:text-[var(--brand)]'
                                        }`}
                                    >
                                        <Icon
                                            size={18}
                                            className={`transition-all duration-300 ${
                                                active
                                                    ? 'text-[var(--brand)]'
                                                    : 'text-[#8b7e6f] group-hover:text-[var(--brand)] group-hover:scale-110'
                                            }`}
                                        />
                                        <span className="tracking-tight">{link.label}</span>
                                        {/* Animated underline indicator */}
                                        <span
                                            className={`absolute bottom-1 left-1/2 -translate-x-1/2 h-[2px] rounded-full transition-all duration-300 ease-out ${
                                                active
                                                    ? 'w-6 bg-[var(--brand)]'
                                                    : 'w-0 bg-[var(--brand)] group-hover:w-4'
                                            }`}
                                        />
                                    </Link>
                                );
                            })}
                        </div>
                    </div>

                    {/* Right Section — Auth */}
                    <div className="flex items-center gap-4 ml-auto shrink-0">
                        {user ? (
                            <div className="flex items-center gap-3">
                                <div className="hidden sm:flex items-center gap-3 px-4 h-12 bg-[#efe8de]/40 rounded-xl border border-[#d4c8b8]/40">
                                    <div className="w-9 h-9 rounded-full bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                                        <User size={18} />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[9px] uppercase tracking-[0.15em] font-bold text-[#8b7e6f]">
                                            Admin
                                        </span>
                                        <span className="text-sm font-bold text-[#3d2e1f]">{user.username}</span>
                                    </div>
                                </div>
                                <button
                                    onClick={logout}
                                    className="h-12 w-12 rounded-xl bg-[#efe8de]/40 text-[#5c5446] hover:text-rose-500 hover:bg-rose-50 border border-[#d4c8b8]/40 hover:border-rose-200 transition-all duration-300 hover:scale-110 active:scale-95 flex items-center justify-center group"
                                    title="Sign Out"
                                >
                                    <LogOut size={19} className="group-hover:-translate-x-0.5 transition-transform duration-300" />
                                </button>
                            </div>
                        ) : (
                            <Link
                                to="/auth"
                                className="btn-primary relative overflow-hidden h-12 px-8 text-sm font-bold uppercase tracking-wider rounded-xl flex items-center gap-2 transition-all duration-300 hover:scale-105 active:scale-95"
                                style={{
                                    animation: 'subtlePulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                                }}
                            >
                                Get Started
                            </Link>
                        )}

                        {/* Mobile hamburger */}
                        <button
                            className="md:hidden flex items-center justify-center h-12 w-12 rounded-xl bg-[#efe8de]/40 border border-[#d4c8b8]/40 text-[#5c5446] hover:text-[var(--brand)] hover:bg-brand/5 transition-all duration-300"
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
                        >
                            {isMobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu Dropdown */}
            <div
                className={`md:hidden overflow-hidden transition-all duration-500 ease-out ${
                    isMobileMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                }`}
            >
                <div className="px-4 pb-5 pt-2">
                    <div className="bg-[#faf7f2]/70 backdrop-blur-xl rounded-2xl border border-[#d4c8b8]/30 p-3 shadow-lg">
                        {navLinks.map((link) => {
                            const Icon = link.icon;
                            const active = isActive(link.path);
                            return (
                                <Link
                                    key={link.path}
                                    to={link.path}
                                    className={`group flex items-center gap-3 px-4 py-3.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                                        active
                                            ? 'bg-brand/10 text-[var(--brand)]'
                                            : 'text-[#5c5446] hover:text-[var(--brand)] hover:bg-brand/5'
                                    }`}
                                >
                                    <Icon
                                        size={20}
                                        className={`transition-all duration-300 ${
                                            active
                                                ? 'text-[var(--brand)]'
                                                : 'text-[#8b7e6f] group-hover:text-[var(--brand)]'
                                        }`}
                                    />
                                    <span className="tracking-tight">{link.label}</span>
                                    {/* Mobile active indicator */}
                                    {active && (
                                        <span className="ml-auto w-2 h-2 rounded-full bg-[var(--brand)]" />
                                    )}
                                </Link>
                            );
                        })}

                        {/* Mobile auth section */}
                        <div className="mt-3 pt-3 border-t border-[#d4c8b8]">
                            {user ? (
                                <div className="flex items-center gap-3 px-4 py-3">
                                    <div className="w-9 h-9 rounded-full bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                                        <User size={18} />
                                    </div>
                                    <div className="flex flex-col flex-1">
                                        <span className="text-sm font-bold text-[#3d2e1f]">{user.username}</span>
                                        <span className="text-[9px] uppercase tracking-[0.15em] font-bold text-[#8b7e6f]">Admin</span>
                                    </div>
                                    <button
                                        onClick={logout}
                                        className="h-10 w-10 rounded-xl bg-[#efe8de] text-[#5c5446] hover:text-rose-500 hover:bg-rose-50 border border-[#d4c8b8] hover:border-rose-200 transition-all duration-300 flex items-center justify-center"
                                        title="Sign Out"
                                    >
                                        <LogOut size={18} />
                                    </button>
                                </div>
                            ) : (
                                <Link
                                    to="/auth"
                                    className="btn-primary w-full h-12 text-sm font-bold uppercase tracking-wider rounded-xl flex items-center justify-center gap-2"
                                >
                                    Get Started
                                </Link>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
