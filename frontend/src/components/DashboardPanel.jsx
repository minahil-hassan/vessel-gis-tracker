// // frontend/src/components/DashboardPanel.jsx
import React, { useEffect, useMemo, useState } from 'react';
import axiosClient from '../api/axiosClient';
import './DashboardPanel.css';
import './VesselSidePanel.css';
import './charts/chartTheme';
import LiverpoolStatsSection from './LiverpoolStatsSection.jsx';
import LastUpdatedFooter from './LastUpdatedFooter';
import TimeRangePicker from './TimeRangePicker.jsx';
import BucketsLineChart from './charts/BucketsLineChart.jsx';
import TypesBarChart from './charts/TypesBarChart.jsx';
import TrendBadge from './charts/TrendBadge.jsx';
import CompareTrafficLine from './charts/CompareTrafficLine.jsx';
import AreaTrafficBar from './charts/AreaTrafficBar.jsx';
import AreaTypesStacked from './charts/AreaTypesStacked.jsx';
import TopAreaFacilities from './TopAreaFacilities.jsx';


/* -------------------------------
   Helpers
-------------------------------- */
function sumTypeGroups(portsArray) {
  // Sums ship type groups across all ports in the array
  return (portsArray || []).reduce((acc, p) => {
    for (const [g, v] of Object.entries(p.ship_type_groups || {})) {
      acc[g] = (acc[g] || 0) + v;
    }
    return acc;
  }, {});
}

function sumTotals(portsArray) {
  // Sums total traffic across all ports in the array
  return (portsArray || []).reduce((acc, p) => acc + (p.total_traffic || 0), 0);
}

/**
 * Flattens a multi-series bucket response into a single time series,
 * summing arrivals by timestamp across all series.
 * Expects input shape: [{ points: [{ t, arrivals }, ...] }, ...]
 */
function flattenBucketSeries(series) {
  const byTs = new Map();
  (series || []).forEach(s => {
    (s.points || []).forEach(pt => {
      const tsIso = new Date(pt.t).toISOString();
      byTs.set(tsIso, (byTs.get(tsIso) || 0) + (pt.arrivals || 0));
    });
  });
  return Array.from(byTs.entries())
    .map(([t, arrivals]) => ({ t: new Date(t), arrivals }))
    .sort((a, b) => a.t - b.t);
}

const RegionSection = ({ title, buckets, unified, groups, label }) => (
  <>
    <div className="dc-section">
      <h4>{title} arrivals trend (6h buckets)</h4>
      <div className="chart-card neon-glass">
        <BucketsLineChart series={buckets} unified={unified} label={label} />
      </div>
    </div>

    <div className="dc-section">
      <h4>{label} vessel type groups</h4>
      <div className="chart-card neon-glass">
        <TypesBarChart groups={groups} />
      </div>
    </div>
  </>
);

