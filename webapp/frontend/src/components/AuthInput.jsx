import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

const AuthInput = ({
    label,
    name,
    type = 'text',
    value,
    onChange,
    placeholder,
    error,
    icon: Icon,
    required = false,
    className
}) => {
    const [isFocused, setIsFocused] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [hasValue, setHasValue] = useState(false);

    const inputType = type === 'password' && showPassword ? 'text' : type;
    const isPassword = type === 'password';

    const handleChange = (e) => {
        setHasValue(e.target.value.length > 0);
        onChange(e);
    };

    return (
        <div className={twMerge("space-y-2", className)}>
            <div className="flex justify-between items-baseline px-1">
                <label
                    htmlFor={name}
                    className={clsx(
                        "text-sm font-semibold transition-colors duration-200 tracking-wide",
                        error ? "text-red-500" : isFocused ? "text-[var(--brand)]" : "text-slate-600"
                    )}
                >
                    {label} {required && <span className="text-[var(--brand)]/70">*</span>}
                </label>
            </div>

            <div className="relative group">
                {/* Focus Ring Animation - Softer & More Premium */}
                <motion.div
                    initial={false}
                    animate={{
                        scale: isFocused ? 1.02 : 1,
                        borderColor: error
                            ? '#fee2e2'
                            : isFocused
                                ? '#ffedd5' // brand-orange-100
                                : 'transparent',
                        backgroundColor: error
                            ? '#fef2f2'
                            : isFocused
                                ? '#fff'
                                : '#f8fafc', // slate-50
                        boxShadow: error
                            ? '0 0 0 4px rgba(239, 68, 68, 0.05)'
                            : isFocused
                                ? '0 10px 30px -5px rgba(249, 115, 22, 0.15)' // Brand orange glow with depth
                                : 'none'
                    }}
                    transition={{ duration: 0.2, ease: "easeOut" }}
                    className={clsx(
                        "absolute inset-0 rounded-2xl border transition-all duration-300",
                        !isFocused && !error ? "border-slate-200 hover:border-slate-300 hover:bg-white" : ""
                    )}
                />

                <div className="relative flex items-center">
                    {/* Leading Icon */}
                    {Icon && (
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 z-20 pointer-events-none">
                            <Icon
                                size={20}
                                strokeWidth={2}
                                className={clsx(
                                    "transition-colors duration-300",
                                    error ? "text-red-400" : isFocused ? "text-[var(--brand)]" : "text-slate-400"
                                )}
                            />
                        </div>
                    )}

                    <input
                        id={name}
                        name={name}
                        type={inputType}
                        value={value}
                        onChange={handleChange}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        placeholder={placeholder}
                        className={clsx(
                            "w-full bg-transparent py-4 outline-none text-slate-700 font-medium placeholder:text-slate-400 relative z-10",
                            "text-base transition-all duration-200",
                            Icon ? "pl-12" : "pl-5", // Adjust padding for icon
                            isPassword ? "pr-12" : "pr-5"
                        )}
                    />

                    {isPassword && (
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:text-[var(--brand)] outline-none transition-colors z-20 p-1 rounded-md hover:bg-slate-100"
                        >
                            {showPassword ? <EyeOff size={18} strokeWidth={2} /> : <Eye size={18} strokeWidth={2} />}
                        </button>
                    )}

                    {error && !isPassword && (
                        <motion.div
                            initial={{ scale: 0, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="absolute right-4 top-1/2 -translate-y-1/2 text-red-400 pointer-events-none z-10"
                        >
                            <AlertCircle size={20} strokeWidth={2} />
                        </motion.div>
                    )}
                </div>
            </div>

            <AnimatePresence>
                {error && (
                    <motion.p
                        initial={{ opacity: 0, y: -5, height: 0 }}
                        animate={{ opacity: 1, y: 0, height: 'auto' }}
                        exit={{ opacity: 0, y: -5, height: 0 }}
                        className="text-xs font-semibold text-red-500 pl-1 flex items-center gap-1"
                    >
                        <span>•</span> {error}
                    </motion.p>
                )}
            </AnimatePresence>
        </div>
    );
};

export default AuthInput;
