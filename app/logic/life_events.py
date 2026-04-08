"""
Life Events System: Real-world risks and opportunities
- Job loss / unemployment
- Medical emergencies
- Geopolitical events (wars, pandemics)
- Real estate / housing events
- Family emergencies
- Market crashes
- Regulatory changes
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple
from enum import Enum


class EventType(Enum):
    """Types of life events"""
    JOB_LOSS = "job_loss"
    PROMOTION = "promotion"
    MEDICAL_EMERGENCY = "medical_emergency"
    ACCIDENT = "accident"
    WAR_CONFLICT = "war_conflict"
    PANDEMIC = "pandemic"
    NATURAL_DISASTER = "natural_disaster"
    REAL_ESTATE_CRASH = "real_estate_crash"
    SCHOOL_EXPENSES = "school_expenses"
    FAMILY_OBLIGATION = "family_obligation"
    MARKET_CRASH = "market_crash"
    RECESSION = "recession"
    INHERITANCE = "inheritance"
    DEBT_CRISIS = "debt_crisis"
    LEGAL_ISSUE = "legal_issue"


@dataclass
class LifeEvent:
    """A life event and its consequences"""
    event_type: EventType
    severity: float  # 0.0-1.0
    cash_impact: float  # Positive or negative
    job_impact: Optional[float] = None  # 0.0 = unemployed, 1.0 = fully employed
    portfolio_impact: Optional[float] = None  # % change to portfolio
    health_impact: Optional[float] = None  # Impact on health/stress
    debt_increase: Optional[float] = None  # Additional debt
    description: str = ""
    duration_months: int = 1


class LifeEventsGenerator:
    """Generates realistic life events based on environment state"""
    
    def __init__(self, seed: int = 42):
        """Initialize event generator"""
        self.rng = np.random.RandomState(seed)
        self.cash_reserves = 50000  # emergency fund
        self.employment_status = 1.0  # fully employed
        self.health_status = 1.0
        
    def generate_job_loss_event(self, base_salary: float) -> LifeEvent:
        """Generate job loss event"""
        severity = self.rng.uniform(0.3, 1.0)
        months_unemployed = int(severity * 12)  # Up to 1 year
        
        cash_impact = -base_salary * months_unemployed / 12  # Lost income
        
        # Unemployment benefits (50% of salary)
        unemployment_benefit = base_salary * 0.5 * months_unemployed / 12
        cash_impact += unemployment_benefit
        
        return LifeEvent(
            event_type=EventType.JOB_LOSS,
            severity=severity,
            cash_impact=cash_impact,
            job_impact=0.0,  # Immediately unemployed
            health_impact=-0.2,  # Stress from job loss
            description=f"Laid off! Unemployed for ~{months_unemployed} months. Receiving unemployment benefits.",
            duration_months=months_unemployed
        )
    
    def generate_promotion_event(self, base_salary: float) -> LifeEvent:
        """Generate promotion/raise event"""
        raise_pct = self.rng.uniform(0.10, 0.35)  # 10-35% raise
        
        # Annual impact
        cash_impact = base_salary * raise_pct
        
        return LifeEvent(
            event_type=EventType.PROMOTION,
            severity=0.6,
            cash_impact=cash_impact,
            job_impact=0.2,  # Job security improves
            health_impact=0.1,  # Stress relief
            description=f"Promotion! Salary increase of {raise_pct*100:.0f}%",
            duration_months=12
        )
    
    def generate_medical_emergency(self, wealth: float) -> LifeEvent:
        """Generate medical emergency"""
        severity = self.rng.uniform(0.3, 1.0)
        
        # Medical costs scale with severity
        # Without insurance: $100k-$1M+
        # With insurance: $5k-$50k out of pocket
        has_insurance = self.rng.rand() > 0.2  # 80% have insurance
        
        if has_insurance:
            medical_cost = self.rng.uniform(5000, 50000)
        else:
            medical_cost = self.rng.uniform(100000, 500000)
        
        # Additional costs: lost work days, medications, etc
        additional_cost = medical_cost * 0.2
        
        health_damage = -severity  # Health goes down
        if severity > 0.7:
            # Chronic condition = ongoing costs
            description = f"Hospital Stay! Chronic condition requiring ongoing treatment. Initial cost: ${medical_cost:,.0f}"
        else:
            description = f"Medical emergency (severity {severity:.1%}). Cost: ${medical_cost + additional_cost:,.0f}"
        
        return LifeEvent(
            event_type=EventType.MEDICAL_EMERGENCY,
            severity=severity,
            cash_impact=-(medical_cost + additional_cost),
            health_impact=health_damage,
            description=description,
            duration_months=int(12 * severity)  # Recovery time
        )
    
    def generate_war_conflict_event(self, portfolio_value: float) -> LifeEvent:
        """Generate geopolitical conflict (war, terrorism, etc)"""
        severity = self.rng.uniform(0.2, 0.8)
        
        # Market impact
        market_crash = self.rng.uniform(0.05, 0.30) * severity  # 5-30% crash
        portfolio_impact = -market_crash
        
        # Economic impact based on severity
        if severity > 0.6:
            # Major war - economic disruption
            cash_impact = -50000  # Supply chain disruption, inflation
            description = "Major geopolitical conflict! Market crash, inflation spike, supply chain chaos."
        elif severity > 0.3:
            # Moderate - market uncertainty
            cash_impact = -20000
            description = "Geopolitical tension rising. Markets volatile."
        else:
            # Minor - brief panic
            cash_impact = -5000
            description = "Tension in world markets. Brief selloff."
        
        return LifeEvent(
            event_type=EventType.WAR_CONFLICT,
            severity=severity,
            cash_impact=cash_impact,
            portfolio_impact=portfolio_impact,
            health_impact=-0.1,  # Anxiety
            description=description,
            duration_months=int(24 * severity)
        )
    
    def generate_pandemic_event(self) -> LifeEvent:
        """Generate pandemic/epidemic"""
        severity = self.rng.uniform(0.3, 1.0)
        
        # Pandemic impacts
        if severity > 0.7:
            # Severe pandemic (like COVID)
            portfolio_impact = -0.25  # 25% market crash
            cash_impact = -100000  # Lost income, medical
            job_impact = 0.5  # Many people lose jobs temporarily
            description = "Severe pandemic! Market crashed 25%, many job losses, lockdowns."
        else:
            portfolio_impact = -0.10
            cash_impact = -30000
            job_impact = 0.8
            description = f"Pandemic outbreak (severity {severity:.1%}). Economic impact moderate."
        
        return LifeEvent(
            event_type=EventType.PANDEMIC,
            severity=severity,
            cash_impact=cash_impact,
            portfolio_impact=portfolio_impact,
            job_impact=job_impact,
            health_impact=-severity,
            description=description,
            duration_months=int(18 * severity)
        )
    
    def generate_school_expenses(self, n_children: int = 1) -> LifeEvent:
        """Generate education expenses (college, private school, etc)"""
        # College cost: ~$30k-$80k per year
        per_year_cost = self.rng.uniform(30000, 80000)
        total_cost = per_year_cost * n_children * self.rng.randint(2, 5)  # 2-4 years
        
        return LifeEvent(
            event_type=EventType.SCHOOL_EXPENSES,
            severity=0.4,
            cash_impact=-total_cost,
            description=f"Child education expenses. Total cost over years: ${total_cost:,.0f}",
            duration_months=48
        )
    
    def generate_natural_disaster(self, owns_home: bool = True) -> LifeEvent:
        """Generate natural disaster (hurricane, earthquake, etc)"""
        severity = self.rng.uniform(0.2, 1.0)
        
        if owns_home:
            # Home damage
            damage_cost = self.rng.uniform(50000, 300000) * severity
            insurance_coverage = self.rng.uniform(0.3, 0.9)
            out_of_pocket = damage_cost * (1 - insurance_coverage)
        else:
            # Rental - displacement costs
            out_of_pocket = self.rng.uniform(5000, 30000)
        
        return LifeEvent(
            event_type=EventType.NATURAL_DISASTER,
            severity=severity,
            cash_impact=-out_of_pocket,
            health_impact=-0.2,
            description=f"Natural disaster! {'Home damage' if owns_home else 'Displacement'} costs: ${out_of_pocket:,.0f}",
            duration_months=12
        )
    
    def get_probability(self, event_type: EventType, 
                       employment_status: float,
                       economic_conditions: float) -> float:
        """Get probability of an event occurring this month"""
        
        base_probabilities = {
            EventType.JOB_LOSS: 0.003 * (1 - employment_status) * (0.5 + economic_conditions),
            EventType.PROMOTION: 0.001 * employment_status * (1 + 0.5 * economic_conditions),
            EventType.MEDICAL_EMERGENCY: 0.002,  # Always possible
            EventType.WAR_CONFLICT: 0.0005 * (1 - economic_conditions),
            EventType.PANDEMIC: 0.0001,  # Rare
            EventType.NATURAL_DISASTER: 0.0002,
            EventType.RECESSION: 0.001 * (1 - economic_conditions),
            EventType.MARKET_CRASH: 0.002 * (1 - economic_conditions),
        }
        
        return base_probabilities.get(event_type, 0.0)
    
    def generate_monthly_events(self, 
                               base_salary: float,
                               portfolio_value: float,
                               wealth: float,
                               employment_status: float = 1.0,
                               economic_conditions: float = 0.5) -> List[LifeEvent]:
        """Generate all events that might occur this month"""
        
        events = []
        
        # Check each event type
        for event_type in EventType:
            prob = self.get_probability(event_type, employment_status, economic_conditions)
            
            if self.rng.rand() < prob:
                if event_type == EventType.JOB_LOSS and employment_status > 0.2:
                    events.append(self.generate_job_loss_event(base_salary))
                elif event_type == EventType.PROMOTION and employment_status > 0.5:
                    events.append(self.generate_promotion_event(base_salary))
                elif event_type == EventType.MEDICAL_EMERGENCY:
                    events.append(self.generate_medical_emergency(wealth))
                elif event_type == EventType.WAR_CONFLICT:
                    events.append(self.generate_war_conflict_event(portfolio_value))
                elif event_type == EventType.PANDEMIC:
                    events.append(self.generate_pandemic_event())
                elif event_type == EventType.SCHOOL_EXPENSES and wealth > 100000:
                    events.append(self.generate_school_expenses())
                elif event_type == EventType.NATURAL_DISASTER:
                    events.append(self.generate_natural_disaster())
        
        return events


if __name__ == '__main__':
    gen = LifeEventsGenerator()
    
    # Example
    events = gen.generate_monthly_events(
        base_salary=100000,
        portfolio_value=500000,
        wealth=600000,
        employment_status=1.0,
        economic_conditions=0.7
    )
    
    for event in events:
        print(f"\n{event.event_type.value.upper()}")
        print(f"Severity: {event.severity:.1%}")
        print(f"Cash Impact: ${event.cash_impact:,.0f}")
        print(event.description)
