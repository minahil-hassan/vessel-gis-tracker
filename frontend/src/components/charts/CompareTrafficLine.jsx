// src/components/charts/CompareTrafficLineChart.jsx
import React, { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Register once (safe to call multiple times)
ChartJS.register(LineElement, PointElement, LinearScale, TimeScale, Tooltip, Legend, Filler);

/**
 * Inputs:
 * - ukUnified: [{ t: Date|string, arrivals: number }, ...]
 * - livUnified: [{ t: Date|string, arrivals: number }, ...]
 */
function alignSeries(ukUnified = [], livUnified = []) {
  const byTs = new Map();

  for (const p of ukUnified) {
    const ts = new Date(p.t).getTime();
    byTs.set(ts, { t: ts, uk: p.arrivals || 0, liverpool: 0 });
  }
  for (const p of livUnified) {
    const ts = new Date(p.t).getTime();
    if (byTs.has(ts)) {
      byTs.get(ts).liverpool = p.arrivals || 0;
    } else {
      byTs.set(ts, { t: ts, uk: 0, liverpool: p.arrivals || 0 });
    }
  }

  const rows = Array.from(byTs.values()).sort((a, b) => a.t - b.t);
  const labels = rows.map(r => new Date(r.t));
  const uk = rows.map(r => r.uk);
  const liv = rows.map(r => r.liverpool);

  return { labels, uk, liv };
}

const CompareTrafficLineChart = ({ ukUnified = [], livUnified = [] }) => {
  const { labels, uk, liv } = useMemo(
    () => alignSeries(ukUnified, livUnified),
    [ukUnified, livUnified]
  );

  const data = {
    labels,
    datasets: [
      {
        label: 'UK',
        data: uk,
        borderColor: '#25F3FF',
        backgroundColor: 'rgba(37,243,255,0.12)',
        tension: 0.3,
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
      },
      {
        label: 'Liverpool',
        data: liv,
        borderColor: '#FFAA33',
        backgroundColor: 'rgba(255,170,51,0.12)',
        tension: 0.3,
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false, // lets the parent .chart-card control height
    interaction: { mode: 'index', intersect: false },
    stacked: false,
    plugins: {
      legend: { display: true, labels: { boxWidth: 12 } },
      tooltip: {
        callbacks: {
          title: (items) => {
            const ts = items?.[0]?.parsed?.x;
            return ts ? new Date(ts).toLocaleString() : '';
          },
        },
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'hour',
          displayFormats: { hour: 'dd MMM HH:mm' },
          tooltipFormat: 'dd MMM yyyy, HH:mm',
        },
        grid: { color: 'rgba(255,255,255,0.08)' },
        ticks: { color: '#ddd', maxRotation: 0, autoSkip: true },
      },
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255,255,255,0.08)' },
        ticks: { color: '#ddd', precision: 0 },
        title: { display: true, text: 'Arrivals', color: '#bbb' },
      },
    },
  };

  return <Line data={data} options={options} />;
};

export default CompareTrafficLineChart;
