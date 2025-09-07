// export default TypesBarChart;
import React, { useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import { pickNeon } from './chartTheme';

const TypesBarChart = ({ groups = {}, height = 240 }) => {
  const labels = Object.keys(groups || []);
  const colors = labels.map((_, i) => pickNeon(i).line);

  const data = useMemo(() => ({
    labels,
    datasets: [{
      label: 'Arrivals',
      data: labels.map(l => groups[l]),
      backgroundColor: colors.map(c => c + '33'),
      borderColor: colors,
      borderWidth: 1.5,
      borderRadius: 6,
      barPercentage: 0.75,
      categoryPercentage: 0.6
    }]
  }), [labels.join('|'), JSON.stringify(groups)]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { mode: 'index', intersect: false },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.06)' },
        ticks: { color: 'rgba(220,230,240,0.85)' }
      },
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255,255,255,0.06)' },
        ticks: { color: 'rgba(220,230,240,0.85)' }
      }
    }
  };

  return (
    <div className="dc-chart neon-glass" style={{ height }}>
      <Bar data={data} options={options} />
    </div>
  );
};

export default TypesBarChart;

