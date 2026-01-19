import { useState, useEffect } from 'react';

/**
 * StockOverview - Overview tab with stock fundamentals
 */
const StockOverview = ({ ticker }) => {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ticker) return;

    const fetchDetails = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `http://localhost:8000/stocks/details?ticker=${ticker}`
        );
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        setDetails(data);
      } catch (error) {
        console.error('Error fetching details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [ticker]);

  const formatNumber = (num, type = 'number') => {
    if (num === null || num === undefined) return '—';
    
    if (type === 'currency') {
      if (num >= 1e12) return `₹${(num / 1e12).toFixed(2)}T`;
      if (num >= 1e9) return `₹${(num / 1e9).toFixed(2)}B`;
      if (num >= 1e7) return `₹${(num / 1e7).toFixed(2)}Cr`;
      if (num >= 1e5) return `₹${(num / 1e5).toFixed(2)}L`;
      return `₹${num.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
    }
    
    if (type === 'price') {
      return `₹${num.toLocaleString('en-IN', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
      })}`;
    }
    
    if (type === 'percent') {
      return `${num.toFixed(2)}%`;
    }
    
    if (type === 'volume') {
      if (num >= 1e7) return `${(num / 1e7).toFixed(2)}Cr`;
      if (num >= 1e5) return `${(num / 1e5).toFixed(2)}L`;
      return num.toLocaleString('en-IN');
    }
    
    return num.toLocaleString('en-IN', { maximumFractionDigits: 2 });
  };

  if (loading) {
    return (
      <div className="overview-grid">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="overview-card">
            <div className="skeleton skeleton-text short" />
            <div className="skeleton skeleton-price" />
          </div>
        ))}
      </div>
    );
  }

  if (!details) {
    return (
      <div className="empty-state">
        <p className="empty-state-text">Unable to load stock details</p>
      </div>
    );
  }

  const metrics = [
    { label: 'Market Cap', value: formatNumber(details.marketCap, 'currency') },
    { label: 'P/E Ratio', value: formatNumber(details.trailingPE) },
    { label: 'P/B Ratio', value: formatNumber(details.priceToBook) },
    { label: 'EPS (TTM)', value: formatNumber(details.trailingEps, 'price') },
    { label: '52W High', value: formatNumber(details.fiftyTwoWeekHigh, 'price') },
    { label: '52W Low', value: formatNumber(details.fiftyTwoWeekLow, 'price') },
    { label: 'Volume', value: formatNumber(details.volume, 'volume') },
    { label: 'Avg Volume', value: formatNumber(details.averageVolume, 'volume') },
    { label: 'Dividend Yield', value: details.dividendYield ? formatNumber(details.dividendYield * 100, 'percent') : '—' },
    { label: 'Beta', value: formatNumber(details.beta) },
    { label: 'Open', value: formatNumber(details.open || details.regularMarketOpen, 'price') },
    { label: 'Previous Close', value: formatNumber(details.previousClose, 'price') },
  ];

  return (
    <div className="overview-grid">
      {metrics.map((metric, index) => (
        <div key={index} className="overview-card">
          <div className="overview-card-title">{metric.label}</div>
          <div className="overview-card-value">{metric.value}</div>
        </div>
      ))}
    </div>
  );
};

export default StockOverview;
