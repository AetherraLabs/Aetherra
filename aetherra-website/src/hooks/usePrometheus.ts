import { useEffect, useState } from 'react';
import { parsePrometheusText, PromSample } from '../utils/prometheus';

export default function usePrometheus(url: string = '/metrics', intervalMs = 5000) {
    const [data, setData] = useState<PromSample[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const isStaticHost = typeof window !== 'undefined' && /(?:^|\.)aetherra\.dev$/i.test(window.location.hostname);
        const explicitlyEnabled = (import.meta as any)?.env?.VITE_ENABLE_PROM;
        if (isStaticHost && !explicitlyEnabled) {
            setData([]);
            setError(null);
            setLoading(false);
            return;
        }

        let cancelled = false;
        let timer: any;

        const fetchOnce = async () => {
            try {
                const res = await fetch(url, { cache: 'no-store' });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const text = await res.text();
                const samples = parsePrometheusText(text);
                if (!cancelled) {
                    setData(samples);
                    setError(null);
                    setLoading(false);
                }
            } catch (e: any) {
                if (!cancelled) {
                    setError(e?.message || 'fetch failed');
                    setLoading(false);
                }
            }
        };

        fetchOnce();
        timer = setInterval(fetchOnce, intervalMs);
        return () => {
            cancelled = true;
            if (timer) clearInterval(timer);
        };
    }, [url, intervalMs]);

    return { data, error, loading };
}
