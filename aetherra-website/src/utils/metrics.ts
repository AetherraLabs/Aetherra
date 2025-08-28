export type Metric = {
    label: string;
    value: string;
    trend: 'up' | 'down' | 'stable';
};

const metricLabels = [
    'Cognitive Load',
    'System Uptime',
    'Plugin Activity',
    'Memory Usage',
    'AI Ops/sec',
    'User Engagement',
];

function randomTrend(): 'up' | 'down' | 'stable' {
    const trends = ['up', 'down', 'stable'] as const;
    return trends[Math.floor(Math.random() * trends.length)];
}

function randomValue(label: string): string {
    switch (label) {
        case 'Cognitive Load':
            return `${Math.floor(Math.random() * 100)}%`;
        case 'System Uptime':
            return `${Math.floor(Math.random() * 1000)}h`;
        case 'Plugin Activity':
            return `${Math.floor(Math.random() * 50)} active`;
        case 'Memory Usage':
            return `${(Math.random() * 32).toFixed(1)} GB`;
        case 'AI Ops/sec':
            return `${Math.floor(Math.random() * 10000)}`;
        case 'User Engagement':
            return `${Math.floor(Math.random() * 1000)} users`;
        default:
            return 'N/A';
    }
}

export function generateMetrics(): Metric[] {
    return metricLabels.map(label => ({
        label,
        value: randomValue(label),
        trend: randomTrend(),
    }));
}
