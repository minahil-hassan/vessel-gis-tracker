

// export default PortAreaPolygons;
import React, { useEffect, useRef } from 'react';
import axiosClient from '../api/axiosClient';
import mapboxgl from 'mapbox-gl';
import ReactDOM from 'react-dom/client';
import PortAreaPopup from './PortAreaPopup';

const PortAreaPolygons = ({ map }) => {
  const popupRef = useRef(null);

  useEffect(() => {
    if (!map) return;

    // Compute centroid by averaging outer ring coords
    const getCentroid = (coords) => {
      const ring = coords[0];
      let sumX = 0, sumY = 0;
      ring.forEach(([lng, lat]) => { sumX += lng; sumY += lat; });
      return [ sumX / ring.length, sumY / ring.length ];
    };

    const renderPolygons = async () => {
      try {
        const { data } = await axiosClient.get('/port_areas');

        // clean up any existing source/layers
        ['port-fill','port-outline','port-other-fill','port-other-outline'].forEach(id => {
          if (map.getLayer(id)) map.removeLayer(id);
        });
        if (map.getSource('port-areas')) map.removeSource('port-areas');

        // add geojson source
        map.addSource('port-areas', { type: 'geojson', data });

        // colour match expression
        const colorExpr = [
          'match',
          ['downcase', ['get','type']],
          'dock', '#1E90FF',
          'lock', '#8A2BE2',
          'storage facility', '#FFD700',
          'grain terminal', '#DAA520',
          'rail terminal', '#20B2AA',
          'ferry terminal', '#FF4500',
          'container terminal', '#32CD32',
          'steel terminal', '#DC143C',
          '#888888'
        ];

        // 1) draw Ports first
        map.addLayer({
          id: 'port-fill',
          type: 'fill',
          source: 'port-areas',
          filter: ['==', ['get','type'], 'Port'],
          paint: { 'fill-color': '#6666FF', 'fill-opacity': 0.2 }
        });
        map.addLayer({
          id: 'port-outline',
          type: 'line',
          source: 'port-areas',
          filter: ['==', ['get','type'], 'Port'],
          paint: { 'line-color': '#2244AA', 'line-width': 2 }
        });

        // 2) then draw everything else on top
        map.addLayer({
          id: 'port-other-fill',
          type: 'fill',
          source: 'port-areas',
          filter: ['!=', ['get','type'], 'Port'],
          paint: { 'fill-color': colorExpr, 'fill-opacity': 0.4 }
        });
        map.addLayer({
          id: 'port-other-outline',
          type: 'line',
          source: 'port-areas',
          filter: ['!=', ['get','type'], 'Port'],
          paint: { 'line-color': '#00FFAA', 'line-width': 1.5 }
        });

        // attach click & hover to both fill layers
        ['port-fill','port-other-fill'].forEach(layerId => {
          map.on('click', layerId, e => {
            const f = e.features[0];
            const coords = f.geometry.type === 'Point'
              ? f.geometry.coordinates
              : getCentroid(f.geometry.coordinates);

            // remove old popup
            if (popupRef.current) popupRef.current.remove();

            // create new popup container
            const container = document.createElement('div');
            popupRef.current = new mapboxgl.Popup({
              closeOnClick: true,
              offset: 15,
              className: 'popup-glass'
            })
              .setLngLat(coords)
              .setDOMContent(container)
              .addTo(map);

            // render React popup
            ReactDOM.createRoot(container)
              .render(<PortAreaPopup properties={f.properties} />);
          });

          map.on('mouseenter', layerId, () => {
            map.getCanvas().style.cursor = 'pointer';
          });
          map.on('mouseleave', layerId, () => {
            map.getCanvas().style.cursor = '';
          });
        });

      } catch (err) {
        console.error('[PortAreaPolygons] Failed:', err);
      }
    };

    map.on('style.load', renderPolygons);
    if (map.isStyleLoaded()) renderPolygons();

    return () => {
      map.off('style.load', renderPolygons);
      if (popupRef.current) popupRef.current.remove();
    };
  }, [map]);

  return null;
};

export default PortAreaPolygons;
