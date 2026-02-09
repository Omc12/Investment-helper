import { useState } from 'react';
import Navbar from './components/Navbar';
import StockDetailView from './components/StockDetailView';
import Dashboard from './components/Dashboard';

function App() {
  const [selectedStock, setSelectedStock] = useState(null);

  const handleStockSelect = (stock) => {
    setSelectedStock(stock);
  };

  const handleBack = () => {
    setSelectedStock(null);
  };

  return (
    <div className="app-container">
      <Navbar onSelectStock={handleStockSelect} />

      <main className="main-content">
        {selectedStock ? (
          <StockDetailView
            stock={selectedStock}
            onBack={handleBack}
          />
        ) : (
          <Dashboard onSelectStock={handleStockSelect} />
        )}
      </main>
    </div>
  );
}

export default App;
