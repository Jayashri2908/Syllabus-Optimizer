import React from 'react';

const SkeletonLoader = ({ type = 'text', count = 1, className = '' }: { type?: 'text' | 'card' | 'chart'; count?: number; className?: string }) => {
  const elements = Array.from({ length: count }, (_, i) => i);

  if (type === 'card') {
    return (
      <>
        {elements.map((_, i) => (
          <div key={i} className={`skeleton skeleton-card ${className}`}>
            <div className="skeleton-title"></div>
            <div className="skeleton-text"></div>
            <div className="skeleton-text" style={{width: '70%'}}></div>
          </div>
        ))}
      </>
    );
  }

  if (type === 'chart') {
    return (
      <div className={`skeleton skeleton-chart ${className}`}>
         <div className="skeleton-bar" style={{width: '40%'}}></div>
         <div className="skeleton-bar" style={{width: '80%'}}></div>
         <div className="skeleton-bar" style={{width: '60%'}}></div>
         <div className="skeleton-bar" style={{width: '90%'}}></div>
         <div className="skeleton-bar" style={{width: '30%'}}></div>
      </div>
    );
  }

  // Default text rows
  return (
    <div className={`skeleton-container ${className}`}>
      {elements.map((_, i) => (
        <div key={i} className="skeleton skeleton-text" style={{ width: i % 2 === 0 ? '100%' : '80%' }}></div>
      ))}
    </div>
  );
}

export default SkeletonLoader;
