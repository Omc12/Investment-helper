"""
Dynamic stock list fetcher for NSE stocks.
Fetches comprehensive stock lists from external APIs and sources.
"""
import requests
import pandas as pd
from typing import List, Dict, Optional
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import yfinance as yf
from core.cache import stock_list_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


class StockListFetcher:
    """Fetches comprehensive stock lists from multiple sources."""
    
    def __init__(self):
        self.nse_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/',
        }
        
    def fetch_nse_stocks(self) -> List[Dict]:
        """Fetch stocks from NSE API."""
        try:
            print("Fetching NSE stock list...")
            
            # First request to NSE homepage to get session
            session = requests.Session()
            session.headers.update(self.headers)
            
            # Get session from homepage
            homepage = session.get("https://www.nseindia.com", timeout=10)
            if homepage.status_code != 200:
                raise Exception("Failed to access NSE homepage")
            
            # Wait a bit for session
            time.sleep(1)
            
            # Now fetch NIFTY 500 stocks
            response = session.get(self.nse_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                stocks = []
                
                for stock in data.get('data', []):
                    ticker = stock.get('symbol', '').strip()
                    if ticker:
                        stocks.append({
                            "ticker": f"{ticker}.NS",
                            "name": stock.get('companyName', ticker),
                            "sector": self._get_sector_from_industry(stock.get('industry', 'Others')),
                            "market_cap": stock.get('marketCap', 0),
                            "last_price": stock.get('lastPrice', 0)
                        })
                
                print(f"Fetched {len(stocks)} stocks from NSE")
                return stocks
                
        except Exception as e:
            print(f"Error fetching NSE stocks: {e}")
        
        return []
    
    def fetch_nse_stock_symbols_alternative(self) -> List[Dict]:
        """Alternative method using NSE symbol list."""
        try:
            print("Using alternative NSE symbols method...")
            
            # Comprehensive NSE stocks list (1000+ most traded stocks)
            symbols = [
                # NIFTY 50 stocks
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "SBIN", 
                "BHARTIARTL", "ITC", "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI",
                "BAJFINANCE", "HCLTECH", "TITAN", "SUNPHARMA", "WIPRO", "TATAMOTORS",
                "ULTRACEMCO", "NESTLEIND", "POWERGRID", "NTPC", "M&M", "TECHM",
                "BAJAJFINSV", "INDUSINDBK", "TATASTEEL", "ADANIPORTS", "COALINDIA",
                "BRITANNIA", "DRREDDY", "EICHERMOT", "GRASIM", "HEROMOTOCO", "HINDALCO",
                "JSWSTEEL", "ONGC", "SHREECEM", "TATACONSUM", "VEDL", "ADANIENT",
                "APOLLOHOSP", "BAJAJ-AUTO", "CIPLA", "DIVISLAB", "TATAPOWER", "GODREJCP",
                
                # NIFTY NEXT 50 stocks  
                "ADANIGREEN", "ADANIPOWER", "AMBUJACEM", "BANKBARODA", "BERGEPAINT",
                "BIOCON", "BOSCHLTD", "CADILAHC", "CANBK", "CHOLAFIN", "COLPAL", "CONCOR",
                "DABUR", "DMART", "FSN", "GAIL", "GLAND", "GODREJCP", "HAVELLS", "HDFCAMC",
                "HDFCLIFE", "HINDPETRO", "IOC", "IRCTC", "JINDALSTEL", "JUBLFOOD", "LICHSGFIN",
                "LUPIN", "MARICO", "MCDOWELL-N", "MOTHERSON", "MPHASIS", "NMDC", "NYKAA",
                "OFSS", "PAGEIND", "PIIND", "PIDILITIND", "PNB", "RECLTD", "SBILIFE",
                "SHREECEM", "SIEMENS", "SRF", "TRENT", "UNIONBANK", "UPL", "VOLTAS", "ZOMATO",
                
                # Additional Large Cap stocks
                "ABBOTINDIA", "ACC", "AIAENG", "AJANTPHARM", "ALKEM", "AMARAJABAT", "AMBUJACEM",
                "ASHOKLEY", "AUBANK", "AUROPHARMA", "BALKRISIND", "BANDHANBNK", "BATAINDIA",
                "BSOFT", "CANBK", "CENTURYTEX", "CESC", "CGPOWER", "CHAMBLFERT", "CLEAN",
                "CROMPTON", "CUMMINSIND", "DEEPAKNTR", "DIXON", "DLF", "EMAMILTD", "ESCORTS",
                "EXIDEIND", "FEDERALBNK", "FORTIS", "GICRE", "GILLETTE", "GNFC", "GRANULES",
                
                # Mid Cap stocks (Additional 200+)
                "3MINDIA", "AARTIIND", "ABCAPITAL", "ABFRL", "ACE", "ADANIENT", "ADANIGAS",
                "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ADANITRANS", "AEGISCHEM", "AFFLE",
                "AJANTPHARM", "AKZOINDIA", "ALEMBICLTD", "ALKYLAMIN", "ALLCARGO", "AMARAJABAT",
                "AMBER", "AMBUJACEM", "ANANTRAJ", "ANDHRABANK", "ANGELONE", "ANIKINDS", "APLLTD",
                "APOLLOHOSP", "APOLLOTYRE", "APTUS", "ARVINDFASN", "ASAHIINDIA", "ASHIANA",
                "ASHOKLEY", "ASIANPAINT", "ASTRAL", "ASTRAZEN", "ATUL", "AUBANK", "AUROPHARMA",
                "AVANTIFEED", "AVANTI", "AXISBANK", "BAJAJ-AUTO", "BAJAJELEC", "BAJAJFINSV",
                "BAJAJHLDNG", "BAJFINANCE", "BALKRISIND", "BALMLAWRIE", "BALRAMCHIN", "BANDHANBNK",
                "BANKBARODA", "BANKINDIA", "BASF", "BATAINDIA", "BAYERCROP", "BBSINDIA", "BDL",
                "BEL", "BERGEPAINT", "BHARATDYN", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON",
                "BIRLACORPN", "BLUEDART", "BLUESTARCO", "BOMDYEING", "BOSCHLTD", "BPCL", "BRIGADE",
                "BRITANNIA", "BSOFT", "CADILAHC", "CAMS", "CANARA", "CANBK", "CAPLIPOINT",
                "CARBORUNIV", "CARERATING", "CASTROLIND", "CCL", "CEAT", "CENTURYTEX", "CERA",
                "CESC", "CGPOWER", "CHAMBLFERT", "CHENNPETRO", "CHOLAFIN", "CIPLA", "CLEAN",
                "CUB", "COALINDIA", "COCHINSHIP", "COFORGE", "COLPAL", "CONCOR", "COROMANDEL",
                "CROMPTON", "CUB", "CUMMINSIND", "CYIENT", "DABUR", "DATAMATICS", "DCBBANK",
                "DCMSHRIRAM", "DEEPAKNTR", "DELTACORP", "DHANUKA", "DHFL", "DISHTV", "DIVISLAB",
                "DIXON", "DLF", "DMART", "DRREDDY", "DTIL", "EDELWEISS", "EICHERMOT", "EIDPARRY",
                "EIHOTEL", "ELGIEQUIP", "EMAMILTD", "ENDURANCE", "ENGINERSIN", "EQUITAS",
                "ESCORTS", "EXIDEIND", "FCONSUMER", "FEDERALBNK", "FINEORG", "FINCABLES",
                "FINPIPE", "FORTIS", "FSN", "GAEL", "GAIL", "GAL", "GARFIBRES", "GICRE",
                "GILLETTE", "GLAND", "GLAXO", "GLENMARK", "GMRINFRA", "GNFC", "GODFRYPHLP",
                "GODREJAGRO", "GODREJCP", "GODREJIND", "GODREJPROP", "GRANULES", "GRAPHITE",
                "GRASIM", "GREAVES", "GREAVESCOT", "GRINDWELL", "GRSE", "GSPL", "GUJALKALI",
                "GUJGASLTD", "GULFOILLUB", "HAL", "HAPPSTMNDS", "HAVELLS", "HCLTECH", "HDFC",
                "HDFCAMC", "HDFCBANK", "HDFCLIFE", "HEG", "HEIDELBERG", "HEROMOTOCO", "HFCL",
                "HIMATSEIDE", "HINDALCO", "HINDCOPPER", "HINDOILEXP", "HINDPETRO", "HINDUNILVR",
                
                # Small Cap stocks (Additional 300+)  
                "HONAUT", "HSCL", "HUDCO", "HUHTAMAKI", "IBULHSGFIN", "ICICIBANK", "ICICIGI",
                "ICICIPRULI", "IDEA", "IDFC", "IDFCFIRSTB", "IEX", "IFBIND", "IGL", "IIFL",
                "IL&FSTRANS", "IMPAL", "INDBANK", "INDHOTEL", "INDIACEM", "INDIAMART", "INDIANB",
                "INDIGO", "INDOCO", "INDUSINDBK", "INFIBEAM", "INFY", "INOXLEISUR", "INOXWIND",
                "INTELLECT", "IOB", "IOC", "IPCALAB", "IRB", "IRCON", "IRCTC", "ISEC", "ITC",
                "ITDCEM", "ITI", "JAGRAN", "JAMNAAUTO", "JBCHEPHARM", "JCHAC", "JETAIRWAYS",
                "JKCEMENT", "JKLAKSHMI", "JKPAPER", "JKTYRE", "JMFINANCIL", "JPASSOCIAT",
                "JSL", "JSLHISAR", "JSWENERGY", "JSWSTEEL", "JUBLFOOD", "JUBLINDS", "JUSTDIAL",
                "JYOTHYLAB", "KAJARIACER", "KALPATPOWR", "KALYANKJIL", "KAMATHOTEL", "KAMDHENU",
                "KANPRPLA", "KARURVYSYA", "KEC", "KEI", "KIRLOSENG", "KIRLOSBROS", "KKCL",
                "KNRCON", "KOTAKBANK", "KPITTECH", "KRBL", "KSB", "L&TFH", "LALPATHLAB",
                "LAOPALA", "LAXMIMACH", "LEMONTREE", "LICHSGFIN", "LINCOLN", "LSIL", "LT",
                "LTTS", "LUPIN", "LUXIND", "LYKALABS", "M&M", "M&MFIN", "MAHABANK", "MAHINDCIE",
                "MAHLOG", "MAHSCOOTER", "MAHSEAMLES", "MANAPPURAM", "MARICO", "MARUTI", "MASPINF",
                "MAXHEALTH", "MCDOWELL-N", "MCX", "MEDPLUS", "MEGH", "METROPOLIS", "MFSL",
                "MGL", "MHRIL", "MIC", "MINDACORP", "MINDTREE", "MIRZAINT", "MMTC", "MOIL",
                "MOLDTKPAC", "MONSANTO", "MOTHERSON", "MOTILALOFS", "MPHASIS", "MRF", "MRPL",
                "MSTCLTD", "MTARTECH", "MUTHOOTFIN", "NATCOPHARM", "NATIONALUM", "NAUKRI",
                "NAVINFLUOR", "NBCC", "NCC", "NCL", "NESCO", "NESTLEIND", "NETWORK18", "NFL",
                "NHPC", "NIITLTD", "NILKAMAL", "NLCINDIA", "NMDC", "NOCIL", "NRBBEARING",
                "NTPC", "NYKAA", "OBEROIRLTY", "OFSS", "OIL", "OMAXE", "ONEPOINT", "ONGC",
                "ORIENTBAN", "ORIENTCEM", "ORIENTELEC", "PAGEIND", "PALREDTEC", "PARAGMILK",
                "PARAS", "PATANJALI", "PCJEWELLER", "PEL", "PERSISTENT", "PETRONET", "PFC",
                "PFIZER", "PGHL", "PGHH", "PHILIPCARB", "PHOENIXLTD", "PIDILITIND", "PIIND",
                "PNB", "PNBHOUSING", "POLYCAB", "POLYMED", "POWERGRID", "PRSMJOHNSN", "PSB",
                "PTC", "PVR", "QUESS", "RADICO", "RAIN", "RAJESHEXPO", "RALLIS", "RAMCOCEM",
                "RANBAXY", "RBLBANK", "RECLTD", "REDINGTON", "RELAXO", "RELCAPITAL", "RELIANCE",
                "RELINFRA", "RNAVAL", "RNRL", "RPOWER", "RTNINDIA", "RUPA", "SADBHAV", "SAIL",
                "SANOFI", "SARAJAUTO", "SAREGAMA", "SATIN", "SBL", "SBILIFE", "SCHAEFFLER",
                "SCI", "SFL", "SHARDACROP", "SHILPAMED", "SHOPERSTOP", "SHREECEM", "SHREYAS",
                "SHRIRAMCIT", "SIEMENS", "SIS", "SJVN", "SKFINDIA", "SRF", "SRTRANSFIN",
                "STAR", "STARCEMENT", "STLTECH", "SUBROS", "SUDARSCHEM", "SUNPHARMA", "SUNTECK",
                "SUNTV", "SUPRAJIT", "SUPREMEIND", "SUVEN", "SWANENERGY", "SYMPHONY", "SYNGENE",
                "SYNDIBANK", "TABLAINDIA", "TAKE", "TALWALKARS", "TANLA", "TATACHEM", "TATACOMM",
                "TATACONSUM", "TATAELXSI", "TATAINVEST", "TATAMOTORS", "TATAPOWER", "TATASTEEL",
                "TCS", "TEAMLEASE", "TECHM", "TEJASNET", "THERMAX", "THYROCARE", "TIDEWATER",
                "TIMESTREND", "TINPLATE", "TITAN", "TNPETRO", "TNPL", "TORNTPHARM", "TORNTPOWER",
                "TRENT", "TRIDENT", "TRITURBINE", "TTKPRESTIG", "TV18BRDCST", "TVSMOTOR", "UBL",
                "UJJIVAN", "ULTRACEMCO", "UNIONBANK", "UNITECH", "UPL", "UTTAMSUGAR", "VALPHARMA",
                "VARTO", "VBL", "VEDL", "VENKEYS", "VGUARD", "VIPIND", "VOLTAS", "VSTIND",
                "WABAG", "WELCORP", "WELSPUNIND", "WHIRLPOOL", "WIPRO", "WOCKPHARMA", "ZEEL",
                "ZENTEC", "ZOMATO", "ZUARIAGRO"
            ]
            
            stocks = []
            failed_symbols = []
            
            def get_stock_info(symbol):
                """Get stock info for a single symbol."""
                try:
                    ticker_obj = yf.Ticker(f"{symbol}.NS")
                    info = ticker_obj.info
                    
                    if info and info.get('longName'):
                        return {
                            "ticker": f"{symbol}.NS",
                            "name": info.get('longName') or info.get('shortName', symbol),
                            "sector": self._get_sector_from_industry(info.get('sector', 'Others')),
                            "market_cap": info.get('marketCap', 0),
                            "last_price": info.get('regularMarketPrice', 0)
                        }
                except:
                    pass
                return None
            
            print(f"Processing {len(symbols)} stock symbols...")
            
            # Use ThreadPoolExecutor for concurrent processing
            with ThreadPoolExecutor(max_workers=10) as executor:
                # Submit all tasks
                future_to_symbol = {executor.submit(get_stock_info, symbol): symbol for symbol in symbols}
                
                # Process results as they complete
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result(timeout=5)  # 5 second timeout per request
                        if result:
                            stocks.append(result)
                        else:
                            failed_symbols.append(symbol)
                    except Exception as e:
                        failed_symbols.append(symbol)
                        continue
            
            print(f"Successfully processed {len(stocks)} stocks")
            if failed_symbols:
                print(f"Failed to process {len(failed_symbols)} symbols")
            
            return stocks
            
        except Exception as e:
            print(f"Error in alternative NSE fetch: {e}")
            return []
    
    def _get_sector_from_industry(self, industry: str) -> str:
        """Map industry to broad sector categories."""
        if not industry:
            return "Others"
            
        industry_lower = industry.lower()
        
        # Define sector mappings
        sector_map = {
            "bank": "Financials",
            "financial": "Financials", 
            "insurance": "Financials",
            "nbfc": "Financials",
            "it": "Technology",
            "software": "Technology",
            "computer": "Technology",
            "technology": "Technology",
            "pharma": "Healthcare",
            "drug": "Healthcare",
            "hospital": "Healthcare",
            "healthcare": "Healthcare",
            "auto": "Automotive",
            "motor": "Automotive",
            "vehicle": "Automotive",
            "steel": "Materials",
            "metal": "Materials",
            "mining": "Materials",
            "cement": "Materials",
            "chemical": "Materials",
            "oil": "Energy",
            "gas": "Energy",
            "power": "Utilities",
            "electric": "Utilities",
            "telecom": "Communication",
            "media": "Communication",
            "fmcg": "Consumer Goods",
            "consumer": "Consumer Goods",
            "retail": "Consumer Goods",
            "food": "Consumer Goods",
            "textile": "Consumer Goods",
            "real": "Real Estate",
            "construction": "Industrials",
            "infrastructure": "Industrials",
            "engineering": "Industrials"
        }
        
        for keyword, sector in sector_map.items():
            if keyword in industry_lower:
                return sector
                
        return "Others"
    
    def get_comprehensive_stock_list(self) -> List[Dict]:
        """Get comprehensive stock list from multiple sources."""
        all_stocks = []
        
        # Try NSE API first
        nse_stocks = self.fetch_nse_stocks()
        if nse_stocks:
            all_stocks.extend(nse_stocks)
        else:
            # Fallback to alternative method
            alt_stocks = self.fetch_nse_stock_symbols_alternative()
            all_stocks.extend(alt_stocks)
        
        # Remove duplicates and sort
        seen_tickers = set()
        unique_stocks = []
        
        for stock in all_stocks:
            ticker = stock.get('ticker', '').upper()
            if ticker not in seen_tickers:
                seen_tickers.add(ticker)
                unique_stocks.append(stock)
        
        # Sort by market cap (descending), then by name
        unique_stocks.sort(key=lambda x: (
            -(x.get('market_cap', 0) or 0),  # Higher market cap first
            x.get('name', '').lower()  # Then alphabetically
        ))
        
        print(f"Final stock list: {len(unique_stocks)} unique stocks")
        return unique_stocks