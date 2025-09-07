// src/components/VesselMap.jsx

import React, { useEffect, useRef, useState } from 'react';
import axiosClient from '../api/axiosClient';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

import VesselMarker from './VesselMarker';
import VesselSidePanel from './VesselSidePanel';
import PortMarker from './PortMarker';
import PortAreaPolygons from './PortAreaPolygons';
import VesselTrajectory from './VesselTrajectory';
import TrajectorySimulator from './TrajectorySimulator';

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;

/**
 * VesselMap renders:
 *  - a Mapbox GL JS map
 *  - vessel & port markers
 *  - port-area polygons (via PortAreaPolygons)
 *  - vessel trajectory & simulator
 *  - side panel on vessel click
 *
 * Props:
 * - mapStyle: Mapbox style URI
 * - onToggleStyle: callback to flip styles (unused here)
 * - filterCities: array of { label, value, coord } to auto-center map
 */
  
  const VesselMap = ({ mapStyle, filterCities = [], selectedLayers = [] }) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);

  // Data state
  const [vessels, setVessels] = useState([]);
  const [ports, setPorts]       = useState([]);
  const [activeFeature, setActiveFeature] = useState(null);
  const [popupData, setPopupData]         = useState(null);
  const [trajectory, setTrajectory]       = useState([]);
  const [startTime, setStartTime]         = useState('');
  const [endTime, setEndTime]             = useState('');
  const [loadingTrajectory, setLoadingTrajectory] = useState(false);
  
  // Fetch trajectory
  const fetchTrajectoryFor = async (mmsi) => {
    setLoadingTrajectory(true);
    setTrajectory([]);
    const params = { limit: 500 };
    if (startTime) params.start_time = new Date(startTime).toISOString();
    if (endTime)   params.end_time   = new Date(endTime).toISOString();
    try {
      const { data } = await axiosClient.get(`/vessel_history/${mmsi}`, { params });
      setTrajectory(data.trajectory);
    } catch {
      console.error('Failed to fetch trajectory');
    } finally {
      setLoadingTrajectory(false);
    }
  };
  const clearTrajectory = () => setTrajectory([]);

  // Initialize or re-style map when mapStyle changes
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (mapRef.current) {
      mapRef.current.setStyle(mapStyle);
      return;
    }

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: mapStyle,
      center: [-3, 55],
      zoom: 5,
      pitch: 45,
      bearing: -30,
      antialias: true
    });

    map.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), 'bottom-right');

    map.on('style.load', () => {
      // Terrain + sky layers
      if (!map.getSource('mapbox-dem')) {
        map.addSource('mapbox-dem', {
          type: 'raster-dem',
          url: 'mapbox://mapbox.terrain-rgb',
          tileSize: 512,
          maxzoom: 14
        });
      }
      map.setTerrain({ source: 'mapbox-dem', exaggeration: 1.5 });

      if (!map.getLayer('sky')) {
        map.addLayer({
          id: 'sky',
          type: 'sky',
          paint: {
            'sky-type': 'atmosphere',
            'sky-atmosphere-sun': [0, 0],
            'sky-atmosphere-sun-intensity': 15
          }
        });
      }

      // Let PortAreaPolygons re-add itself on style.load
    });

    mapRef.current = map;
  }, [mapStyle]);

  // Fly to city when filterCities changes
  useEffect(() => {
    if (filterCities.length > 0 && mapRef.current) {
      const [lng, lat] = filterCities[0].coord;
      mapRef.current.flyTo({ center: [lng, lat], zoom: 10 });
    }
  }, [filterCities]);

  // Load ports
  useEffect(() => {
    axiosClient.get('/ports')
      .then(res => setPorts(res.data.features))
      .catch(() => console.error('Failed to load ports'));
  }, []);

  // Fetch popup data on vessel select
  useEffect(() => {
    if (!activeFeature) {
      setPopupData(null);
      return;
    }
    axiosClient.get(`/vessel_popup/${activeFeature.properties.mmsi}`)
      .then(res => setPopupData(res.data))
      .catch(() => {
        console.error('Failed to load popup data');
        setPopupData(null);
      });
  }, [activeFeature]);

  // Poll vessels
  useEffect(() => {
    const fetchVessels = async () => {
      try {
        const res = await axiosClient.get('/vessels');
        setVessels(res.data.features);
      } catch {
        console.error('Failed to load vessels');
      }
    };
    fetchVessels();
    const id = setInterval(fetchVessels, 30000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
  const handler = (e) => {
    if (!mapRef.current || !e.detail) return;
    const [lon, lat] = e.detail;
    mapRef.current.flyTo({ center: [lon, lat], zoom: 12 });
  };

  window.addEventListener('flyToCoords', handler);
  return () => window.removeEventListener('flyToCoords', handler);
}, []);


  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Map */}
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Vessels */}
      {mapRef.current && vessels.map(v => (
        <VesselMarker
          key={v.properties.mmsi}
          feature={v}
          map={mapRef.current}
          mapStyle={mapStyle}
          isActive={activeFeature?.properties.mmsi === v.properties.mmsi}
          onClick={setActiveFeature}
        />
      ))}

      {/* Side Panel */}
      {mapRef.current && activeFeature && (
        <VesselSidePanel
          map={mapRef.current}
          activeFeature={activeFeature}
          popupData={popupData}
          startTime={startTime}
          endTime={endTime}
          setStartTime={setStartTime}
          setEndTime={setEndTime}
          onShowTrajectory={() => fetchTrajectoryFor(activeFeature.properties.mmsi)}
          onClearTrajectory={clearTrajectory}
          loading={loadingTrajectory}
          closePanel={() => setActiveFeature(null)}
        />
      )}

      {/* Ports */}
      {mapRef.current && ports.map((port, i) => (
        <PortMarker
          key={`${port.properties.locode || port.properties.name}-${i}`}
          feature={port}
          map={mapRef.current}
        />
      ))}

      {/* Port-area Polygons */}
      {/* only show these polygons if user selected that layer */}
      {mapRef.current && selectedLayers.includes('port-areas') && (
        <PortAreaPolygons map={mapRef.current} />
      )}


      {/* Trajectory */}
      {mapRef.current && trajectory.length > 1 && (
        <>
          <VesselTrajectory map={mapRef.current} trajectory={trajectory} />
          <TrajectorySimulator map={mapRef.current} trajectory={trajectory} visible />
        </>
      )}
    </div>
  );
};

export default VesselMap;
