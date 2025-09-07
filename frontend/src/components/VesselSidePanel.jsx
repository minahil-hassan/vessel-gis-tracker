import React from 'react';
import VesselFlag from './VesselFlag';
import PortCallsPopup from './PortCallsPopup';
import DateRangeFilter from './DateRangeFilter';
import './VesselSidePanel.css';

export default function VesselSidePanel({
  activeFeature,
  popupData,
  startTime,
  endTime,
  setStartTime,
  setEndTime,
  onShowTrajectory,
  onClearTrajectory,
  loading,
  closePanel
}) {
  if (!activeFeature) return null;
  const { name, mmsi, type, sog, cog, heading, destination, nav_status, timestamp } =
    activeFeature.properties;

// Build and open the trajectory page in a new tab
  const handleShowTrajectory = () => {
    const params = new URLSearchParams({ mmsi });
    if (startTime) params.set('startTime', new Date(startTime).toISOString());
    if (endTime)   params.set('endTime',   new Date(endTime).toISOString());

    const url = `${window.location.origin}/trajectory?${params.toString()}`;
    window.open(url, '_blank');
  };

  return (
    <div className="side-panel">
      
      <div className="popup-glass">
        <button className="popup-close" onClick={closePanel}>×</button>
        <div className="popup-header">
          <VesselFlag mmsi={mmsi} />
          <div>
            <div className="ship-name">{name || 'Unknown'}</div>
            <div className="ship-type">{type || 'N/A'}</div>
          </div>
        </div>
        <div className="popup-image-container">
          <img
            className="vessel-image"
            src={`/vessel_images/${name}.png`}
            alt={name}
            onError={e => e.currentTarget.src = '/vessel_images/NO_IMAGE.PNG'}
          />
        </div>
        <table className="popup-table">
          <tbody>
            <tr><td><strong>MMSI</strong></td><td>{mmsi}</td></tr>
            <tr><td><strong>Destination</strong></td><td>{destination || 'N/A'}</td></tr>
            <tr><td><strong>Speed (kn)</strong></td><td>{sog ?? 'N/A'}</td></tr>
            <tr><td><strong>Course (°)</strong></td><td>{cog ?? 'N/A'}</td></tr>
            <tr><td><strong>Heading</strong></td><td>{heading ?? cog ?? 'N/A'}</td></tr>
            <tr><td><strong>Status</strong></td><td>{nav_status || 'N/A'}</td></tr>
            <tr>
              <td><strong>Last Seen</strong></td>
              <td>{timestamp ? new Date(timestamp).toLocaleString('en-GB') : 'N/A'}</td>
            </tr>
          </tbody>
        </table>
        <PortCallsPopup mmsi={mmsi} />
        <div className="date-filter">
            <DateRangeFilter
                startTime={startTime}
                endTime={endTime}
                setStartTime={setStartTime}
                setEndTime={setEndTime}
            />
        </div>
        <div className="popup-button-group">
          <button onClick={handleShowTrajectory} className="btn-orange" disabled={loading}>
            {loading ? 'Loading…' : 'Show Trajectory'}
          </button>
          <button onClick={onClearTrajectory} className="btn-clear">
            Clear Trajectory
          </button>
        </div>
      </div>
    </div>
  );
}
