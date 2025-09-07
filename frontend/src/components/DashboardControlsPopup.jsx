//components/DashboardControlsPopup.jsx
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import './DashboardControlsPopup.css';

/**
 * A frosted‐glass popup listing dashboard sections and their controls.
 *
 * Props:
 * - sections: [
 *     { key, label, items: [ { key, label } ] }
 *   ]
 * - selected: array of item-keys currently checked
 * - viewAll: boolean for the “View All” toggle
 * - onApply({ selected, viewAll }): called when Apply clicked
 * - onClose(): dismiss without applying
 */
export default function DashboardControlsPopup({
  sections,
  selected,
  viewAll,
  onApply,
  onClose
}) {
  // Local copies so Cancel doesn’t mutate parent
  const [localSel, setLocalSel] = useState(new Set(selected));
  const [localViewAll, setLocalViewAll] = useState(viewAll);

  const toggleItem = key => {
    const s = new Set(localSel);
    s.has(key) ? s.delete(key) : s.add(key);
    setLocalSel(s);
  };

  return (
    <div className="dc-backdrop" onClick={onClose}>
      <div className="dc-popup" onClick={e => e.stopPropagation()}>
        <h3>Dashboard Controls</h3>
        {sections.map(sec => (
          <div key={sec.key} className="dc-section">
            <h4>{sec.label}</h4>
            <ul>
              {sec.items.map(it => (
                <li key={it.key}>
                  <label>
                    <input
                      type="checkbox"
                      checked={localSel.has(it.key)}
                      onChange={() => toggleItem(it.key)}
                    />{' '}
                    {it.label}
                  </label>
                </li>
              ))}
            </ul>
          </div>
        ))}
        <div className="dc-view-all">
          <label>
            <input
              type="checkbox"
              checked={localViewAll}
              onChange={() => setLocalViewAll(v => !v)}
            />{' '}
            View all
          </label>
        </div>
        <div className="dc-buttons">
          <button className="btn-clear" onClick={onClose}>Cancel</button>
          <button
            className="btn-orange"
            onClick={() => onApply({
              selected: Array.from(localSel),
              viewAll: localViewAll
            })}
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  );
}

DashboardControlsPopup.propTypes = {
  sections: PropTypes.array.isRequired,
  selected: PropTypes.array.isRequired,
  viewAll:  PropTypes.bool.isRequired,
  onApply:  PropTypes.func.isRequired,
  onClose:  PropTypes.func.isRequired,
};
