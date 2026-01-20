import { useState, useEffect } from 'react';
import PriceChart from './PriceChart';
import PredictionPanel from './PredictionPanel';
import StockOverview from './StockOverview';

/**
 * StockDetailView - Full stock detail page with tabs (Groww-style)
 */
const StockDetailView = ({ stock, onBack }) => {
  const [activeTab, setActiveTab] = useState('chart');
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'chart', label: 'Chart', icon: '📈' },
    { id: 'prediction', label: 'AI Prediction', icon: '🤖' },
  ];

  useEffect(() => {
    if (!stock?.ticker) return;

    const fetchDetails = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `http://localhost:8000/stocks/details?ticker=${stock.ticker}`
        );
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        setDetails(data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [stock?.ticker]);

  const formatPrice = (price) => {
    if (!price) return '—';
    return '₹' + new Intl.NumberFormat('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const price = details?.currentPrice || details?.regularMarketPrice || 0;
  const prevClose = details?.previousClose || details?.regularMarketPreviousClose || price;
  const change = price - prevClose;
  const changePercent = prevClose > 0 ? (change / prevClose) * 100 : 0;
  const isPositive = change >= 0;

  return (
    <div className="stock-detail-view">
      {/* Back Button */}
      <button className="stock-back-btn" onClick={onBack}>
        ← Back to Dashboard
      </button>

      {/* Header */}
      <div className="stock-detail-header">
        <div className="stock-detail-top">
          <div className="stock-detail-info">
            <h1 className="stock-detail-name">
              {details?.shortName || details?.longName || stock.name}
            </h1>
            <div className="stock-detail-meta">
              <span className="stock-detail-ticker">{stock.ticker}</span>
              <span className="stock-detail-sector">{stock.sector}</span>
            </div>
          </div>
          
          <div className="stock-detail-pricing">
            {loading ? (
              <>
                <div className="skeleton skeleton-price" />
                <div className="skeleton skeleton-text short" style={{ marginTop: 8 }} />
              </>
            ) : (
              <>
                <div className="stock-detail-price">{formatPrice(price)}</div>
                <div className={`stock-detail-change ${isPositive ? 'positive' : 'negative'}`}>
                  <span className="change-value">
                    {isPositive ? '+' : ''}{formatPrice(change)}
                  </span>
                  <span className="change-percent">
                    {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        <div className="tabs-list">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span style={{ marginRight: 6 }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <StockOverview ticker={stock.ticker} />
        )}
        
        {activeTab === 'chart' && (
          <PriceChart ticker={stock.ticker} />
        )}
        
        {activeTab === 'prediction' && (
          <PredictionPanel 
            ticker={stock.ticker} 
            stockName={stock.name} 
          />
        )}
      </div>
    </div>
  );
};

export default StockDetailView;
