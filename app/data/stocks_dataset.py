"""
Comprehensive Stock Market Dataset Generator
Creates realistic historical and simulated price data for training
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os


class StockTickerDB:
    """Real stock tickers by sector for realistic portfolio composition"""
    
    TICKERS = {
        "tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "ADBE", "NFLX", "CRM"],
        "finance": ["JPM", "BAC", "WFC", "GS", "MS", "BLK", "SCHW", "CME", "ICE", "AXP"],
        "healthcare": ["JNJ", "UNH", "PFE", "ABBV", "LLY", "MRK", "AZN", "TMO", "REGN", "BNTX"],
        "energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "PXD", "HAL", "BKR"],
        "consumer": ["WMT", "PG", "MCD", "NKE", "COST", "AMZN", "TJX", "HD", "KO", "PEP"],
        "industrials": ["BA", "CAT", "GE", "LMT", "RTX", "HON", "MMM", "PH", "URI", "ITW"],
        "real_estate": ["PLD", "DLR", "SPG", "AMT", "WELL", "PSA", "O", "VICI", "EQIX", "CCI"],
        "utilities": ["NEE", "DUK", "SO", "ED", "AEP", "PEG", "XEL", "PPL", "EXC", "IDXX"],
        "crypto_adjacent": ["MSTR", "CLSK", "RIOT", "MARA", "COIN"],
        "etfs": ["SPY", "VOO", "VTI", "QQQ", "AGG", "BND", "VNQ", "VTV", "VUG", "VWO"]
    }
    
    @classmethod
    def get_all_tickers(cls) -> List[str]:
        all_tickers = []
        for tickers in cls.TICKERS.values():
            all_tickers.extend(tickers)
        return all_tickers
    
    @classmethod
    def get_sector(cls, ticker: str) -> str:
        for sector, tickers in cls.TICKERS.items():
            if ticker in tickers:
                return sector
        return "other"


class HistoricalStockDataGenerator:
    """Generate realistic historical stock data using GBM"""
    
    def __init__(self, start_date: str = "2018-01-01", end_date: str = "2024-12-31", 
                 days_per_year: int = 252, seed: int = 42):
        np.random.seed(seed)
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.days_per_year = days_per_year
        self.total_days = (self.end_date - self.start_date).days
        self.market_crashes = [
            (datetime(2020, 3, 1), -0.30, 30),  # COVID crash
            (datetime(2022, 9, 1), -0.20, 60),  # 2022 bear market
        ]
    
    def generate_ticker_history(self, ticker: str, initial_price: float = 100.0,
                               annual_return: float = 0.10, 
                               annual_volatility: float = 0.20) -> pd.DataFrame:
        """Generate daily OHLCV data for a ticker"""
        
        dates = pd.date_range(self.start_date, self.end_date, freq='B')  # Business days
        num_days = len(dates)
        
        # Adjust volatility for market crashes
        daily_vol = annual_volatility / np.sqrt(self.days_per_year)
        daily_return = annual_return / self.days_per_year
        
        prices = np.zeros(num_days)
        prices[0] = initial_price
        
        returns = np.zeros(num_days)
        
        for i in range(1, num_days):
            # Check for market crash dates
            crash_impact = 1.0
            for crash_date, crash_pct, duration in self.market_crashes:
                days_since_crash = (dates[i] - crash_date).days
                if 0 <= days_since_crash < duration:
                    # Gradually recover from crash
                    recovery_factor = (days_since_crash / duration) ** 0.5
                    crash_impact = 1.0 + crash_pct * (1 - recovery_factor)
                    daily_vol *= 1.5  # Increased volatility during crash
            
            shock = np.random.normal(daily_return, daily_vol) * crash_impact
            returns[i] = shock
            prices[i] = prices[i-1] * np.exp(shock)
        
        # Generate OHLCV
        data = {
            'date': dates,
            'ticker': ticker,
            'open': prices * (1 + np.random.normal(0, 0.005, num_days)),
            'high': prices * (1 + np.abs(np.random.normal(0.01, 0.015, num_days))),
            'low': prices * (1 - np.abs(np.random.normal(0.01, 0.015, num_days))),
            'close': prices,
            'volume': np.random.lognormal(15, 1, num_days).astype(int)
        }
        
        df = pd.DataFrame(data)
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        
        return df
    
    def generate_portfolio_history(self, tickers: List[str], weights: List[float]) -> pd.DataFrame:
        """Generate historical price data for multiple tickers"""
        
        dfs = []
        ticker_params = {
            "tech": (0.15, 0.20),
            "finance": (0.10, 0.18),
            "healthcare": (0.12, 0.16),
            "energy": (0.05, 0.25),
            "consumer": (0.08, 0.15),
            "industrials": (0.09, 0.17),
            "real_estate": (0.06, 0.18),
            "utilities": (0.04, 0.12),
            "etfs": (0.08, 0.10),
            "crypto_adjacent": (0.20, 0.50),
        }
        
        for ticker in tickers:
            sector = StockTickerDB.get_sector(ticker)
            annual_return, annual_vol = ticker_params.get(sector, (0.08, 0.15))
            df = self.generate_ticker_history(ticker, annual_return=annual_return, 
                                            annual_volatility=annual_vol)
            dfs.append(df)
        
        return pd.concat(dfs, ignore_index=True)


class FinancialDataSynthesizer:
    """Synthesize additional financial metadata and indicators"""
    
    @staticmethod
    def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add common technical indicators"""
        
        df = df.sort_values(['ticker', 'date']).reset_index(drop=True)
        
        # SMA (Simple Moving Average)
        df['sma_20'] = df.groupby('ticker')['close'].rolling(20).mean().values
        df['sma_50'] = df.groupby('ticker')['close'].rolling(50).mean().values
        
        # RSI (Relative Strength Index)
        def compute_rsi(prices, period=14):
            deltas = np.diff(prices)
            seed = deltas[:period+1]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            rs = up / down
            rsi = np.zeros_like(prices)
            rsi[:period] = 100.0 - 100.0 / (1.0 + rs)
            
            for i in range(period, len(prices)):
                delta = deltas[i-1]
                if delta > 0:
                    upval = delta
                    downval = 0.0
                else:
                    upval = 0.0
                    downval = -delta
                
                up = (up * (period - 1) + upval) / period
                down = (down * (period - 1) + downval) / period
                
                rs = up / down
                rsi[i] = 100.0 - 100.0 / (1.0 + rs)
            
            return rsi
        
        df['rsi'] = df.groupby('ticker')['close'].transform(
            lambda x: pd.Series(compute_rsi(x.values), index=x.index)
        )
        
        # MACD
        df['ema_12'] = df.groupby('ticker')['close'].ewm(span=12).mean().values
        df['ema_26'] = df.groupby('ticker')['close'].ewm(span=26).mean().values
        df['macd'] = df['ema_12'] - df['ema_26']
        
        # Bollinger Bands
        df['bb_middle'] = df.groupby('ticker')['close'].rolling(20).mean().values
        df['bb_std'] = df.groupby('ticker')['close'].rolling(20).std().values
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        return df
    
    @staticmethod
    def add_fundamental_data(df: pd.DataFrame) -> pd.DataFrame:
        """Add simulated fundamental data"""
        
        fundamental_ranges = {
            "pe_ratio": (10, 40),
            "pb_ratio": (0.5, 5),
            "dividend_yield": (0, 0.08),
            "earnings_growth": (-0.20, 0.30),
            "revenue_growth": (-0.10, 0.25),
            "debt_to_equity": (0, 2.0),
        }
        
        for metric, (min_val, max_val) in fundamental_ranges.items():
            ticker_values = {}
            for ticker in df['ticker'].unique():
                base_value = np.random.uniform(min_val, max_val)
                ticker_values[ticker] = base_value
            
            df[metric] = df['ticker'].map(ticker_values) + np.random.uniform(-0.05, 0.05, len(df))
            df[metric] = np.clip(df[metric], min_val, max_val)
        
        return df


