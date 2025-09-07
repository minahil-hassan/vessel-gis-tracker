// src/components/VesselListPanel.jsx

import React, { useEffect, useState } from 'react';
import './VesselListPanel.css';
import axiosClient from '../api/axiosClient';

export default function VesselListPanel() {
  const [vessels, setVessels] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    axiosClient
      .get('/vessels/')                // <-- no `/api` prefix here
      .then(res => {
        setVessels(res.data.features || []);
      })
      .catch(err => {
        console.error('Failed to load vessels', err);
        setError('Could not load vessels');
      });
  }, []);

  const filtered = vessels.filter(v =>
    (v.properties.name || '')
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  const flyTo = coords =>
    window.dispatchEvent(
      new CustomEvent('flyToCoords', { detail: coords })
    );

  return (
    <div className="vessel-list">
      <h3>Vessels</h3>

      {error && <div className="error">{error}</div>}

      <input
        type="text"
        placeholder="Search vessels..."
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
      />

      {filtered.length === 0 ? (
        <p className="no-results">No vessels found.</p>
      ) : (
        <ul>
          {filtered.map(v => (
            <li key={v.properties.mmsi}>
              <img
                src={`/vessel_images/${v.properties.name}.png`}
                onError={e =>
                  (e.currentTarget.src = '/vessel_images/NO_IMAGE.PNG')
                }
                alt={v.properties.name}
              />
              <div className="vessel-info">
                <strong>{v.properties.name || 'Unknown'}</strong>
                <br />
                <span>{v.properties.type}</span>
              </div>
              <button
                className="btn-show-map"
                onClick={() => flyTo(v.geometry.coordinates)}
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
