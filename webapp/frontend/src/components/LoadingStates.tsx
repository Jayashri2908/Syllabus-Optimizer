import React from 'react';

export const PageLoader: React.FC = () => (
  <div className="page-loader" role="status" aria-label="Loading">
    <div className="spinner" />
    <p>Loading...</p>
  </div>
);

export const CardLoader: React.FC = () => (
  <div className="card-loader" role="status" aria-label="Loading content">
    <div className="skeleton skeleton-title" />
    <div className="skeleton skeleton-text" />
    <div className="skeleton skeleton-text" />
    <div className="skeleton skeleton-text short" />
  </div>
);

export const ButtonLoader: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => (
  <button disabled className="btn-loading" aria-busy="true">
    <span className="spinner-small" />
    {text}
  </button>
);
