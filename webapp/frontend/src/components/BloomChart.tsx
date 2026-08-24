import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const bloomOrder = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'];

const bloomColors = {
  remember: '#9ca3af',
  understand: '#60a5fa',
  apply: '#34d399',
  analyze: '#fbbf24',
  evaluate: '#f87171',
  create: '#c084fc'
};

type BloomLevel = 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';

interface BloomChartProps {
  data: Record<string, number>;
}

const BloomChart: React.FC<BloomChartProps> = ({ data }) => {
  // Normalize data for chart
  const chartData = bloomOrder.map(level => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    level: level,
    count: data[level] || 0
  }));

  const total = chartData.reduce((acc, curr) => acc + curr.count, 0);

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
        >
          <XAxis type="number" hide />
          <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} />
          <Tooltip 
            cursor={{ fill: 'rgba(0,0,0,0.05)' }} 
            /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
            formatter={(value: any) => [`${value} (${((Number(value)/total)*100).toFixed(1)}%)`, 'Outcomes']}
          />
          <Bar dataKey="count" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={bloomColors[entry.level as BloomLevel]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BloomChart;
