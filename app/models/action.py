from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class StockTrade(BaseModel):
    """Individual stock transaction"""
    ticker: str
    action: str  # "buy", "sell"
    quantity: float
    order_type: str = "market"  # market, limit, stop
    price_limit: Optional[float] = None


class DerivativeTrade(BaseModel):
    """Options/derivatives trade"""
    underlying: str
    contract_type: str  # "call", "put", "future"
    action: str  # "buy", "sell"
    quantity: int
    strike_price: float
    premium: float


class RebalanceInstruction(BaseModel):
    """Portfolio rebalancing targets"""
    equity_target: float  # 0-1
    debt_target: float    # 0-1
    cash_target: float    # 0-1
    rebalance_threshold: float = 0.05  # rebalance if deviation > 5%


class Action(BaseModel):
    # Traditional SIP actions
    sip_amount: float = 0.0
    allocate_equity: float = 0.0
    allocate_debt: float = 0.0
    allocate_cash: float = 0.0
    
    # Spending and luxury
    spend_luxury: float = 0.0
    spend_healthcare: float = 0.0
    spend_education: float = 0.0
    
    # Loan actions
    take_loan: bool = False
    loan_amount: float = 0.0
    loan_type: str = "personal"
    
    # Stock trading
    stock_trades: List[StockTrade] = Field(default_factory=list)
    
    # Derivatives trading
    derivative_trades: List[DerivativeTrade] = Field(default_factory=list)
    
    # Portfolio rebalancing
    rebalance: Optional[RebalanceInstruction] = None
    
    # Tax loss harvesting
    tax_loss_harvest: bool = False
    
    # Dividend reinvestment
    reinvest_dividends: bool = True
    
    # Financial planning
    goal_contribution: float = 0.0  # Amount to contribute to goals
    insurance_premium: float = 0.0  # Life/health insurance
    
    # Domain knowledge annotations (for LLM training)
    reasoning: str = ""  # Why this action was taken
    risk_level: str = "medium"  # low, medium, high
    time_horizon: str = "long"  # short, medium, long