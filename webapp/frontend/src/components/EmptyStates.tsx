import React from 'react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action }) => (
  <div className="empty-state" role="status">
    {icon && <div className="empty-state-icon">{icon}</div>}
    <h3>{title}</h3>
    {description && <p>{description}</p>}
    {action && <div className="empty-state-action">{action}</div>}
  </div>
);

export const NoSyllabusSelected: React.FC = () => (
  <EmptyState
    title="No syllabus selected"
    description="Upload a syllabus or generate a new one to get started."
  />
);

export const NoAnalysisResults: React.FC = () => (
  <EmptyState
    title="No analysis results"
    description="Run an analysis to see results here."
  />
);

export const NoGenerateResults: React.FC = () => (
  <EmptyState
    title="No generated syllabus"
    description="Fill in the form and click Generate to create a syllabus."
  />
);
