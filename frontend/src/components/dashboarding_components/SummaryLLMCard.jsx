// import React from 'react';
// import useTrafficSummary from './hooks/useTrafficSummary';
// import './MaritimeDashboardOverlay.css';

// export default function SummaryLLMCard({ scope = 'uk', days = 7, height = 300, title }) {
//   const { summary, insights, loading, error } = useTrafficSummary(scope, days);

//   return (
//     <div className="chart-card neon-glass insight-card" style={{ height }}>
//       <div className="insight-header">
//         <h4 className="insight-title">{title || (scope === 'uk' ? 'UK Summary' : 'Liverpool Summary')}</h4>
//         <span className="insight-sub">last {days}d</span>
//       </div>

//       {loading ? (
//         <div className="insight-loading">Generating summary…</div>
//       ) : error ? (
//         <div className="insight-error">Could not load summary.</div>
//       ) : (
//         <>
//           <div className="insight-body">
//             {/* LLM Text */}
//             <p className="insight-text">{summary}</p>
//           </div>

//           {/* Chips with key metrics */}
//           {insights && (
//             <div className="insight-chips">
//               {'busiest_day' in insights && (
//                 <Chip label="Busiest Day" value={insights.busiest_day} />
//               )}
//               {!!(insights.also_busy_days || []).length && (
//                 <Chip label="Also Busy" value={(insights.also_busy_days || []).join(', ')} />
//               )}
//               {'least_busy_day' in insights && (
//                 <Chip label="Least Busy Day" value={insights.least_busy_day} />
//               )}
//               {'peak_time_slot_utc' in insights && (
//                 <Chip label="Peak Slot (UTC)" value={insights.peak_time_slot_utc} />
//               )}
//               {'top_port' in insights && <Chip label="Top Port" value={insights.top_port} />}
//               {'most_common_vessel_group' in insights && (
//                 <Chip label="Top Vessel Group" value={insights.most_common_vessel_group} />
//               )}
//             </div>
//           )}
//         </>
//       )}
//     </div>
//   );
// }

// function Chip({ label, value }) {
//   return (
//     <span className="insight-chip" title={`${label}: ${value}`}>
//       <span className="chip-label">{label}</span>
//       <span className="chip-value">{value}</span>
//     </span>
//   );
// }

// frontend/src/components/dashboarding_components/SummaryLLMCard.jsx
import React, { useMemo } from 'react';
import useTrafficSummary from './hooks/useTrafficSummary';
import './MaritimeDashboardOverlay.css';

/**
 * SummaryLLMCard
 * - Shows insight chips FIRST (busiest day, etc.)
 * - Then a well formatted, neon-themed report body
 * - Accepts: scope ('uk' | 'liverpool'), days, height, title
 */
export default function SummaryLLMCard({ scope = 'uk', days = 7, height = 300, title }) {
  const { summary, insights, loading, error } = useTrafficSummary(scope, days);

  // Convert minimal markdown (**bold**) + paragraphs -> HTML safely
  const html = useMemo(() => {
    if (!summary) return '';
    // Basic escape
    let safe = summary
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // **bold** -> <strong>
    safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Split on blank lines into paragraphs, keep single newlines as <br>
    const parts = safe.split(/\n{2,}/).map(p => `<p>${p.replace(/\n/g, '<br/>')}</p>`);
    return parts.join('');
  }, [summary]);

  return (
    <div className="chart-card neon-glass insight-card" style={{ height }}>
      <div className="insight-header">
        <h4 className="insight-title">
          {title || (scope === 'uk' ? 'UK Summary' : 'Liverpool Summary')}
        </h4>
        <span className="insight-sub">last {days}d</span>
      </div>

      {loading ? (
        <div className="insight-loading">Generating summary…</div>
      ) : error ? (
        <div className="insight-error">Could not load summary.</div>
      ) : (
        <>
          {/* METRIC CHIPS — now on top */}
          {insights && (
            <div className="insight-chips">
              {'busiest_day' in insights && (
                <Chip label="Busiest Day" value={insights.busiest_day} />
              )}
              {!!(insights.also_busy_days || []).length && (
                <Chip label="Also Busy" value={(insights.also_busy_days || []).join(', ')} />
              )}
              {'least_busy_day' in insights && (
                <Chip label="Least Busy Day" value={insights.least_busy_day} />
              )}
              {'peak_time_slot_utc' in insights && (
                <Chip label="Peak Slot (UTC)" value={insights.peak_time_slot_utc} />
              )}
              {'top_port' in insights && <Chip label="Top Port" value={insights.top_port} />}
              {'most_common_vessel_group' in insights && (
                <Chip label="Top Vessel Group" value={insights.most_common_vessel_group} />
              )}
            </div>
          )}

          {/* Divider */}
          <div className="insight-divider" />

          {/* PROSE */}
          <div className="insight-body">
            <div
              className="insight-text prose-neon"
              // Summary comes from your own backend; bold-only transform applied above.
              dangerouslySetInnerHTML={{ __html: html }}
            />
          </div>
        </>
      )}
    </div>
  );
}

function Chip({ label, value }) {
  return (
    <span className="insight-chip" title={`${label}: ${value}`}>
      <span className="chip-label">{label}</span>
      <span className="chip-value">{value}</span>
    </span>
  );
}

