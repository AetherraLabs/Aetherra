import { useEffect, useState } from 'react';

export type HubPlugin = {
    name?: string;
    version?: string;
    id?: string;
    [k: string]: any;
};

export default function useHubPlugins(url: string = '/api/plugins', intervalMs = 10000) {
    const [plugins, setPlugins] = useState<HubPlugin[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        // In static deployments (like GitHub Pages at aetherra.dev), there's no backend.
        // Avoid noisy 404s by short-circuiting unless explicitly enabled.
        const isStaticHost = typeof window !== 'undefined' && /(?:^|\.)aetherra\.dev$/i.test(window.location.hostname);
        const explicitlyEnabled = (import.meta as any)?.env?.VITE_ENABLE_HUB_POLLING;
        if (isStaticHost && !explicitlyEnabled) {
            setPlugins([]);
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
                const json = await res.json();
                const arr = Array.isArray(json) ? json : (json?.plugins ?? []);
                if (!cancelled) {
                    setPlugins(arr);
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

    return { plugins, error, loading };
}
