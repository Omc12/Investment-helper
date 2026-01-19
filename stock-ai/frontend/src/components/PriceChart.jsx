import { useState, useEffect, useRef, useCallback } from 'react';
import { createChart } from 'lightweight-charts';

/**
 * PriceChart - TradingView-style professional chart with dark theme
 */
const PriceChart = ({ ticker }) => {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  
  const [timeframe, setTimeframe] = useState('1mo');
  const [interval, setInterval] = useState('1d');
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);

  const timeframes = [
    { label: '1D', value: '1d' },
    { label: '1W', value: '5d' },
    { label: '1M', value: '1mo' },
    { label: '3M', value: '3mo' },
    { label: '6M', value: '6mo' },
    { label: '1Y', value: '1y' },
    { label: '5Y', value: '5y' },
  ];

  const intervals = [
    { label: '5m', value: '5m' },
    { label: '15m', value: '15m' },
    { label: '1D', value: '1d' },
  ];

  // Initialize chart
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 380,
      layout: {
        background: { type: 'solid', color: '#1a1f2e' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.04)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.04)' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: 'rgba(255, 255, 255, 0.3)',
          width: 1,
          style: 2,
          labelBackgroundColor: '#6366f1',
        },
        horzLine: {
          color: 'rgba(255, 255, 255, 0.3)',
          width: 1,
          style: 2,
          labelBackgroundColor: '#6366f1',
        },
      },
      rightPriceScale: {
        borderColor: 'rgba(255, 255, 255, 0.06)',
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
      timeScale: {
        borderColor: 'rgba(255, 255, 255, 0.06)',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
    });

    const areaSeries = chart.addAreaSeries({
      lineColor: '#00d09c',
      topColor: 'rgba(0, 208, 156, 0.3)',
      bottomColor: 'rgba(0, 208, 156, 0.02)',
      lineWidth: 2,
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
    });

    chartRef.current = chart;
    seriesRef.current = areaSeries;

    // Handle resize
    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: containerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        seriesRef.current = null;
      }
    };
  }, []);

  // Fetch and update chart data
  const fetchData = useCallback(async () => {
    if (!ticker || !seriesRef.current) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/stocks/candles?ticker=${ticker}&period=${timeframe}&interval=${interval}`
      );
      
      if (!response.ok) throw new Error('Failed to fetch chart data');
      
      const responseData = await response.json();
      const data = responseData.candles || responseData || [];
      
      if (!data || data.length === 0) {
        throw new Error('No chart data available');
      }

      // Transform data for lightweight-charts
      const chartData = data.map((candle) => {
        const dateStr = candle.time || candle.date || candle.Date;
        const timestamp = new Date(dateStr).getTime() / 1000;
        
        return {
          time: timestamp,
          value: candle.close || candle.Close || 0,
        };
      }).filter(d => d.value > 0);

      // Sort by time
      chartData.sort((a, b) => a.time - b.time);

      // Update series
      seriesRef.current.setData(chartData);
      
      // Determine line color based on price movement
      if (chartData.length >= 2) {
        const firstPrice = chartData[0].value;
        const lastPrice = chartData[chartData.length - 1].value;
        const isPositive = lastPrice >= firstPrice;
        
        seriesRef.current.applyOptions({
          lineColor: isPositive ? '#00d09c' : '#eb5757',
          topColor: isPositive 
            ? 'rgba(0, 208, 156, 0.3)' 
            : 'rgba(235, 87, 87, 0.3)',
          bottomColor: isPositive 
            ? 'rgba(0, 208, 156, 0.02)' 
            : 'rgba(235, 87, 87, 0.02)',
        });
      }

      // Fit content
      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }

      setLastUpdated(new Date());
    } catch (err) {
      console.error('Chart error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [ticker, timeframe, interval]);

  // Fetch data when ticker or timeframe changes
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh for intraday
  useEffect(() => {
    if (!ticker) return;

    // Set refresh interval based on interval
    const refreshMs = interval === '1d' ? 5 * 60 * 1000 : 10 * 1000; // 5min for daily, 10s for intraday
    
    const refreshInterval = setInterval(fetchData, refreshMs);
    
    return () => clearInterval(refreshInterval);
  }, [ticker, interval, fetchData]);

  if (!ticker) return null;

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div className="chart-timeframes">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              className={`timeframe-btn ${timeframe === tf.value ? 'active' : ''}`}
              onClick={() => setTimeframe(tf.value)}
            >
              {tf.label}
            </button>
          ))}
        </div>
        <div className="chart-intervals">
          {intervals.map((int) => (
            <button
              key={int.value}
              className={`interval-btn ${interval === int.value ? 'active' : ''}`}
              onClick={() => setInterval(int.value)}
            >
              {int.label}
            </button>
          ))}
        </div>
      </div>
      
      <div className="chart-body">
        {loading && (
          <div className="skeleton skeleton-chart" style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0,
            zIndex: 10,
          }} />
        )}
        {error && (
          <div className="loading-overlay" style={{ position: 'absolute', inset: 0 }}>
            <span>{error}</span>
          </div>
        )}
        <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      </div>
      
      <div className="chart-footer">
        <div className="chart-last-updated">
          {lastUpdated && (
            <>
              <span className="live-indicator" />
              <span>Last updated: {lastUpdated.toLocaleTimeString()}</span>
            </>
          )}
        </div>
        <span>Scroll to zoom • Drag to pan</span>
      </div>
    </div>
  );
};

export default PriceChart;
