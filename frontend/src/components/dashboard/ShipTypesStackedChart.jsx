// src/components/dashboard/ShipTypesStackedChart.jsx
import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';

const ShipTypesStackedChart = ({ data = [], range }) => {
  const allTypes = useMemo(
    () => Array.from(new Set(data.flatMap(d => Object.keys(d.ship_type_groups || {})))),
    [data]
  );

  const series = useMemo(() => allTypes.map(type => ({
    name: type,
    type: 'bar',
    stack: 'types',
    emphasis: { focus: 'series' },
    data: data.map(d => d.ship_type_groups?.[type] || 0),
  })), [allTypes, data]);

  const option = useMemo(() => ({
    title: { text: `Ship Type Groups by Dock (last ${range}d)`, textStyle: { color: '#fff' } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { textStyle: { color: '#ccc' } },
    grid: { left: 40, right: 30, bottom: 80, top: 50 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.area_name || 'Unknown'),
      axisLabel: { rotate: 45, color: '#DDE3EA' },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#DDE3EA' },
    },
    series,
  }), [data, series, range]);

  return (
    <div className="chart-card neon-glass">
      <ReactECharts option={option} notMerge={true} lazyUpdate={false} style={{ height: 320 }} />
    </div>
  );
};

export default ShipTypesStackedChart;
