// frontend/src/components/dashboarding_components/dashboardUtils.js

// Utility function to flatten the bucket series for easier processing
export function flattenBucketSeries(series) {
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

export function sumTypeGroups(portsArray) {
  return (portsArray || []).reduce((acc, p) => {
    for (const [g, v] of Object.entries(p.ship_type_groups || {})) {
      acc[g] = (acc[g] || 0) + v;
    }
    return acc;
  }, {});
}

// frontend/src/components/dashboarding_components/dashboardUtils.js

/**
 * Average arrivals per timestamp across the given per-port series.
 * Input: [{ port_name, points: [{ t, arrivals }, ...] }, ...]
 * Output: [{ t: Date, arrivals: number }, ...]  // average at each timestamp
 */
export function averageBucketSeries(series = []) {
  const byTs = new Map(); // ts -> { sum, count }
  for (const s of series || []) {
    for (const p of s.points || []) {
      const ts = new Date(p.t).getTime();
      const rec = byTs.get(ts) || { sum: 0, count: 0 };
      rec.sum += (p.arrivals || 0);
      rec.count += 1;
      byTs.set(ts, rec);
    }
  }
  return Array.from(byTs.entries())
    .map(([t, { sum, count }]) => ({
      t: new Date(t),
      arrivals: count ? sum / count : 0
    }))
    .sort((a, b) => a.t - b.t);
}

/**
 * Compute totals by hour-of-day and day-of-week from a unified [{t, arrivals}] series.
 * Returns:
 *   - hourly: number[24]  // totals per hour (0..23)
 *   - weekday: { Monday..Sunday: number }
 *   - weekdayOnlyHourly: number[24]  // using Mon-Fri only
 *   - weekendOnlyHourly: number[24]  // using Sat-Sun only
 */
export function computeTemporalDistribution(unified = []) {
  const weekdayNames = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const weekday = { Sunday:0, Monday:0, Tuesday:0, Wednesday:0, Thursday:0, Friday:0, Saturday:0 };
  const hourly = new Array(24).fill(0);
  const weekdayOnlyHourly = new Array(24).fill(0);
  const weekendOnlyHourly = new Array(24).fill(0);

  for (const p of unified || []) {
    if (!p || !p.t) continue;
    const d = new Date(p.t);
    const cnt = Number(p.arrivals || 0);
    const dowIdx = d.getUTCDay();  // use UTC to remain consistent with bucket timestamps
    const hour = d.getUTCHours();

    hourly[hour] += cnt;
    const name = weekdayNames[dowIdx];
    weekday[name] += cnt;

    if (dowIdx >= 1 && dowIdx <= 5) { // Mon..Fri
      weekdayOnlyHourly[hour] += cnt;
    } else { // Sat/Sun
      weekendOnlyHourly[hour] += cnt;
    }
  }

  return { hourly, weekday, weekdayOnlyHourly, weekendOnlyHourly };
}

/** Format an hour integer (0–23) like "4pm" */
export function fmtHourShort(h) {
  const hours = Number(h) % 24;
  const ampm = hours >= 12 ? 'pm' : 'am';
  const hr12 = hours % 12 === 0 ? 12 : hours % 12;
  return `${hr12}${ampm}`;
}

/** Return {label, percent} for the max item of a numeric array or object */
export function maxWithPercent(collection) {
  if (Array.isArray(collection)) {
    const total = collection.reduce((a,b)=>a+Number(b||0),0) || 1;
    let idx = 0, maxVal = -Infinity;
    collection.forEach((v,i)=>{ if (v>maxVal){maxVal=v; idx=i;} });
    return { index: idx, value: maxVal, percent: (maxVal/total)*100 };
  }
  // object map
  const entries = Object.entries(collection || {});
  const total = entries.reduce((a, [,v])=>a+Number(v||0),0) || 1;
  let best = entries[0] || ['N/A',0];
  for (const e of entries) if (Number(e[1]) > Number(best[1])) best = e;
  return { key: best[0], value: best[1], percent: (Number(best[1])/total)*100 };
}

// dashboardUtils.js

// NEW: label like "00–06", "06–12", etc.
export function fmtSixHourSlotLabel(startHour) {
  const pad = n => String(n).padStart(2, '0');
  const end = (startHour + 6) % 24;
  return `${pad(startHour)}–${pad(end)}`;
}

// NEW: compute 6h slot totals (UTC) for all / weekdays / weekends
export function computeSixHourDistributions(unified = []) {
  const slotsAll = { 0:0, 6:0, 12:0, 18:0 };
  const slotsWeekdayOnly = { 0:0, 6:0, 12:0, 18:0 };
  const slotsWeekendOnly = { 0:0, 6:0, 12:0, 18:0 };
  const weekday = { Sunday:0, Monday:0, Tuesday:0, Wednesday:0, Thursday:0, Friday:0, Saturday:0 };
  const weekdayNames = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

  for (const p of unified || []) {
    if (!p || !p.t) continue;
    const d = new Date(p.t);
    const cnt = Number(p.arrivals || 0);
    const h = d.getUTCHours();
    const dow = d.getUTCDay(); // 0=Sun..6=Sat
    const slot = (Math.floor(h / 6) * 6) % 24;

    slotsAll[slot] += cnt;
    const name = weekdayNames[dow];
    weekday[name] += cnt;

    if (dow >= 1 && dow <= 5) {
      slotsWeekdayOnly[slot] += cnt;
    } else {
      slotsWeekendOnly[slot] += cnt;
    }
  }

  return { slotsAll, slotsWeekdayOnly, slotsWeekendOnly, weekday };
}

// Small utility you already have but mirrored for objects
export function maxKeyWithPercent(obj) {
  const entries = Object.entries(obj || {});
  const total = entries.reduce((a,[,v]) => a + Number(v || 0), 0) || 1;
  let best = entries[0] || ['0', 0];
  for (const e of entries) if (Number(e[1]) > Number(best[1])) best = e;
  return { key: best[0], value: Number(best[1]), percent: (Number(best[1]) / total) * 100 };
}





