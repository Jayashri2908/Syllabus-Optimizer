import React from 'react';
import { COPOMappingData } from '../types';
import './Charts.css';

interface COPOHeatmapProps {
  mapping: COPOMappingData & {
    co_averages?: number[];
    po_averages?: number[];
  };
}

const COPOHeatmap: React.FC<COPOHeatmapProps> = ({ mapping }) => {
  if (!mapping || !mapping.matrix) return null;

  const { matrix, co_averages, po_averages } = mapping;
  const numCOs = matrix.length;
  if(numCOs === 0) return null;
  const numPOs = matrix[0].po_scores.length;

  const getIntensityColor = (score: number | string): string => {
    if (score === 0 || score === '-') return 'bg-empty';
    if (typeof score === 'string') return 'bg-empty';
    if (score < 1.5) return 'bg-level-1';
    if (score < 2.5) return 'bg-level-2';
    return 'bg-level-3';
  };

  return (
    <div className="heatmap-container">
      <div className="heatmap-grid" style={{ gridTemplateColumns: `auto repeat(${numPOs}, 1fr) auto` }}>
        {/* Header Row */}
        <div className="heatmap-cell header"></div>
        {Array.from({ length: numPOs }).map((_, i) => (
          <div key={`po-head-${i}`} className="heatmap-cell header">
            PO{i + 1}
          </div>
        ))}
        <div className="heatmap-cell header">Avg</div>

        {/* Matrix Rows */}
        {matrix.map((row, i) => (
          <React.Fragment key={`co-row-${i}`}>
            <div className="heatmap-cell header">CO{i + 1}</div>
            {row.po_scores.map((score: number, j: number) => (
              <div 
                key={`cell-${i}-${j}`} 
                className={`heatmap-cell value ${getIntensityColor(score)}`}
                title={`CO${i+1} ↔ PO${j+1}: ${score}`}
              >
                {score === 0 ? '-' : score.toFixed(1)}
              </div>
            ))}
            <div className="heatmap-cell avg">{co_averages?.[i]?.toFixed(2) || '-'}</div>
          </React.Fragment>
        ))}

        {/* Average Row */}
        <div className="heatmap-cell header">Avg</div>
        {(po_averages || []).map((avg: number, j: number) => (
          <div key={`po-avg-${j}`} className="heatmap-cell avg">
            {avg === 0 ? '-' : avg.toFixed(2)}
          </div>
        ))}
        <div className="heatmap-cell avg grand"></div>
      </div>
      
      <div className="heatmap-legend">
        <span>Correlation:</span>
        <div className="legend-item"><div className="color-box bg-level-1"></div> 1 - Low</div>
        <div className="legend-item"><div className="color-box bg-level-2"></div> 2 - Medium</div>
        <div className="legend-item"><div className="color-box bg-level-3"></div> 3 - High</div>
      </div>
    </div>
  );
};

export default COPOHeatmap;