class LLMTrainingDatasetBuilder:
    """Convert market data into LLM training examples"""
    
    FINANCIAL_REASONING_TEMPLATES = [
        "Given the {ticker} price of ${price:.2f}, RSI of {rsi:.2f}, and SMA20 of ${sma20:.2f}, the analyst recommends a {action} signal based on {reason}.",
        "With {ticker} trading at ${price:.2f}, a P/E ratio of {pe:.2f}, and dividend yield of {div:.2f}%, an investor might consider {action} as {justification}.",
        "The market is showing {vix_level} volatility (VIX: {vix:.2f}). For {ticker} at ${price:.2f}, {reasoning}.",
        "Considering sector rotation toward {sector} and {ticker}'s technical position, the decision would be {action} with conviction level {confidence:.2f}.",
        "Portfolio rebalancing: Reducing {ticker} from {old_weight:.1%} to {new_weight:.1%} due to {reason}.",
    ]
    
    @staticmethod
    def create_trading_scenarios(df: pd.DataFrame, window: int = 5) -> List[Dict]:
        """Create realistic trading decision scenarios"""
        
        scenarios = []
        df = df.sort_values(['ticker', 'date']).reset_index(drop=True)
        
        for ticker in df['ticker'].unique():
            ticker_data = df[df['ticker'] == ticker].reset_index(drop=True)
            
            for i in range(window, len(ticker_data) - 1):
                hist_window = ticker_data.iloc[i-window:i]
                current = ticker_data.iloc[i]
                next_day = ticker_data.iloc[i+1]
                
                price_change = (next_day['close'] - current['close']) / current['close']
                action = "BUY" if price_change > 0.02 else ("SELL" if price_change < -0.02 else "HOLD")
                
                scenario = {
                    "date": current['date'],
                    "ticker": ticker,
                    "current_price": current['close'],
                    "technical_indicators": {
                        "rsi": current['rsi'],
                        "macd": current['macd'],
                        "sma_20": current['sma_20'],
                        "sma_50": current['sma_50'],
                        "bb_upper": current['bb_upper'],
                        "bb_lower": current['bb_lower'],
                    },
                    "fundamentals": {
                        "pe_ratio": current['pe_ratio'],
                        "pb_ratio": current['pb_ratio'],
                        "dividend_yield": current['dividend_yield'],
                        "debt_to_equity": current['debt_to_equity'],
                    },
                    "price_history": hist_window['close'].tolist(),
                    "recommendation": action,
                    "actual_outcome": price_change,
                    "reasoning": LLMTrainingDatasetBuilder._generate_reasoning(
                        ticker, current, action, price_change
                    )
                }
                
                scenarios.append(scenario)
        
        return scenarios
    
    @staticmethod
    def _generate_reasoning(ticker: str, current: pd.Series, action: str, outcome: float) -> str:
        """Generate human-like financial reasoning"""
        
        reasons = {
            "BUY": [
                f"{ticker} has crossed above the 20-day moving average with increasing volume",
                f"The RSI shows oversold conditions at {current['rsi']:.2f}, suggesting a potential reversal",
                f"{ticker} is maintaining support at ${current['bb_lower']:.2f} with positive earnings momentum",
                f"Sector rotation into {StockTickerDB.get_sector(ticker)} presents opportunity",
            ],
            "SELL": [
                f"{ticker} has broken below key support level near ${current['bb_lower']:.2f}",
                f"MACD divergence suggests weakening momentum for {ticker}",
                f"Valuation concerns with P/E at {current['pe_ratio']:.2f} relative to sector average",
                f"Technical exhaustion at ${current['sma_50']:.2f} resistance level",
            ],
            "HOLD": [
                f"{ticker} consolidating near the 50-day MA - waiting for clear breakout",
                f"Balanced risk-reward for {ticker} with dividend yield of {current['dividend_yield']:.2%}",
                f"Monitor {ticker} for support at ${current['bb_lower']:.2f}",
                f"Maintaining position in {ticker} pending earnings announcement",
            ]
        }
        
        return np.random.choice(reasons.get(action, reasons["HOLD"]))
    
    @staticmethod
    def export_llm_dataset(scenarios: List[Dict], output_path: str):
        """Export scenarios as JSONL for LLM fine-tuning"""
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            for scenario in scenarios:
                training_example = {
                    "prompt": f"Analyze {scenario['ticker']}: Current Price: ${scenario['current_price']:.2f}, RSI: {scenario['technical_indicators']['rsi']:.2f}, SMA20: ${scenario['technical_indicators']['sma_20']:.2f}. What should investors do?",
                    "completion": f" {scenario['recommendation']}: {scenario['reasoning']} Historical outcome: {scenario['actual_outcome']:+.2%}",
                    "metadata": {
                        "ticker": scenario['ticker'],
                        "date": str(scenario['date']),
                        "fundamentals": scenario['fundamentals'],
                    }
                }
                f.write(json.dumps(training_example) + '\n')


