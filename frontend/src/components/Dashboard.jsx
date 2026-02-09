import { useState } from 'react';

const Dashboard = ({ onSelectStock }) => {
    const [activeList, setActiveList] = useState('gainers');

    // Mock Data
    const indices = [
        { name: 'NIFTY 50', value: 24852.15, change: 125.30, percent: 0.51, isPositive: true },
        { name: 'SENSEX', value: 81750.45, change: 350.20, percent: 0.43, isPositive: true },
        { name: 'BANK NIFTY', value: 52400.10, change: -150.50, percent: -0.29, isPositive: false },
    ];

    const gainers = [
        { ticker: 'RELIANCE', name: 'Reliance Industries', price: 2985.45, change: 45.20, percent: 1.54 },
        { ticker: 'TCS', name: 'Tata Consultancy Svcs', price: 4120.30, change: 50.15, percent: 1.23 },
        { ticker: 'INFY', name: 'Infosys Limited', price: 1650.00, change: 22.50, percent: 1.38 },
        { ticker: 'HDFCBANK', name: 'HDFC Bank', price: 1680.20, change: 15.10, percent: 0.91 },
    ];

    const losers = [
        { ticker: 'ADANIENT', name: 'Adani Enterprises', price: 3150.00, change: -45.50, percent: -1.42 },
        { ticker: 'SBIN', name: 'State Bank of India', price: 820.50, change: -8.20, percent: -0.99 },
        { ticker: 'TATAMOTORS', name: 'Tata Motors', price: 980.10, change: -12.30, percent: -1.24 },
    ];

    const displayList = activeList === 'gainers' ? gainers : losers;

    const formatPrice = (price) => {
        return '₹' + new Intl.NumberFormat('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(price);
    };

    return (
        <div className="dashboard">
            <h2 className="section-title">Market Overview</h2>

            {/* Indices */}
            <div className="indices-container">
                {indices.map((index) => (
                    <div key={index.name} className="index-card">
                        <div className="index-header">{index.name}</div>
                        <div className="index-price">{formatPrice(index.value)}</div>
                        <div className={`index-change ${index.isPositive ? 'text-green' : 'text-red'}`}>
                            {index.change > 0 ? '+' : ''}{index.change} ({index.percent}%)
                        </div>
                    </div>
                ))}
            </div>

            {/* Lists */}
            <div className="section-title">Top Movers</div>
            <div className="stock-table-card">
                <div className="tabs-header">
                    <button
                        className={`tab-btn ${activeList === 'gainers' ? 'active' : ''}`}
                        onClick={() => setActiveList('gainers')}
                    >
                        Top Gainers
                    </button>
                    <button
                        className={`tab-btn ${activeList === 'losers' ? 'active' : ''}`}
                        onClick={() => setActiveList('losers')}
                    >
                        Top Losers
                    </button>
                </div>

                <div className="stock-list">
                    {displayList.map((stock) => (
                        <div
                            key={stock.ticker}
                            className="stock-item"
                            onClick={() => onSelectStock(stock)}
                        >
                            <div className="stock-info-main">
                                <div className="stock-icon">{stock.ticker[0]}</div>
                                <div>
                                    <div className="stock-name">{stock.name}</div>
                                    <div className="stock-symbol">{stock.ticker}</div>
                                </div>
                            </div>
                            <div className="stock-row-price">
                                <div className="price-val">{formatPrice(stock.price)}</div>
                                <div className={`price-change ${stock.percent >= 0 ? 'text-green' : 'text-red'}`}>
                                    {stock.percent > 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.percent}%)
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
