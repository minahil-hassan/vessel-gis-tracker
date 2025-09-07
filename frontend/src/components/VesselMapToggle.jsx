import React from 'react';

const VesselMapToggle = ({ currentStyle, onToggle }) => {
  const isSatellite = currentStyle.includes('satellite');

  return (
    <div style={styles.container}>
      <button
        style={{
          ...styles.button,
          ...(isSatellite ? styles.inactive : styles.active)
        }}
        onClick={() => {
          if (isSatellite) onToggle();
        }}
      >
        Navigation view
      </button>
      <button
        style={{
          ...styles.button,
          ...(isSatellite ? styles.active : styles.inactive)
        }}
        onClick={() => {
          if (!isSatellite) onToggle();
        }}
      >
        Satellite view
      </button>
    </div>
  );
};

const styles = {
  container: {
    position: 'absolute',
    top: '10px',
    right: '10px',
    display: 'flex',
    border: '1px solid #007bff',
    borderRadius: '999px',
    overflow: 'hidden',
    backgroundColor: 'white',
    zIndex: 1000,
    boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
  },
  button: {
    padding: '6px 16px',
    border: 'none',
    backgroundColor: 'white',
    color: '#333',
    fontWeight: 'normal',
    cursor: 'pointer',
    outline: 'none',
    transition: 'all 0.2s ease-in-out',
    fontSize: '14px',
    whiteSpace: 'nowrap'
  },
  active: {
    backgroundColor: '#e6f0ff',
    color: '#007bff',
    fontWeight: 'bold'
  },
  inactive: {
    backgroundColor: 'white',
    color: '#333'
  }
};

export default VesselMapToggle;
