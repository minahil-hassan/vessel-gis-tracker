import { useEffect, useState } from 'react';
import axiosClient from '../../../api/axiosClient';

export default function useTrafficSummary(scope = 'uk', days = 7) {
  const [summary, setSummary] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();

    async function run() {
      setLoading(true);
      setError(null);
      try {
        // NOTE: axiosClient likely has baseURL '/api', so this becomes:
        // GET /api/traffic-insights/traffic-insights/:scope?days=...
        const { data } = await axiosClient.get(
          `/traffic-insights/traffic-insights/${scope}`,
          { params: { days }, signal: controller.signal }
        );
        if (!cancelled) {
          setSummary(data?.summary_llm || '');
          setInsights(data?.insight_data || {});
        }
      } catch (e) {
        if (!cancelled) setError(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    run();
    return () => { cancelled = true; controller.abort(); };
  }, [scope, days]);

  return { summary, insights, loading, error };
}
