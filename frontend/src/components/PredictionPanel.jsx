import { useState } from 'react';
import { Zap, Cpu, Target, Shield } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const ConfidenceGauge = ({ score }) => {
  const radius = 30;
  const stroke = 6;
  const normalizedScore = Math.max(0, Math.min(100, score));
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - ((normalizedScore / 100) * circumference);

  return (
    <div className="gauge-container">
      <svg width="80" height="80">
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke="var(--bg-elevated)"
          strokeWidth={stroke}
        />
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke="var(--primary-green)"
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 40 40)"
        />
      </svg>
      <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <span style={{ fontSize: '18px', fontWeight: 'bold' }}>{Math.round(normalizedScore)}%</span>
      </div>
    </div>
  );
};

const PredictionPanel = ({ ticker, stockName }) => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    setLoading(true);
    // Simulating API call for now to ensure UI stability first
    await new Promise(r => setTimeout(r, 1000));

    setPrediction({
      signal: 'BUY',
      probability: 0.85,
      action: 'Accumulate',
      reason: 'Technical indicators (RSI, MACD) suggest bullish momentum with strong volume support.',
      trading_params: {
        target_profit: '2650.00',
        stop_loss: '2420.00'
      }
    });
    setLoading(false);
  };

  return (
    <div className="prediction-panel">
      <div style={{ margin: '24px 0' }}>
        {!prediction && !loading && (
          <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
            <Cpu size={40} color="var(--primary-green)" style={{ marginBottom: '16px' }} />
            <h3>AI Market Analysis</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
              Generate real-time buy/sell signals based on technicals.
            </p>
            <button className="btn btn-primary" onClick={handlePredict}>
              Run Analysis
            </button>
          </div>
        )}

        {loading && (
          <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
            Loading analysis for {ticker}...
          </div>
        )}

        {prediction && !loading && (
          <div className="ai-results-grid">
            <div className="prediction-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>SIGNAL</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--primary-green)' }}>{prediction.signal}</div>
                </div>
                <ConfidenceGauge score={prediction.probability * 100} />
              </div>
              <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                Recommended Action: <span style={{ color: 'var(--text-primary)' }}>{prediction.action}</span>
              </div>
            </div>

            <div className="prediction-card">
              <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Target size={16} /> Targets
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Target</span>
                <span style={{ fontWeight: '500', color: 'var(--primary-green)' }}>{prediction.trading_params.target_profit}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Stop Loss</span>
                <span style={{ fontWeight: '500', color: 'var(--primary-red)' }}>{prediction.trading_params.stop_loss}</span>
              </div>
            </div>

            <div className="prediction-card" style={{ gridColumn: '1 / -1' }}>
              <div style={{ marginBottom: '8px', fontWeight: '500' }}>Analysis</div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{prediction.reason}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionPanel;
