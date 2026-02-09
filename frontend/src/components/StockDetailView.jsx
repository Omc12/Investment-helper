import { useState, useEffect } from 'react';
import { ArrowLeft, Info, BarChart3, Cpu } from 'lucide-react';
import PriceChart from './PriceChart';
import PredictionPanel from './PredictionPanel';
import StockOverview from './StockOverview';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const StockDetailView = ({ stock, onBack }) => {
  const [activeTab, setActiveTab] = useState('chart');
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Info size={16} /> },
    { id: 'chart', label: 'Chart', icon: <BarChart3 size={16} /> },
    { id: 'prediction', label: 'AI Prediction', icon: <Cpu size={16} /> },
  ];

  useEffect(() => {
    if (!stock?.ticker) return;

    const fetchDetails = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/stocks/details?ticker=${stock.ticker}`);
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        setDetails(data);
      } catch (error) {
        console.warn('Using fallback data');
        setDetails({
          currentPrice: stock.current_price || 2500,
          previousClose: stock.current_price ? stock.current_price * 0.98 : 2450,
          fiftyTwoWeekHigh: 2800,
          fiftyTwoWeekLow: 2200,
          sector: stock.sector || 'Equity',
          longName: stock.name
        });
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

  const price = details?.currentPrice || details?.regularMarketPrice || stock.current_price || 0;
  const prevClose = details?.previousClose || details?.regularMarketPreviousClose || price * 0.98;
  const change = price - prevClose;
  const changePercent = prevClose > 0 ? (change / prevClose) * 100 : 0;
  const isPositive = change >= 0;

  return (
    <div className="stock-detail-container">
      {/* Header */}
      <div className="stock-header-minimal">
        <div className="header-top-row">
          <button className="back-btn" onClick={onBack}>
            <ArrowLeft size={20} />
          </button>

          <div className="stock-identity">
            <h1>{details?.shortName || details?.longName || stock.name}</h1>
            <div className="stock-badges">
              <span className="badge">{stock.ticker}</span>
              <span className="badge">{stock.sector || 'Equity'}</span>
            </div>
          </div>
        </div>

        <div className="header-price-row">
          <span className="current-price">{formatPrice(price)}</span>
          <span className={`price-change-clean ${isPositive ? 'text-green' : 'text-red'}`}>
            {isPositive ? '+' : ''}{formatPrice(change)} ({changePercent.toFixed(2)}%)
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-clean">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn-clean ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="content-area">
        {activeTab === 'overview' && (
          <StockOverview ticker={stock.ticker} details={details} />
        )}

        {activeTab === 'chart' && (
          <PriceChart ticker={stock.ticker} />
        )}

        {activeTab === 'prediction' && (
          <PredictionPanel ticker={stock.ticker} stockName={stock.name} />
        )}
      </div>
    </div>
  );
};

export default StockDetailView;
