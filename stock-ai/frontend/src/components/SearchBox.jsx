import { useState, useEffect, useRef } from 'react';

/**
 * SearchBox - Groww-style dark mode autocomplete search
 */
const SearchBox = ({ onSelectStock, placeholder = "Search stocks..." }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Click outside handler
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

  // Debounced search
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
          `http://localhost:8000/stocks/search?query=${encodeURIComponent(query)}`
        );
        const data = await response.json();
        const stockResults = data.results || data || []; // Extract results array from response
        setResults(stockResults.slice(0, 10)); // Limit to 10 results
        setShowDropdown(true);
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Search error:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (stock) => {
    setQuery('');
    setShowDropdown(false);
    setResults([]);
    onSelectStock(stock);
  };

  const handleKeyDown = (e) => {
    if (!showDropdown || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => 
          prev < results.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => 
          prev > 0 ? prev - 1 : results.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          handleSelect(results[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        setSelectedIndex(-1);
        break;
      default:
        break;
    }
  };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setShowDropdown(false);
    inputRef.current?.focus();
  };

  return (
    <div className="search-box">
      <div className="search-input-wrapper">
        <span className="search-icon">🔍</span>
        <input
          ref={inputRef}
          type="text"
          className="search-input"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setShowDropdown(true)}
        />
        {loading && <div className="search-spinner" />}
        {!loading && query && (
          <button className="search-clear" onClick={clearSearch}>
            ✕
          </button>
        )}
      </div>

      {showDropdown && (
        <div className="search-dropdown" ref={dropdownRef}>
          {results.length > 0 ? (
            results.map((stock, index) => (
              <div
                key={stock.ticker}
                className={`search-result-item ${index === selectedIndex ? 'selected' : ''}`}
                onClick={() => handleSelect(stock)}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <div className="stock-result-info">
                  <span className="stock-result-name">{stock.name}</span>
                  <span className="stock-result-ticker">{stock.ticker}</span>
                </div>
                <span className="stock-result-sector">{stock.sector}</span>
              </div>
            ))
          ) : (
            <div className="search-empty">
              No stocks found for "{query}"
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBox;
