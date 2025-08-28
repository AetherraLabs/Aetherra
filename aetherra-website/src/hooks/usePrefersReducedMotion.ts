import { useEffect, useState } from 'react';

export default function usePrefersReducedMotion(): boolean {
    const [reduced, setReduced] = useState(false);

    useEffect(() => {
        const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
        setReduced(mq.matches);
        const handler = (event: MediaQueryListEvent) => setReduced(event.matches);
        mq.addEventListener('change', handler);
        return () => mq.removeEventListener('change', handler);
    }, []);

    return reduced;
}
