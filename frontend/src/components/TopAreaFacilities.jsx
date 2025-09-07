// frontend/src/components/TopAreaFacilities.jsx
import React, { useEffect, useMemo, useState } from 'react';
import axiosClient from '../api/axiosClient';

/**
 * Props:
 *  - data: [{ area_name, total_traffic, ... }, ...]  // from /area-traffic
 *  - maxAreas: number (default 3)
 *  - maxItems: number (default 5)
 */
const TopAreaFacilities = ({ data = [], maxAreas = 3, maxItems = 5 }) => {
  const [rows, setRows] = useState([]);

  const topNames = useMemo(() => {
    const arr = (Array.isArray(data) ? data.slice() : [])
      .sort((a, b) => (b.total_traffic || 0) - (a.total_traffic || 0))
      .slice(0, maxAreas)
      .map(r => r.area_name)
      .filter(Boolean);
    return arr;
  }, [data, maxAreas]);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      if (!topNames.length) {
        setRows([]);
        return;
      }
      try {
        const res = await axiosClient.get('/port-areas/facilities', {
          params: { names: topNames },
          paramsSerializer: (p) => topNames.map(n => `names=${encodeURIComponent(n)}`).join('&')
        });
        if (!cancelled) {
          const areas = res?.data?.areas || [];
          // cap items per area
          setRows(areas.map(a => ({
            name: a.name,
            facilities: (a.facilities || []).slice(0, maxItems)
          })));
        }
      } catch {
        if (!cancelled) setRows([]); // fail silently; component hides
      }
    }
    run();
    return () => { cancelled = true; };
  }, [topNames, maxItems]);

  if (!rows.length) return null;

  return (
    <div className="facilities-wrap">
      {rows.map((r) => (
        <div key={r.name} className="facilities-card neon-glass">
          <div className="facilities-title">{r.name}</div>
          {r.facilities?.length ? (
            <ul className="facilities-list">
              {r.facilities.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          ) : (
            <div className="facilities-empty">No facility details available.</div>
          )}
        </div>
      ))}
    </div>
  );
};

export default TopAreaFacilities;
