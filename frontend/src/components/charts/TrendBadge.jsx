//frontend/src/components/charts/TrendBadge
import React from 'react';

const TrendBadge = ({ currentTotal = 0, previousTotal = 0, previousTotalLabel = 'previous' }) => {
  const diff = currentTotal - previousTotal;
  const pct = previousTotal > 0 ? (diff / previousTotal) * 100 : 0;
  const up = diff > 0;
  return (
    <div className={`trend-badge ${up ? 'up' : 'down'}`}>
      <span>
        {up ? '▲ Rising' : '▼ Falling'} {Math.abs(pct).toFixed(1)}% vs {previousTotalLabel}
      </span>
    </div>
  );
};

export default TrendBadge;
