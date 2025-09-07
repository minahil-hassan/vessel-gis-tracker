//frontend/components/dashboarding_components/TimeRangePicker.jsx
import React from 'react';

const TimeRangePicker = ({ label, value, onChange, options = [1,3,7,14] }) => {
  return (
    <label className="dc-range">
      <span>{label}:</span>
      <select value={value} onChange={e => onChange(Number(e.target.value))}>
        {options.map(opt => (
          <option key={opt} value={opt}>{opt}d</option>
        ))}
      </select>
    </label>
  );
};

export default TimeRangePicker;
