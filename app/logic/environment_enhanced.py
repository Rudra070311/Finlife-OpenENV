"""
Enhanced Financial Environment
Integrates all modules: state, actions, events, logging
Simulates realistic life with brutal consequences
"""

import json
from typing import Dict, Tuple, Optional, Any
from dataclasses import asdict

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.enhanced_state import EnhancedState, StateFactory, EmploymentStatus
from models.enhanced_action import EnhancedAction, ActionType
from logic.life_events import LifeEventsGenerator
from logic.decision_logger import DecisionLogger
from data.expanded_stocks import ExpandedStockDatabase, BankDatabase


class EnhancedFinancialEnvironment:
    """
    Realistic financial life simulator with:
    - 2000+ stock options
    - 99+ banks with competitive lending
    - 15+ life event types (job loss, medical, war, etc.)
    - Brutal consequences and detailed decision logging
    """
    
    def __init__(self, task: str = "wealth_accumulation"):
        self.task = task
        self.state = None
        self.decision_logger = None
        self.event_generator = LifeEventsGenerator()
        self.stock_db = ExpandedStockDatabase()
        self.bank_db = BankDatabase()
        self.step_count = 0
        self.episode_complete = False
        
        # Task-specific goals
        self.goals = {
            "wealth_accumulation": {
                "target_net_worth": 1000000,
                "max_steps": 120,  # 10 years
                "name": "Build $1M net worth while managing risk",
            },
            "crisis_management": {
                "preserve_capital": True,
                "max_steps": 24,  # 2 years
                "name": "Survive job loss + medical emergency + market crash",
            },
            "financial_mastery": {
                "multi_objective": True,
                "max_steps": 120,
                "name": "Optimize wealth, health, job, life balance simultaneously",
            },
        }
    
    def reset(self, seed: Optional[int] = None) -> Tuple[Dict, Dict]:
        """Reset environment and return initial observation"""
        
        self.step_count = 0
        self.episode_complete = False
        
        # Create initial state
        self.state = StateFactory.create_initial_state(episode=1)
        
        # Initialize logger
        self.decision_logger = DecisionLogger(f"FinLife-Agent-{self.task}")
        
        # Inject initial life events for crisis mode
        if self.task == "crisis_management":
            self._inject_crisis_events()
        
        return self.get_observation(), self.get_info()
    
    def _inject_crisis_events(self):
        """Inject crisis events for crisis_management task"""
        
        # Simulate job loss
        self.state = StateFactory.apply_life_event(
            self.state,
            {"type": "JOB_LOSS"}
        )
        
        # Simulate medical emergency
        self.state = StateFactory.apply_life_event(
            self.state,
            {"type": "MEDICAL_EMERGENCY", "cost": 100000}
        )
        
        # Simulate recession/market crash
        self.state = StateFactory.apply_life_event(
            self.state,
            {"type": "RECESSION"}
        )
    
    def step(self, action: EnhancedAction) -> Tuple[Dict, float, bool, Dict]:
        """
        Execute one step
        
        Returns:
            observation: Current state
            reward: Step reward
            done: Episode complete?
            info: Additional info
        """
        
        self.step_count += 1
        
        # Generate life events for this month
        monthly_events = self.event_generator.generate_monthly_events(self.state)
        
        # Apply each life event
        for event in monthly_events:
            self.state = StateFactory.apply_life_event(self.state, event)
            self.decision_logger.life_log.append(
                f"[Month {self.state.current_month}] EVENT: {event.get('type', 'UNKNOWN')}"
            )
        
        # Execute agent action
        action_impacts = self._execute_action(action)
        
        # Calculate reward
        reward = self._calculate_reward(action_impacts)
        
        # Check if done
        goal_info = self.goals[self.task]
        max_steps = goal_info["max_steps"]
        done = self.step_count >= max_steps or self.episode_complete
        
        # Advance time
        self.state.current_month += 1
        if self.state.current_month > 12:
            self.state.current_month = 1
            self.state.current_year += 1
        
        self.decision_logger.current_month = self.state.current_month
        self.decision_logger.current_year = self.state.current_year
        
        info = self.get_info()
        info["action_impacts"] = action_impacts
        info["reward_breakdown"] = self._get_reward_breakdown(action_impacts)
        
        return self.get_observation(), reward, done, info
    
    def _execute_action(self, action: EnhancedAction) -> Dict:
        """Execute action and return impacts"""
        
        impacts = {
            "cash_impact": 0.0,
            "portfolio_impact": 0.0,
            "risk_impact": 0.0,
            "decisions_logged": 0,
        }
        
        if action.action_type == ActionType.BUY_STOCKS:
            for txn in action.stock_transactions:
                # Log purchase
                self.decision_logger.log_stock_purchase(
                    ticker=txn.ticker,
                    shares=txn.shares,
                    price=200.0,  # Placeholder
                    portfolio=self.state.to_dict(),
                    market={"vix": 20},
                    life_status={"employed": self.state.employment_status.value == "employed"},
                    rationale=action.decision_rationale,
                    confidence=action.confidence,
                )
                
                impacts["cash_impact"] -= txn.shares * 200
                impacts["portfolio_impact"] += txn.shares * 200
                impacts["decisions_logged"] += 1
        
        elif action.action_type == ActionType.TAKE_LOAN:
            if action.loan_request:
                self.decision_logger.log_loan_taken(
                    bank_name=action.loan_request.bank_name,
                    amount=action.loan_request.amount,
                    rate=0.05,
                    term_months=action.loan_request.desired_term_months,
                    portfolio=self.state.to_dict(),
                    life_status={"employed": self.state.employment_status.value == "employed"},
                    rationale=action.decision_rationale,
                )
                
                impacts["cash_impact"] += action.loan_request.amount
                impacts["risk_impact"] += 0.1  # Debt increases risk
                impacts["decisions_logged"] += 1
        
        elif action.action_type == ActionType.INCREASE_EMERGENCY_FUND:
            self.state.financial.emergency_fund += action.emergency_fund_deposit
            impacts["cash_impact"] -= action.emergency_fund_deposit
            impacts["risk_impact"] -= 0.05  # Reduces vulnerability
            impacts["decisions_logged"] += 1
        
        return impacts
    
    def _calculate_reward(self, action_impacts: Dict) -> float:
        """Calculate reward based on state and actions"""
        
        # Base reward components
        rewards = {
            "net_worth_change": 0.0,
            "resilience_bonus": 0.0,
            "decision_quality": 0.0,
            "crisis_penalty": 0.0,
        }
        
        # Net worth improvement (main objective)
        net_worth = self.state.get_net_worth()
        # Normalize to 0-100 scale
        nw_reward = min(100, net_worth / 10000)
        rewards["net_worth_change"] = nw_reward * 0.5
        
        # Resilience bonus (having emergency fund + low debt = good)
        ef_status = self.state.get_emergency_fund_status()
        vulnerability = self.state.get_vulnerability_score()
        rewards["resilience_bonus"] = (ef_status * (1 - vulnerability)) * 0.3
        
        # Decision quality (how good was the action?)
        if action_impacts["decisions_logged"] > 0:
            # Prefer fewer, better decisions
            decision_quality = 1.0 / (1 + action_impacts["decisions_logged"])
            rewards["decision_quality"] = decision_quality * 0.2
        
        # Crisis penalty: huge penalty if bankrupt or extremely vulnerable
        if net_worth < 0:
            rewards["crisis_penalty"] = -1.0
        elif vulnerability > 0.9:
            rewards["crisis_penalty"] = -0.3
        
        total_reward = sum(rewards.values())
        return max(-1.0, min(1.0, total_reward))  # Clamp [-1, 1]
    
    def _get_reward_breakdown(self, action_impacts: Dict) -> Dict:
        """Detailed reward calculation breakdown"""
        
        return {
            "net_worth": f"${self.state.get_net_worth():,.0f}",
            "emergency_fund_coverage": f"{self.state.get_emergency_fund_status()*100:.0f}%",
            "vulnerability": f"{self.state.get_vulnerability_score()*100:.0f}%",
            "decisions_made": action_impacts["decisions_logged"],
        }
    
    def get_observation(self) -> Dict:
        """Get current observation (state)"""
        
        return self.state.to_dict()
    
    def get_info(self) -> Dict:
        """Get metadata about environment"""
        
        goal = self.goals[self.task]
        
        return {
            "task": self.task,
            "step": self.step_count,
            "goal": goal["name"],
            "month": self.state.current_month,
            "year": self.state.current_year,
        }
    
    def render(self, mode: str = "human") -> Optional[str]:
        """Render current state"""
        
        if mode == "human":
            print(f"\nMonth {self.state.current_month}/{self.state.current_year}")
            print(f"Net Worth: ${self.state.get_net_worth():,.0f}")
            print(f"Employment: {self.state.employment_status.value}")
            print(f"Stress: {self.state.stress_level*100:.0f}%")
            print(f"Vulnerability: {self.state.get_vulnerability_score()*100:.0f}%")
        
        return None
    
    def get_decision_transcript(self) -> str:
        """Get full decision transcript"""
        
        return self.decision_logger.get_detailed_transcript()


