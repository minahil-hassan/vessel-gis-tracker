import React from 'react';
const UKStatsSection = ({ uk }) => {
  const { total_vessels, avg_speed, last_update, top_destinations = [] } = uk;
console.log('Top destinations:', top_destinations);
const seen = new Set();
top_destinations.forEach((d, i) => {
  if (seen.has(d)) console.warn('Duplicate key in top_destinations:', d);
  seen.add(d);
});
  return (    
    <ul>
      <li><strong>Total Vessels:</strong> {total_vessels}</li>
      <li><strong>Avg Speed:</strong> {avg_speed} kn</li>
      <li><strong>Top Destinations:</strong>
        <ul>
          {top_destinations.map((dest, i) => (
            <li key={`${dest}-${i}`}>{dest}</li>
          ))}
        </ul>
      </li>
    </ul>
  );
};
export default UKStatsSection;
