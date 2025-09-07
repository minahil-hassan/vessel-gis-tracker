import React from 'react';

const LastUpdatedFooter = ({ timestamp }) => {
  if (!timestamp) return null;

  return (
    <p className="last-updated">
      Last updated: {timestamp.toLocaleString('en-GB', { timeZone: 'Europe/London' })}
    </p>
  );
};

export default LastUpdatedFooter;
