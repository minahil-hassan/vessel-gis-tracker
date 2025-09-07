import React, { useState } from 'react';
import PropTypes from 'prop-types';
import './LayersChecklistPopup.css';

export default function LayersChecklistPopup({
  availableLayers,
  selected,
  onApply,
  onClose
}) {
  const [local, setLocal] = useState(new Set(selected));

  const toggle = (key) => {
    const s = new Set(local);
    s.has(key) ? s.delete(key) : s.add(key);
    setLocal(s);
  };

  return (
    <div className="layers-backdrop" onClick={onClose}>
      <div className="layers-popup" onClick={e => e.stopPropagation()}>
        <h4>Map Layers</h4>
        <ul className="layers-list">
          {availableLayers.map(({ key, label }) => (
            <li key={key}>
              <label>
                <input
                  type="checkbox"
                  checked={local.has(key)}
                  onChange={() => toggle(key)}
                />{' '}
                {label}
              </label>
            </li>
          ))}
        </ul>
        <div className="layers-buttons">
          <button className="btn-clear" onClick={onClose}>Cancel</button>
          <button
            className="btn-orange"
            onClick={() => onApply(Array.from(local))}
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  );
}

LayersChecklistPopup.propTypes = {
  availableLayers: PropTypes.array.isRequired,
  selected:        PropTypes.array.isRequired,
  onApply:         PropTypes.func.isRequired,
  onClose:         PropTypes.func.isRequired,
};
