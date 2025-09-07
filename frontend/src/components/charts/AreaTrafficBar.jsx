import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { NEON, pickNeon } from './chartTheme';

/**
 * Props:
 *  - data: [
 *      {
 *        area_name: string,
 *        total_traffic: number,
 *        ship_type_groups?: { [groupName: string]: number },
 *        groups?: { [groupName: string]: number } // alias supported
 *      },
 *      ...
 *    ]
 *  - height: number
 *  - topN: number
 *  - stacked: boolean (if true and group data exists, render stacked bars)
 */
const AreaTrafficBar = ({ data = [], height = 280, topN = 12, stacked = true }) => {
  // Take topN by total_traffic
  const rows = useMemo(() => {
    const arr = Array.isArray(data) ? data.slice() : [];
    return arr
      .sort((a, b) => (b.total_traffic || 0) - (a.total_traffic || 0))
      .slice(0, topN);
  }, [data, topN]);

  // Detect if grouped data is present
  const hasGroups = useMemo(() => {
    return rows.some(
      r =>
        (r.ship_type_groups && Object.keys(r.ship_type_groups).length > 0) ||
        (r.groups && Object.keys(r.groups).length > 0)
    );
  }, [rows]);

  // Build stacked series if we have group data and stacked=true
  const memo = useMemo(() => {
    const categories = rows.map(r => r.area_name);

    // Single-series fallback (kept neon)
    if (!(stacked && hasGroups)) {
      const c = pickNeon(0).line;
      return {
        categories,
        legend: [],
        series: [
          {
            type: 'bar',
            name: 'Arrivals',
            data: rows.map(r => r.total_traffic || 0),
            barWidth: '60%',
            barGap: '20%',
            itemStyle: {
              color: c + '33',              // translucent fill
              borderColor: c,               // neon edge
              borderWidth: 1.5,
              barBorderRadius: 0,
              shadowBlur: 12,
              shadowColor: c + '55',
            },
            emphasis: {
              itemStyle: { shadowBlur: 18, shadowColor: c + '99' },
            },
          },
        ],
      };
    }

    // Collect stable order of all groups across these ports
    const groupSet = new Set();
    rows.forEach(r => {
      const g = r.ship_type_groups || r.groups || {};
      Object.keys(g).forEach(k => groupSet.add(k));
    });
    const groupNames = Array.from(groupSet);
    const legend = groupNames;

    // Series per group, aligned to the same category list
    const series = groupNames.map((gName, i) => {
      const c = pickNeon(i).line;
      const dataPoints = rows.map(r => {
        const g = r.ship_type_groups || r.groups || {};
        return Number(g[gName] || 0);
      });
      return {
        name: gName,
        type: 'bar',
        stack: 'total',
        data: dataPoints,
        barWidth: '60%',
        barGap: 0,
        // Rounded right edge (horizontal bars grow rightwards)
        itemStyle: {
          color: c + '33',
          borderColor: c,
          borderWidth: 1.2,
          barBorderRadius: 0,
          shadowBlur: 10,
          shadowColor: c + '55',
        },
        emphasis: {
          itemStyle: { shadowBlur: 16, shadowColor: c + '99' },
        },
      };
    });

    return { categories, series, legend };
  }, [rows, stacked, hasGroups]);

  const { categories, series, legend } = memo;

  // ECharts option: “liquid glass + neon” to match ChartJS theme
  const option = useMemo(() => {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        confine: true,
        backgroundColor: 'rgba(8, 12, 20, 0.9)',
        borderColor: 'rgba(0,255,255,0.15)',
        borderWidth: 1,
        textStyle: { color: '#DDE3EA' },
        formatter: params => {
          // params is an array of stacks at a category
          const name = params?.[0]?.name ?? '';
          const lines = [`<strong>${name}</strong>`];
          params.forEach(p => {
            lines.push(`${p.marker} ${p.seriesName}: ${Number(p.value).toLocaleString()}`);
          });
          return lines.join('<br/>');
        },
      },
      legend:
        legend && legend.length
          ? {
              data: legend,
              top: 2,
              textStyle: { color: '#DDE3EA' },
              icon: 'roundRect',
              itemWidth: 10,
              itemHeight: 8,
            }
          : undefined,
      grid: {
        left: 8,
        right: 8,
        top: legend && legend.length ? 28 : 20,
        bottom: 8,
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#DDE3EA' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      yAxis: {
        type: 'category',
        data: categories,
        axisLabel: { color: '#DDE3EA' },
        axisTick: { show: false },
        axisLine: { show: false },
      },
      series,
      animationDuration: 450,
      animationEasing: 'cubicOut',
    };
  }, [categories, series, legend]);

  return (
    <div className="chart-card neon-glass" style={{ height }}>
      <ReactECharts option={option} notMerge lazyUpdate style={{ height: '100%' }} />
    </div>
  );
};

export default AreaTrafficBar;
