import { useState, useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

/**
 * TrendingStocks - Top 10 stocks with sparklines
 */
const TrendingStocks = ({ onSelectStock }) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrendingStocks = async () => {
      try {
        // Get stock list
        const stocksResponse = await fetch('http://localhost:8000/stocks');
        const data = await stocksResponse.json();
        const allStocks = data.stocks || []; // Extract stocks array from response
        
        // Get top 10 stocks with price data
        const topStocks = allStocks.slice(0, 10);
        
        const stocksWithData = await Promise.all(
          topStocks.map(async (stock) => {
            try {
              // Fetch stock details
              const detailsResponse = await fetch(
                `http://localhost:8000/stocks/details?ticker=${stock.ticker}`
              );
              const details = await detailsResponse.json();
              
              // Fetch recent candles for sparkline
              const candlesResponse = await fetch(
                `http://localhost:8000/stocks/candles?ticker=${stock.ticker}&period=1mo&interval=1d`
              );
              const candlesData = await candlesResponse.json();
              const candles = candlesData.candles || candlesData || [];
              
              const price = details.currentPrice || details.regularMarketPrice || 0;
              const prevClose = details.previousClose || details.regularMarketPreviousClose || price;
              const change = price - prevClose;
              const changePercent = prevClose > 0 ? (change / prevClose) * 100 : 0;
              
              return {
                ...stock,
                price,
                change,
                changePercent,
                candles: candles.slice(-20), // Last 20 data points for sparkline
              };
            } catch (error) {
              return {
                ...stock,
                price: 0,
                change: 0,
                changePercent: 0,
                candles: [],
              };
            }
          })
        );
        
        setStocks(stocksWithData);
      } catch (error) {
        console.error('Error fetching trending stocks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrendingStocks();
  }, []);

  const formatPrice = (price) => {
    if (!price) return '—';
    return '₹' + new Intl.NumberFormat('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  if (loading) {
    return (
      <section className="section">
        <div className="section-header">
          <h2 className="section-title">🔥 Trending Stocks</h2>
        </div>
        <div className="trending-grid">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="trending-card skeleton-card">
              <div className="skeleton skeleton-text short" />
              <div className="skeleton skeleton-text" style={{ width: '40%' }} />
              <div className="skeleton skeleton-price" style={{ marginTop: 12 }} />
            </div>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="section">
      <div className="section-header">
        <h2 className="section-title">🔥 Trending Stocks</h2>
      </div>
      <div className="trending-grid">
        {stocks.map((stock) => (
          <div
            key={stock.ticker}
            className="trending-card"
            onClick={() => onSelectStock(stock)}
          >
            <div className="trending-card-header">
              <div className="trending-stock-info">
                <span className="trending-stock-name">{stock.name}</span>
                <span className="trending-stock-ticker">{stock.ticker}</span>
              </div>
              <span
                className={`trending-stock-change ${stock.change >= 0 ? 'positive' : 'negative'}`}
                style={{
                  background: stock.change >= 0 
                    ? 'var(--accent-green-soft)' 
                    : 'var(--accent-red-soft)',
                  color: stock.change >= 0 
                    ? 'var(--accent-green)' 
                    : 'var(--accent-red)',
                }}
              >
                {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent?.toFixed(2)}%
              </span>
            </div>
            <div className="trending-card-body">
              <span className="trending-stock-price">{formatPrice(stock.price)}</span>
              <SparklineChart 
                data={stock.candles} 
                isPositive={stock.change >= 0} 
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

/**
 * SparklineChart - Mini line chart for trending cards
 */
const SparklineChart = ({ data, isPositive }) => {
  const containerRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !data || data.length === 0) return;

    // Clear previous chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(containerRef.current, {
      width: 60,
      height: 30,
      layout: {
        background: { type: 'solid', color: 'transparent' },
        textColor: 'transparent',
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { visible: false },
      },
      crosshair: {
        mode: 0, // No crosshair
      },
      rightPriceScale: { visible: false },
      timeScale: { visible: false },
      handleScale: false,
      handleScroll: false,
    });

    const lineSeries = chart.addLineSeries({
      color: isPositive ? '#00d09c' : '#eb5757',
      lineWidth: 1.5,
      priceLineVisible: false,
      lastValueVisible: false,
      crosshairMarkerVisible: false,
    });

    const chartData = data.map((candle, index) => ({
      time: index,
      value: candle.close || candle.Close || 0,
    }));

    lineSeries.setData(chartData);
    chart.timeScale().fitContent();
    
    chartRef.current = chart;

    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [data, isPositive]);

  return <div ref={containerRef} className="sparkline-container" />;
};

export default TrendingStocks;
