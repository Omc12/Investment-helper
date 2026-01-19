import SearchBox from './SearchBox';

/**
 * Navbar - Sticky top navigation with Groww-style design
 */
const Navbar = ({ onSelectStock, onRefresh, refreshing }) => {
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="navbar-brand" onClick={() => window.location.reload()}>
          <span className="navbar-logo">StockAI</span>
          <span className="navbar-tagline">AI-Powered Indian Stocks</span>
        </div>

        <div className="navbar-search">
          <SearchBox 
            onSelectStock={onSelectStock} 
            placeholder="Search stocks (e.g., Reliance, TCS)..."
          />
        </div>

        <div className="navbar-actions">
          <button 
            className={`navbar-btn ${refreshing ? 'refreshing' : ''}`}
            onClick={onRefresh}
            title="Refresh data"
          >
            🔄
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
