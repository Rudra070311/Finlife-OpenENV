"""
Enhanced State Representation
Includes job, health, credit, loans, and life event tracking
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import json


class EmploymentStatus(Enum):
    """Job status"""
    EMPLOYED = "employed"
    UNEMPLOYED = "unemployed"
    UNDEREMPLOYED = "underemployed"
    FREELANCE = "freelance"
    STARTUP = "startup"
    RETIRED = "retired"


class InsuranceStatus(Enum):
    """Health insurance coverage"""
    UNINSURED = "uninsured"
    BASIC = "basic"  # 80% coverage
    STANDARD = "standard"  # 90% coverage
    PREMIUM = "premium"  # 95% coverage


@dataclass
class LoanInfo:
    """Active loan"""
    bank_name: str
    principal: float
    rate: float
    remaining_term_months: int
    monthly_payment: float
    remaining_balance: float
    status: str = "active"  # active, delinquent, paid_off


@dataclass
class EmploymentRecord:
    """Employment history"""
    employer: str
    salary: float
    job_security: float  # 0.0-1.0 (0 = likely to be fired, 1 = tenured)
    industry: str  # tech, finance, healthcare, etc.
    employment_months: int  # How long in current role
    promotions_available: float  # Probability of raise in next year


@dataclass
class HealthRecord:
    """Health status"""
    health_score: float  # 0.0-1.0 (0 = critical, 1 = perfect health)
    chronic_conditions: List[str] = field(default_factory=list)
    medical_debt: float = 0.0
    insurance_status: InsuranceStatus = InsuranceStatus.BASIC
    medication_costs_annual: float = 0.0


@dataclass
class FinancialSnapshot:
    """Current financial position snapshot"""
    liquid_cash: float
    stocks: Dict[str, float]  # ticker -> shares
    stock_values: Dict[str, float]  # ticker -> current_value
    total_portfolio_value: float
    real_estate_value: float
    vehicle_value: float
    
    # Debt
    active_loans: List[LoanInfo] = field(default_factory=list)
    credit_card_debt: float = 0.0
    total_debt: float = 0.0
    
    # Credit
    credit_score: int = 750  # 300-850 FICO
    payment_history: float = 1.0  # 0.0-1.0 (1.0 = perfect)
    credit_utilization: float = 0.0  # 0.0-1.0
    
    # Emergency
    emergency_fund: float = 0.0
    emergency_fund_target: float = 15000.0  # 6 months expenses


@dataclass
class EnhancedState:
    """Complete agent state representation"""
    
    # Episode metadata
    episode_number: int
    current_month: int
    current_year: int
    
    # Financial position
    financial: FinancialSnapshot
    
    # Employment
    employment_status: EmploymentStatus
    employment_record: Optional[EmploymentRecord]
    
    # Health
    health: HealthRecord
    
    # Life events history
    recent_events: List[str] = field(default_factory=list)  # Last 3-5 major events
    
    # Risk metrics
    portfolio_volatility: float = 0.0  # 0.0-100.0
    diversification_score: float = 0.0  # 0.0-1.0 (1.0 = perfectly diversified)
    concentration_risk: float = 0.0  # 0.0-1.0 (0.0 = no concentration)
    
    # Subjective - what the agent "feels"
    stress_level: float = 0.0  # 0.0-1.0
    optimism_level: float = 0.5  # 0.0-1.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "episode": self.episode_number,
            "month": self.current_month,
            "year": self.current_year,
            "cash": self.financial.liquid_cash,
            "portfolio_value": self.financial.total_portfolio_value,
            "net_worth": self.get_net_worth(),
            "employment": self.employment_status.value,
            "health_score": self.health.health_score,
            "credit_score": self.financial.credit_score,
            "total_debt": self.financial.total_debt,
            "stress": self.stress_level,
            "recent_events": self.recent_events[-3:],
        }
    
    def get_net_worth(self) -> float:
        """Calculate net worth: (cash + portfolio + real_estate + vehicles) - debt"""
        assets = (
            self.financial.liquid_cash +
            self.financial.total_portfolio_value +
            self.financial.real_estate_value +
            self.financial.vehicle_value
        )
        return assets - self.financial.total_debt
    
    def get_emergency_fund_status(self) -> float:
        """0.0-1.0 how much of emergency fund target is covered"""
        if self.financial.emergency_fund_target == 0:
            return 1.0
        return min(1.0, self.financial.emergency_fund / self.financial.emergency_fund_target)
    
    def get_credit_health(self) -> float:
        """0.0-1.0 overall credit health"""
        # Score normalized (300-850 -> 0.0-1.0)
        score_normalized = (self.financial.credit_score - 300) / 550
        # Payment history factor
        payment_factor = self.financial.payment_history
        # Utilization penalty (higher utilization = lower health)
        utilization_penalty = self.financial.credit_utilization
        
        health = (score_normalized * 0.6 + payment_factor * 0.3 - utilization_penalty * 0.1)
        return max(0.0, min(1.0, health))
    
    def get_financial_stability(self) -> Dict:
        """Comprehensive financial stability metrics"""
        net_worth = self.get_net_worth()
        debt_to_income = (
            self.financial.total_debt / (self.employment_record.salary * 12)
            if self.employment_record and self.employment_record.salary > 0
            else 999
        )
        
        return {
            "net_worth": net_worth,
            "net_worth_trend": "stable",  # Would need history tracking
            "debt_to_income": min(10.0, debt_to_income),  # Cap at 10.0
            "emergency_fund_months": (
                self.financial.emergency_fund / 
                (self.employment_record.salary / 12)
                if self.employment_record and self.employment_record.salary > 0
                else 0
            ),
            "liquidity_ratio": (
                self.financial.liquid_cash / 
                (self.employment_record.salary / 12)
                if self.employment_record and self.employment_record.salary > 0
                else 0
            ),
        }
    
    def get_vulnerability_score(self) -> float:
        """
        0.0-1.0 how vulnerable agent is to life events
        High = more vulnerable (bad)
        """
        vulnerabilities = []
        
        # No emergency fund
        if self.get_emergency_fund_status() < 0.5:
            vulnerabilities.append(0.3)
        
        # High debt
        if self.financial.total_debt > self.get_net_worth() * 0.5:
            vulnerabilities.append(0.25)
        
        # Unemployed
        if self.employment_status == EmploymentStatus.UNEMPLOYED:
            vulnerabilities.append(0.4)
        
        # Poor health
        if self.health.health_score < 0.5:
            vulnerabilities.append(0.15)
        
        # Bad credit
        if self.get_credit_health() < 0.5:
            vulnerabilities.append(0.2)
        
        # High stress
        if self.stress_level > 0.7:
            vulnerabilities.append(0.1)
        
        if not vulnerabilities:
            return 0.0
        
        return min(1.0, sum(vulnerabilities) / len(vulnerabilities))


class StateFactory:
    """Factory for creating initial and updated states"""
    
    @staticmethod
    def create_initial_state(episode: int) -> EnhancedState:
        """Create starting state for episode"""
        
        initial_cash = 50000.0
        initial_portfolio = {
            "VTI": 3000,  # Vanguard Total Stock Market ETF
            "BND": 1000,  # Vanguard Total Bond Market ETF
            "VXUS": 1000,  # Vanguard International Stock ETF
        }
        
        financial = FinancialSnapshot(
            liquid_cash=initial_cash,
            stocks={ticker: shares for ticker, shares in initial_portfolio.items()},
            stock_values={
                "VTI": 240 * 3000,
                "BND": 80 * 1000,
                "VXUS": 140 * 1000,
            },
            total_portfolio_value=240000,
            real_estate_value=0,  # Assume renting
            vehicle_value=15000,  # Modest car
            credit_score=720,
        )
        
        employment = EmploymentRecord(
            employer="TechCorp Inc",
            salary=120000,
            job_security=0.7,  # Moderate security
            industry="tech",
            employment_months=24,
            promotions_available=0.3,
        )
        
        health = HealthRecord(
            health_score=0.8,
            insurance_status=InsuranceStatus.STANDARD,
        )
        
        return EnhancedState(
            episode_number=episode,
            current_month=1,
            current_year=2025,
            financial=financial,
            employment_status=EmploymentStatus.EMPLOYED,
            employment_record=employment,
            health=health,
            stress_level=0.3,
            optimism_level=0.6,
        )
    
    @staticmethod
    def apply_life_event(state: EnhancedState, event: Dict) -> EnhancedState:
        """Update state based on a life event"""
        
        event_type = event.get("type")
        
        if event_type == "JOB_LOSS":
            state.employment_status = EmploymentStatus.UNEMPLOYED
            state.employment_record.salary = 0
            state.stress_level = min(1.0, state.stress_level + 0.4)
            state.optimism_level = max(0.0, state.optimism_level - 0.3)
            state.recent_events.append(f"Lost job at {state.employment_record.employer}")
        
        elif event_type == "PROMOTION":
            old_salary = state.employment_record.salary
            state.employment_record.salary *= 1.25  # 25% raise
            state.employment_record.job_security = min(1.0, state.employment_record.job_security + 0.1)
            state.stress_level = max(0.0, state.stress_level - 0.1)
            state.recent_events.append(f"Promotion: ${old_salary:,.0f} → ${state.employment_record.salary:,.0f}")
        
        elif event_type == "MEDICAL_EMERGENCY":
            cost = event.get("cost", 50000)
            insurance_coverage = {"basic": 0.2, "standard": 0.1, "premium": 0.05}
            out_of_pocket = cost * insurance_coverage.get(state.health.insurance_status.value, 0.5)
            state.financial.liquid_cash -= out_of_pocket
            state.health.medical_debt += out_of_pocket
            state.health.health_score = max(0.0, state.health.health_score - 0.2)
            state.stress_level = min(1.0, state.stress_level + 0.3)
            state.recent_events.append(f"Medical emergency: ${out_of_pocket:,.0f} out-of-pocket")
        
        elif event_type == "RECESSION":
            portfolio_loss = state.financial.total_portfolio_value * 0.25
            state.financial.total_portfolio_value *= 0.75
            state.stress_level = min(1.0, state.stress_level + 0.2)
            state.optimism_level = max(0.0, state.optimism_level - 0.2)
            state.recent_events.append(f"Recession: Portfolio down ${portfolio_loss:,.0f}")
        
        # Update derived metrics
        state.stress_level = min(1.0, max(0.0, state.stress_level))
        state.optimism_level = min(1.0, max(0.0, state.optimism_level))
        
        return state


if __name__ == '__main__':
    # Example: Create initial state
    state = StateFactory.create_initial_state(episode=1)
    
    print("Initial State:")
    print(json.dumps(state.to_dict(), indent=2))
    
    print(f"\nNet Worth: ${state.get_net_worth():,.0f}")
    print(f"Emergency Fund Status: {state.get_emergency_fund_status()*100:.0f}%")
    print(f"Credit Health: {state.get_credit_health()*100:.0f}")
    print(f"Vulnerability Score: {state.get_vulnerability_score()*100:.0f}%")
    
    print("\nStability Metrics:")
    stability = state.get_financial_stability()
    for key, value in stability.items():
        print(f"  {key}: {value}")
    
    # Example: Apply job loss event
    print("\n" + "="*70)
    print("Applying JOB_LOSS event...")
    print("="*70)
    
    state = StateFactory.apply_life_event(state, {"type": "JOB_LOSS"})
    
    print("\nState After Job Loss:")
    print(json.dumps(state.to_dict(), indent=2))
    print(f"Vulnerability Score: {state.get_vulnerability_score()*100:.0f}%")
