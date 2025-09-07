import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import mapboxgl from 'mapbox-gl';

const VesselMarker = ({ feature, map, mapStyle, isActive, onClick }) => {
  const { geometry, properties } = feature;
  const rotation = typeof properties.heading === 'number'
    ? properties.heading
    : typeof properties.cog === 'number'
    ? properties.cog
    : 0;

  const contentRef = useRef(document.createElement('div'));
  const markerRef = useRef(null);

  useEffect(() => {
    markerRef.current = new mapboxgl.Marker(contentRef.current)
      .setLngLat(geometry.coordinates)
      .addTo(map);
    return () => markerRef.current.remove();
  }, [map]);

  const icon = mapStyle.includes('satellite') ? '/orange_pointer.png' : '/vessel_pointer.png';

  return createPortal(
    <div
      onClick={() => onClick?.(feature)}
      style={{
        width: '30px',
        height: '30px',
        backgroundImage: `url(${icon})`,
        backgroundSize: 'contain',
        backgroundRepeat: 'no-repeat',
        transform: `rotate(${rotation}deg)`,
        transformOrigin: 'center',
        cursor: 'pointer',
        filter: isActive ? 'drop-shadow(0 0 6px orange)' : 'none',
        transition: 'filter 0.3s ease'
      }}
    />,
    contentRef.current
  );
};

export default VesselMarker;