def build_massive_dataset(output_dir: str = "data/stocks_dataset"):
    """Build comprehensive stocks dataset for training"""
    
    print("🏗️  Building comprehensive stocks dataset...")
    
    # Get diverse tickers
    tickers = StockTickerDB.get_all_tickers()
    print(f"📊 Generating data for {len(tickers)} tickers...")
    
    # Generate historical data
    generator = HistoricalStockDataGenerator(
        start_date="2018-01-01",
        end_date="2024-12-31",
        seed=42
    )
    
    df_history = generator.generate_portfolio_history(tickers, weights=None)
    print(f"✅ Generated {len(df_history)} daily records")
    
    # Add technical indicators
    synthesizer = FinancialDataSynthesizer()
    df_with_indicators = synthesizer.compute_technical_indicators(df_history)
    df_with_fundamentals = synthesizer.add_fundamental_data(df_with_indicators)
    print("✅ Added technical indicators and fundamental data")
    
    # Create training scenarios
    builder = LLMTrainingDatasetBuilder()
    scenarios = builder.create_trading_scenarios(df_with_fundamentals, window=20)
    print(f"✅ Created {len(scenarios)} training scenarios")
    
    # Export dataset
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as CSV
    csv_path = f"{output_dir}/stock_prices.csv"
    df_with_fundamentals.to_csv(csv_path, index=False)
    print(f"✅ Saved price data to {csv_path}")
    
    # Save LLM training dataset
    llm_path = f"{output_dir}/llm_training_dataset.jsonl"
    builder.export_llm_dataset(scenarios, llm_path)
    print(f"✅ Saved LLM training data to {llm_path}")
    
    # Metadata
    metadata = {
        "total_tickers": len(tickers),
        "date_range": f"2018-01-01 to 2024-12-31",
        "total_records": len(df_with_fundamentals),
        "scenarios": len(scenarios),
        "sectors": list(StockTickerDB.TICKERS.keys()),
    }
    
    meta_path = f"{output_dir}/metadata.json"
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Saved metadata to {meta_path}")
    
    return df_with_fundamentals, scenarios


if __name__ == "__main__":
    df, scenarios = build_massive_dataset()
    print("\n🎉 Dataset building complete!")
