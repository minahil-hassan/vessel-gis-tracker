// Reusable placeholder card for chart slots
// Matches neon glass styling and accepts height to mirror a chart's size.

import React from 'react';
import './MaritimeDashboardOverlay.css';

export default function PlaceholderCard({
  title = 'Notes',
  subtitle = 'Add insights, TODOs, or interpretation here.',
  height = 300,
  children,
}) {
  return (
    <div
      className="chart-card neon-glass chart-placeholder"
      style={{ height }}
      aria-label="Chart Placeholder"
    >
      <div className="chart-placeholder-inner">
        <h5 className="ph-title">{title}</h5>
        {children ? (
          <div className="ph-content">{children}</div>
        ) : (
          <p className="ph-subtitle">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
