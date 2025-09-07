// src/components/dashboard/DockTrafficBarChart.jsx
import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';

const DockTrafficBarChart = ({ data = [], range }) => {
  const option = useMemo(() => ({
    title: { text: `Vessel Traffic per Dock (last ${range}d)`, textStyle: { color: '#fff' } },
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 30, bottom: 50, top: 50 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.area_name || 'Unknown'),
      axisLabel: { rotate: 45, color: '#DDE3EA' },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#DDE3EA' },
    },
    series: [
      {
        data: data.map(d => d.total_traffic ?? 0),
        type: 'bar',
        itemStyle: {
          color: 'rgba(37, 243, 255, 1)',
          shadowBlur: 10,
          shadowColor: 'rgba(37, 243, 255, 0.5)',
        },
        barWidth: '60%',
      },
    ],
  }), [data, range]);

  return (
    <div className="chart-card neon-glass">
      <ReactECharts option={option} notMerge={true} lazyUpdate={false} style={{ height: 300 }} />
    </div>
  );
};

export default DockTrafficBarChart;
