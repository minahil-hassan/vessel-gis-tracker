import React, { useMemo } from 'react';
import './MaritimeDashboardOverlay.css';
import {
  computeSixHourDistributions,
  fmtSixHourSlotLabel,
  maxWithPercent
} from './dashboardUtils';


/**
 * PeakTrafficCard
 * Displays:
 *  - Busiest Hour (all days)
 *  - Busiest Hour (weekdays only)
 *  - Busiest Hour (weekend only)
 *  - Busiest Day of Week
 *  - Compact spark-bar histograms for Hourly and Weekday distributions
 *
 * Props:
 *  - unified: [{ t: Date|ISO, arrivals: number }]
 *  - height: number (card height to match a chart)
 *  - title: optional title
 */
const order = [0, 6, 12, 18];
const weekOrder = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];

export default function PeakTrafficCard({ unified = [], height = 300 }) {

  const {
    slotsAll,
    slotsWeekdayOnly,
    slotsWeekendOnly,
    weekday,
  } = useMemo(() => computeSixHourDistributions(unified), [unified]);

  // Top KPIs
  const busiestAll = useMemo(() => {
    const { key, percent } = maxWithPercent(slotsAll);
    return { slot: Number(key), label: fmtSixHourSlotLabel(Number(key)), percent };
  }, [slotsAll]);

  const busiestWeekdays = useMemo(() => {
    const { key, percent } = maxWithPercent(slotsWeekdayOnly);
    return { slot: Number(key), label: fmtSixHourSlotLabel(Number(key)), percent };
  }, [slotsWeekdayOnly]);

  const busiestWeekend = useMemo(() => {
  const { key, percent } = maxWithPercent(slotsWeekendOnly);
    return { slot: Number(key), label: fmtSixHourSlotLabel(Number(key)), percent };
  }, [slotsWeekendOnly]);

  // Busiest day of the week (unchanged)
  const busiestDay = useMemo(() => {
    const { key, percent } = maxWithPercent(weekday);
    return { name: key, percent };
  }, [weekday]);

 // --- Mini bars: per 6-hour slot (UTC) ---
 
  const slotBars = useMemo(() => {
    const vals = order.map(h => ({ slot: h, val: Number(slotsAll[h] || 0) }));
    const max = Math.max(1, ...vals.map(v => v.val));
    return vals.map(v => ({
      ...v,
      pct: (v.val / max) * 100,
      label: fmtSixHourSlotLabel(v.slot),
    }));
  }, [slotsAll]);

 
  const weekdayBars = useMemo(() => {
    const vals = weekOrder.map(name => ({ name, y: Number(weekday[name] || 0) }));
    const max = Math.max(1, ...vals.map(v => v.y));
    return vals.map(v => ({ ...v, pct: (v.y / max) * 100 }));
  }, [weekday]);

   return (
    <div className="chart-card neon-glass peak-card" style={{ height }}>
      {/* KPI row */}
      <div className="peak-kpis">
        <KpiBlock
          title="Busiest 6-hour slot (UTC)"
          big={busiestAll.label}
          sub={`${busiestAll.percent.toFixed(1)}% of arrivals`}
        />
        <KpiBlock
          title="(weekdays only)"
          big={busiestWeekdays.label}
          sub={`${busiestWeekdays.percent.toFixed(1)}% of arrivals`}
        />
        <KpiBlock
          title="(weekend only)"
          big={busiestWeekend.label}
          sub={`${busiestWeekend.percent.toFixed(1)}% of arrivals`}
        />
        <KpiBlock
          title="Busiest Day of the week"
          big={`${busiestDay.name || '–'}`}
          sub={`${busiestDay.percent.toFixed(1)}% of arrivals`}
        />
      </div>

      {/* Mini histograms */}
      <div className="peak-bars">
        <div className="peak-bar-card">
          <div className="peak-bar-title">Traffic per 6 hours (UTC)</div>
          <div className="peak-bar-row" aria-label="6-hour slot traffic bars">
            {slotBars.map(b => (
              <span
                key={b.slot}
                className={`bar ${b.slot === busiestAll.slot ? 'bar-active' : ''}`}
                style={{ height: `${Math.max(6, b.pct)}%` }}
                title={`${b.label} • ${b.val.toLocaleString()} arrivals`}
              />
            ))}
          </div>
          <div className="peak-bar-xlabels">
            {slotBars.map(b => <span key={b.slot}>{b.label}</span>)}
          </div>
        </div>

        <div className="peak-bar-card">
          <div className="peak-bar-title">Traffic per day of week</div>
          <div className="peak-bar-row" aria-label="Weekday traffic bars">
            {weekdayBars.map(b => (
              <span
                key={b.name}
                className={`bar ${b.name === (busiestDay.name || '') ? 'bar-active' : ''}`}
                style={{ height: `${Math.max(6, b.pct)}%` }}
                title={`${b.name} • ${b.y.toLocaleString()} arrivals`}
              />
            ))}
          </div>
          <div className="peak-bar-xlabels">
            {weekOrder.map(w => <span key={w}>{w.slice(0,3)}</span>)}
          </div>
        </div>
      </div>
    </div>
  );
}


function KpiBlock({ icon, title, big, sub }) {
  return (
    <div className="kpi">
      <div className="kpi-icon" aria-hidden>{icon}</div>
      <div className="kpi-texts">
        <div className="kpi-title">{title}</div>
        <div className="kpi-big">{big}</div>
        <div className="kpi-sub">{sub}</div>
      </div>
    </div>
  );
}
