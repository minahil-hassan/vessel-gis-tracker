// src/components/PortListPanel.jsx

import React, { useEffect, useState } from 'react';
import './VesselListPanel.css';    // reuse the same styling
import axiosClient from '../api/axiosClient';

export default function PortListPanel() {
  const [ports, setPorts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    axiosClient
      .get('/ports/')                // <-- note trailing slash
      .then(res => {
        setPorts(res.data.features || []);
      })
      .catch(err => {
        console.error('Failed to load ports', err);
        setError('Could not load ports');
      });
  }, []);

  const filtered = ports.filter(p =>
    (p.properties.name || '')
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  const flyTo = coords =>
    window.dispatchEvent(
      new CustomEvent('flyToCoords', { detail: coords })
    );

  return (
    <div className="vessel-list">
      <h3>Ports</h3>

      {error && <div className="error">{error}</div>}

      <input
        type="text"
        placeholder="Search ports..."
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
      />

      {filtered.length === 0 ? (
        <p className="no-results">No ports found.</p>
      ) : (
        <ul>
          {filtered.map(p => (
            <li key={p.properties.locode || p.properties.name}>
              <div className="vessel-info">
                <strong>{p.properties.name}</strong><br />
                <span>{p.properties.locode}</span>
              </div>
              <button
                className="btn-show-map"
                onClick={() => flyTo(p.geometry.coordinates)}
              >
                Show on Map
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
