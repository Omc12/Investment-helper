import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, BarChart3 } from 'lucide-react';
import Navbar from './components/Navbar';
import StockDetailView from './components/StockDetailView';
import './styles.css';

/**
 * App - Main application with modern dark mode UI
 */
function App() {
  const [selectedStock, setSelectedStock] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  const handleSelectStock = useCallback((stock) => {
    // Handle both full stock object and search result
    const stockData = stock.ticker ? stock : { 
      ticker: stock, 
      name: stock.replace('.NS', ''),
      sector: 'Unknown' 
    };
    setSelectedStock(stockData);
  }, []);

  const handleBack = useCallback(() => {
    setSelectedStock(null);
  }, []);

  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    setRefreshKey(prev => prev + 1);
    setTimeout(() => setRefreshing(false), 1000);
  }, []);

  return (
    <div className="app-container">
      {/* Navbar */}
      <Navbar 
        onSelectStock={handleSelectStock}
        onRefresh={handleRefresh}
        refreshing={refreshing}
      />

      {/* Main Content */}
      <main className="app-main">
        <AnimatePresence mode="wait">
          {selectedStock ? (
            /* Stock Detail View */
            <motion.div
              key="stock-detail"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <StockDetailView 
                stock={selectedStock} 
                onBack={handleBack} 
              />
            </motion.div>
          ) : (
            /* Empty State - Only shows search prompt */
            <motion.div 
              key="empty-state"
              className="empty-state-center"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              >
                <Search size={64} className="empty-state-icon-svg" />
              </motion.div>
              <motion.h2 
                className="empty-state-title"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                Search for a Stock
              </motion.h2>
              <motion.p 
                className="empty-state-text"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                Use the search bar above to find any stock. We'll fetch fresh data from APIs,
                show you the charts, details, and AI-powered price predictions.
              </motion.p>
              <motion.div 
                className="empty-state-steps"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <motion.div 
                  className="step"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 }}
                  whileHover={{ scale: 1.05, x: 10 }}
                >
                  <span className="step-number">1</span>
                  <span className="step-text">Search for a stock</span>
                </motion.div>
                <motion.div 
                  className="step"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 }}
                  whileHover={{ scale: 1.05, x: 10 }}
                >
                  <span className="step-number">2</span>
                  <span className="step-text">We fetch fresh data</span>
                </motion.div>
                <motion.div 
                  className="step"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8 }}
                  whileHover={{ scale: 1.05, x: 10 }}
                >
                  <span className="step-number">3</span>
                  <span className="step-text">View charts & predictions</span>
                </motion.div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
