import { motion } from 'framer-motion';
import { TrendingUp, RefreshCw } from 'lucide-react';
import SearchBox from './SearchBox';

/**
 * Navbar - Sticky top navigation with modern design and animations
 */
const Navbar = ({ onSelectStock, onRefresh, refreshing }) => {
  return (
    <motion.nav 
      className="navbar"
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="navbar-content">
        <motion.div 
          className="navbar-brand" 
          onClick={() => window.location.reload()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <TrendingUp size={24} className="navbar-icon" />
          <span className="navbar-logo">StockAI</span>
          <span className="navbar-tagline">AI-Powered Indian Stocks</span>
        </motion.div>

        <div className="navbar-search">
          <SearchBox 
            onSelectStock={onSelectStock} 
            placeholder="Search stocks (e.g., Reliance, TCS)..."
          />
        </div>

        <div className="navbar-actions">
          <motion.button 
            className={`navbar-btn ${refreshing ? 'refreshing' : ''}`}
            onClick={onRefresh}
            title="Refresh data"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <RefreshCw 
              size={18} 
              className={refreshing ? 'spinning' : ''}
            />
          </motion.button>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
