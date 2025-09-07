// frontend/src/components/dashboarding_components/SummaryStatsPanel.jsx
import React, { useMemo } from 'react';
import MiniSparkline from './MiniSparkLine';
import './SummaryStatsPanel.css';

// Sum a group count whether it's already a number (flat)
// or is a nested object of subtype counts (UK snapshot).
function sumMaybeNested(value) {
  if (value == null) return 0;
  if (typeof value === 'number') return value;
  if (typeof value === 'object') {
    return Object.values(value).reduce((a, b) => a + (typeof b === 'number' ? b : 0), 0);
  }
  return 0;
}

// Normalize whole groups object to { group: number }
function normalizeGroups(groups = {}) {
  const out = {};
  for (const [k, v] of Object.entries(groups)) {
    out[k] = sumMaybeNested(v);
  }
  return out;
}

export default function SummaryStatsPanel({ total = 0, groups = {}, sparklineData = [], viewMode }) {
  const flatGroups = useMemo(() => normalizeGroups(groups), [groups]);

  const passengerCount = flatGroups['Passenger Vessels'] || 0;
  const freightCount = (flatGroups['Cargo Vessels'] || 0) + (flatGroups['Tankers'] || 0);

  return (
    <div className="summary-grid">
      <div className="summary-card">
        <h3>TOTAL VOLUME</h3>
        <p>{Number(total || 0).toLocaleString()} vessels</p>
      </div>

      <div className="summary-card">
        <h3>PASSENGER VESSELS</h3>
        <p>{Number(passengerCount).toLocaleString()} vessels</p>
        {Array.isArray(sparklineData) && sparklineData.length > 0 ? (
          <MiniSparkline data={sparklineData} label="Passenger Vessels" type="passenger" />
        ) : (
          <small>No trend data available</small>
        )}
      </div>

      <div className="summary-card">
        <h3>FREIGHT VESSELS</h3>
        <p>{Number(freightCount).toLocaleString()} vessels</p>
        {Array.isArray(sparklineData) && sparklineData.length > 0 ? (
          <MiniSparkline data={sparklineData} label="Freight Vessels" type="freight" />
        ) : (
          <small>No trend data available</small>
        )}
      </div>
    </div>
  );
}
