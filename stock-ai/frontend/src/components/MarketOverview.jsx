import { useState, useEffect } from 'react';

/**
 * MarketOverview - NIFTY 50 and BANKNIFTY index cards
 */
const MarketOverview = () => {
  const [indices, setIndices] = useState([
    {
      name: 'NIFTY 50',
      ticker: '^NSEI',
      price: null,
      change: null,
      changePercent: null,
      loading: true,
    },
    {
      name: 'BANK NIFTY',
      ticker: '^NSEBANK',
      price: null,
      change: null,
      changePercent: null,
      loading: true,
    },
  ]);

  useEffect(() => {
    const fetchIndexData = async () => {
      const updatedIndices = await Promise.all(
        indices.map(async (index) => {
          try {
            const response = await fetch(
              `http://localhost:8000/stocks/details?ticker=${index.ticker}`
            );
            if (!response.ok) throw new Error('Failed to fetch');
            const data = await response.json();
            
            const price = data.currentPrice || data.regularMarketPrice || 0;
            const prevClose = data.previousClose || data.regularMarketPreviousClose || price;
            const change = price - prevClose;
            const changePercent = prevClose > 0 ? (change / prevClose) * 100 : 0;
            
            return {
              ...index,
              price,
              change,
              changePercent,
              loading: false,
            };
          } catch (error) {
            console.error(`Error fetching ${index.name}:`, error);
            return { ...index, loading: false };
          }
        })
      );
      setIndices(updatedIndices);
    };

    fetchIndexData();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchIndexData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price) => {
    if (!price) return '—';
    return new Intl.NumberFormat('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  return (
    <section className="section">
      <div className="section-header">
        <h2 className="section-title">📊 Market Overview</h2>
      </div>
      <div className="market-cards">
        {indices.map((index) => (
          <div key={index.ticker} className="market-card">
            <div className="market-card-header">
              <span className="market-card-name">{index.name}</span>
              <span className="market-card-badge index">INDEX</span>
            </div>
            {index.loading ? (
              <>
                <div className="skeleton skeleton-price" style={{ marginBottom: 8 }} />
                <div className="skeleton skeleton-text short" />
              </>
            ) : (
              <>
                <div className="market-card-price">
                  {formatPrice(index.price)}
                </div>
                <div className={`market-card-change ${index.change >= 0 ? 'positive' : 'negative'}`}>
                  <span className="change-value">
                    {index.change >= 0 ? '+' : ''}{formatPrice(index.change)}
                  </span>
                  <span className="change-percent">
                    {index.changePercent >= 0 ? '+' : ''}{index.changePercent?.toFixed(2)}%
                  </span>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

export default MarketOverview;