# Example usage and integration test
if __name__ == "__main__":
    print("="*80)
    print("Enhanced Financial Environment - Integration Test")
    print("="*80)
    
    # Create environment
    env = EnhancedFinancialEnvironment(task="wealth_accumulation")
    
    # Reset
    obs, info = env.reset()
    print(f"\nInitial Observation:")
    print(json.dumps(obs, indent=2))
    
    # Run one step with a simple action
    from models.enhanced_action import EnhancedAction, ActionType
    
    action = EnhancedAction(
        action_type=ActionType.INCREASE_EMERGENCY_FUND,
        emergency_fund_deposit=5000,
        decision_rationale="Building safety net",
        confidence=0.9,
    )
    
    obs, reward, done, info = env.step(action)
    
    print(f"\nAfter Step 1:")
    print(f"  Reward: {reward:.3f}")
    print(f"  Net Worth: ${obs['net_worth']:,.0f}")
    print(f"  Emergency Fund: ${obs.get('emergency_fund', 0):,.0f}")
    
    # Test crisis mode
    print("\n" + "="*80)
    print("Testing Crisis Management Task")
    print("="*80)
    
    env_crisis = EnhancedFinancialEnvironment(task="crisis_management")
    obs, info = env_crisis.reset()
    
    print(f"\nInitial State (Post-Crisis Injection):")
    print(f"  Employment: {obs['employment']}")
    print(f"  Stress: {obs['stress']*100:.0f}%")
    print(f"  Recent Events: {obs['recent_events']}")
    
    # Show transcript
    print("\n" + "="*80)
    print("DECISION TRANSCRIPT")
    print("="*80)
    print(env.get_decision_transcript())
