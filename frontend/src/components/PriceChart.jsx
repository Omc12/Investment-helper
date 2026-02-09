import { useState, useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import { BarChart3, CandlestickChart, Activity, RefreshCw } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const PriceChart = ({ ticker }) => {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);

  const [timeframe, setTimeframe] = useState('1mo');
  const [chartType, setChartType] = useState('candles'); // 'area' or 'candles'
  const [loading, setLoading] = useState(false);

  const timeframes = [
    { label: '1D', value: '1d', interval: '5m' },
    { label: '1W', value: '5d', interval: '15m' },
    { label: '1M', value: '1mo', interval: '1d' },
    { label: '1Y', value: '1y', interval: '1d' },
    { label: '5Y', value: '5y', interval: '1wk' },
  ];

  // Mock Data Generator
  const generateMockData = (period) => {
    const data = [];
    const now = new Date();
    let time = Math.floor(now.getTime() / 1000);
    const points = 100; // Number of data points
    let price = 2500; // Base price

    for (let i = points; i >= 0; i--) {
      const vol = Math.floor(Math.random() * 1000000) + 500000;
      const move = (Math.random() - 0.48) * 20;
      const close = price;
      const open = price - move;
      const high = Math.max(open, close) + Math.random() * 10;
      const low = Math.min(open, close) - Math.random() * 10;

      data.push({
        time: time - (i * (period === '1d' ? 300 : 86400)),
        open: open, high: high, low: low, close: close,
        value: close, volume: vol,
        color: close >= open ? '#00d09c' : '#EB5B3C'
      });
      price = close + (Math.random() - 0.48) * 15;
    }
    return data;
  };

  useEffect(() => {
    if (!containerRef.current) return;

    const handleResize = () => {
      if (chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#9b9b9b',
        fontFamily: 'Roboto, -apple-system, sans-serif',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.04)', style: 1 },
        horzLines: { color: 'rgba(255, 255, 255, 0.04)', style: 1 },
      },
      crosshair: {
        mode: 1,
        vertLine: { width: 1, color: 'rgba(255, 255, 255, 0.2)', style: 3, labelBackgroundColor: '#121212' },
        horzLine: { width: 1, color: 'rgba(255, 255, 255, 0.2)', style: 3, labelBackgroundColor: '#121212' },
      },
      rightPriceScale: { borderColor: 'rgba(255, 255, 255, 0.1)' },
      timeScale: { borderColor: 'rgba(255, 255, 255, 0.1)', timeVisible: true },
    });

    chartRef.current = chart;

    if (chartType === 'area') {
      seriesRef.current = chart.addAreaSeries({
        lineColor: '#00d09c',
        topColor: 'rgba(0, 208, 156, 0.2)',
        bottomColor: 'rgba(0, 208, 156, 0.0)',
        lineWidth: 2,
      });
    } else {
      seriesRef.current = chart.addCandlestickSeries({
        upColor: '#00d09c', downColor: '#EB5B3C',
        borderVisible: false, wickUpColor: '#00d09c', wickDownColor: '#EB5B3C'
      });
    }

    volumeSeriesRef.current = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [chartType]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const selectedTf = timeframes.find(t => t.value === timeframe);
        const interval = selectedTf ? selectedTf.interval : '1d';

        let data = [];
        let volumeData = [];

        try {
          const response = await fetch(
            `${API_BASE_URL}/stocks/candles?ticker=${ticker}&period=${timeframe}&interval=${interval}`
          );
          if (!response.ok) throw new Error('API Error');
          const result = await response.json();
          const rawData = result.candles || [];
          if (rawData.length === 0) throw new Error('No Data');

          data = rawData.map(d => ({
            time: Math.floor(new Date(d.date || d.datetime || d.time).getTime() / 1000),
            open: d.open, high: d.high, low: d.low, close: d.close, value: d.close,
          })).sort((a, b) => a.time - b.time);

          volumeData = rawData.map(d => ({
            time: Math.floor(new Date(d.date || d.datetime || d.time).getTime() / 1000),
            value: d.volume,
            color: d.close >= d.open ? 'rgba(0, 208, 156, 0.3)' : 'rgba(235, 91, 60, 0.3)',
          })).sort((a, b) => a.time - b.time);

        } catch (err) {
          console.warn('Using mock chart data');
          const mock = generateMockData(timeframe);
          data = mock.map(d => ({ ...d }));
          volumeData = mock.map(d => ({
            time: d.time, value: d.volume,
            color: d.close >= d.open ? 'rgba(0, 208, 156, 0.3)' : 'rgba(235, 91, 60, 0.3)'
          }));
        }

        if (seriesRef.current) seriesRef.current.setData(data);
        if (volumeSeriesRef.current) volumeSeriesRef.current.setData(volumeData);
        if (chartRef.current) chartRef.current.timeScale().fitContent();

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [ticker, timeframe, chartType]);

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div className="chart-title">Price Chart</div>

        <div className="chart-controls">
          <div className="chart-type-toggle">
            <button
              className={`type-btn ${chartType === 'area' ? 'active' : ''}`}
              onClick={() => setChartType('area')}
            >
              <Activity size={16} />
            </button>
            <button
              className={`type-btn ${chartType === 'candles' ? 'active' : ''}`}
              onClick={() => setChartType('candles')}
            >
              <CandlestickChart size={16} />
            </button>
          </div>

          <div className="divider-vertical"></div>

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
      </div>

      <div className="chart-body">
        {loading && (
          <div className="chart-loading-overlay">
            <RefreshCw className="spin" size={24} />
          </div>
        )}
        <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      </div>
    </div>
  );
};

export default PriceChart;
