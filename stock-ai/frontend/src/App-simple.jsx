import './styles.css';

/**
 * Simple App test - Basic functionality without charts
 */
function App() {
  return (
    <div className="app-container">
      <div style={{ padding: '20px', color: 'white', background: 'var(--bg-primary)' }}>
        <h1>StockAI - Test Mode</h1>
        <p>If you can see this, the basic React app is working.</p>
        <div style={{ 
          background: 'var(--bg-card)', 
          padding: '20px', 
          borderRadius: '10px',
          margin: '20px 0'
        }}>
          <h2>Test Card</h2>
          <p>This should have dark styling from CSS variables.</p>
        </div>
      </div>
    </div>
  );
}

export default App;