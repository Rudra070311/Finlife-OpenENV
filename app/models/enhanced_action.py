"""
Enhanced Action Space
Supports stock selection (from 2000+), bank loans, and detailed decisions
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import json


class ActionType(Enum):
    """Types of actions agent can take"""
    BUY_STOCKS = "buy_stocks"
    SELL_STOCKS = "sell_stocks"
    REBALANCE = "rebalance"
    TAKE_LOAN = "take_loan"
    REPAY_LOAN = "repay_loan"
    INCREASE_EMERGENCY_FUND = "increase_emergency_fund"
    CHANGE_INSURANCE = "change_insurance"
    REFINANCE = "refinance"
    DO_NOTHING = "do_nothing"


@dataclass
class StockTransaction:
    """Single stock buy/sell"""
    ticker: str
    action: str  # "buy" or "sell"
    shares: int
    limit_price: Optional[float] = None  # For limit orders
    urgency: float = 0.5  # 0.0-1.0 (0 = patient, 1 = market order)


@dataclass
class LoanRequest:
    """Request for new loan"""
    bank_name: str
    amount: float
    desired_term_months: int
    rationale: str  # Why taking loan
    use_case: str  # "emergency", "education", "home", "investment"


@dataclass
class EnhancedAction:
    """Full action representation with reasoning"""
    
    # What action
    action_type: ActionType
    
    # Stock actions
    stock_transactions: List[StockTransaction] = field(default_factory=list)
    
    # Loan actions
    loan_request: Optional[LoanRequest] = None
    
    # Emergency fund target
    emergency_fund_deposit: float = 0.0  # Amount to add
    
    # Insurance change
    new_insurance_level: Optional[str] = None  # "basic", "standard", "premium"
    
    # Refinance request
    refinance_target_loan_id: Optional[str] = None
    
    # Reasoning
    decision_rationale: str = ""  # Explain why
    expected_return: float = 0.0  # 0.0-1.0 expected return over next period
    risk_tolerance: float = 0.5  # 0.0-1.0 (0 = conservative, 1 = aggressive)
    
    # Confidence
    confidence: float = 0.5  # 0.0-1.0
    
    def to_dict(self) -> Dict:
        """Serialize action"""
        return {
            "type": self.action_type.value,
            "transactions": [
                {
                    "ticker": t.ticker,
                    "action": t.action,
                    "shares": t.shares,
                    "limit_price": t.limit_price,
                }
                for t in self.stock_transactions
            ],
            "loan_request": self.loan_request.__dict__ if self.loan_request else None,
            "emergency_fund_deposit": self.emergency_fund_deposit,
            "new_insurance": self.new_insurance_level,
            "rationale": self.decision_rationale,
            "confidence": self.confidence,
        }


class ActionValidator:
    """Validates actions are legal given current state"""
    
    @staticmethod
    def validate(action: EnhancedAction, state: Dict) -> tuple[bool, str]:
        """
        Returns: (is_valid, error_message)
        """
        
        # Check stock transactions
        total_cost = 0
        for txn in action.stock_transactions:
            if txn.action == "buy":
                # Rough cost estimate (assume $200/share average)
                estimated_cost = txn.shares * 200
                total_cost += estimated_cost
        
        available_cash = state.get("cash", 0)
        if total_cost > available_cash:
            return False, f"Insufficient cash: need ${total_cost:,.0f}, have ${available_cash:,.0f}"
        
        # Check loan request
        if action.loan_request:
            amount = action.loan_request.amount
            income = state.get("annual_income", 0)
            
            # Debt-to-income ratio check (max 4.0x annual income)
            existing_debt = state.get("total_debt", 0)
            if existing_debt + amount > income * 4:
                return False, f"Loan would exceed debt-to-income limits"
        
        return True, ""
    
    @staticmethod
    def suggest_action(state: Dict) -> EnhancedAction:
        """Suggest reasonable action based on state"""
        
        # If no emergency fund, suggest filling it
        ef_status = state.get("emergency_fund_status", 0.0)
        if ef_status < 0.5:
            return EnhancedAction(
                action_type=ActionType.INCREASE_EMERGENCY_FUND,
                emergency_fund_deposit=5000,
                decision_rationale="Emergency fund below target",
                confidence=0.95,
            )
        
        # If unemployed, suggest conservative action
        if state.get("employment_status") == "unemployed":
            return EnhancedAction(
                action_type=ActionType.DO_NOTHING,
                decision_rationale="Unemployed - preserve capital",
                confidence=0.9,
            )
        
        # Default: do nothing
        return EnhancedAction(
            action_type=ActionType.DO_NOTHING,
            decision_rationale="No priority action identified",
            confidence=0.5,
        )


class ActionParser:
    """Parse agent output into structured actions"""
    
    @staticmethod
    def parse_buy_intent(agent_output: str) -> EnhancedAction:
        """
        Example agent output:
        "I should buy AAPL and MSFT for growth. 
         100 shares of AAPL, 50 shares of MSFT.
         This diversifies into tech which has good fundamentals."
        """
        
        # Very simple parser - in production would use LLM to extract
        transactions = []
        
        # Look for patterns like "100 shares of AAPL"
        # This is a simplified version
        
        if "aapl" in agent_output.lower():
            transactions.append(StockTransaction(
                ticker="AAPL",
                action="buy",
                shares=100,
            ))
        
        if "msft" in agent_output.lower():
            transactions.append(StockTransaction(
                ticker="MSFT",
                action="buy",
                shares=50,
            ))
        
        return EnhancedAction(
            action_type=ActionType.BUY_STOCKS,
            stock_transactions=transactions,
            decision_rationale=agent_output,
            confidence=0.7,
        )
    
    @staticmethod
    def parse_loan_intent(agent_output: str) -> EnhancedAction:
        """
        Example agent output:
        "I need a loan from Chase for $50,000 over 60 months
         to cover emergency expenses while unemployed."
        """
        
        loan = LoanRequest(
            bank_name="Chase",
            amount=50000,
            desired_term_months=60,
            rationale=agent_output,
            use_case="emergency",
        )
        
        return EnhancedAction(
            action_type=ActionType.TAKE_LOAN,
            loan_request=loan,
            decision_rationale=agent_output,
            confidence=0.8,
        )


# Example: Action templates for different scenarios
class ActionTemplates:
    """Pre-built action templates"""
    
    @staticmethod
    def conservative_rebalance() -> EnhancedAction:
        """60/40 stock/bond allocation"""
        return EnhancedAction(
            action_type=ActionType.REBALANCE,
            decision_rationale="Rebalance to 60/40 stocks/bonds for stability",
            risk_tolerance=0.4,
            confidence=0.9,
        )
    
    @staticmethod
    def emergency_fund_boost(amount: float) -> EnhancedAction:
        """Increase emergency fund"""
        return EnhancedAction(
            action_type=ActionType.INCREASE_EMERGENCY_FUND,
            emergency_fund_deposit=amount,
            decision_rationale=f"Build emergency fund by ${amount:,.0f}",
            confidence=0.95,
        )
    
    @staticmethod
    def aggressive_growth(stock_selection: List[str]) -> EnhancedAction:
        """Build growth portfolio"""
        transactions = [
            StockTransaction(
                ticker=ticker,
                action="buy",
                shares=50,
            )
            for ticker in stock_selection[:10]  # Top 10 stocks
        ]
        
        return EnhancedAction(
            action_type=ActionType.BUY_STOCKS,
            stock_transactions=transactions,
            decision_rationale="Growth portfolio - high conviction positions",
            risk_tolerance=0.8,
            expected_return=0.15,
            confidence=0.7,
        )
    
    @staticmethod
    def crisis_response(loan_needed: float, bank: str = "Chase") -> EnhancedAction:
        """Emergency response to crisis"""
        return EnhancedAction(
            action_type=ActionType.TAKE_LOAN,
            loan_request=LoanRequest(
                bank_name=bank,
                amount=loan_needed,
                desired_term_months=60,
                rationale="Emergency liquidity for crisis response",
                use_case="emergency",
            ),
            decision_rationale="Securing emergency funding",
            risk_tolerance=0.3,
            confidence=0.9,
        )


if __name__ == '__main__':
    # Example: Create and validate actions
    
    action1 = EnhancedAction(
        action_type=ActionType.BUY_STOCKS,
        stock_transactions=[
            StockTransaction("AAPL", "buy", 100),
            StockTransaction("MSFT", "buy", 50),
        ],
        decision_rationale="Diversify into tech mega-caps",
        confidence=0.8,
    )
    
    print("Action 1 - Buy Stocks:")
    print(json.dumps(action1.to_dict(), indent=2))
    
    # Validate against state
    state = {
        "cash": 50000,
        "annual_income": 120000,
        "total_debt": 5000,
        "employment_status": "employed",
    }
    
    is_valid, error = ActionValidator.validate(action1, state)
    print(f"\nValidation: {is_valid}")
    if not is_valid:
        print(f"Error: {error}")
    
    # Example: Crisis action
    action2 = ActionTemplates.crisis_response(loan_needed=50000)
    print("\n" + "="*70)
    print("Action 2 - Crisis Response (Loan Request):")
    print(json.dumps(action2.to_dict(), indent=2))
    
    # Example: Emergency fund
    action3 = ActionTemplates.emergency_fund_boost(10000)
    print("\n" + "="*70)
    print("Action 3 - Emergency Fund:")
    print(json.dumps(action3.to_dict(), indent=2))
