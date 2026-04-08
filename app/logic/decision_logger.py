"""
Detailed Decision Logger
Tracks every financial decision with full context and reasoning
Outputs "life journal" style logs of what happened and why
"""

import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from enum import Enum


class DecisionCategory(Enum):
    """Types of financial decisions"""
    STOCK_BUY = "stock_buy"
    STOCK_SELL = "stock_sell"
    LOAN_OBTAIN = "loan_obtain"
    LOAN_REPAY = "loan_repay"
    REBALANCE = "rebalance"
    TAX_HARVEST = "tax_harvest"
    EMERGENCY_FUND = "emergency_fund"
    INSURANCE = "insurance"
    BUDGET_ADJUST = "budget_adjust"
    BANK_SWITCH = "bank_switch"
    MARGIN_USE = "margin_use"
    DIVIDEND_REINVEST = "dividend_reinvest"


@dataclass
class Decision:
    """A single financial decision made by agent"""
    timestamp: str
    category: DecisionCategory
    
    # what
    action: str  # "Buy 100 shares of AAPL"
    
    # context
    portfolio_state: Dict[str, float]
    market_conditions: Dict[str, float]
    life_status: Dict[str, Any]
    
    # impact
    cash_impact: float
    portfolio_impact: Optional[float] = None
    risk_impact: Optional[float] = None
    
    # reasoning
    rationale: str  # "Undervalued tech stock before earnings"
    expected_outcome: str  # "15% upside potential"
    confidence: float  # 0.0-1.0
    
    # result
    result_status: str = "pending"  # pending, success, failure
    actual_impact: Optional[float] = None
    outcome_notes: Optional[str] = None
    
    decision_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))


class DecisionLogger:
    """Logs all decisions in detail"""
    
    def __init__(self, agent_name: str = "AI_Agent"):
        self.agent_name = agent_name
        self.decisions: List[Decision] = []
        self.life_log: List[str] = []
        self.current_month = 1
        self.current_year = 2024
    
    def log_stock_purchase(self,
                           ticker: str,
                           shares: int,
                           price: float,
                           portfolio: Dict,
                           market: Dict,
                           life_status: Dict,
                           rationale: str,
                           confidence: float = 0.7) -> Decision:
        """Log stock purchase decision"""
        
        cash_impact = -shares * price
        
        decision = Decision(
            timestamp=self._get_timestamp(),
            category=DecisionCategory.STOCK_BUY,
            action=f"BUY {shares} shares of {ticker} @ ${price:.2f}",
            portfolio_state=portfolio,
            market_conditions=market,
            life_status=life_status,
            cash_impact=cash_impact,
            rationale=rationale,
            expected_outcome=f"Target holding for portfolio diversification/growth",
            confidence=confidence,
        )
        
        self.decisions.append(decision)
        self.life_log.append(
            f"[Month {self.current_month}, {self.current_year}] "
            f"PURCHASED {shares} shares of {ticker} at ${price:.2f} "
            f"(Total: ${shares * price:,.0f}). "
            f"Reasoning: {rationale}"
        )
        
        return decision
    
    def log_loan_taken(self,
                       bank_name: str,
                       amount: float,
                       rate: float,
                       term_months: int,
                       portfolio: Dict,
                       life_status: Dict,
                       rationale: str) -> Decision:
        """Log taking a loan"""
        
        monthly_payment = amount * (rate/12) / (1 - (1 + rate/12)**(-term_months))
        total_interest = monthly_payment * term_months - amount
        
        decision = Decision(
            timestamp=self._get_timestamp(),
            category=DecisionCategory.LOAN_OBTAIN,
            action=f"LOAN from {bank_name}: ${amount:,.0f} @ {rate*100:.2f}%",
            portfolio_state=portfolio,
            market_conditions={},
            life_status=life_status,
            cash_impact=amount,  # Positive: received cash
            rationale=rationale,
            expected_outcome=f"Monthly payment: ${monthly_payment:.0f}. Total interest: ${total_interest:.0f}",
            confidence=0.9,
        )
        
        self.decisions.append(decision)
        self.life_log.append(
            f"[Month {self.current_month}, {self.current_year}] "
            f"OBTAINED LOAN from {bank_name}: ${amount:,.0f} "
            f"at {rate*100:.2f}% APR ({term_months} months). "
            f"Monthly payment: ${monthly_payment:.0f}. "
            f"Purpose: {rationale}"
        )
        
        return decision
    
    def log_rebalance(self,
                      changes: Dict[str, float],  # ticker -> new %
                      reason: str,
                      portfolio: Dict,
                      market: Dict,
                      life_status: Dict) -> Decision:
        """Log portfolio rebalancing"""
        
        changes_str = ", ".join([f"{k}: {v*100:.1f}%" for k, v in list(changes.items())[:5]])
        
        decision = Decision(
            timestamp=self._get_timestamp(),
            category=DecisionCategory.REBALANCE,
            action=f"REBALANCE portfolio: {changes_str}...",
            portfolio_state=portfolio,
            market_conditions=market,
            life_status=life_status,
            cash_impact=0,
            risk_impact=0.05,  # Minor risk reduction
            rationale=reason,
            expected_outcome="Restore target allocation, reduce concentration risk",
            confidence=0.85,
        )
        
        self.decisions.append(decision)
        self.life_log.append(
            f"[Month {self.current_month}, {self.current_year}] "
            f"REBALANCED portfolio. {len(changes)} positions adjusted. "
            f"Reason: {reason}"
        )
        
        return decision
    
    def log_job_loss_event(self, salary: float, unemployment_months: int):
        """Log major life event: job loss"""
        
        self.life_log.append(
            f"[Month {self.current_month}, {self.current_year}] "
            f"⚠️ MAJOR EVENT: JOB LOSS! "
            f"Monthly income: ${salary:,.0f} → $0. "
            f"Estimated unemployment: ~{unemployment_months} months. "
            f"**CRITICAL: Portfolio stress test initiated. Review cash reserves immediately.**"
        )
    
    def log_life_event(self, event_type: str, description: str, impact: float):
        """Log any life event"""
        
        impact_emoji = "📈" if impact > 0 else "📉"
        
        self.life_log.append(
            f"[Month {self.current_month}, {self.current_year}] "
            f"{impact_emoji} {event_type.upper()}: {description}"
        )
    
    def get_detailed_transcript(self) -> str:
        """Get full life journal transcript"""
        
        transcript = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                     FINANCIAL LIFE JOURNAL - {self.agent_name}                      ║
