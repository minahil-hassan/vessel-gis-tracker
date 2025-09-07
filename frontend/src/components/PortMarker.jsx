import { useEffect } from 'react';
import mapboxgl from 'mapbox-gl';

const PortMarker = ({ feature, map }) => {
  useEffect(() => {
    if (!feature?.geometry?.coordinates || !map) return;

    const { geometry, properties } = feature;

    const marker = new mapboxgl.Marker({ color: 'red' })
      .setLngLat(geometry.coordinates)
      .setPopup(
        new mapboxgl.Popup().setHTML(`<b>Port:</b> ${properties.name || 'Unnamed Port'}`)
      )
      .addTo(map);

    return () => marker.remove(); // Cleanup
  }, [feature, map]);

  return null;
};

export default PortMarker;
