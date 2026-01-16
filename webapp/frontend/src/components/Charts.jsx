import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

// Colors for Bloom's taxonomy levels
const BLOOM_COLORS = {
    remember: '#3b82f6',
    understand: '#60a5fa',
    apply: '#10b981',
    analyze: '#f59e0b',
    evaluate: '#ef4444',
    create: '#8b5cf6',
};

export const BloomDistributionChart = ({ bloomAnalysis }) => {
    console.log('BloomDistributionChart received:', bloomAnalysis);

    if (!bloomAnalysis) {
        console.log('No bloom analysis data');
        return null;
    }

    // Handle the actual data structure from optimization
    let data = [];

    if (bloomAnalysis.distribution) {
        // Has distribution object
        data = Object.entries(bloomAnalysis.distribution).map(([level, count]) => ({
            name: level.charAt(0).toUpperCase() + level.slice(1),
            value: count,
            percentage: bloomAnalysis.percentages?.[level] || 0,
        }));
    } else if (bloomAnalysis.comparison) {
        // Has comparison object (current structure)
        data = Object.entries(bloomAnalysis.comparison).map(([level, info]) => ({
            name: level.charAt(0).toUpperCase() + level.slice(1),
            value: Math.round(info.current || 0),
            percentage: info.current || 0,
        }));
    }

    // Filter out zero values to prevent cluttered chart
    data = data.filter(item => item.value > 0 || item.percentage > 0);

    if (data.length === 0) {
        console.log('No valid data to display');
        return null;
    }

    console.log('Chart data:', data);

    // Custom label renderer that only shows for significant slices
    const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percentage, name }) => {
        // Only show label if percentage is significant (> 5%)
        if (percentage < 5) return null;

        const RADIAN = Math.PI / 180;
        const radius = outerRadius + 30;
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);

        return (
            <text
                x={x}
                y={y}
                fill="#333"
                textAnchor={x > cx ? 'start' : 'end'}
                dominantBaseline="central"
                fontSize={12}
            >
                {`${name}: ${percentage.toFixed(0)}%`}
            </text>
        );
    };

    return (
        <div className="chart-container">
            <h3 className="chart-title">Bloom's Taxonomy Distribution</h3>
            <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="45%"
                        labelLine={true}
                        label={renderCustomLabel}
                        outerRadius={90}
                        fill="#8884d8"
                        dataKey="percentage"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={BLOOM_COLORS[entry.name.toLowerCase()] || '#999'} />
                        ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value.toFixed(1)}%`]} />
                    <Legend
                        layout="horizontal"
                        align="center"
                        verticalAlign="bottom"
                        wrapperStyle={{ paddingTop: '20px' }}
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export const BloomBalanceChart = ({ bloomAnalysis }) => {
    console.log('BloomBalanceChart received:', bloomAnalysis);

    if (!bloomAnalysis) return null;

    let data = [];

    if (bloomAnalysis.comparison) {
        // Use comparison data (current structure)
        data = Object.entries(bloomAnalysis.comparison).map(([level, info]) => ({
            level: level.charAt(0).toUpperCase() + level.slice(1),
            actual: info.current || 0,
            recommended: ((info.recommended_min || 0) + (info.recommended_max || 0)) / 2,
        }));
    } else if (bloomAnalysis.distribution) {
        // Fallback to distribution
        data = Object.entries(bloomAnalysis.distribution).map(([level, count]) => ({
            level: level.charAt(0).toUpperCase() + level.slice(1),
            actual: bloomAnalysis.percentages?.[level] || 0,
            recommended: getRecommendedPercentage(level),
        }));
    }

    if (data.length === 0) return null;

    console.log('Balance chart data:', data);

    return (
        <div className="chart-container">
            <h3 className="chart-title">Bloom's Level Balance</h3>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="level" />
                    <YAxis label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="actual" fill="#3b82f6" name="Current" />
                    <Bar dataKey="recommended" fill="#10b981" name="Recommended" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

// Helper function for recommended percentages
function getRecommendedPercentage(level) {
    const recommended = {
        remember: 10,
        understand: 20,
        apply: 30,
        analyze: 20,
        evaluate: 15,
        create: 5,
    };
    return recommended[level.toLowerCase()] || 0;
}

export const COPOHeatmap = ({ mapping }) => {
    console.log('COPOHeatmap received:', mapping);

    if (!mapping) return null;

    // Convert mapping to heatmap data
    const cos = Object.keys(mapping);
    const pos = [...new Set(Object.values(mapping).flatMap(m => Object.keys(m)))].sort();

    const data = cos.map(co => ({
        co,
        ...pos.reduce((acc, po) => ({
            ...acc,
            [po]: mapping[co]?.[po] || 0
        }), {})
    }));

    return (
        <div className="chart-container">
            <h3 className="chart-title">CO-PO Mapping Matrix</h3>
            <div className="heatmap-container">
                <table className="heatmap-table">
                    <thead>
                        <tr>
                            <th>CO</th>
                            {pos.map(po => <th key={po}>{po}</th>)}
                        </tr>
                    </thead>
                    <tbody>
                        {data.map(row => (
                            <tr key={row.co}>
                                <td className="heatmap-label">{row.co}</td>
                                {pos.map(po => (
                                    <td key={po} className={`heatmap-cell level-${row[po]}`}>
                                        {row[po] || '-'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className="heatmap-legend">
                <span><span className="legend-box level-3"></span> 3 = High</span>
                <span><span className="legend-box level-2"></span> 2 = Medium</span>
                <span><span className="legend-box level-1"></span> 1 = Low</span>
            </div>
        </div>
    );
};

export default { BloomDistributionChart, BloomBalanceChart, COPOHeatmap };
