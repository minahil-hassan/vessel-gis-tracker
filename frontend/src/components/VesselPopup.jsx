// src/components/VesselPopup.jsx

import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import mapboxgl from 'mapbox-gl';
import DateRangeFilter from './DateRangeFilter';
import VesselFlag from './VesselFlag';
import PortCallsPopup from './PortCallsPopup';
import './VesselPopup.css';

/**
 * VesselPopup displays vessel details in a floating glass-style popup on the map.
 * It is rendered via a React portal into Mapbox's popup DOM container.
 *
 * Props:
 * - map: Mapbox GL JS map instance
 * - activeFeature: GeoJSON Feature for the selected vessel
 * - onClearTrajectory: callback to clear any displayed trajectory
 * - loading: boolean flag while trajectory data is loading
 * - startTime, endTime: ISO date strings for history range selection
 * - setStartTime, setEndTime: setters for the date range filter
 * - closePopup: function to close this popup
 */
const VesselPopup = ({
  map,
  activeFeature,
  onClearTrajectory,
  loading,
  startTime,
  endTime,
  setStartTime,
  setEndTime,
  closePopup
}) => {
  // Reference to the Mapbox Popup object and its content container
  const popupRef = useRef(null);
  const contentRef = useRef(document.createElement('div'));

  // Guard against missing feature
  const properties = activeFeature?.properties || {};
  const {
    name,
    mmsi,
    type,
    sog,
    cog,
    heading,
    destination,
    nav_status,
    timestamp
  } = properties;

  // Local state for vessel image src, with fallback on error
  // const [imgSrc, setImgSrc] = useState(`/vessel_images/${name}.png`);
  // const handleImageError = () => {
  //   setImgSrc('/vessel_images/NO_IMAGE.PNG');
  // };

      // Generate image path from vessel name
  const imageName = name;
  const [imgSrc, setImgSrc] = useState(`/vessel_images/${imageName}.png`);
  // Handle image error fallback
  const handleImageError = () => {
    setImgSrc('/vessel_images/NO_IMAGE.PNG');
  };

  /**
   * When the user clicks "Show Trajectory", open a new tab/window
   * to our /trajectory route with the vessel's MMSI and date filters.
   */
  const handleShowTrajectory = () => {
    const params = new URLSearchParams({ mmsi });
    if (startTime) params.set('startTime', new Date(startTime).toISOString());
    if (endTime)   params.set('endTime',   new Date(endTime).toISOString());
    const url = `${window.location.origin}/trajectory?${params.toString()}`;
    window.open(url, '_blank');
  };

  // Initialize Mapbox popup once when `map` becomes available
  useEffect(() => {
    if (!map) return;
    popupRef.current = new mapboxgl.Popup({ closeOnClick: false, offset: 20 });
    // Cleanup on unmount
    return () => popupRef.current.remove();
  }, [map]);

  // Whenever activeFeature changes, attach the popup to the map at its coords
  useEffect(() => {
    if (!activeFeature) return;
    popupRef.current
      .setLngLat(activeFeature.geometry.coordinates)
      .setDOMContent(contentRef.current)
      .addTo(map);
    // Slight reposition after render to avoid anchor issues
    setTimeout(() => {
      popupRef.current.setLngLat(activeFeature.geometry.coordinates);
    }, 50);
  }, [activeFeature, map]);


  

  // Render the popup's HTML via React Portal
  return createPortal(
    <div className="popup-glass">
      {/* Close button */}
      <button className="popup-close" onClick={closePopup}>×</button>

      {/* Header: Vessel flag, name and type */}
      <div className="popup-header">
        <VesselFlag mmsi={mmsi} />
        <div>
          <div className="ship-name">{name || 'Unknown'}</div>
          <div className="ship-type">{type || 'N/A'}</div>
        </div>
      </div>

      {/* Vessel image with fallback */}
      <div className="popup-image-container">
        <img
          className="vessel-image"
          src={imgSrc}
          alt={name || 'Vessel'}
          onError={handleImageError}
        />
      </div>

      {/* Key metadata table */}
      <table className="popup-table">
        <tbody>
          <tr>
            <td><strong>MMSI</strong></td>
            <td>{mmsi}</td>
          </tr>
          <tr>
            <td><strong>Destination</strong></td>
            <td>{destination || 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Speed (kn)</strong></td>
            <td>{sog ?? 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Course (°)</strong></td>
            <td>{cog ?? 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Heading</strong></td>
            <td>{heading ?? cog ?? 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Status</strong></td>
            <td>{nav_status || 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Last Seen</strong></td>
            <td>
              {timestamp
                ? new Date(timestamp).toLocaleString('en-GB')
                : 'N/A'}
            </td>
          </tr>
        </tbody>
      </table>

      {/* List of recent port calls */}
      <PortCallsPopup mmsi={mmsi} />

      {/* Date range filter for trajectory */}
      <DateRangeFilter
        startTime={startTime}
        endTime={endTime}
        setStartTime={setStartTime}
        setEndTime={setEndTime}
      />

      {/* Action buttons */}
      <div className="popup-button-group">
        <button
          className="btn-orange"
          onClick={handleShowTrajectory}
          disabled={loading}
        >
          {loading ? 'Loading…' : 'Show Trajectory'}
        </button>
        <button
          className="btn-clear"
          onClick={onClearTrajectory}
        >
          Clear Trajectory
        </button>
      </div>
    </div>,
    contentRef.current
  );
};

export default VesselPopup;

