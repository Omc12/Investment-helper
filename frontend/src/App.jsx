import { useState, useCallback } from 'react';
import Navbar from './components/Navbar';
import StockDetailView from './components/StockDetailView';
import './styles.css';

/**
 * App - Main application with Groww-like dark mode UI
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
        {selectedStock ? (
          /* Stock Detail View */
          <StockDetailView 
            stock={selectedStock} 
            onBack={handleBack} 
          />
        ) : (
          /* Empty State - Only shows search prompt */
          <div className="empty-state-center">
            <span className="empty-state-icon">🔍</span>
            <h2 className="empty-state-title">Search for a Stock</h2>
            <p className="empty-state-text">
              Use the search bar above to find any stock. We'll fetch fresh data from APIs,
              show you the charts, details, and AI-powered price predictions.
            </p>
            <div className="empty-state-steps">
              <div className="step">
                <span className="step-number">1</span>
                <span className="step-text">Search for a stock</span>
              </div>
              <div className="step">
                <span className="step-number">2</span>
                <span className="step-text">We fetch fresh data</span>
              </div>
              <div className="step">
                <span className="step-number">3</span>
                <span className="step-text">View charts & predictions</span>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
