"""
Task Graders for FinLife-OpenEnv
Scores task performance on scale 0.0-1.0
"""

import numpy as np
from typing import Dict, Any


class WealthAccumulationGrader:
    """Grade wealth accumulation task (easy)"""
    
    def __init__(self, target_net_worth: float = 1000000):
        self.target_net_worth = target_net_worth
    
    def grade(self, final_state: Dict[str, Any], episode_data: Dict) -> float:
        """
        Wealth accumulation grading:
        - Final net worth vs target (main score)
        - Bankruptcy penalty
        - Savings maintenance bonus
        """
        score = 0.0
        
        # Primary metric: net worth accumulation (0-0.6)
        if final_state['net_worth'] > 0:
            wealth_ratio = final_state['net_worth'] / self.target_net_worth
            wealth_score = min(wealth_ratio, 1.0) * 0.6
            score += wealth_score
        else:
            return 0.0  # Bankruptcy = fail
        
        # Savings maintenance (0-0.2)
        if final_state['savings'] > final_state['expenses'] * 6:
            score += 0.2
        elif final_state['savings'] > 0:
            score += 0.1
        
        # Portfolio growth bonus (0-0.2)
        if episode_data.get('portfolio_value', 0) > 100000:
            portfolio_ratio = episode_data['portfolio_value'] / final_state['net_worth']
            if 0.3 <= portfolio_ratio <= 0.7:  # Good allocation
                score += 0.2
            elif portfolio_ratio > 0:
                score += 0.1
        
        return min(score, 1.0)


class CrisisManagementGrader:
    """Grade crisis management task (medium)"""
    
    def __init__(self, target_preservation: float = 0.8):
        self.target_preservation = target_preservation  # Preserve 80%+ during crash
    
    def grade(self, final_state: Dict[str, Any], episode_data: Dict) -> float:
        """
        Crisis management grading:
        - Capital preservation during crashes (main score)
        - Diversification maintenance
        - Quick recovery
        - Tax optimization
        """
        score = 0.0
        
        # Check if episode included market crash
        max_vix = episode_data.get('max_vix', 20)
        if max_vix < 30:  # No real crisis
            return 0.5  # Incomplete test
        
        # Capital preservation during crash (0-0.5)
        peak_drawdown = episode_data.get('peak_drawdown', 0.0)
        if peak_drawdown < 0.30:  # Preserved >70%
            score += 0.5
        elif peak_drawdown < 0.50:  # Preserved >50%
            score += 0.3
        else:
            score += 0.1
        
        # Diversification bonus (0-0.2)
        diversification = final_state.get('diversification_score', 0)
        if diversification > 0.6:
            score += 0.2
        elif diversification > 0.4:
            score += 0.1
        
        # Recovery quality (0-0.2)
        recovery_ratio = episode_data.get('recovery_ratio', 0)
        if recovery_ratio > 0.95:  # Recovered to near-peak
            score += 0.2
        elif recovery_ratio > 0.8:
            score += 0.1
        
        # Tax loss harvesting (0-0.1)
        if episode_data.get('used_tax_harvesting', False):
            score += 0.1
        
        return min(score, 1.0)


class PortfolioOptimizationGrader:
    """Grade portfolio optimization task (hard)"""
    
    def __init__(self):
        self.max_volatility = 0.25
        self.tax_efficiency_target = 0.9
    
    def grade(self, final_state: Dict[str, Any], episode_data: Dict) -> float:
        """
        Portfolio optimization grading:
        - Final wealth (0-0.30)
        - Risk-adjusted returns (0-0.25)
        - Tax efficiency (0-0.20)
        - Goal achievement (0-0.15)
        - Diversification (0-0.10)
        """
        score = 0.0
        
        # Component 1: Wealth accumulation (0-0.30)
        if final_state['net_worth'] > 2000000:
            score += 0.30
        elif final_state['net_worth'] > 1000000:
            score += 0.20
        elif final_state['net_worth'] > 500000:
            score += 0.15
        elif final_state['net_worth'] > 100000:
            score += 0.10
        
        # Component 2: Risk-adjusted returns (0-0.25)
        realized_gains = final_state.get('realized_gains', 0)
        portfolio_return = realized_gains / (final_state['net_worth'] + 1)
        
        if portfolio_return > 0.1:  # 10%+ return
            risk_adjusted = 0.25
        elif portfolio_return > 0.05:
            risk_adjusted = 0.20
        elif portfolio_return > 0:
            risk_adjusted = 0.15
        else:
            risk_adjusted = 0.05
        
        # penalize for crashes
        max_vix = episode_data.get('max_vix', 20)
        if max_vix > 50:
            risk_adjusted *= 0.8
        
        score += risk_adjusted
        
        # Component 3: Tax efficiency (0-0.20)
        tax_loss_harvested = episode_data.get('tax_loss_harvested', 0)
        realized_losses = final_state.get('realized_losses', 0)
        
        if tax_loss_harvested > realized_gains * 0.3:  # Used harvesting well
            score += 0.20
        elif realized_losses > 0:
            score += 0.10
        
        # Component 4: Goal achievement (0-0.15)
        goal_progress = final_state.get('goal_progress_summary', 0)
        if goal_progress > 0.8:
            score += 0.15
        elif goal_progress > 0.5:
            score += 0.10
        elif goal_progress > 0.2:
            score += 0.05
        
        # Component 5: Diversification (0-0.10)
        diversification = final_state.get('diversification_score', 0)
        if diversification > 0.7:
            score += 0.10
        elif diversification > 0.5:
            score += 0.05
        
        return min(score, 1.0)


def grade_task(task_name: str, final_state: Dict, episode_data: Dict) -> float:
    """
    Main grading function.
    
    Args:
        task_name: "wealth_accumulation", "crisis_management", or "portfolio_optimization"
        final_state: Final state dict from environment
        episode_data: Collected episode metrics
        
    Returns:
        Score in 0.0-1.0 range
    """
    
    graders = {
        "wealth_accumulation": WealthAccumulationGrader(),
        "crisis_management": CrisisManagementGrader(),
        "portfolio_optimization": PortfolioOptimizationGrader(),
    }
    
    if task_name not in graders:
        raise ValueError(f"Unknown task: {task_name}")
    
    grader = graders[task_name]
    score = grader.grade(final_state, episode_data)
    
    # Ensure score is in valid range
    return max(0.0, min(1.0, score))
