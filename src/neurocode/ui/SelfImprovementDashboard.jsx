import { useEffect, useState } from 'react';
import './SelfImprovementDashboard.css';

const API_URL = '/api/self_improvement_dashboard'; // Adjust if needed

export default function SelfImprovementDashboard() {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch(`${API_URL}/metrics`)
            .then((res) => res.json())
            .then((data) => {
                setMetrics(data.metrics || data);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="sidash-loading">Loading self-improvement metrics...</div>;
    if (error) return <div className="sidash-error">Error: {error}</div>;

    return (
        <div className="sidash-container">
            <h2>🧠 Lyrixa Self-Improvement Dashboard</h2>
            <div className="sidash-section">
                <strong>Evaluation Cycles (last {metrics.period_days} days):</strong> {metrics.total_evaluation_cycles}
            </div>
            <div className="sidash-section">
                <strong>Total Recommendations:</strong> {metrics.total_recommendations}
            </div>
            <div className="sidash-section">
                <strong>Auto-Improvements:</strong> {metrics.total_auto_improvements}
            </div>
            <div className="sidash-section">
                <strong>Avg Recommendations/Cycle:</strong> {metrics.avg_recommendations_per_cycle?.toFixed(2)}
            </div>
            <div className="sidash-section">
                <strong>Improvement Rate:</strong> {(metrics.improvement_rate * 100).toFixed(1)}%
            </div>
            <div className="sidash-section">
                <strong>Last Evaluation:</strong> {metrics.last_evaluation || 'N/A'}
            </div>
            {/* TODO: Add review/approval UI for proposed code/config changes */}
        </div>
    );
}
