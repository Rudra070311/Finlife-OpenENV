import numpy as np
from app.models.state import State
from app.logic.goals import compute_goal_penalty


def compute_reward(state: State) -> float:
    """
    Comprehensive reward function for sophisticated finance training
    Rewards not just wealth accumulation but intelligent financial behavior
    """
    reward = 0.0
    
    # 1. WEALTH ACCUMULATION (Base Signal)
    if state.savings > 0:
        reward += 1.0
    else:
        reward -= 2.0
    
    # 2. PORTFOLIO GROWTH
    reward += min(state.net_worth * 0.00001, 5)
    
    # 3. INVESTMENT RETURNS (Reward positive stock gains)
    unrealized_gains = sum([pos.value - (pos.shares * pos.average_cost) 
                           for pos in state.stock_positions])
    if unrealized_gains > 0:
        reward += min(unrealized_gains * 0.0001, 3.0)
    
    # 4. REALIZED GAINS (Profit taking)
    if state.realized_gains > 0:
        reward += min(state.realized_gains * 0.00005, 2.0)
    
    # 5. LOSSES MINIMIZATION (But slight penalty for losses)
    if state.realized_losses > state.net_worth * 0.05:
        reward -= min(state.realized_losses * 0.00002, 1.0)
    
    # 6. GOAL ACHIEVEMENT
    if state.goals:
        avg_progress = sum([g.progress for g in state.goals]) / len(state.goals)
        reward += avg_progress * 3.0
    
    # 7. DEBT MANAGEMENT (Healthy debt-to-income ratio)
    total_emi = sum([l.emi for l in state.loans])
    if total_emi > state.income * 0.4:
        reward -= 3.0
    elif total_emi < state.income * 0.2:
        reward += 1.0  # Healthy leverage
    
    # 8. EMERGENCY FUND (6 months of expenses)
    if state.savings >= state.expenses * 6:
        reward += 2.0
    elif state.savings >= state.expenses * 3:
        reward += 1.0
    
    # 9. DIVERSIFICATION (Penalize concentration risk)
    total_stock_value = sum([pos.value for pos in state.stock_positions])
    if total_stock_value > 0:
        position_sizes = [pos.value / total_stock_value for pos in state.stock_positions]
        herfindahl_index = sum([ps**2 for ps in position_sizes])
        if herfindahl_index > 0.3:  # Over-concentrated
            reward -= 1.5
        elif herfindahl_index < 0.15:  # Well diversified
            reward += 1.5
    
    # 10. MARKET TIMING SOPHISTICATION (Reward contrarian behavior)
    if state.market_regime == "crash" and state.stock_positions and total_stock_value > state.portfolio.cash:
        reward += 2.0  # Buying in crashes is smart
    elif state.market_regime == "bull" and state.portfolio.cash > state.net_worth * 0.2:
        reward += 1.0  # Some defensive positioning in bull markets
    
    # 11. TRADING FREQUENCY (Not overtrading)
    if state.trades_executed > state.month / 3:  # More than 1 trade per month
        reward -= 0.5
    
    # 12. VOLATILITY AWARENESS (Risk adjustment)
    risk_score = state.vix_level / 100.0
    if state.risk_profile == "aggressive" and risk_score > 0.3:
        reward -= 1.0  # Aggressive portfolio unsuitable for high VIX
    elif state.risk_profile == "conservative" and state.portfolio.equity in [0] and risk_score < 0.2:
        reward += 0.5  # Conservative stance when safe
    
    # 13. INFLATION HEDGE (Maintaining purchasing power)
    real_savings = state.savings / (1 + state.inflation_rate) ** (state.age - 18)
    if real_savings > state.savings * 0.8:
        reward += 1.0
    
    # 14. BANKRUPTCY PENALTY
    if state.is_bankrupt:
        reward -= 25.0
    
    # 15. GOAL PENALTY
    reward += compute_goal_penalty(state)
    
    # Extra rewards for financial sophistication
    total_positions = len(state.stock_positions) + len(state.derivatives)
    if total_positions > 5 and total_positions < 30:  # Reasonable portfolio size
        reward += 0.5
    
    # Reward regular rebalancing
    if state.month % 3 == 0 and total_stock_value > 0:
        reward += 0.3
    
    return reward


def compute_reasoning_reward(action_reasoning: str, state: State) -> float:
    """
    Reward clear financial reasoning and domain knowledge
    For LLM training, bonus rewards for articulate decision-making
    """
    reasoning_reward = 0.0
    
    financial_terms = [
        "diversification", "risk-adjusted", "volatility", "correlation",
        "rebalancing", "tax-loss harvesting", "dollar-cost averaging",
        "momentum", "mean reversion", "sector rotation", "value",
        "growth", "dividend discount", "earnings yield"
    ]
    
    reasoning_lower = action_reasoning.lower()
    term_count = sum([1 for term in financial_terms if term in reasoning_lower])
    
    # Reward articulate reasoning
    if term_count >= 2:
        reasoning_reward += 0.5 * min(term_count / 5, 1.0)
    
    return reasoning_reward