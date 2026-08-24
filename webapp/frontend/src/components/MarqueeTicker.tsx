import React from 'react';
import './MarqueeTicker.css';

const MarqueeTicker = () => {
  const items = [
    "✦ NBA Accredited",
    "✦ NEP 2020 Aligned",
    "✦ Powered by IBM Granite",
    "✦ ABET Standardized",
    "✦ RAG Vector Grounding",
    "✦ Bloom's Balanced",
    "✦ Institutional Grade"
  ];

  return (
    <div className="marquee-container">
      <div className="marquee-content">
        {/* Render multiple sets to ensure seamless infinite looping */}
        {[...Array(3)].map((_, i) => (
          <div key={i} className="marquee-group">
            {items.map((item, index) => (
              <span key={index} className="marquee-item">{item}</span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarqueeTicker;
