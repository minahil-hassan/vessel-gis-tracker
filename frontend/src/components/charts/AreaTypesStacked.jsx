//src/components/charts/AreaTypesStacked
import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { NEON } from './chartTheme';

/**
 * Props:
 *  - data: [{
 *      area_name,
 *      ship_type_groups: { "Cargo Vessels": 10, "Tankers": 3, ... }
 *    }, ...]
 *  - height: number (px)
 *  - topN: limit areas by highest total_traffic (like the bar chart)
 */
const AreaTypesStacked = ({ data = [], height = 320, topN = 10 }) => {
  // Sort by total_traffic desc and limit
  const areas = useMemo(() => {
    const arr = Array.isArray(data) ? data.slice() : [];
    return arr.sort((a, b) => (b.total_traffic || 0) - (a.total_traffic || 0)).slice(0, topN);
  }, [data, topN]);

  // Collect all group labels (union across areas)
  const allGroups = useMemo(() => {
    const set = new Set();
    for (const row of areas) {
      const groups = row.ship_type_groups || {};
      Object.keys(groups).forEach(k => set.add(k));
    }
    // Stable order (optional: prioritize common groups)
    return Array.from(set);
  }, [areas]);

  // Build series (one series per group, stacked)
  const series = useMemo(() => {
    const palette = Object.values(NEON); // cycle neon colors
    return allGroups.map((g, i) => ({
      name: g,
      type: 'bar',
      stack: 'types',
      emphasis: { focus: 'series' },
      itemStyle: {
        color: palette[i % palette.length].line,
        shadowBlur: 8,
        shadowColor: 'rgba(0,0,0,0.3)',
      },
      data: areas.map(a => (a.ship_type_groups?.[g] ?? 0)),
      barWidth: '60%',
    }));
  }, [allGroups, areas]);

  const option = useMemo(() => {
    return {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: {
        top: 0,
        textStyle: { color: '#DDE3EA' },
        icon: 'roundRect',
        itemWidth: 12,
        itemHeight: 8,
      },
      grid: { left: 10, right: 10, top: 36, bottom: 8, containLabel: true },
      xAxis: {
        type: 'category',
        axisLabel: { color: '#DDE3EA', interval: 0, rotate: 20 },
        axisTick: { show: false },
        axisLine: { show: false },
        data: areas.map(a => a.area_name),
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#DDE3EA' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series,
    };
  }, [areas, series]);

  return (
    <div className="chart-card neon-glass" style={{ height }}>
      <ReactECharts option={option} notMerge lazyUpdate style={{ height: '100%' }} />
    </div>
  );
};

export default AreaTypesStacked;
