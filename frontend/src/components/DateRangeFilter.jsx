import React from 'react';

const DateRangeFilter = ({ startTime, endTime, setStartTime, setEndTime }) => {
  return (
    <div className="date-range-filter" style={{ fontSize: '12px', marginTop: '8px' }}>
      <div style={{ marginBottom: '4px' }}>
        <label>Start Time:&nbsp;</label>
        <input
          type="datetime-local"
          value={startTime}
          onChange={e => setStartTime(e.target.value)}
          style={{ fontSize: '12px', padding: '2px' }}
        />
      </div>
      <div>
        <label>End Time:&nbsp;</label>
        <input
          type="datetime-local"
          value={endTime}
          onChange={e => setEndTime(e.target.value)}
          style={{ fontSize: '12px', padding: '2px' }}
        />
      </div>
    </div>
  );
};

export default DateRangeFilter;
