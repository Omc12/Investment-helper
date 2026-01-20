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
      
      // Handle prediction response properly
      const predictionValue = data.prediction || data.direction || 'Unknown';
      const confidence = data.confidence ? (data.confidence * 100).toFixed(1) : 'N/A';
      
      setPrediction({
        ...data,
        prediction: predictionValue,
        confidence: confidence,
        price_target: data.price_target || data.target_price || null,
        change_percent: data.change_percent || data.expected_change || null
      });
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
          <div>
            <div className="prediction-main-result">
              <div className="prediction-signal">
                <span className="signal-label">Direction</span>
                <div className={`signal-badge ${getSignalClass(prediction.prediction || prediction.signal)}`}>
                  {(prediction.prediction || prediction.signal) === 'BUY' || (prediction.prediction || prediction.signal) === 'UP' ? '↑ UP' : 
                   (prediction.prediction || prediction.signal) === 'SELL' || (prediction.prediction || prediction.signal) === 'DOWN' ? '↓ DOWN' : 
                   'HOLD'}
                </div>
              </div>

              <div className="prediction-probability">
                <span className="probability-label">Confidence</span>
                <div className="probability-value">
                  {prediction.confidence && !isNaN(prediction.confidence) ? `${prediction.confidence}%` : 'N/A'}
                </div>
              </div>

              {prediction.price_target && !isNaN(prediction.price_target) && (
                <div className="prediction-confidence">
                  <span className="signal-label">Price Target</span>
                  <div className="confidence-badge">
                    ₹{parseFloat(prediction.price_target).toFixed(2)}
                  </div>
                </div>
              )}
            </div>

            {prediction.change_percent && !isNaN(prediction.change_percent) && (
              <div className="prediction-metrics">
                <div className="metric-item">
                  <span className="metric-label">Expected Change</span>
                  <span className="metric-value">
                    {parseFloat(prediction.change_percent).toFixed(2)}%
                  </span>
                </div>
              </div>
            )}

            {prediction.accuracy && !isNaN(prediction.accuracy) && (
              <div className="prediction-metrics">
                <div className="metric-item">
                  <span className="metric-label">Model Accuracy</span>
                  <span className="metric-value">
                    {(parseFloat(prediction.accuracy) * 100).toFixed(1)}%
                  </span>
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
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionPanel;
