import React from 'react';

const PortAreaPopup = ({ properties }) => {
  const {
    name,
    type,
    area,
    description,
    facility,
    operator,
    berth,
    storage,
    cargo
  } = properties || {};

  return (
    <div className="popup-content">
      <div className="popup-header">
        <strong>{name || 'Unnamed Area'}</strong><br/>
        <small>{type || 'Unknown Type'} – {area || ''}</small>
      </div>
      <hr/>
      <table>
        {description && <tr><td><b>Description:</b></td><td>{description}</td></tr>}
        {facility   && <tr><td><b>Facility:</b></td><td>{facility}</td></tr>}
        {operator   && <tr><td><b>Operator:</b></td><td>{operator}</td></tr>}
        {berth      && <tr><td><b>Berths:</b></td><td>{berth}</td></tr>}
        {storage    && <tr><td><b>Storage:</b></td><td>{storage}</td></tr>}
        {cargo      && <tr><td><b>Cargo:</b></td><td>{cargo}</td></tr>}
      </table>
    </div>
  );
};

export default PortAreaPopup;
