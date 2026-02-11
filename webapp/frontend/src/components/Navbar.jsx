import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Menu, X, LayoutDashboard, FileText, Zap } from 'lucide-react';
import SCDOLogo from './SCDOLogo';

const Navbar = () => {
    const { user, logout } = useAuth();
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    const navLinks = [
        { path: '/', label: 'Home', icon: LayoutDashboard },
        { path: '/analyze', label: 'Analyze', icon: Menu },
        { path: '/generate', label: 'Generate', icon: FileText },
        { path: '/optimize', label: 'Optimize', icon: Zap },
    ];

    return (
        <nav className="glass-panel sticky top-4 mx-4 rounded-2xl z-50 mb-6 shadow-xl transition-all duration-300 border border-white/20">
            <div className="container px-8 relative h-22">
                <div className="flex items-center h-full py-2">
                    {/* Logo - Pinned Left */}
                    <div className="flex-1 flex justify-start">
                        <Link to="/" className="hover:no-underline">
                            <SCDOLogo size="md" />
                        </Link>
                    </div>


                    {/* Navigation Hub - Perfectly Centered */}
                    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 hidden md:block">
                        <div className="flex items-center gap-2 bg-surface/40 rounded-2xl p-2 border border-border/40 shadow-inner backdrop-blur-md">

                            {navLinks.map((link) => {
                                const Icon = link.icon;
                                return (
                                    <Link
                                        key={link.path}
                                        to={link.path}
                                        className={`group flex items-center gap-3 px-6 h-12 rounded-xl text-lg font-black transition-all ${isActive(link.path)
                                            ? 'bg-[#1e1b4b] text-white shadow-xl scale-105'
                                            : 'text-secondary hover:text-brand hover:bg-white hover:-translate-y-1 hover:shadow-md'
                                            }`}
                                    >
                                        <div className={`p-1.5 rounded-lg transition-all duration-300 ${isActive(link.path) ? 'bg-white/20 text-white' : 'bg-zinc-100 text-slate-500 group-hover:bg-brand/10 group-hover:text-brand group-hover:rotate-12'}`}>
                                            <Icon size={20} />
                                        </div>
                                        <span className="tracking-tight">{link.label}</span>
                                    </Link>
                                );
                            })}
                        </div>
                    </div>

                    {/* Right Section (Auth Hub) - Pinned Right */}
                    <div className="flex items-center gap-6 ml-auto z-10">
                        {user ? (
                            <div className="flex items-center gap-5">
                                <div className="flex items-center gap-4 px-5 h-14 bg-surface/40 rounded-2xl border border-border/30">
                                    <div className="w-10 h-10 rounded-full bg-brand/10 border border-brand/20 flex items-center justify-center text-brand shadow-inner">
                                        <User size={20} />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[10px] uppercase tracking-widest font-black text-tertiary opacity-60">Verified Admin</span>
                                        <span className="text-base font-black text-secondary">{user.username}</span>
                                    </div>
                                </div>
                                <button
                                    onClick={logout}
                                    className="h-14 w-14 rounded-2xl bg-surface/40 text-secondary hover:text-error hover:bg-error-bg border border-border/40 hover:border-error/20 transition-all hover:scale-110 active:scale-95 shadow-sm flex items-center justify-center group"
                                    title="Sign Out"
                                >
                                    <LogOut size={22} className="group-hover:-translate-x-1 transition-transform" />
                                </button>
                            </div>
                        ) : (
                            <Link to="/auth" className="btn btn-primary h-14 px-10 text-base font-black uppercase tracking-widest rounded-2xl shadow-[0_10px_25px_-5px_rgba(249,115,22,0.4)] hover:shadow-[0_15px_30px_-5px_rgba(249,115,22,0.5)] hover:scale-105 active:scale-95 transition-all">
                                Sign In
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
