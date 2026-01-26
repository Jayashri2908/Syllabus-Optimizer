import React from 'react';
import { Info } from 'lucide-react';

/**
 * Professional Tooltip Component
 * @param {Object} props
 * @param {string} props.text - The content to display in the tooltip
 * @param {React.ReactNode} props.children - The element to hover over
 * @param {string} [props.position] - Optional position customization (default: top)
 */
const Tooltip = ({ text, children, position = 'top' }) => {
    return (
        <div className="tooltip-container">
            {children}
            <div className={`tooltip-content tooltip-${position}`}>
                {text}
            </div>
        </div>
    );
};

export const InfoTooltip = ({ text }) => (
    <Tooltip text={text}>
        <Info size={16} className="text-subtle hover:text-brand transition-colors cursor-help" />
    </Tooltip>
);

export default Tooltip;
