import { useState, useCallback } from 'react';
import Navbar from './components/Navbar';
import MarketOverview from './components/MarketOverview';
import TrendingStocks from './components/TrendingStocks';
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
          /* Dashboard View */
          <>
            {/* Market Overview (NIFTY 50 & BANKNIFTY) */}
            <MarketOverview key={`market-${refreshKey}`} />

            {/* Trending Stocks */}
            <TrendingStocks 
              key={`trending-${refreshKey}`}
              onSelectStock={handleSelectStock} 
            />

            {/* Empty State */}
            <div className="empty-state">
              <span className="empty-state-icon">🔍</span>
              <h2 className="empty-state-title">Search Any Stock</h2>
              <p className="empty-state-text">
                Use the search bar above to find any NSE stock. Get live prices, 
                interactive charts, and AI-powered predictions.
              </p>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
