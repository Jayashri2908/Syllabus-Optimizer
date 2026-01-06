import React from 'react';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import './EmptyState.css';

export const EmptyState = ({
    icon: Icon = FileText,
    title,
    description,
    action,
    actionLabel,
    variant = 'default'
}) => {
    return (
        <div className={`empty-state empty-state-${variant}`}>
            <div className="empty-icon">
                <Icon size={64} strokeWidth={1.5} />
            </div>
            <h3 className="empty-title">{title}</h3>
            {description && <p className="empty-description">{description}</p>}
            {action && (
                <button className="btn btn-primary" onClick={action}>
                    {actionLabel || 'Get Started'}
                </button>
            )}
        </div>
    );
};

export const UploadEmptyState = ({ onUpload }) => (
    <EmptyState
        icon={Upload}
        title="No Syllabus Uploaded"
        description="Upload a PDF syllabus to analyze, optimize, or compare."
        action={onUpload}
        actionLabel="Upload Syllabus"
    />
);

export const NoResultsState = ({ onReset }) => (
    <EmptyState
        icon={AlertCircle}
        title="No Results Found"
        description="Try adjusting your search or filters."
        action={onReset}
        actionLabel="Clear Filters"
        variant="secondary"
    />
);

export default EmptyState;
