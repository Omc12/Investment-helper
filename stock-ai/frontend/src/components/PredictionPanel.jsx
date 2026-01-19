import { useState } from 'react';

/**
 * PredictionPanel - Premium dark mode ML prediction display
 */
const PredictionPanel = ({ ticker, stockName }) => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    if (!ticker) {
      setError('Please select a stock first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/predict?ticker=${ticker}`);
      if (!response.ok) throw new Error('Prediction failed');
      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError(err.message);
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  const getSignalClass = (signal) => {
    if (signal === 'BUY' || signal === 'UP') return 'up';
    if (signal === 'SELL' || signal === 'DOWN') return 'down';
    return 'hold';
  };

  const getConfidenceClass = (conf) => {
    if (conf === 'High') return 'high';
    if (conf === 'Medium') return 'medium';
    return 'low';
  };

  if (!ticker) {
    return (
      <div className="prediction-card">
        <div className="prediction-body">
          <div className="empty-state">
            <span className="empty-state-icon">🤖</span>
            <p className="empty-state-text">
              Select a stock to get AI-powered predictions
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="prediction-card">
      <div className="prediction-header">
        <h3 className="prediction-title">AI Prediction</h3>
        <button
          className="predict-btn"
          onClick={handlePredict}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="loading-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
              Analyzing...
            </>
          ) : (
            <>
              🧠 Get Prediction
            </>
          )}
        </button>
      </div>

      <div className="prediction-body">
        {error && (
          <div className="prediction-disclaimer" style={{ borderLeftColor: 'var(--accent-red)' }}>
            <span className="prediction-disclaimer-icon">❌</span>
            <span>{error}</span>
          </div>
        )}

        {!prediction && !error && !loading && (
          <div className="empty-state" style={{ padding: '40px 20px' }}>
            <span className="empty-state-icon">📊</span>
            <p className="empty-state-text">
              Click "Get Prediction" to analyze {stockName || ticker}
            </p>
          </div>
        )}

        {prediction && (
          <>
            <div className="prediction-main-result">
              <div className="prediction-signal">
                <span className="signal-label">Direction</span>
                <div className={`signal-badge ${getSignalClass(prediction.signal)}`}>
                  {prediction.signal === 'BUY' || prediction.signal === 'UP' ? '↑ UP' : 
                   prediction.signal === 'SELL' || prediction.signal === 'DOWN' ? '↓ DOWN' : 
                   'HOLD'}
                </div>
              </div>

              <div className="prediction-probability">
                <span className="probability-label">Probability Up</span>
                <div className="probability-value">
                  {(prediction.probability * 100).toFixed(1)}%
                </div>
              </div>

              <div className="prediction-confidence">
                <span className="signal-label">Confidence</span>
                <div className={`confidence-badge ${getConfidenceClass(prediction.confidence)}`}>
                  {prediction.confidence}
                </div>
              </div>
            </div>

            {prediction.validation_scores && (
              <div className="prediction-metrics">
                <div className="metric-item">
                  <span className="metric-label">Fold 1 Accuracy</span>
                  <span className="metric-value">
                    {(prediction.validation_scores.fold_1 * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Fold 2 Accuracy</span>
                  <span className="metric-value">
                    {(prediction.validation_scores.fold_2 * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Fold 3 Accuracy</span>
                  <span className="metric-value">
                    {(prediction.validation_scores.fold_3 * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Average Accuracy</span>
                  <span className="metric-value" style={{ color: 'var(--accent-green)' }}>
                    {(prediction.validation_scores.average * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            )}

            {prediction.features_used && (
              <div className="prediction-metrics" style={{ gridTemplateColumns: '1fr 1fr' }}>
                <div className="metric-item">
                  <span className="metric-label">Features Used</span>
                  <span className="metric-value">{prediction.features_used}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Model</span>
                  <span className="metric-value">HistGradientBoosting</span>
                </div>
              </div>
            )}

            <div className="prediction-disclaimer">
              <span className="prediction-disclaimer-icon">⚠️</span>
              <span>
                For educational purposes only. This is not financial advice. 
                Always do your own research before investing.
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PredictionPanel;
