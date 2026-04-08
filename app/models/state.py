from pydantic import BaseModel, Field
from typing import List, Dict
from dataclasses import dataclass


class Portfolio(BaseModel):
    equity: float = 0.0
    debt: float = 0.0
    cash: float = 0.0


@dataclass
class StockPosition:
    """Individual stock holdings"""
    ticker: str
    shares: float
    average_cost: float
    current_price: float
    acquisition_date: int  # month
    
    @property
    def value(self) -> float:
        return self.shares * self.current_price
    
    @property
    def gain_loss_pct(self) -> float:
        if self.average_cost == 0:
            return 0.0
        return (self.current_price - self.average_cost) / self.average_cost


@dataclass 
class Derivative:
    """Options and other derivatives"""
    contract_type: str  # "call", "put", "future"
    underlying: str
    strike_price: float
    expiration_date: int  # month
    quantity: int
    premium_paid: float
    current_value: float


class Loan(BaseModel):
    amount: float
    interest_rate: float
    tenure_months: int
    remaining_months: int
    emi: float
    loan_type: str = "personal"  # personal, home, auto, student


class Goal(BaseModel):
    name: str
    type: str
    target_amount: float
    current_amount: float = 0.0
    priority: int = 1
    years_left: int = 0

    @property
    def progress(self) -> float:
        if self.target_amount == 0:
            return 0.0
        return min(self.current_amount / self.target_amount, 1.0)


class State(BaseModel):
    age: int
    month: int

    income: float
    expenses: float
    savings: float
    net_worth: float

    portfolio: Portfolio
    stock_positions: List[StockPosition] = Field(default_factory=list)
    derivatives: List[Derivative] = Field(default_factory=list)
    
    loans: List[Loan] = Field(default_factory=list)
    goals: List[Goal] = Field(default_factory=list)

    risk_profile: str  # conservative, moderate, aggressive

    dependents: int
    job_stability: float
    health_factor: float
    education_level: str = "bachelor"  # Affects earning potential

    is_bankrupt: bool = False
    
    last_income: float = 0.0
    last_expenses: float = 0.0
    
    # Market state
    market_regime: str = "normal"  # normal, high_vol, crash, bull
    vix_level: float = 20.0
    inflation_rate: float = 0.03
    interest_rate: float = 0.05
    
    # Trading history
    trades_executed: int = 0
    realized_gains: float = 0.0
    realized_losses: float = 0.0
    
    # Behavioral metrics
    risk_taken: float = 0.0  # Aggregate risk exposure
    diversification_score: float = 0.0  # Portfolio diversification metric