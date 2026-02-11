import React from 'react';
import { motion } from 'framer-motion';
import { Quote } from 'lucide-react';

const TestimonialCard = ({ quote, author, role, image }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="relative hidden xl:block mt-auto"
        >
            <div className="relative bg-white/10 backdrop-blur-xl border border-white/20 p-6 rounded-2xl shadow-2xl overflow-hidden">
                {/* Decorative sheen */}
                <div className="absolute inset-0 bg-gradient-to-tr from-white/10 to-transparent opacity-50 pointer-events-none"></div>

                <div className="relative z-10 space-y-4">
                    <div className="inline-flex p-2 rounded-lg bg-indigo-500/20 text-indigo-300 mb-2">
                        <Quote size={20} fill="currentColor" className="opacity-80" />
                    </div>

                    <p className="text-lg text-slate-200 font-light leading-relaxed italic">
                        "{quote}"
                    </p>

                    <div className="flex items-center gap-4 pt-2">
                        {image ? (
                            <img src={image} alt={author} className="w-10 h-10 rounded-full object-cover border-2 border-white/30" />
                        ) : (
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-cyan-400 flex items-center justify-center text-white font-bold text-sm shadow-inner">
                                {author.charAt(0)}
                            </div>
                        )}
                        <div>
                            <div className="text-white font-semibold">{author}</div>
                            <div className="text-slate-400 text-xs uppercase tracking-wider">{role}</div>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default TestimonialCard;
