import { useEffect, useRef, useState } from 'react';
import './TrajectorySimulator.css';
import mapboxgl from 'mapbox-gl';

// Safely normalize any trajectory coordinate to [lon, lat]
const normalizeCoordinate = (point) => {
  if (!point) return null;
  const raw = point.coordinates;
  const coord = Array.isArray(raw) ? raw : raw?.coordinates;
  return (
    Array.isArray(coord) &&
    coord.length === 2 &&
    !isNaN(coord[0]) &&
    !isNaN(coord[1])
  ) ? coord : null;
};

const TrajectorySimulator = ({ map, trajectory, visible }) => {
  const markerRef = useRef(null);         // Ref to the moving ship marker
  const animationRef = useRef(null);      // Ref to the animation frame
  const [index, setIndex] = useState(0);  // Current coordinate index
  const [forward, setForward] = useState(true); // Forward/backward toggle
  const [running, setRunning] = useState(false); // Whether simulation is active
  const [buttonPos, setButtonPos] = useState(null); // Screen position of start/stop button
  // Recalculate button position and add marker
  useEffect(() => {
    if (!map || !trajectory || trajectory.length < 2 || !visible) return;
    const lastCoord = normalizeCoordinate(trajectory[trajectory.length - 1]);
    if (!lastCoord) return;
    // Create marker if it doesn't exist
    if (!markerRef.current) {
      const el = document.createElement('div');
      el.className = 'ship-marker';
      markerRef.current = new mapboxgl.Marker(el).setLngLat(lastCoord).addTo(map);
    }

    // Project last coordinate to screen for button positioning
    const projected = map.project(lastCoord);
    setButtonPos({ left: projected.x, top: projected.y });

    // Reset simulation state
    setIndex(0);
    setForward(true);
    setRunning(false);

    return () => {
      if (markerRef.current) {
        markerRef.current.remove();
        markerRef.current = null;
      }
      cancelAnimationFrame(animationRef.current);
      setButtonPos(null);
    };
  }, [map, trajectory, visible]);

  // Animation logic
  useEffect(() => {
    if (!running || !map || !trajectory || trajectory.length < 2) return;

    const step = () => {
      let newIndex = forward ? index + 1 : index - 1;

      // Bounce back at ends
      if (newIndex >= trajectory.length || newIndex < 0) {
        setForward(!forward);
        animationRef.current = requestAnimationFrame(step);
        return;
      }
      const coord = normalizeCoordinate(trajectory[newIndex]);
      if (!coord || !markerRef.current) {
        setTimeout(() => animationRef.current = requestAnimationFrame(step), 250);
        return;
      }
      // Update marker and recenter map
      // Update marker
        markerRef.current.setLngLat(coord);

        // Only pan the map if still running
        if (running) {
        map.panTo(coord, { duration: 300 });
        }
        setIndex(newIndex);

      // Slightly slowed down speed (~350ms per frame)
      setTimeout(() => {
        animationRef.current = requestAnimationFrame(step);
      }, 250);
    };

    animationRef.current = requestAnimationFrame(step);

    return () => cancelAnimationFrame(animationRef.current);
  }, [running, index, forward, map, trajectory]);

  // Toggle button click
  const toggleSimulation = () => {
    setRunning(prev => !prev);
  };

  // Only render button when visible and position known
  return (
    <>
      {visible && buttonPos && (
        <div
          className="sim-button-thin"
          style={{
            position: 'absolute',
            top: `${buttonPos.top}px`,
            left: `${buttonPos.left + 24}px`,
            zIndex: 20
          }}
          onClick={toggleSimulation}
        >
          {running ? 'Stop' : 'Start'}
        </div>
      )}
    </>
  );
};

export default TrajectorySimulator;
