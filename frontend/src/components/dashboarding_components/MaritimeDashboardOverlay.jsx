
// frontend/src/components/dashboarding_components/MaritimeDashboardOverlay.jsx
//adding comments
import React, { useEffect, useMemo, useState, useCallback } from 'react';
import axiosClient from '../../api/axiosClient';
import TimeRangePicker from '../TimeRangePicker';
import UkDashboard from './UkDashboard';
import LiverpoolDashboard from './LiverpoolDashboard';
import './MaritimeDashboardOverlay.css';
import { flattenBucketSeries, sumTypeGroups } from './dashboardUtils'; // keep helpers here

// Liverpool regex for port matching
const LIVERPOOL_REGEX =
  '(Birkenhead Dock Estate|Port of Liverpool|Port of Garston|Port of Gartson)';

// Main component
export default function MaritimeDashboardOverlay({ isVisible, onClose }) {
  //defining state variables such as viewMode, range, ukTrafficAgg for UK data
  const [viewMode, setViewMode] = useState('uk');   // 'uk' | 'liverpool'
  const [range, setRange]   = useState(7);
  // UK data
  const [ukTrafficAgg, setUkTrafficAgg] = useState({ total: 0, groups: {} });
  const [ukBucketsSeries, setUkBucketsSeries] = useState([]); // per-port
  const [ukUnified, setUkUnified] = useState([]);
  // Liverpool data
  const [livTrafficAgg, setLivTrafficAgg] = useState({ total: 0, groups: {} });
  const [livBucketsSeries, setLivBucketsSeries] = useState([]); // per-port (3 ports)
  const [livUnified, setLivUnified] = useState([]);

  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading] = useState(true);

  // this function fetches all traffic data 
  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      //defining API requests for UK and Liverpool traffic data
      const [ukTrafficRes, livTrafficRes, ukBucketsRes, livBucketsRes] = await Promise.all([
        axiosClient.get('/traffic/uk', { params: { days: range } }),
        axiosClient.get('/traffic', { params: { days: range, port_name_contains: LIVERPOOL_REGEX } }),
        axiosClient.get('/traffic/buckets/uk', { params: { days: range } }),
        axiosClient.get('/traffic/buckets', { params: { days: range, port_name_contains: LIVERPOOL_REGEX } }),
      ]);

      // UK aggregates (arrivals)
      const ukPorts = ukTrafficRes.data?.traffic_data || [];
      setUkTrafficAgg({
        total: ukPorts.reduce((acc, p) => acc + (p.total_traffic || 0), 0),
        groups: sumTypeGroups(ukPorts)
      });

      // UK buckets (series + unified)
      const ukSeries = ukBucketsRes.data?.series || [];
      setUkBucketsSeries(ukSeries);
      setUkUnified(flattenBucketSeries(ukSeries));

      // Liverpool aggregates (arrivals over the three ports)
      const livPorts = livTrafficRes.data?.traffic_data || [];
      setLivTrafficAgg({
        total: livPorts.reduce((acc, p) => acc + (p.total_traffic || 0), 0),
        groups: sumTypeGroups(livPorts)
      });

      // Liverpool buckets (series + unified)
      const livSeries = livBucketsRes.data?.series || [];
      setLivBucketsSeries(livSeries);
      setLivUnified(flattenBucketSeries(livSeries));

      setLastUpdated(new Date());
    } catch (e) {
      console.error('Dashboard overlay fetch failed:', e);
    } finally {
      setLoading(false);
    }
  }, [range]);

  useEffect(() => {
    if (isVisible) fetchAll();
  }, [isVisible, fetchAll]);

  const current = useMemo(() => {
    if (viewMode === 'uk') {
      return {
        total: ukTrafficAgg.total,
        groups: ukTrafficAgg.groups,
        series: ukBucketsSeries,
        unified: ukUnified,
      };
    }
    return {
      total: livTrafficAgg.total,
      groups: livTrafficAgg.groups,
      series: livBucketsSeries,
      unified: livUnified,
    };
  }, [
    viewMode,
    ukTrafficAgg, ukBucketsSeries, ukUnified,
    livTrafficAgg, livBucketsSeries, livUnified
  ]);

  if (!isVisible) return null;

  return (
    <div className="dashboard-overlay">
      <button className="dashboard-close" onClick={onClose}>×</button>

      <div className="dashboard-content">
        <h1 className="dashboard-title">Maritime Traffic Dashboard</h1>
        <p className="dashboard-intro">
          View national and local vessel activity, cargo movement, and passenger flow across UK ports using live AIS data.
        </p>

        <div className="dashboard-controls">
          <div className="toggle-buttons">
            <button
              className={viewMode === 'uk' ? 'active' : ''}
              onClick={() => setViewMode('uk')}
            >
              UK Overview
            </button>
            <button
              className={viewMode === 'liverpool' ? 'active' : ''}
              onClick={() => setViewMode('liverpool')}
            >
              Liverpool Overview
            </button>
          </div>

          <TimeRangePicker
            label="Date Range"
            value={range}
            onChange={setRange}
            options={[1, 2, 3, 7, 14, 30]}
          />
        </div>

        {loading ? (
          <div className="dashboard-loading">Loading data…</div>
        ) : viewMode === 'uk' ? (
          <UkDashboard
            total={current.total}
            groups={current.groups}
            sparklineData={current.unified} // UK SUM curve for the sparkline
            series={current.series}         // UK per-port (used to compute avg)
            range={range}
            lastUpdated={lastUpdated}
          />
        ) : (
          <LiverpoolDashboard
            total={current.total}
            groups={current.groups}
            sparklineData={current.unified}
            series={current.series}
            range={range}
            lastUpdated={lastUpdated}
          />
        )}
      </div>
    </div>
  );
}
