//src/components/dashboard/DockDwellTimeHeatmap.jsx
import React from 'react';
import ReactECharts from 'echarts-for-react';

const DockDwellTimeHeatmap = ({ data }) => {
  const categories = (data || []).map(d => d.area_name || 'Unknown');
  const values = (data || []).map((d, i) => [0, i, d.avg_stay_min ?? 0]);

  const option = {
    title: { text: 'Average Dwell Time per Dock (min)', textStyle: { color: '#fff' } },
    tooltip: {
      formatter: function (p) {
        const dock = categories[p.data[1]];
        return `${dock}<br/>Dwell Time: ${p.data[2]} min`;
      },
    },
    grid: { height: '70%', top: '10%' },
    xAxis: { type: 'category', data: ['Dwell Time'], show: false },
    yAxis: { type: 'category', data: categories, axisLabel: { color: '#ccc' } },
    visualMap: {
      min: 0,
      max: Math.max(...data.map(d => d.avg_stay_min || 0), 0),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      textStyle: { color: '#ccc' },
    },
    series: [
      {
        name: 'Dwell Time',
        type: 'heatmap',
        data: values,
        label: { show: false },
        emphasis: { itemStyle: { shadowBlur: 10 } },
      },
    ],
  };

  return (
    <div className="chart-card neon-glass">
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  );
};

export default DockDwellTimeHeatmap;
