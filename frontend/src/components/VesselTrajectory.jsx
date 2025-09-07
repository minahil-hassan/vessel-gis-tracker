import { useEffect } from 'react';
import mapboxgl from 'mapbox-gl';

const VesselTrajectory = ({ map, trajectory }) => {
  useEffect(() => {
    if (!map || !trajectory || trajectory.length < 2) return;

    // Step 1: Parse trajectory coordinates
    const coordinates = trajectory.map(p =>
      Array.isArray(p.coordinates)
        ? p.coordinates
        : p.coordinates.coordinates
    );

    // Step 2: Create GeoJSON LineString for path
    const lineGeoJSON = {
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates
      }
    };

    // Step 2.5: Create GeoJSON for directional arrows
    const directionFeatures = [];

    for (let i = 0; i < coordinates.length - 1; i += Math.ceil(coordinates.length / 10)) {
      const [lon1, lat1] = coordinates[i];
      const [lon2, lat2] = coordinates[i + 1];

      const bearing = Math.atan2(
        Math.sin((lon2 - lon1) * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180),
        Math.cos(lat1 * Math.PI / 180) * Math.sin(lat2 * Math.PI / 180) -
          Math.sin(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.cos((lon2 - lon1) * Math.PI / 180)
      ) * 180 / Math.PI;

      directionFeatures.push({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: coordinates[i]
        },
        properties: {
          bearing
        }
      });
    }

    const directionGeoJSON = {
      type: 'FeatureCollection',
      features: directionFeatures
    };
    // Step 3: Create GeoJSON FeatureCollection for each point
    const pointGeoJSON = {
      type: 'FeatureCollection',
      features: coordinates.map((coord, index) => ({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: coord
        },
        properties: {
          title: `Lat: ${coord[1].toFixed(4)}, Lon: ${coord[0].toFixed(4)}`
        }
      }))
    };

    // Step 4: Remove any existing trajectory layers/sources
    if (map.getSource('trajectory')) {
      map.removeLayer('trajectory-line');
      map.removeSource('trajectory');
    }
    if (map.getSource('trajectory-points')) {
      map.removeLayer('trajectory-points');
      map.removeSource('trajectory-points');
    }

    // Step 5: Add neon trajectory line
    map.addSource('trajectory', {
      type: 'geojson',
      data: lineGeoJSON
    });

    map.addLayer({
      id: 'trajectory-line',
      type: 'line',
      source: 'trajectory',
      paint: {
        'line-color': '#00f7ff',      // Neon cyan
        'line-width': 2,
        'line-opacity': 0.9,
        'line-blur': 1.8,
        'line-dasharray': [2, 2] // Optional: dashed line effect
      },
      layout: {
        'line-cap': 'round',
        'line-join': 'round'
      }
    });

    // Step 6: Add neon points at each coordinate
    map.addSource('trajectory-points', {
      type: 'geojson',
      data: pointGeoJSON
    });

    map.addLayer({
      id: 'trajectory-points',
      type: 'symbol',
      source: 'trajectory-points',
      layout: {
        'text-field': '•',
        'text-size': 16,
        'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
        'text-anchor': 'center'
      },
      paint: {
        'text-color': '#00f7ff',       // Neon cyan
        'text-halo-color': '#00f7ff',
        'text-halo-width': 1.2,
        'text-opacity': 0.9
      }
    });

    // Step 6.5: Add directional arrows
    if (map.getSource('trajectory-arrows')) {
      map.removeLayer('trajectory-arrows');
      map.removeSource('trajectory-arrows');
    }

    map.addSource('trajectory-arrows', {
      type: 'geojson',
      data: directionGeoJSON
    });

      map.addLayer({
      id: 'trajectory-arrows',
      type: 'symbol',
      source: 'trajectory-arrows',
      layout: {
        'text-field': '▴',
        'text-size': 35,
        'text-rotate': ['get', 'bearing'],
        'text-rotation-alignment': 'map',
        'text-allow-overlap': true
      },
      paint: {
        'text-color': '#ff9900'
      }
    });

    map.moveLayer('trajectory-arrows');
    console.log('Direction features:', directionGeoJSON.features);



    // Step 7: Tooltip behavior on hover
    map.on('mouseenter', 'trajectory-points', () => {
      map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'trajectory-points', () => {
      map.getCanvas().style.cursor = '';
      map.getCanvas().title = '';
    });

    map.on('mousemove', 'trajectory-points', (e) => {
      const title = e.features[0]?.properties?.title;
      if (title) {
        map.getCanvas().title = title;
      }
    });

    // Step 8: Cleanup on unmount
    return () => {
      if (map.getSource('trajectory')) {
        map.removeLayer('trajectory-line');
        map.removeSource('trajectory');
      }
      if (map.getSource('trajectory-arrows')) {
        map.removeLayer('trajectory-arrows');
        map.removeSource('trajectory-arrows');
      }
      if (map.getSource('trajectory-points')) {
        map.removeLayer('trajectory-points');
        map.removeSource('trajectory-points');
        map.getCanvas().title = '';
      }
    };
  }, [map, trajectory]);

  return null;
};

export default VesselTrajectory;
