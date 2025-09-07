//src/components/charts/chartTheme.js
// One place to set chart defaults + neon helpers + soft glow
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, TimeScale,
  PointElement, LineElement, BarElement,
  Tooltip, Legend, Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale, LinearScale, TimeScale,
  PointElement, LineElement, BarElement,
  Tooltip, Legend, Filler
);

// Global defaults for “liquid glass” UI
ChartJS.defaults.color = '#DDE3EA';
ChartJS.defaults.font.family = 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif';
ChartJS.defaults.font.size = 12;
ChartJS.defaults.plugins.legend.labels.boxWidth = 10;
ChartJS.defaults.plugins.legend.labels.boxHeight = 10;
ChartJS.defaults.plugins.tooltip.backgroundColor = 'rgba(8, 12, 20, 0.9)';
ChartJS.defaults.plugins.tooltip.borderColor = 'rgba(0,255,255,0.15)';
ChartJS.defaults.plugins.tooltip.borderWidth = 1;
ChartJS.defaults.elements.line.tension = 0.35;
ChartJS.defaults.elements.point.radius = 0;
ChartJS.defaults.elements.point.hoverRadius = 4;

// Neon palette
export const NEON = {
  cyan:    { line: '#25F3FF', fill: 'rgba(37, 243, 255, 0.18)' },
  magenta: { line: '#FF57F1', fill: 'rgba(255, 87, 241, 0.18)' },
  lime:    { line: '#2BFF88', fill: 'rgba(43, 255, 136, 0.18)' },
  orange:  { line: '#FFB34D', fill: 'rgba(255, 179, 77, 0.18)' },
  purple:  { line: '#9D8CFF', fill: 'rgba(157, 140, 255, 0.18)' },
  yellow:  { line: '#F5FF5E', fill: 'rgba(245, 255, 94, 0.18)' },
};

// Cycle through palette
export const pickNeon = (i) => Object.values(NEON)[i % Object.values(NEON).length];

// Smooth gradient fill matching the line color
export const makeLineGradient = (ctx, area, color) => {
  const g = ctx.createLinearGradient(0, area.top, 0, area.bottom);
  g.addColorStop(0, color.fill);
  g.addColorStop(1, 'rgba(0,0,0,0)');
  return g;
};

// Tiny plugin to add soft neon glow on strokes
export const neonShadow = {
  id: 'neonShadow',
  beforeDatasetDraw(chart, args, opts) {
    const { ctx } = chart;
    const { glowColor = 'rgba(0,255,255,0.35)', blur = 12 } = opts || {};
    ctx.save();
    ctx.shadowColor = glowColor;
    ctx.shadowBlur = blur;
  },
  afterDatasetDraw(chart) {
    chart.ctx.restore();
  }
};
