import { useState, useEffect } from 'react';
import { DollarSign, BarChart2, Calendar, TrendingUp, Percent, Target, Building2, Users, Globe, Phone, MapPin, Zap, Shield } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const StockOverview = ({ ticker, details: passedDetails }) => {
  const [details, setDetails] = useState(passedDetails || null);
  const [loading, setLoading] = useState(!passedDetails);

  useEffect(() => {
    if (passedDetails) {
      setDetails(passedDetails);
      setLoading(false);
      return;
    }

    if (!ticker) return;

    const fetchDetails = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${API_BASE_URL}/stocks/details?ticker=${ticker}`
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
  }, [ticker, passedDetails]);

  const formatNumber = (num, type = 'number') => {
    if (num === null || num === undefined) return '—';
    if (type === 'currency') {
      if (num >= 1e7) return `₹${(num / 1e7).toFixed(2)}Cr`;
      if (num >= 1e5) return `₹${(num / 1e5).toFixed(2)}L`;
      return `₹${num.toLocaleString('en-IN')}`;
    }
    if (type === 'price') return `₹${num.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
    if (type === 'percent') return `${(num * 100).toFixed(2)}%`;
    if (type === 'percentRaw') return `${num.toFixed(2)}%`;
    return num.toLocaleString('en-IN');
  };

  if (loading || !details) return <div style={{ color: 'var(--text-muted)' }}>Loading fundamentals...</div>;

  const sections = [
    {
      title: 'Market Data', icon: <DollarSign size={16} />, items: [
        { label: 'Market Cap', value: formatNumber(details.marketCap, 'currency') },
        { label: 'P/E Ratio', value: formatNumber(details.trailingPE) },
        { label: 'P/B Ratio', value: formatNumber(details.priceToBook) },
        { label: 'Ind. P/E', value: formatNumber(details.industryPE || 0) }, // Mock if not avail
        { label: 'Debt to Equity', value: formatNumber(details.debtToEquity) },
        { label: 'ROE', value: formatNumber(details.returnOnEquity, 'percent') },
      ]
    },
    {
      title: 'Performance', icon: <BarChart2 size={16} />, items: [
        { label: '52W High', value: formatNumber(details.fiftyTwoWeekHigh, 'price') },
        { label: '52W Low', value: formatNumber(details.fiftyTwoWeekLow, 'price') },
        { label: 'Day High', value: formatNumber(details.dayHigh, 'price') },
        { label: 'Day Low', value: formatNumber(details.dayLow, 'price') },
      ]
    }
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
      {/* Company Bio */}
      <div className="overview-card" style={{ gridColumn: '1 / -1' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontWeight: 600, color: 'var(--text-primary)' }}>
          <Building2 size={18} color="var(--primary-green)" />
          About {details.shortName || details.longName}
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.6 }}>
          {details.longBusinessSummary || details.businessSummary}
        </p>
      </div>

      {sections.map((section, idx) => (
        <div key={idx} className="overview-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', fontWeight: 600, color: 'var(--text-primary)' }}>
            {section.icon} {section.title}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px 24px' }}>
            {section.items.map((item, i) => (
              <div key={i}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>{item.label}</div>
                <div style={{ fontSize: '14px', color: 'var(--text-primary)', fontWeight: 500 }}>{item.value || '—'}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default StockOverview;