const DashboardPanel = () => {
  // Controls
  const [ukDays, setUkDays] = useState(7);
  const [livDays, setLivDays] = useState(3);
  const [liveMode, setLiveMode] = useState(false);

  // Data
  const [ukSummary, setUkSummary] = useState([]);
  const [ukBuckets, setUkBuckets] = useState([]);
  const [livSummary, setLivSummary] = useState([]);
  const [livBuckets, setLivBuckets] = useState([]);
  const [areaTraffic, setAreaTraffic] = useState([]); // Liverpool dock/terminal traffic

  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [ukRes, ukBRes, livRes, livBRes, areaRes] = await Promise.all([
        axiosClient.get('/traffic/uk', { params: { days: ukDays } }),
        axiosClient.get('/traffic/buckets/uk', { params: { days: ukDays } }),
        axiosClient.get('/traffic', { params: { days: livDays, port_name_contains: 'Liverpool' } }),
        axiosClient.get('/traffic/buckets', { params: { days: livDays, port_name_contains: 'Liverpool' } }),
        axiosClient.get('/area-traffic/area-traffic', { params: { days: livDays } }),
      ]);

      setUkSummary(ukRes.data?.traffic_data || []);
      setUkBuckets(ukBRes.data?.series || []);

      setLivSummary(livRes.data?.traffic_data || []);
      setLivBuckets(livBRes.data?.series || []);
      setAreaTraffic(areaRes.data?.traffic_data || []);

      setLastUpdated(new Date());
    } catch (e) {
      console.error('Dashboard fetch failed:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, liveMode ? 60_000 : 300_000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ukDays, livDays, liveMode]);

  // Derived values
  const ukTotals = useMemo(() => sumTotals(ukSummary), [ukSummary]);
  const ukTypeGroups = useMemo(() => sumTypeGroups(ukSummary), [ukSummary]);
  const ukUnifiedBuckets = useMemo(() => flattenBucketSeries(ukBuckets), [ukBuckets]);

  const livTotals = useMemo(() => sumTotals(livSummary), [livSummary]);
  const livTypeGroups = useMemo(() => sumTypeGroups(livSummary), [livSummary]);
  const livUnifiedBuckets = useMemo(() => flattenBucketSeries(livBuckets), [livBuckets]);

  // We cannot compute a previous window from current API responses without an additional call.
  // So we hide the TrendBadge unless you later add a previousWindow fetch.
  const previousTotal = null;

  if (loading) {
    return (
      <div className="dashboard-panel">
        <div className="dashboard-loading">Loading dashboard…</div>
      </div>
    );
  }

  return (
    <div className="dashboard-panel">
      {/* Controls */}
      <div className="dc-controls">
        <TimeRangePicker
          label="UK days"
          value={ukDays}
          onChange={setUkDays}
          options={[1, 2, 3, 7, 14, 30]}
        />
        <TimeRangePicker
          label="Liverpool days"
          value={livDays}
          onChange={setLivDays}
          options={[1, 2, 3, 7, 14]}
        />
        <label className="dc-toggle">
          <input
            type="checkbox"
            checked={liveMode}
            onChange={e => setLiveMode(e.target.checked)}
          />
          <span>Live refresh</span>
        </label>
      </div>

      {/* UK section */}
      <RegionSection
        title="UK"
        buckets={ukBuckets}
        unified={ukUnifiedBuckets}
        groups={ukTypeGroups}
        label="UK"
      />

      {/* Liverpool section */}
      <h3>Liverpool Port (Last {livDays} Day{livDays > 1 ? 's' : ''})</h3>
      <LiverpoolStatsSection
        liverpool={{ vessel_count_last_3d: livTotals }}
      />
      {previousTotal != null && (
        <TrendBadge
          currentTotal={livTotals}
          previousTotalLabel={`${livDays}d prior`}
          previousTotal={previousTotal}
        />
      )}
      <RegionSection
        title="Liverpool"
        buckets={livBuckets}
        unified={livUnifiedBuckets}
        groups={livTypeGroups}
        label="Liverpool"
      />

      
      {/* Liverpool dock/terminal charts */}
      <div className="dc-section">
        <h4>Dock / Terminal traffic (last {livDays} day{livDays > 1 ? 's' : ''})</h4>
        <TopAreaFacilities data={areaTraffic} />
        <AreaTrafficBar data={areaTraffic} height={280} topN={12} />
      </div>

      <div className="dc-section">
        <h4>Ship type groups by dock/terminal</h4>
        <AreaTypesStacked data={areaTraffic} height={320} topN={10} />
      </div>

      {/* UK vs Liverpool comparison */}
    <div className="dc-section">
      <h4>UK vs Liverpool — Arrivals (6h buckets)</h4>
      <div className="chart-card neon-glass">
        <CompareTrafficLine
          ukUnified={ukUnifiedBuckets}
          livUnified={livUnifiedBuckets}
          yLabel="Arrivals"
        />
      </div>
      </div>

      {/* Footer */}
      <hr />
      <LastUpdatedFooter timestamp={lastUpdated} />
    </div>
  );
};

export default DashboardPanel;