║                      Detailed Decision Transcript                          ║
╚════════════════════════════════════════════════════════════════════════════╝

"""
        
        # Add chronological events
        transcript += "\n".join(self.life_log)
        
        # Summary statistics
        transcript += f"\n\n{'='*80}\nDECISION SUMMARY\n{'='*80}\n"
        
        by_category = {}
        for decision in self.decisions:
            cat = decision.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(decision)
        
        for category, decisions in sorted(by_category.items()):
            transcript += f"\n{category.upper()}: {len(decisions)} decisions\n"
            for dec in decisions[-3:]:  # Show last 3
                transcript += f"  - {dec.action}\n"
        
        return transcript
    
    def get_detailed_decision_view(self, decision_id: str) -> Dict:
        """Get detailed view of a single decision"""
        
        for dec in self.decisions:
            if dec.decision_id == decision_id:
                return {
                    "when": dec.timestamp,
                    "what": dec.action,
                    "category": dec.category.value,
                    "rationale": dec.rationale,
                    "confidence": f"{dec.confidence*100:.0f}%",
                    "expected_outcome": dec.expected_outcome,
                    "cash_impact": f"${dec.cash_impact:,.0f}",
                    "portfolio_state": {
                        k: f"${v:,.0f}" if isinstance(v, (int, float)) else v
                        for k, v in dec.portfolio_state.items()
                    },
                    "market_conditions": dec.market_conditions,
                    "life_status": dec.life_status,
                    "result": {
                        "status": dec.result_status,
                        "actual_impact": f"${dec.actual_impact:,.0f}" if dec.actual_impact else None,
                        "notes": dec.outcome_notes,
                    }
                }
        
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return f"{self.current_month}/{self.current_year}"
    
    def advance_month(self):
        """Move to next month"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
    
    def export_json(self) -> str:
        """Export all decisions as JSON"""
        
        decisions_dict = []
        for dec in self.decisions:
            decisions_dict.append({
                "timestamp": dec.timestamp,
                "category": dec.category.value,
                "action": dec.action,
                "cash_impact": dec.cash_impact,
                "rationale": dec.rationale,
                "confidence": dec.confidence,
                "result_status": dec.result_status,
            })
        
        return json.dumps(decisions_dict, indent=2)


# Example usage
if __name__ == '__main__':
    logger = DecisionLogger("GPT-4")
    
    # Simulate decisions
    logger.log_stock_purchase(
        ticker="AAPL",
        shares=100,
        price=150.0,
        portfolio={"cash": 50000, "stocks": 200000},
        market={"vix": 18, "S&P500": 4500},
        life_status={"employed": True, "salary": 120000},
        rationale="Strong fundamentals, good valuation before earnings",
    )
    
    logger.advance_month()
    
    logger.log_job_loss_event(120000, 3)
    
    logger.advance_month()
    
    logger.log_loan_taken(
        bank_name="Chase",
        amount=50000,
        rate=0.05,
        term_months=60,
        portfolio={"cash": 30000, "stocks": 200000},
        life_status={"employed": False, "salary": 0},
        rationale="Emergency liquidity after job loss"
    )
    
    print(logger.get_detailed_transcript())
