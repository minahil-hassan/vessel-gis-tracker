// // export default BucketsLineChart;
// import React, { useMemo } from 'react';
// import { Line } from 'react-chartjs-2';
// import 'chartjs-adapter-date-fns';
// import { neonShadow, pickNeon, makeLineGradient } from './chartTheme';

// const BucketsLineChart = ({ series = [], unified = [], label = 'Series', height = 250 }) => {
//   const unifiedDataset = useMemo(() => {
//     const neon = pickNeon(0);
//     return {
//       label: `${label} (total)`,
//       data: (unified || []).map(p => ({ x: new Date(p.t), y: p.arrivals })),
//       borderColor: neon.line,
//       backgroundColor: (ctx) => {
//         const chart = ctx?.chart;
//         if (!chart || !chart.chartArea) return neon.fill;
//         const { ctx: c, chartArea } = chart;
//         return makeLineGradient(c, chartArea, neon);
//       },
//       borderWidth: 2.5,
//       fill: true,
//       pointRadius: 0,
//       tension: 0.35,
//     };
//   }, [unified, label]);

//   const multiDatasets = useMemo(() => {
//     return (series || []).map((s, i) => {
//       const neon = pickNeon(i + 1);
//       return {
//         label: s.port_name,
//         data: (s.points || []).map(p => ({ x: new Date(p.t), y: p.arrivals })),
//         borderColor: neon.line,
//         backgroundColor: (ctx) => {
//           const chart = ctx?.chart;
//           if (!chart || !chart.chartArea) return neon.fill;
//           const { ctx: c, chartArea } = chart;
//           return makeLineGradient(c, chartArea, neon);
//         },
//         borderWidth: 2,
//         fill: true,
//         pointRadius: 0,
//         tension: 0.35,
//       };
//     });
//   }, [series]);

//   const options = useMemo(() => ({
//     responsive: true,
//     maintainAspectRatio: false,
//     plugins: {
//       legend: { labels: { color: '#DDE3EA' } },
//       neonShadow: { glowColor: 'rgba(37,243,255,0.35)', blur: 10 },
//       tooltip: { intersect: false, mode: 'index' },
//     },
//     scales: {
//       x: {
//         type: 'time',
//         time: { unit: 'hour' },
//         grid: { color: 'rgba(255,255,255,0.06)' },
//         ticks: { color: 'rgba(220,230,240,0.85)' }
//       },
//       y: {
//         beginAtZero: true,
//         grid: { color: 'rgba(255,255,255,0.06)' },
//         ticks: { color: 'rgba(220,230,240,0.85)' }
//       }
//     },
//     elements: { point: { radius: 0, hoverRadius: 4 } }
//   }), []);

//   return (
//     <div className="dc-chart neon-glass" style={{ height }}>
//       {/* unified */}
//       <Line
//         data={{ datasets: [unifiedDataset] }}
//         options={options}
//         plugins={[neonShadow]}
//         height={height}
//       />
//       {/* per-port */}
//       <div style={{ height, marginTop: 12 }}>
//         <Line
//           data={{ datasets: multiDatasets }}
//           options={options}
//           plugins={[neonShadow]}
//           height={height}
//         />
//       </div>
//     </div>
//   );
// };

// export default BucketsLineChart;

// frontend/src/components/dashboarding_components/charts/BucketsLineChart.jsx
import React, { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';
import { neonShadow, pickNeon, makeLineGradient } from './chartTheme';

/**
 * BucketsLineChart
 * - Renders a unified (sum) curve and multi-port curves.
 * - Adapts x-axis tick density to the selected time range.
 *
 * Props:
 *  - series: [{ port_name, points: [{ t: ISO|ms, arrivals: number }] }]
 *  - unified: [{ t: ISO|ms, arrivals: number }]
 *  - label: string (legend label for the unified dataset)
 *  - height: number
 *  - range: number of days selected in the picker (1,2,3,7,14,30)
 */
const BucketsLineChart = ({ series = [], unified = [], label = 'Series', height = 300, range = 7 }) => {
  const isWideRange = range > 3; // 7/14/30 days => daily ticks; else 6-hour ticks

  const unifiedDataset = useMemo(() => {
    const neon = pickNeon(0);
    return {
      label: `${label} (total)`,
      data: (unified || []).map(p => ({ x: new Date(p.t), y: p.arrivals })),
      borderColor: neon.line,
      backgroundColor: (ctx) => {
        const chart = ctx?.chart;
        if (!chart || !chart.chartArea) return neon.fill;
        const { ctx: c, chartArea } = chart;
        return makeLineGradient(c, chartArea, neon);
      },
      borderWidth: 2.5,
      fill: true,
      pointRadius: 0,
      tension: 0.35,
    };
  }, [unified, label]);

  const multiDatasets = useMemo(() => {
    return (series || []).map((s, i) => {
      const neon = pickNeon(i + 1);
      return {
        label: s.port_name,
        data: (s.points || []).map(p => ({ x: new Date(p.t), y: p.arrivals })),
        borderColor: neon.line,
        backgroundColor: (ctx) => {
          const chart = ctx?.chart;
          if (!chart || !chart.chartArea) return neon.fill;
          const { ctx: c, chartArea } = chart;
          return makeLineGradient(c, chartArea, neon);
        },
        borderWidth: 2,
        fill: true,
        pointRadius: 0,
        tension: 0.35,
      };
    });
  }, [series]);

  // Recompute options when range changes so the x-axis adapts.
  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#DDE3EA' } },
      neonShadow: { glowColor: 'rgba(37,243,255,0.35)', blur: 10 },
      tooltip: {
        intersect: false,
        mode: 'index',
        callbacks: {
          // Optional: friendlier title format per range
          title: (items) => {
            const d = items?.[0]?.parsed?.x ?? items?.[0]?.raw?.x;
            if (!d) return '';
            const dt = new Date(d);
            if (isWideRange) {
              // e.g., "24 Aug"
              return dt.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
            }
            // e.g., "10:00, 24 Aug"
            return `${dt.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', hour12: false })}, ` +
                   dt.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
          },
        }
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          // <=3d: 6h buckets shown; >3d: daily ticks
          unit: isWideRange ? 'day' : 'hour',
          stepSize: isWideRange ? 1 : 6,
          // display formats for date-fns adapter
          displayFormats: {
            hour: 'HH:mm',
            day: 'd MMM',
          },
        },
        grid: { color: 'rgba(255,255,255,0.06)' },
        ticks: {
          color: 'rgba(220,230,240,0.85)',
          maxRotation: 0,
          autoSkip: true,
          autoSkipPadding: 8,
        }
      },
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255,255,255,0.06)' },
        ticks: { color: 'rgba(220,230,240,0.85)' }
      }
    },
    elements: { point: { radius: 0, hoverRadius: 4 } }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }), [range]); // depend on range so axis rebuilds
    return (
    <div className="dc-chart chart-card neon-glass" style={{ height }}>
      <Line
        key={`unified-${range}`}                 // force full canvas rebuild on range change
        data={{ datasets: [unifiedDataset] }}
        options={options}
        plugins={[neonShadow]}
        height={height}
      />
      {/* Per-port curves */}
      <div style={{ height, marginTop: 12 }}>
        <Line
          key={`multi-${range}`}                 // force full canvas rebuild on range change
          data={{ datasets: multiDatasets }}
          options={options}
          plugins={[neonShadow]}
          height={height}
        />
      </div>
    </div>
  );
};

export default BucketsLineChart;
