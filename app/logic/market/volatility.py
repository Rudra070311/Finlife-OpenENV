import math
import numpy as np
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class MarketMetrics:
    """Track market health and volatility metrics"""
    vix: float = 20.0  # Volatility index
    market_return: float = 0.0
    inflation_rate: float = 0.03  # Annual 3%
    interest_rate: float = 0.05  # Base rate 5%
    unemployment: float = 0.04  # 4%
    gdp_growth: float = 0.025  # 2.5% annual
    sector_returns: Dict[str, float] = None
    
    def __post_init__(self):
        if self.sector_returns is None:
            self.sector_returns = {
                "tech": 0.02,
                "finance": 0.01,
                "healthcare": 0.015,
                "energy": 0.005,
                "consumer": 0.01,
                "industrials": 0.008,
                "real_estate": 0.012,
                "utilities": 0.006
            }


class VolatilitySimulator:
    """Simulate realistic market volatility and price movements"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.base_vix = 20.0
        self.price_history = {}
        self.market_regime = "normal"  # normal, high_vol, crash, bull
        self.regime_duration = 0
        
    def update_market_metrics(self, metrics: MarketMetrics, step: int) -> MarketMetrics:
        """Update market metrics based on macro conditions and randomness"""
        
        # Regime changes (20% chance every 30 steps)
        if step % 30 == 0 and np.random.random() < 0.2:
            self._change_regime()
        
        # Update VIX based on regime
        vix_change = self._calculate_vix_change()
        metrics.vix = max(10, min(80, metrics.vix + vix_change))
        
        # Update interest rates (slow changes)
        metrics.interest_rate += np.random.normal(0, 0.001)
        metrics.interest_rate = max(0.01, min(0.08, metrics.interest_rate))
        
        # Update inflation
        metrics.inflation_rate += np.random.normal(0, 0.0005)
        metrics.inflation_rate = max(0.01, min(0.08, metrics.inflation_rate))
        
        # Market return correlates with regime and VIX
        if self.market_regime == "crash":
            metrics.market_return = np.random.normal(-0.02, 0.03)
        elif self.market_regime == "high_vol":
            metrics.market_return = np.random.normal(0.005, 0.02)
        elif self.market_regime == "bull":
            metrics.market_return = np.random.normal(0.015, 0.01)
        else:  # normal
            metrics.market_return = np.random.normal(0.008, 0.012)
        
        # Update sector returns
        for sector in metrics.sector_returns:
            sector_volatility = metrics.vix / 20.0
            metrics.sector_returns[sector] += np.random.normal(0, sector_volatility * 0.001)
        
        return metrics
    
    def _change_regime(self):
        """Transition to a new market regime"""
        regimes = ["normal", "high_vol", "bull", "crash"]
        self.market_regime = np.random.choice(regimes)
        self.regime_duration = 0
    
    def _calculate_vix_change(self) -> float:
        """Calculate VIX change based on current regime"""
        if self.market_regime == "crash":
            change = np.random.normal(2, 5)  # VIX spikes
        elif self.market_regime == "high_vol":
            change = np.random.normal(0.5, 2)
        elif self.market_regime == "bull":
            change = np.random.normal(-1, 1)
        else:  # normal
            change = np.random.normal(-0.2, 0.5)
        
        self.regime_duration += 1
        return change
    
    def generate_stock_price(self, ticker: str, initial_price: float, 
                           volatility: float, step: int) -> float:
        """Generate realistic stock price using GBM with regime awareness"""
        
        if ticker not in self.price_history:
            self.price_history[ticker] = [initial_price]
            return initial_price
        
        last_price = self.price_history[ticker][-1]
        
        # Adjust volatility based on market regime
        regime_multiplier = {
            "normal": 1.0,
            "high_vol": 1.8,
            "bull": 0.6,
            "crash": 2.5
        }
        
        adjusted_vol = volatility * regime_multiplier.get(self.market_regime, 1.0)
        
        # Geometric Brownian Motion
        drift = 0.0001  # Daily drift
        random_shock = np.random.normal(0, adjusted_vol)
        
        price_change_pct = drift + random_shock
        new_price = last_price * (1 + price_change_pct)
        new_price = max(1.0, new_price)  # Prevent negative prices
        
        self.price_history[ticker].append(new_price)
        return new_price
    
    def get_price_volatility(self, ticker: str, lookback: int = 20) -> float:
        """Calculate realized volatility from price history"""
        if ticker not in self.price_history or len(self.price_history[ticker]) < lookback:
            return 0.15  # Default volatility
        
        prices = self.price_history[ticker][-lookback:]
        returns = [math.log(prices[i] / prices[i-1]) for i in range(1, len(prices))]
        volatility = np.std(returns) * math.sqrt(252)  # Annualized
        
        return volatility