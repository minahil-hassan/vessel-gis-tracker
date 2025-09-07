import React from 'react';
import ReactECharts from 'echarts-for-react';

const DockAreaTreemap = ({ data }) => {
  const treemapData = (data || []).map(d => ({
    name: d.area_name || 'Unknown',
    value: typeof d.total_traffic === 'number' ? d.total_traffic : 0,
  }));

  const option = {
    title: { text: 'Dock Area vs. Vessel Count', textStyle: { color: '#fff' } },
    tooltip: {
      formatter: ({ data }) => `${data.name}<br/>Vessels: ${data.value}`,
    },
    series: [
      {
        type: 'treemap',
        data: treemapData,
        label: {
          show: true,
          color: '#fff',
          formatter: '{b}',
        },
        itemStyle: {
          borderColor: '#222',
          borderWidth: 1,
        },
      },
    ],
  };

  return (
    <div className="chart-card neon-glass">
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  );
};

export default DockAreaTreemap;
