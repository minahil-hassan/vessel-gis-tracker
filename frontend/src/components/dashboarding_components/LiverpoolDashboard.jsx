// frontend/src/components/dashboarding_components/LiverpoolDashboard.jsx
// -----------------------------------------------------------------------------
// LiverpoolDashboard
// - Mirrors the UK dashboard and now includes PeakTrafficCard.
// - Responds to `range` changes reliably (force re-mount + notMerge in children).
// - Fetches area traffic for the selected range and renders dock + type charts.
// -----------------------------------------------------------------------------

import React, { useEffect, useMemo, useState } from 'react';
import axiosClient from '../../api/axiosClient';

import SummaryStatsPanel from './SummaryStatsPanel';
import BucketsLineChart from '../charts/BucketsLineChart';
import SummaryLLMCard from './SummaryLLMCard';
import PeakTrafficCard from './PeakTrafficCard';
import AreaTrafficBar from '../charts/AreaTrafficBar';

// Charts
import DockTrafficBarChart from '../dashboard/DockTrafficBarChart';
import ShipTypesStackedChart from '../dashboard/ShipTypesStackedChart';

const EmptyChartState = ({ message = 'No data available for this range.' }) => (
  <div
    className="chart-card neon-glass"
    style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
  >
    <span style={{ color: '#A8B2BF' }}>{message}</span>
  </div>
);

export default function LiverpoolDashboard({
  total,
  groups,
  sparklineData,    // unified Liverpool 6h buckets (array of { t, arrivals })
  series = [],      // per-port Liverpool series (if used by BucketsLineChart)
  range = 7,
  lastUpdated
}) {
  const [areaTraffic, setAreaTraffic] = useState([]);
  const [loadingAreas, setLoadingAreas] = useState(false);
  const [err, setErr] = useState(null);

  // Keys to force re-mount of charts on range/data changes (prevents stale ECharts state)
  const lineKey  = useMemo(
    () => `lpl-line-${range}-${(sparklineData?.length || 0)}-${(series?.length || 0)}`,
    [range, sparklineData, series]
  );
  const dockKey  = useMemo(
    () => `lpl-docks-${range}-${(areaTraffic?.length || 0)}`,
    [range, areaTraffic]
  );
  const typesKey = useMemo(
    () => `lpl-types-${range}-${(areaTraffic?.length || 0)}`,
    [range, areaTraffic]
  );
  const peakKey  = useMemo(
    () => `lpl-peak-${range}-${(sparklineData?.length || 0)}`,
    [range, sparklineData]
  );

  useEffect(() => {
    let cancelled = false;
    const ctrl = new AbortController();

    async function fetchAreas() {
      try {
        setLoadingAreas(true);
        setErr(null);
        // Make sure your FastAPI endpoint reads this `days` param.
        const res = await axiosClient.get('/area-traffic/area-traffic', {
          params: { days: range },
          signal: ctrl.signal
        });
        const rows = res.data?.traffic_data || [];
        if (!cancelled) setAreaTraffic(rows);
      } catch (e) {
        if (!cancelled) {
          if (e?.name === 'CanceledError' || String(e?.message).toLowerCase().includes('cancel')) return;
          setErr(e?.response?.data?.detail || e?.message || 'Failed to load area traffic');
        }
      } finally {
        if (!cancelled) setLoadingAreas(false);
      }
    }

    fetchAreas();
    return () => {
      cancelled = true;
      ctrl.abort();
    };
  }, [range]);

  return (
    <div className="dashboard-section">
      <SummaryStatsPanel
        total={total}
        groups={groups}
        sparklineData={sparklineData}
        viewMode="liverpool"
      />

      {/* Peak traffic insights (busiest 6h slots + weekday/weekend split) */}
      {/* <h4>Peak Traffic (Liverpool)</h4>
      <PeakTrafficCard
        key={peakKey}
        unified={sparklineData}
        height={220}
        title={`Busiest 6-hour slots (last ${range}d)`}
      /> */}

      {/* Arrivals line (6h buckets; BucketsLineChart already adapts labels in your codebase) */}
      {/* <h4>Liverpool Arrivals — 6-hour Buckets (last {range}d)</h4>
      <BucketsLineChart
        key={lineKey}
        series={series}
        unified={sparklineData}
        label="Liverpool"
        height={260}
      /> */}

      {/* Row: 6-hour buckets (left) + Peak Traffic (right) */}
    <div className="chart-grid-2">
      <div className="chart-container">
        <h4 className="chart-title">
          Liverpool Arrivals — 6-hour Buckets (last {range}d)
        </h4>
        <BucketsLineChart
          key={lineKey}
          series={series}
          unified={sparklineData}
          label="Liverpool"
          height={300}
          range={range}
        />
      </div>

      <div className="chart-container">
        <h4 className="chart-title">Peak Traffic (Liverpool)</h4>
        <PeakTrafficCard
          key={peakKey}
          unified={sparklineData}
          height={300}
          title={`Busiest 6-hour slots (last ${range}d)`}
        />
      </div>
    </div>
          

      {/* Per-dock volumes */}
      <h4>Volume per Dock / Terminal</h4>
      {err ? (
        <EmptyChartState message={err} />
      ) : loadingAreas ? (
        <EmptyChartState message="Loading…" />
      ) : areaTraffic?.length ? (
        <DockTrafficBarChart key={dockKey} data={areaTraffic} range={range} />
      ) : (
        <EmptyChartState />
      )}

      {/* Stacked vessel-type groups per dock */}
      <h4>Vessel Type Groups by Dock / Terminal</h4>
      {err ? (
        <EmptyChartState message={err} />
      ) : loadingAreas ? (
        <EmptyChartState message="Loading…" />
      ) : areaTraffic?.length ? (
        <AreaTrafficBar
          key={typesKey}
          data={areaTraffic}
          height={600}
          topN={areaTraffic.length}   // or a fixed number like 20
          stacked={true}              // ensure stacked by vessel-type groups
        />
      ) : (
        <EmptyChartState />
      )}

      {/* AI-generated narrative for the selected window */}
      <div className="chart-container">
        <h4>AI Insights</h4>
        <SummaryLLMCard scope="liverpool" days={range} height={300} lastUpdated={lastUpdated} />
      </div>
    </div>
  );
}
