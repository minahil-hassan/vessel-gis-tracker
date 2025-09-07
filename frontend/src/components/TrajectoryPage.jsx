
// src/pages/TrajectoryPage.jsx

import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import axiosClient from '../api/axiosClient';
import TrajectoryOnlyMap from '../components/TrajectoryOnlyMap';

export default function TrajectoryPage() {
  const [params]        = useSearchParams();
  const mmsi            = params.get('mmsi');
  const startTimeParam = params.get('startTime');
  const endTimeParam   = params.get('endTime');

  const [trajectory, setTrajectory] = useState([]);
  const [loading, setLoading]       = useState(true);

  useEffect(() => {
    if (!mmsi) return;
    const fetch = async () => {
      setLoading(true);
      const p = { limit: 500 };
      if (startTimeParam) p.start_time = startTimeParam;
      if (endTimeParam)   p.end_time   = endTimeParam;
      try {
        const res = await axiosClient.get(`/vessel_history/${mmsi}`, { params: p });
        setTrajectory(res.data.trajectory || []);
      } catch (err) {
        console.error('Failed to fetch trajectory:', err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [mmsi, startTimeParam, endTimeParam]);

  if (loading) {
    return <p style={{ padding: 20 }}>Loading trajectory&hellip;</p>;
  }

  return (
    <div style={{ position: 'absolute', top: 0, bottom: 0, width: '100%' }}>
      <TrajectoryOnlyMap trajectory={trajectory} />
    </div>
  );
}
