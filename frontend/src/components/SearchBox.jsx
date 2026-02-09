import { useState, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const SearchBox = ({ onSelectStock, placeholder = "Search stocks (e.g. Reliance, TCS)" }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target) &&
        inputRef.current &&
        !inputRef.current.contains(e.target)
      ) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (!query || query.length < 1) {
      setResults([]);
      setShowDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${API_BASE_URL}/stocks?search=${encodeURIComponent(query)}&limit=8`
        );

        if (!response.ok) throw new Error('Search failed');

        const data = await response.json();
        const stockResults = data.stocks || [];

        setResults(stockResults);
        setShowDropdown(true); // Always show dropdown if query exists, even if empty results (handled below)
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Search error:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (stock) => {
    setQuery('');
    setShowDropdown(false);

    // Normalize stock object
    const normalizedStock = {
      name: stock.name,
      ticker: stock.symbol || stock.ticker,
      symbol: stock.symbol || stock.ticker,
      sector: stock.sector,
      exchange: stock.exchange,
      current_price: stock.current_price || stock.price,
      ...stock
    };

    onSelectStock(normalizedStock);
  };

  const handleKeyDown = (e) => {
    if (!showDropdown || results.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev < results.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev > 0 ? prev - 1 : results.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0) handleSelect(results[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  return (
    <>
      <div className="search-icon">
        <Search size={18} color="#757575" />
      </div>
      <input
        ref={inputRef}
        type="text"
        className="search-input"
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => { if (query) setShowDropdown(true); }}
      />

      {showDropdown && (
        <div
          ref={dropdownRef}
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            marginTop: '8px',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            boxShadow: 'var(--shadow-popover)',
            zIndex: 1000,
            maxHeight: '400px',
            overflowY: 'auto',
            padding: '8px 0'
          }}
        >
          {loading ? (
            <div style={{ padding: '16px', color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center' }}>
              Loading...
            </div>
          ) : results.length > 0 ? (
            results.map((stock, index) => (
              <div
                key={stock.symbol || stock.ticker || index}
                onClick={() => handleSelect(stock)}
                onMouseEnter={() => setSelectedIndex(index)}
                style={{
                  padding: '12px 16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  background: index === selectedIndex ? 'var(--bg-card-hover)' : 'transparent',
                  borderBottom: '1px solid var(--border-subtle)'
                }}
              >
                <div>
                  <div style={{ color: 'var(--text-primary)', fontSize: '14px', fontWeight: 500 }}>
                    {stock.name}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: '2px' }}>
                    {stock.symbol || stock.ticker}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  {stock.current_price && (
                    <div style={{ color: 'var(--text-primary)', fontWeight: 500, fontSize: '14px' }}>
                      ₹{stock.current_price}
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              No results found
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default SearchBox;
