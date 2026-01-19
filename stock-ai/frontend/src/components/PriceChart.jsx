import { useState, useEffect, useRef } from 'react';
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

    // Clear previous chart with proper cleanup
    if (chartRef.current) {
      try {
        // Clear series reference first
        if (seriesRef.current) {
          seriesRef.current = null;
        }
        
        // Remove chart only if not already disposed
        if (!chartRef.current._disposed) {
          chartRef.current.remove();
        }
      } catch (error) {
        console.warn('Error removing previous chart:', error);
      } finally {
        chartRef.current = null;
        seriesRef.current = null;
      }
    }

    try {
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
          scaleMargins: { top: 0.1, bottom: 0.1 },
        },
        timeScale: {
          borderColor: 'rgba(255, 255, 255, 0.06)',
          timeVisible: true,
          secondsVisible: false,
        },
      });

      const areaSeries = chart.addAreaSeries({
        lineColor: '#00d09c',
        topColor: 'rgba(0, 208, 156, 0.3)',
        bottomColor: 'rgba(0, 208, 156, 0.02)',
        lineWidth: 2,
        priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
      });

      chartRef.current = chart;
      seriesRef.current = areaSeries;

      // Handle container resize
      const resizeHandler = () => {
        if (chart && containerRef.current) {
          chart.applyOptions({ width: containerRef.current.clientWidth });
        }
      };

      window.addEventListener('resize', resizeHandler);

      return () => {
        window.removeEventListener('resize', resizeHandler);
        // Cleanup chart properly
        if (chartRef.current) {
          try {
            if (seriesRef.current) {
              seriesRef.current = null;
            }
            if (!chartRef.current._disposed) {
              chartRef.current.remove();
            }
          } catch (error) {
            console.warn('Error removing chart on cleanup:', error);
          } finally {
            chartRef.current = null;
            seriesRef.current = null;
          }
        }
      };

    } catch (error) {
      console.error('Error initializing chart:', error);
      setError('Failed to create chart: ' + error.message);
    }
  }, []);

  // Fetch and update chart data
  const fetchChartData = async () => {
    if (!ticker || !seriesRef.current) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/stocks/candles?ticker=${ticker}&period=${timeframe}&interval=${interval}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch chart data');
      }
      
      const result = await response.json();
      const data = result.candles || [];
      
      if (data && data.length > 0) {
        // Process and validate chart data
        const chartData = data
          .map((candle) => {
            // Try multiple date formats and ensure valid timestamp
            let timestamp;
            const dateValue = candle.time || candle.date || candle.Date || candle.Datetime || candle.datetime || 
                             candle.timestamp || candle.Timestamp;
            
            if (typeof dateValue === 'string') {
              timestamp = new Date(dateValue).getTime();
            } else if (typeof dateValue === 'number') {
              // Handle Unix timestamps (seconds or milliseconds)
              timestamp = dateValue > 1e12 ? dateValue : dateValue * 1000;
            } else {
              console.warn('Invalid date format:', dateValue, 'from candle:', candle);
              return null;
            }
            
            // Validate timestamp
            if (isNaN(timestamp) || timestamp <= 0) {
              console.warn('Invalid timestamp:', dateValue, timestamp);
              return null;
            }
            
            return {
              time: Math.floor(timestamp / 1000), // Convert to seconds
              value: parseFloat(candle.close || candle.Close || 0),
            };
          })
          .filter(item => item !== null) // Remove invalid entries
          .sort((a, b) => a.time - b.time); // Ensure ascending time order
        
        // Only set data if we have valid entries
        if (chartData.length > 0 && seriesRef.current) {
          try {
            seriesRef.current.setData(chartData);
            
            if (chartRef.current) {
              chartRef.current.timeScale().fitContent();
            }
          } catch (dataError) {
            console.error('Error setting chart data:', dataError);
            setError('Failed to display chart data: ' + dataError.message);
          }
        } else {
          console.warn('No valid chart data available');
          setError('No valid chart data available');
        }
      }
    } catch (err) {
      console.error('Error fetching chart data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch data when ticker, timeframe, or interval changes
  useEffect(() => {
    const timer = setTimeout(fetchChartData, 100);
    return () => clearTimeout(timer);
  }, [ticker, timeframe, interval]);

  return (
    <div className="price-chart-container">
      <div className="chart-header">
        <div className="chart-controls">
          <div className="timeframe-selector">
            {timeframes.map((tf) => (
              <button
                key={tf.value}
                className={`timeframe-btn ${
                  timeframe === tf.value ? 'active' : ''
                }`}
                onClick={() => setTimeframe(tf.value)}
                disabled={loading}
              >
                {tf.label}
              </button>
            ))}
          </div>

          <div className="interval-selector">
            {intervals.map((int) => (
              <button
                key={int.value}
                className={`interval-btn ${
                  interval === int.value ? 'active' : ''
                }`}
                onClick={() => setInterval(int.value)}
                disabled={loading}
              >
                {int.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="chart-wrapper">
        {loading && (
          <div className="chart-loading">
            <div className="spinner"></div>
            <span>Loading chart data...</span>
          </div>
        )}
        {error && (
          <div className="chart-error">
            <span className="error-icon">⚠️</span>
            <span>Error: {error}</span>
            <button onClick={fetchChartData} className="retry-btn">
              Retry
            </button>
          </div>
        )}
        <div ref={containerRef} className="chart-container" />
      </div>
    </div>
  );
};

export default PriceChart;
