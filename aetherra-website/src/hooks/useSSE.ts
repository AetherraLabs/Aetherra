import { useEffect, useRef, useState } from 'react';

export type SSEEvent = { event?: string; data: string };

export default function useSSE(url: string = '/api/ai/stream') {
    const esRef = useRef<EventSource | null>(null);
    const [connected, setConnected] = useState(false);
    const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Skip SSE on static hosts (e.g., GitHub Pages) unless explicitly enabled.
        const isStaticHost = typeof window !== 'undefined' && /(?:^|\.)aetherra\.dev$/i.test(window.location.hostname);
        const explicitlyEnabled = (import.meta as any)?.env?.VITE_ENABLE_SSE;
        if (isStaticHost && !explicitlyEnabled) {
            setConnected(false);
            setError(null);
            return;
        }

        const es = new EventSource(url);
        esRef.current = es;
        es.onopen = () => setConnected(true);
        es.onerror = () => {
            setConnected(false);
            setError('SSE disconnected');
        };
        es.onmessage = (ev) => {
            setLastEvent({ data: ev.data });
        };
        return () => {
            es.close();
            esRef.current = null;
        };
    }, [url]);

    return { connected, lastEvent, error };
}
