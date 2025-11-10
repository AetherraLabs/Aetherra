import { useEffect, useState } from 'react';

interface EmotionState {
    current_emotion: string;
    current_expression: string;
    state_duration_seconds: number;
    last_trigger?: {
        trigger_source: string;
        message_preview?: string;
        timestamp?: string;
    };
}

interface EmotionDisplayProps {
    hubUrl?: string;
    refreshInterval?: number;
}

/**
 * EmotionDisplay - Shows Interactive Lyrixa's current emotion state
 * Polls the Hub API /api/interactive/emotion endpoint to display real-time emotions
 */
export default function EmotionDisplay({
    hubUrl = 'http://localhost:3001',
    refreshInterval = 2000
}: EmotionDisplayProps) {
    const [emotion, setEmotion] = useState<EmotionState | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    useEffect(() => {
        const fetchEmotion = async () => {
            try {
                const response = await fetch(`${hubUrl}/api/interactive/emotion`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                setEmotion(data);
                setError(null);
                setLastUpdate(new Date());
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch emotion');
            }
        };

        // Initial fetch
        fetchEmotion();

        // Set up polling
        const interval = setInterval(fetchEmotion, refreshInterval);

        return () => clearInterval(interval);
    }, [hubUrl, refreshInterval]);

    const getEmotionColor = (emotionName: string): string => {
        const colors: Record<string, string> = {
            excited: '#FFB800',
            curious: '#00B4D8',
            focused: '#7209B7',
            thoughtful: '#3A0CA3',
            calm: '#48CAE4',
            neutral: '#90E0EF',
        };
        return colors[emotionName.toLowerCase()] || colors.neutral;
    };

    const getEmotionEmoji = (emotionName: string): string => {
        const emojis: Record<string, string> = {
            excited: '✨',
            curious: '🔍',
            focused: '🎯',
            thoughtful: '🤔',
            calm: '😌',
            neutral: '😐',
        };
        return emojis[emotionName.toLowerCase()] || emojis.neutral;
    };

    if (error) {
        return (
            <div className="emotion-display error">
                <h3>Interactive Lyrixa Emotion</h3>
                <p className="error-message">⚠️ {error}</p>
                <p className="hint">Make sure the Hub is running on {hubUrl}</p>
            </div>
        );
    }

    if (!emotion) {
        return (
            <div className="emotion-display loading">
                <h3>Interactive Lyrixa Emotion</h3>
                <p>Loading...</p>
            </div>
        );
    }

    const emotionColor = getEmotionColor(emotion.current_emotion);
    const emotionEmoji = getEmotionEmoji(emotion.current_emotion);

    return (
        <div className="emotion-display" style={{ borderColor: emotionColor }}>
            <h3>Interactive Lyrixa Emotion</h3>

            <div className="emotion-main" style={{ backgroundColor: `${emotionColor}20` }}>
                <span className="emotion-emoji" style={{ fontSize: '3rem' }}>
                    {emotionEmoji}
                </span>
                <div className="emotion-text">
                    <div className="emotion-name" style={{ color: emotionColor }}>
                        {emotion.current_emotion.toUpperCase()}
                    </div>
                    <div className="expression-name">
                        {emotion.current_expression}
                    </div>
                </div>
            </div>

            <div className="emotion-details">
                <div className="detail-item">
                    <span className="detail-label">Duration:</span>
                    <span className="detail-value">{Math.round(emotion.state_duration_seconds)}s</span>
                </div>

                {emotion.last_trigger && (
                    <>
                        <div className="detail-item">
                            <span className="detail-label">Trigger:</span>
                            <span className="detail-value">{emotion.last_trigger.trigger_source}</span>
                        </div>

                        {emotion.last_trigger.message_preview && (
                            <div className="detail-item message-preview">
                                <span className="detail-label">Context:</span>
                                <span className="detail-value">"{emotion.last_trigger.message_preview}"</span>
                            </div>
                        )}
                    </>
                )}
            </div>

            {lastUpdate && (
                <div className="last-update">
                    Last update: {lastUpdate.toLocaleTimeString()}
                </div>
            )}
        </div>
    );
}
