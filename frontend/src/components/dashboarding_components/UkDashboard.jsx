// frontend/src/components/dashboarding_components/UkDashboard.jsx
import React, { useEffect, useMemo, useState } from 'react';
import axiosClient from '../../api/axiosClient';

import SummaryStatsPanel from './SummaryStatsPanel';
import BucketsLineChart from '../charts/BucketsLineChart';
import TypesBarChart from '../charts/TypesBarChart';
import CompareTrafficLineChart from '../charts/CompareTrafficLine';
import AreaTrafficBar from '../charts/AreaTrafficBar';
import { averageBucketSeries, flattenBucketSeries } from './dashboardUtils';
import './MaritimeDashboardOverlay.css';
import PlaceholderCard from './PlaceholderCard';
import PeakTrafficCard from './PeakTrafficCard';
import SummaryLLMCard from './SummaryLLMCard';

// Liverpool scope for compare chart (exact names + common typo)
const LIVERPOOL_PORTS_REGEX =
  '(Birkenhead Dock Estate|Port of Liverpool|Port of Garston|Port of Gartson)';

export default function UkDashboard({
  total,
  groups,              // grouped_vessel_types (UK)
  sparklineData,       // unified UK SUM trend (already flattened)
  series = [],         // per-port series for UK (optional; we’ll fetch if empty)
  range = 7,
  lastUpdated
}) {
  const [ukSeries, setUkSeries] = useState(series);
  const [ukUnifiedSum, setUkUnifiedSum] = useState(sparklineData); // sum curve
  const [livUnified, setLivUnified] = useState([]);                 // Liverpool total
  const [ukTopPorts, setUkTopPorts] = useState([]);                 // from /traffic/uk

  const needBuckets = (ukSeries?.length || 0) === 0 || (ukUnifiedSum?.length || 0) === 0;

  useEffect(() => {
    setUkSeries(series);
    setUkUnifiedSum(sparklineData);
  }, [series, sparklineData]);

 useEffect(() => {
    const fetchWhenNeeded = async () => {
      try {
        const reqs = [
          axiosClient.get('/traffic/uk', { params: { days: range } }),
          axiosClient.get('/traffic/buckets', {
            params: { days: range, port_name_contains: LIVERPOOL_PORTS_REGEX }
          })
        ];
        if (needBuckets) {
          reqs.push(axiosClient.get('/traffic/buckets/uk', { params: { days: range } }));
        }

        const [ukTrafficRes, livBucketsRes, maybeUkBucketsRes] = await Promise.all(reqs);

        // Top 5 ports with GROUPS (key change here)
        const traffic = ukTrafficRes.data?.traffic_data || [];
        const top5 = traffic
          .slice()
          .sort((a, b) => (b.total_traffic || 0) - (a.total_traffic || 0))
          .slice(0, 5)
          .map(p => ({
            area_name: p.area_name,
            total_traffic: p.total_traffic || 0,
            // pass through the group breakdown (either key for safety)
            ship_type_groups: p.ship_type_groups || p.groups || {}
          }));
        setUkTopPorts(top5);

        // Liverpool unified for compare (TOTAL)
        const livSeries = livBucketsRes.data?.series || [];
        setLivUnified(flattenBucketSeries(livSeries));

        // UK buckets if we didn’t have them from overlay
        if (needBuckets) {
          const ukBuckets = maybeUkBucketsRes?.data?.series || [];
          setUkSeries(ukBuckets);
          setUkUnifiedSum(flattenBucketSeries(ukBuckets));
        }
      } catch (e) {
        console.error('UKDashboard fetch failed:', e);
      }
    };

    fetchWhenNeeded();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [range]);

  // Build UK average per timestamp from the per-port series
  const ukUnifiedAvg = useMemo(
    () => averageBucketSeries(ukSeries),
    [ukSeries]
  );

  return (
    <div className="dashboard-section">
      {/* Summary cards */}
      <SummaryStatsPanel
        total={total}
        groups={groups}
        sparklineData={ukUnifiedSum}
        viewMode="uk"
      />

      {/* Line Chart: UK 6h Arrival Buckets (unified + per-port) */}
      {/* The changes required here probably inside the BucketsLineChart component itself are that it needs to change according to the range. also can it be changed to use x axis as days instead of 6 hours (one label for 2 6 hour buckets) whenever the range is greater than 3 */}
      <div className="chart-grid-2">
        {/* BucketsLineChart with its title */}
        <div className="chart-container">
          <h4 className="chart-title">UK Arrivals — 6-hour Buckets (last {range}d)</h4>
          <BucketsLineChart 
            series={ukSeries} 
            unified={ukUnifiedSum} 
            label="UK arrivals" 
            height={300}
            range={range}
          />
        </div>

        {/* PeakTrafficCard with its title */}
        <div className="chart-container">
          <h4 className="chart-title">Peak Vessel Traffic - Insights</h4>
          <PeakTrafficCard
            unified={ukUnifiedSum}
            height={300}
            
          />
        </div>
      </div>

      

      {/* NEW: LLM summary card */}
      <div className="chart-container">
        <h4> AI Insights </h4>
        <SummaryLLMCard scope="uk" days={range} height={300} />
      </div>


      {/* Bar Chart: Vessel Type Group Totals (UK) */}
      {/* to do: for this chart, I like the styles so I need to replicate them for other bar charts specially the ones used in liverpool dashboard. 
      check if these styles can be reused or if they are defined separately . 
    Also, i need to add a section that reuses these vessel type charts to get the types at any one of the UK ports that the user selects. the user should be able to select atleast the top 5 from a drop down at the frontend */}
      <h4>Vessel Type Groups (Arrivals)</h4>
      
        <TypesBarChart groups={groups} height={260} />
        
      

       {/* Horizontal Bar: Top 5 Ports by Traffic (NOW STACKED by vessel type group) */}
      <h4>Top 5 Ports by Traffic</h4>
      
        <AreaTrafficBar
          data={ukTopPorts}
          height={300}
          topN={5}
          stacked={true}  // explicitly stacked; component will detect group data
        />
       
      
      



      {/* Dual Line Chart: UK (avg per port) vs Liverpool (total) */}
      <h4>UK (avg per port) vs Liverpool — Arrivals (6h buckets)</h4>
        
          <div className="chart-card neon-glass" style={{ height: 300 }}>      <CompareTrafficLineChart
                ukUnified={ukUnifiedAvg}
                livUnified={livUnified}     
            />
          </div>
            
       



    </div>
  );
}
