
type Props = {
    values: number[];
    width?: number;
    height?: number;
    stroke?: string;
    fill?: string;
};

export default function PromSparkline({ values, width = 240, height = 48, stroke = '#6ee7b7', fill = 'rgba(110,231,183,0.12)' }: Props) {
    if (!values || values.length < 2) {
        return <div className="text-xs text-aetherra-text-tertiary">No data</div>;
    }
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min || 1;
    const stepX = width / (values.length - 1);
    const pts = values.map((v, i) => {
        const x = i * stepX;
        const y = height - ((v - min) / span) * height;
        return `${x},${y}`;
    }).join(' ');

    const last = values[values.length - 1];

    return (
        <div>
            <svg width={width} height={height} className="block">
                <polyline points={`0,${height} ${pts} ${width},${height}`} fill={fill} stroke="none" />
                <polyline points={pts} fill="none" stroke={stroke} strokeWidth={2} />
            </svg>
            <div className="text-xs text-aetherra-text-tertiary">min {min.toFixed(2)} · max {max.toFixed(2)} · last {last.toFixed(2)}</div>
        </div>
    );
}
