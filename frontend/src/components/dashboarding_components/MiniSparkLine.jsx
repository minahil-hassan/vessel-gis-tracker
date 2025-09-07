import React from 'react';
import ReactECharts from 'echarts-for-react';

export default function MiniSparkline({ data, label, type }) {
  if (!data || data.length === 0) {
    return <div style={{ fontSize: '12px', color: '#aaa' }}>No trend data available</div>;
  }

  const lineColor = type === 'freight' ? '#37f8ff' : '#ff7edf';

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: params => {
        const point = params[0];
        const date = new Date(point.name).toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
          hour12: true
        });
        return `
          <div class="tooltip-container">
            <div class="tooltip-title">${date}</div>
            <div class="tooltip-value">${point.value} arrivals</div>
          </div>
        `;
      },
      backgroundColor: 'rgba(10, 12, 20, 0.85)', // Match theme
      borderColor: '#00ffe7', // Neon-style border
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12
      },
      padding: 10
    },
    grid: { left: 0, right: 0, top: 10, bottom: 0 },
    xAxis: { type: 'category', show: false, data: data.map(d => d.t) },
    yAxis: { type: 'value', show: false },
    series: [
      {
        type: 'line',
        showSymbol: false,
        data: data.map(d => d.arrivals),
        lineStyle: { width: 2, color: lineColor },
        areaStyle: { color: `${lineColor}33` }
      }
    ]
  };

  return (
    <div className="mini-sparkline">
      <ReactECharts option={option} style={{ height: '60px' }} />
    </div>
  );
}
