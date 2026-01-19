import { useState, useEffect, useRef } from 'react';

// Simple CSS-based fallback chart component
const FallbackChart = ({ symbol, error }) => {
  return (
    <div className="price-chart-container">
      <div className="chart-header">
        <div className="chart-controls">
          <div className="timeframe-selector">
            <button className="timeframe-btn active">1D</button>
            <button className="timeframe-btn">1W</button>
            <button className="timeframe-btn">1M</button>
            <button className="timeframe-btn">3M</button>
            <button className="timeframe-btn">6M</button>
            <button className="timeframe-btn">1Y</button>
            <button className="timeframe-btn">5Y</button>
          </div>
          <div className="interval-selector">
            <button className="interval-btn">5m</button>
            <button className="interval-btn">15m</button>
            <button className="interval-btn active">1D</button>
          </div>
        </div>
      </div>
      
      <div className="chart-wrapper">
        <div className="chart-fallback">
          <div className="fallback-content">
            <div className="error-message">
              <span className="error-icon">📊</span>
              <h3>Chart Temporarily Unavailable</h3>
              <p>{error || 'Loading chart data...'}</p>
            </div>
            
            <div className="mock-chart">
              <div className="chart-line">
                <div className="line-segment" style={{height: '60%', background: '#00d09c'}}></div>
                <div className="line-segment" style={{height: '40%', background: '#00d09c'}}></div>
                <div className="line-segment" style={{height: '80%', background: '#00d09c'}}></div>
                <div className="line-segment" style={{height: '30%', background: '#00d09c'}}></div>
                <div className="line-segment" style={{height: '70%', background: '#00d09c'}}></div>
                <div className="line-segment" style={{height: '90%', background: '#00d09c'}}></div>
                <div className="line-segment" style={{height: '50%', background: '#00d09c'}}></div>
              </div>
            </div>
            
            <div className="chart-info">
              <p>Showing mock data for {symbol || 'STOCK'}</p>
              <button 
                onClick={() => window.location.reload()} 
                className="retry-btn"
              >
                🔄 Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * PriceChart - Professional chart with fallback support
 */
const PriceChart = ({ ticker }) => {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // For now, always show fallback until we can fix the lightweight-charts issue
  useEffect(() => {
    setError('Chart library integration in progress');
    setLoading(false);
  }, [ticker]);

  if (error || loading) {
    return <FallbackChart symbol={ticker} error={error} />;
  }

  return <FallbackChart symbol={ticker} error="Chart integration pending" />;
};

export default PriceChart;
