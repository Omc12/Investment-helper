# 🇮🇳 Indian Stock Predictor AI - Production Edition

A production-grade full-stack application for predicting Indian stock movements using machine learning. Features clean architecture, caching, walk-forward validation, and 25+ engineered features.

## 🎯 Key Features

### Backend (FastAPI)
- ✅ **Clean Architecture**: Modular structure with separation of concerns (core/, services/, routes/)
- ✅ **Intelligent Caching**: Multi-level TTL cache (5min - 1hr) for optimal performance
- ✅ **Walk-Forward Validation**: 3-fold time-series cross-validation (60-80%, 70-90%, 80-100%)
- ✅ **25+ ML Features**: RSI, MACD, Bollinger Bands, EMA, Stochastic, ATR, Volume ratios, and more
- ✅ **200+ NSE Stocks**: Comprehensive coverage of NIFTY 50 + popular mid/small caps
- ✅ **Free Data Only**: Uses Yahoo Finance via yfinance (no paid APIs)

### Frontend (React + Vite)
- ✅ **Component-Based**: SearchBox, StockCard, PriceChart, PredictionPanel
- ✅ **Autocomplete Search**: Fast debounced search with keyboard navigation
- ✅ **Interactive Charts**: Multi-timeframe price & volume charts with Chart.js
- ✅ **Live Stock Details**: Market cap, P/E ratio, 52-week high/low, volume
- ✅ **ML Predictions**: Buy/Sell/Hold signals with confidence scores

### ML Model
- **Algorithm**: HistGradientBoostingClassifier (fast & accurate)
- **Features**: 25+ technical indicators
- **Validation**: Walk-forward time-series validation
- **Target**: Next-day price movement (Up/Down)
- **Caching**: Model predictions cached for 10 minutes

## 📁 Project Structure

```
stock-ai/
├── backend/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration (API, CORS, cache TTLs)
│   │   └── cache.py           # Caching utilities & decorators
│   ├── services/
│   │   ├── __init__.py
│   │   ├── yahoo_service.py   # Yahoo Finance wrapper
│   │   ├── stock_service.py   # Stock list management
│   │   ├── features.py        # Feature engineering (25+ features)
│   │   └── model_service.py   # ML model training & prediction
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py          # Health check + cache info
│   │   ├── stocks.py          # Stock endpoints
│   │   └── predict.py         # Prediction endpoint
│   ├── data/
│   │   └── stocks_nse.json    # 200+ NSE stocks database
│   ├── main.py                # FastAPI app initialization
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBox.jsx       # Autocomplete search
│   │   │   ├── StockCard.jsx       # Stock details display
│   │   │   ├── PriceChart.jsx      # Interactive chart
│   │   │   └── PredictionPanel.jsx # ML predictions
│   │   ├── App.jsx            # Main application
│   │   ├── api.js             # API client functions
│   │   └── styles.css         # Complete styling
│   └── package.json           # Node dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd stock-ai/backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python3 main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: **http://localhost:8000**

API Docs (Swagger): **http://localhost:8000/docs**

### 2. Frontend Setup

```bash
cd stock-ai/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run at: **http://localhost:5173**

## 📊 API Endpoints

### Health & Monitoring
- `GET /health` - Health check
- `GET /health/cache` - Cache statistics

### Stock Data
- `GET /stocks` - Get all available stocks (200+)
- `GET /stocks/search?query={text}` - Search stocks (autocomplete)
- `GET /stocks/details?ticker={ticker}` - Get stock details (cached 5min)
- `GET /stocks/candles?ticker={ticker}&period={period}` - Get OHLCV data (cached)

### Predictions
- `GET /predict?ticker={ticker}` - Get ML prediction (cached 10min)

### Supported Periods for Candles
- `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `max`

## 🧠 ML Features (25+)

### Price-based Features
- Return_1, Return_5, Return_10, Return_20
- LogReturn_1
- HL_Range (High-Low range)
- Gap (Open vs Previous Close)

### Moving Averages
- SMA_10, SMA_20, SMA_50
- EMA_10, EMA_20

### Volatility
- Volatility_10, Volatility_20

### Technical Indicators
- RSI_14 (Relative Strength Index)
- MACD, MACD_Signal
- Stochastic_K, Stochastic_D
- Bollinger_Upper, Bollinger_Lower, Bollinger_Width
- ATR_14 (Average True Range)

### Volume Features
- Volume_Change
- Volume_SMA20
- Volume_Ratio

## ⚙️ Configuration

Edit `backend/core/config.py` to customize:

```python
# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Cache TTLs (in seconds)
CACHE_STOCK_DETAILS = 300      # 5 minutes
CACHE_CANDLES_DAILY = 1800     # 30 minutes
CACHE_CANDLES_INTRADAY = 30    # 30 seconds
CACHE_MODEL = 600              # 10 minutes
CACHE_STOCK_LIST = 3600        # 1 hour

