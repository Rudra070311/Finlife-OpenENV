"""
Enhanced environment with stock market integration
"""

from app.models.state import State, Portfolio, StockPosition
from app.models.action import Action
from app.models.observation import Observation
from app.logic.transitions import step
from app.reward import compute_reward, compute_reasoning_reward
from app.logic.market.volatility import VolatilitySimulator, MarketMetrics
from app.data.stocks_dataset import HistoricalStockDataGenerator, StockTickerDB
import random
import numpy as np
import pandas as pd


class EnhancedFinLifeEnv:
    """
    Enhanced financial life environment with:
    - Real stock market data
    - Trading capabilities  
    - Derivatives
    - Market regimes and volatility
    - Sophisticated reward signals
    """
    
    def __init__(self, config, use_historical_data: bool = True):
        self.config = config
        self.use_historical_data = use_historical_data
        
        # Market simulator
        self.volatility_sim = VolatilitySimulator(seed=42)
        self.market_metrics = MarketMetrics()
        
        # Stock price data
        if use_historical_data:
            generator = HistoricalStockDataGenerator()
            self.stock_data = generator.generate_portfolio_history(
                StockTickerDB.get_all_tickers(),
                weights=None
            )
            self.stock_data = self.stock_data.sort_values(['ticker', 'date']).reset_index(drop=True)
            self.current_prices = {}
        else:
            self.stock_data = None
            self.current_prices = {ticker: 100.0 for ticker in StockTickerDB.get_all_tickers()}
        
        self.step_count = 0
    
    def reset(self):
        """Initialize the environment"""
        self.step_count = 0
        
        self.state = State(
            age=self.config.initial_age,
            month=0,
            
            income=self.config.initial_income,
            expenses=self.config.initial_expenses,
            savings=self.config.initial_savings,
            
            net_worth=self.config.initial_savings,
            
            portfolio=Portfolio(
                equity=0.0,
                debt=0.0,
                cash=self.config.initial_savings
            ),
            
            stock_positions=[],
            derivatives=[],
            
            loans=[],
            goals=[],
            
            risk_profile=self.config.risk_profile,
            
            dependents=random.randint(0, self.config.max_dependents),
            
            job_stability=self.config.job_stability,
            health_factor=self.config.health_factor,
            
            is_bankrupt=False,
            
            last_income=self.config.initial_income,
            last_expenses=self.config.initial_expenses,
            
            market_regime="normal",
            vix_level=20.0,
            inflation_rate=0.03,
            interest_rate=0.05,
        )
        
        return self._get_observation()
    
    def step(self, action: Action):
        """Execute one step"""
        self.step_count += 1
        
        # Update market metrics
        self.market_metrics = self.volatility_sim.update_market_metrics(
            self.market_metrics, self.step_count
        )
        
        # Update stock prices
        self._update_stock_prices()
        
        # Update state with market data
        self.state.market_regime = self.volatility_sim.market_regime
        self.state.vix_level = self.market_metrics.vix
        self.state.inflation_rate = self.market_metrics.inflation_rate
        self.state.interest_rate = self.market_metrics.interest_rate
        
        # Execute action (trades, rebalancing, etc.)
        self.state = self._execute_action(self.state, action)
        
        # Standard transitions (income, expenses, loans, etc.)
        self.state = step(self.state, action)
        
        # Update net worth with current portfolio values
        self._update_portfolio_value()
        
        # Compute rewards
        reward = compute_reward(self.state)
        reward += compute_reasoning_reward(action.reasoning, self.state)
        
        done = self._is_done()
        obs = self._get_observation()
        
        return obs, reward, done, {}
    
    def _update_stock_prices(self):
        """Update all stock prices based on market regime"""
        for ticker in StockTickerDB.get_all_tickers():
            if ticker not in self.current_prices:
                self.current_prices[ticker] = 100.0
            
            sector = StockTickerDB.get_sector(ticker)
            sector_return = self.market_metrics.sector_returns.get(sector, 0.0)
            
            # GBM-based price update
            volatility = 0.20
            daily_return = sector_return / 252.0 + np.random.normal(0, volatility / np.sqrt(252))
            
            self.current_prices[ticker] *= (1 + daily_return)
            self.current_prices[ticker] = max(1.0, self.current_prices[ticker])
    
    def _execute_action(self, state: State, action: Action) -> State:
        """Execute stock trades and derivatives trades"""
        
        # Process stock trades
        for trade in action.stock_trades:
            current_price = self.current_prices.get(trade.ticker, 100.0)
            
            if trade.action == "buy":
                cost = trade.quantity * current_price
                if state.savings >= cost:
                    state.savings -= cost
                    
                    # Update or create position
                    existing = next((p for p in state.stock_positions if p.ticker == trade.ticker), None)
                    if existing:
                        avg_cost = (existing.average_cost * existing.shares + cost) / (existing.shares + trade.quantity)
                        existing.average_cost = avg_cost
                        existing.shares += trade.quantity
                        existing.current_price = current_price
                    else:
                        state.stock_positions.append(StockPosition(
                            ticker=trade.ticker,
                            shares=trade.quantity,
                            average_cost=current_price,
                            current_price=current_price,
                            acquisition_date=state.month
                        ))
                    
                    state.trades_executed += 1
                    state.portfolio.equity += cost
            
            elif trade.action == "sell":
                existing = next((p for p in state.stock_positions if p.ticker == trade.ticker), None)
                if existing and existing.shares >= trade.quantity:
                    proceeds = trade.quantity * current_price
                    state.savings += proceeds
                    
                    # Realize gains/losses
                    cost_basis = trade.quantity * existing.average_cost
                    gain_loss = proceeds - cost_basis
                    
                    if gain_loss > 0:
                        state.realized_gains += gain_loss
                    else:
                        state.realized_losses += abs(gain_loss)
                    
                    existing.shares -= trade.quantity
                    if existing.shares == 0:
                        state.stock_positions.remove(existing)
                    
                    state.trades_executed += 1
                    state.portfolio.equity -= cost_basis
        
        # Update diversification score
        self._compute_diversification_score(state)
        
        return state
    
    def _compute_diversification_score(self, state: State):
        """Calculate portfolio diversification metric"""
        if not state.stock_positions:
            state.diversification_score = 0.0
            return
        
        total_value = sum([pos.value for pos in state.stock_positions]) or 1.0
        weights = [pos.value / total_value for pos in state.stock_positions]
        
        # Herfindahl-Hirschman Index
        hhi = sum([w**2 for w in weights])
        # Normalize to 0-1 (1 = perfectly diversified, 0 = concentrated)
        state.diversification_score = 1.0 - min(hhi, 1.0)
    
    def _update_portfolio_value(self):
        """Update total portfolio value with current market prices"""
        stock_value = sum([pos.value for pos in self.state.stock_positions])
        derivative_value = sum([d.current_value for d in self.state.derivatives])
        
        total_portfolio_value = (
            self.state.portfolio.equity +
            self.state.portfolio.debt +
            self.state.portfolio.cash +
            stock_value +
            derivative_value
        )
        
        total_liabilities = sum([l.amount for l in self.state.loans])
        self.state.net_worth = self.state.savings + total_portfolio_value - total_liabilities
    
    def _get_observation(self) -> Observation:
        """Create observation from state"""
        portfolio_value = (
            self.state.portfolio.equity +
            self.state.portfolio.debt +
            self.state.portfolio.cash +
            sum([pos.value for pos in self.state.stock_positions])
        )
        
        if self.state.goals:
            goal_progress = sum([g.progress for g in self.state.goals]) / len(self.state.goals)
        else:
            goal_progress = 0.0
        
        return Observation(
            age=self.state.age,
            month=self.state.month,
            
            income=self.state.income,
            expenses=self.state.expenses,
            savings=self.state.savings,
            net_worth=self.state.net_worth,
            
            equity=self.state.portfolio.equity,
            debt=self.state.portfolio.debt,
            cash=self.state.portfolio.cash,
            
            loans=self.state.loans,
            goals=self.state.goals,
            
            risk_profile=self.state.risk_profile,
            dependents=self.state.dependents,
            
            job_stability=self.state.job_stability,
            health_factor=self.state.health_factor,
            
            is_bankrupt=self.state.is_bankrupt,
            
            portfolio_value=portfolio_value,
            goal_progress_summary=goal_progress,
            
            # Market state
            market_regime=self.state.market_regime,
            vix_level=self.state.vix_level,
            inflation_rate=self.state.inflation_rate,
            interest_rate=self.state.interest_rate,
            
            # Stock positions
            stock_positions=self.state.stock_positions,
            diversification_score=self.state.diversification_score,
            realized_gains=self.state.realized_gains,
            realized_losses=self.state.realized_losses,
        )
    
    def _is_done(self) -> bool:
        """Episode termination conditions"""
        if self.state.is_bankrupt:
            return True
        if self.state.age >= 65:
            return True
        if self.step_count >= self.config.max_steps:
            return True
        return False
