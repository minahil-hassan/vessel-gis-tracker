// frontend/src/components/LiverpoolStatsSection.jsx
import React, { useEffect, useState } from 'react';
import axiosClient from '../api/axiosClient';

export default function LiverpoolStatsSection({ range = 3 }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await axiosClient.get('/dashboard', {
        params: { view: 'liverpool', days: range }
      });
      setData(res.data?.liverpool || {});
    } catch (err) {
      console.error("Failed to load Liverpool stats:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [range]);

  if (loading) {
    return <div className="liverpool-loading">Loading Liverpool stats…</div>;
  }

  const vesselCount = data?.vessel_count ?? 0;
  const avgSpeed = data?.avg_speed ?? 0;

  return (
    <div className="liverpool-stats">
      <ul>
        <li><strong>Vessels Seen:</strong> {vesselCount}</li>
        <li><strong>Avg Speed:</strong> {avgSpeed.toFixed(1)} kn</li>
      </ul>
    </div>
  );
}
