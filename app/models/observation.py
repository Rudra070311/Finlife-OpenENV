from pydantic import BaseModel
from typing import List, Optional


class Observation(BaseModel):
    age: int
    month: int
    income: float
    expenses: float
    savings: float
    net_worth: float
    equity: float
    debt: float
    cash: float
    loans: List
    goals: List
    risk_profile: str
    dependents: int
    job_stability: float
    health_factor: float
    is_bankrupt: bool
    portfolio_value: float
    goal_progress_summary: float
    
    # Market state
    market_regime: str = "normal"
    vix_level: float = 20.0
    inflation_rate: float = 0.03
    interest_rate: float = 0.05
    
    # Stock positions and metrics
    stock_positions: List = []
    diversification_score: float = 0.0
    realized_gains: float = 0.0
    realized_losses: float = 0.0
    
    # Derived metrics (optional)
    income_trend: float = 0.0
    expense_trend: float = 0.0