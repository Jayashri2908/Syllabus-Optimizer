import React from 'react';

/**
 * SCDOLogo - Displays the brand logo text only.
 * Removed the 'S' icon as per request.
 */
const SCDOLogo = ({ size = "md", className = "", showText = true, isCentered = false, theme = "light" }) => {

    // Text size mapping
    const textSizes = {
        sm: "text-2xl",
        md: "text-4xl",
        lg: "text-6xl",
        xl: "text-7xl"
    };

    const subTextSizes = {
        sm: "hidden",
        md: "text-[10px]",
        lg: "text-xs",
        xl: "text-sm"
    };

    return (
        <div className={`flex ${isCentered ? 'flex-col items-center text-center' : 'items-center'} gap-4 group cursor-pointer transition-all duration-500 ${className}`}>

            {/* --- BRAND TEXT --- */}
            {showText && (
                <div className="flex flex-col select-none">
                    <h1 className={`${textSizes[size]} font-black tracking-tight flex items-baseline leading-none ${isCentered ? 'justify-center' : ''}`}>
                        <span className={`${theme === 'dark' ? 'text-white' : 'text-[var(--primary)]'} group-hover:text-[#d32f2f] transition-colors duration-500`}>SCD</span>
                        <span className="text-transparent bg-clip-text bg-gradient-to-br from-[var(--primary)] to-[var(--brand)] drop-shadow-sm">O</span>
                        <span className="h-2 w-2 bg-[var(--brand)] rounded-full ml-1 animate-bounce group-hover:bg-orange-400 transition-colors duration-700"></span>
                    </h1>

                    <span className={`${subTextSizes[size]} font-bold tracking-[0.3em] uppercase ${theme === 'dark' ? 'text-[#8b7e6f]' : 'text-[#8b7e6f]'} mt-1 transition-all duration-500 group-hover:text-[#5c5446] group-hover:tracking-[0.4em]`}>
                        SyllabusOptimizer
                    </span>
                </div>
            )}
        </div>
    );
};

export default SCDOLogo;
