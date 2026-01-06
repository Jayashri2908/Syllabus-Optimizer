import React from 'react';
import './LoadingSpinner.css';

export const LoadingSpinner = ({ message = 'Loading...', size = 'md' }) => {
    return (
        <div className="loading-container">
            <div className={`spinner spinner-${size}`}></div>
            {message && <p className="loading-message">{message}</p>}
        </div>
    );
};

export const LoadingOverlay = ({ message, progress }) => {
    return (
        <div className="loading-overlay">
            <div className="loading-content">
                <div className="spinner spinner-lg"></div>
                <p className="loading-message">{message}</p>
                {progress !== undefined && (
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                    </div>
                )}
            </div>
        </div>
    );
};

export const SkeletonLoader = ({ type = 'text', count = 1 }) => {
    return (
        <div className="skeleton-container">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className={`skeleton skeleton-${type}`}></div>
            ))}
        </div>
    );
};

export default LoadingSpinner;