# ML Model
MODEL_FEATURES = 25+
MODEL_TEST_SIZE = 0.2
CONFIDENCE_THRESHOLD_HIGH = 0.7
CONFIDENCE_THRESHOLD_LOW = 0.55
```

## 🎨 Frontend Components

### SearchBox
- Debounced autocomplete search
- Keyboard navigation (Arrow keys, Enter, Escape)
- Sector badges
- 300ms debounce delay

### StockCard
- Live stock price
- Market cap, P/E ratio
- 52-week high/low
- Volume & average volume
- Price change percentage

### PriceChart
- Interactive Line + Bar chart
- Multiple timeframes (1D, 5D, 1M, 3M, 6M, 1Y)
- Price & volume overlay
- Responsive design

### PredictionPanel
- Buy/Sell/Hold signals
- Probability scores
- Confidence levels (High/Medium/Low)
- Walk-forward validation scores
- Feature importance display

## 📦 Dependencies

### Backend
```
fastapi          # Web framework
uvicorn          # ASGI server
yfinance         # Yahoo Finance API
pandas           # Data manipulation
numpy            # Numerical operations
scikit-learn     # ML models
cachetools       # Caching utilities
```

### Frontend
```
react            # UI framework
react-dom        # React DOM rendering
chart.js         # Charting library
react-chartjs-2  # React wrapper for Chart.js
vite             # Build tool
```

## 🔍 How It Works

### 1. Data Collection
- Fetches historical price data from Yahoo Finance (1 year)
- Supports NSE tickers (e.g., RELIANCE.NS, TCS.NS)

### 2. Feature Engineering
- Calculates 25+ technical indicators
- Uses rolling windows (10, 20, 50 days)
- Handles missing data gracefully

### 3. Model Training (Walk-Forward Validation)
- **Fold 1**: Train on 60-80% of data, test on next 20%
- **Fold 2**: Train on 70-90% of data, test on next 20%
- **Fold 3**: Train on 80-100% of data, predict tomorrow
- Averages validation scores across folds

### 4. Prediction
- Predicts next-day price movement (Up/Down)
- Returns probability & confidence level
- Caches results for 10 minutes

### 5. Caching Strategy
- **Stock List**: 1 hour (rarely changes)
- **Stock Details**: 5 minutes (market data)
- **Daily Candles**: 30 minutes (historical data)
- **Intraday Candles**: 30 seconds (real-time data)
- **Model Predictions**: 10 minutes (computationally expensive)

## 🚨 Important Notes

1. **Not Financial Advice**: This is an educational project. Always do your own research before investing.

2. **Data Limitations**: Uses free Yahoo Finance data which may have:
   - 15-20 minute delays
   - Occasional missing data
   - Rate limiting

3. **Model Performance**: ML models are trained on historical data and cannot predict unforeseen events (earnings, news, global events).

4. **Cache Behavior**: First prediction for a stock will take 5-10 seconds (model training). Subsequent requests will be instant (cached).

5. **Stock Tickers**: Must use NSE format (e.g., `RELIANCE.NS`, not just `RELIANCE`)

## 🧪 Testing

### Test Backend
```bash
# Health check
curl http://localhost:8000/health

# Search stocks
curl "http://localhost:8000/stocks/search?query=reliance"

# Get stock details
curl "http://localhost:8000/stocks/details?ticker=RELIANCE.NS"

# Get prediction
curl "http://localhost:8000/predict?ticker=RELIANCE.NS"
```

### Test Frontend
1. Open http://localhost:5173
2. Search for "Reliance"
3. Select "RELIANCE.NS"
4. View stock details, chart, and click "Get Prediction"

## 📈 Adding More Stocks

Edit `backend/data/stocks_nse.json`:

```json
{
  "ticker": "STOCKNAME.NS",
  "name": "Stock Full Name",
  "sector": "Sector Name"
}
```

The app will automatically pick up the new stock on next startup.

## 🛠️ Troubleshooting

### Backend won't start
- Check if port 8000 is available: `lsof -i :8000`
- Verify Python version: `python3 --version` (3.8+ required)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Frontend won't start
- Check if port 5173 is available
- Delete `node_modules` and run `npm install` again
- Clear browser cache

### Predictions taking too long
- First prediction trains the model (5-10 sec)
- Check cache status: `curl http://localhost:8000/health/cache`
- Reduce historical data period in `config.py`

### Yahoo Finance errors
- Check internet connection
- Verify ticker format (must end with .NS for NSE)
- Try different stock (some stocks may have limited data)

## 🎯 Future Enhancements

- [ ] Add more ML models (LSTM, Random Forest, XGBoost)
- [ ] Feature importance visualization
- [ ] Portfolio tracking
- [ ] Real-time alerts
- [ ] Historical prediction accuracy tracking
- [ ] News sentiment analysis
- [ ] Backtesting module
- [ ] Mobile responsive improvements
- [ ] Dark mode

## 📜 License

This project is for educational purposes only. Not licensed for commercial use.

## 🤝 Contributing

This is a personal educational project, but suggestions are welcome!

## 📧 Support

For issues or questions, check the code comments or review the API docs at http://localhost:8000/docs

---

**Happy Trading! 📈** (But remember: This is not financial advice! 😊)
