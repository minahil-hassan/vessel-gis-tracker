// frontend/src/components/dashboard/DockInsightsPanel.jsx
import React from 'react';

const DockInsightsPanel = ({ data }) => {
  if (!data?.length) return null;

  const sortedByDraught = [...data].sort((a, b) => (b.avg_draught || 0) - (a.avg_draught || 0));
  const sortedByVariety = [...data].sort((a, b) =>
    Object.keys(b.ship_type_groups || {}).length -
    Object.keys(a.ship_type_groups || {}).length
  );
  const sortedByTraffic = [...data].sort((a, b) => b.total_traffic - a.total_traffic);

  return (
    <div className="dc-section neon-glass chart-card">
      <h4>🧭 Dock Insights</h4>
      <ul className="dock-insights">
        <li><strong>Largest Vessels:</strong> {sortedByDraught[0]?.area_name} (avg draught {sortedByDraught[0]?.avg_draught} m)</li>
        <li><strong>Most Diverse Types:</strong> {sortedByVariety[0]?.area_name} ({Object.keys(sortedByVariety[0]?.ship_type_groups || {}).length} types)</li>
        <li><strong>Most Traffic:</strong> {sortedByTraffic[0]?.area_name} ({sortedByTraffic[0]?.total_traffic} vessels)</li>
        <li><strong>Facilities:</strong> {sortedByTraffic[0]?.facilities}</li>
      </ul>
    </div>
  );
};

export default DockInsightsPanel;
