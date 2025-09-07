// src/components/TrajectoryOnlyMap.jsx

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import axiosClient from '../api/axiosClient';

import VesselTrajectory from './VesselTrajectory';
import PortMarker from './PortMarker';

// Use satellite style
const SATELLITE_STYLE = 'mapbox://styles/mapbox/satellite-streets-v12';

export default function TrajectoryOnlyMap({ trajectory }) {
  const containerRef = useRef(null);
  const mapRef       = useRef(null);
  const [ports, setPorts] = useState([]);

  // 1) Initialize the map once
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    // Center on first trajectory point (or fallback to [0,0])
    const startCoord = (trajectory && trajectory.length >= 1)
      ? (Array.isArray(trajectory[0].coordinates)
          ? trajectory[0].coordinates
          : trajectory[0].coordinates.coordinates)
      : [0, 0];

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: SATELLITE_STYLE,
      center: startCoord,
      zoom: trajectory && trajectory.length >= 2 ? 6 : 2,
    });

    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    mapRef.current = map;
  }, [trajectory]);

  // 2) Fetch ports for markers
  useEffect(() => {
    axiosClient.get('/ports')
      .then(res => setPorts(res.data.features))
      .catch(err => {
        console.error('Failed to load ports:', err);
        // optionally setPorts([]) or show error state
      });
  }, []);

  // If no valid trajectory, show error overlay
  if (!trajectory || trajectory.length < 2) {
    return (
      <div
        style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(0,0,0,0.6)',
          color: 'white',
          fontSize: '18px',
          zIndex: 1000
        }}
      >
        No trajectory data available for this vessel.
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      style={{ position: 'absolute', top: 0, bottom: 0, width: '100%' }}
    >
      {mapRef.current && (
        <>
          {/* Render port markers */}
          {ports.map((port, i) => (
            <PortMarker
              key={`port-${i}`}
              map={mapRef.current}
              feature={port}
            />
          ))}

          {/* Render the neon trajectory line & points */}
          <VesselTrajectory
            map={mapRef.current}
            trajectory={trajectory}
          />
        </>
      )}
    </div>
  );
}
