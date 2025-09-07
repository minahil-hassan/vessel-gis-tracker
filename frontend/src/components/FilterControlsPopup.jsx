// src/components/FilterControlsPopup.jsx

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';
import './FilterControlsPopup.css';

/**
 * A frosted‐glass popup with a searchable multi‐select of UK cities.
 *
 * Props:
 * - onApply(cities): called with an array of selected city objects
 * - onClose(): called to dismiss the popup
 */
export default function FilterControlsPopup({ onApply, onClose }) {
  // Static list of major UK cities with lat/lng
  const cityOptions = [
    { label: 'London',     value: 'london',     coord: [-0.1278, 51.5074] },
    { label: 'Birmingham', value: 'birmingham', coord: [-1.8904, 52.4862] },
    { label: 'Manchester', value: 'manchester', coord: [-2.2426, 53.4808] },
    { label: 'Glasgow',    value: 'glasgow',    coord: [-4.2518, 55.8642] },
    { label: 'Leeds',      value: 'leeds',      coord: [-1.5491, 53.8008] },
    { label: 'Sheffield',  value: 'sheffield',  coord: [-1.4701, 53.3811] },
    { label: 'Edinburgh',  value: 'edinburgh',  coord: [-3.1883, 55.9533] },
    { label: 'Liverpool',  value: 'liverpool',  coord: [-2.9916, 53.4084] },
    { label: 'Bristol',    value: 'bristol',    coord: [-2.5879, 51.4545] },
    { label: 'Cardiff',    value: 'cardiff',    coord: [-3.1791, 51.4816] },
    { label: 'Belfast',    value: 'belfast',    coord: [-5.9301, 54.5973] }
  ];

  const [selected, setSelected] = useState([]);

  return (
    <div className="filter-backdrop" onClick={onClose}>
      <div className="filter-popup" onClick={e => e.stopPropagation()}>
        <h4>Select UK Cities</h4>
        <Select
          options={cityOptions}
          isMulti
          placeholder="Search cities..."
          closeMenuOnSelect={false}
          className="filter-select"
          classNamePrefix="filter"
          value={selected}
          onChange={setSelected}
        />
        <div className="filter-buttons">
          <button className="btn-clear" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn-orange"
            onClick={() => onApply(selected)}
            disabled={selected.length === 0}
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  );
}

FilterControlsPopup.propTypes = {
  onApply: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired
};
