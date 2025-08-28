export type PromSample = {
    name: string;
    value: number;
};

// Minimal Prometheus text exposition parser (label-less lines only)
export function parsePrometheusText(text: string): PromSample[] {
    const samples: PromSample[] = [];
    const lines = text.split(/\r?\n/);
    for (const line of lines) {
        const t = line.trim();
        if (!t || t.startsWith('#')) continue; // skip HELP/TYPE/comments
        // ignore samples with labels: metric{label="v"} 123
        if (t.includes('{')) continue;
        const parts = t.split(/\s+/);
        if (parts.length < 2) continue;
        const name = parts[0];
        const valStr = parts[parts.length - 1];
        const val = Number(valStr);
        if (!Number.isNaN(val)) {
            samples.push({ name, value: val });
        }
    }
    return samples;
}

export function pickSamples(samples: PromSample[], predicate?: (s: PromSample) => boolean, limit = 6): PromSample[] {
    const filtered = predicate ? samples.filter(predicate) : samples;
    return filtered.slice(0, limit);
}
