// src/components/ViewTogglePopup.jsx

import React from 'react';
import './ViewTogglePopup.css';

/**
 * A small frosted‐glass popup to switch between Navigation & Satellite.
 *
 * Props:
 * - currentStyle: the current Mapbox style URI
 * - toggleStyle(): callback to flip between NAVIGATION_DAY ↔ SATELLITE
 * - onClose(): hide this popup
 */
export default function ViewTogglePopup({ currentStyle, toggleStyle, onClose }) {
  const isSatellite = currentStyle.includes('satellite');

  return (
    <div className="view-toggle-backdrop" onClick={onClose}>
      <div className="view-toggle-popup" onClick={e => e.stopPropagation()}>
        <button
          className={`vt-btn ${isSatellite ? '' : 'active'}`}
          onClick={() => { if (isSatellite) toggleStyle(); }}
        >
          Navigation view
        </button>
        <button
          className={`vt-btn ${isSatellite ? 'active' : ''}`}
          onClick={() => { if (!isSatellite) toggleStyle(); }}
        >
          Satellite view
        </button>
      </div>
    </div>
  );
}
