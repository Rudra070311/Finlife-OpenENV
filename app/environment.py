from app.models.state import State
from app.models.action import Action
from app.models.observation import Observation
from app.logic.transitions import step
from app.reward import compute_reward
from app.models.state import State, Portfolio
import random

class FinLifeEnv:
    def __init__(self, config):
        self.config = config

    def reset(self):
        self.state = State(
            age=self.config.initial_age,
            month=0,

            income = self.config.initial_income,
            expenses = self.config.initial_expenses,
            savings = self.config.initial_savings,

            net_worth = self.config.initial_savings,

            portfolio = Portfolio(
                equity=0.0,
                debt=0.0,
                cash=self.config.initial_savings
            ),

            loans=[],
            goals=[],

            risk_profile = self.config.risk_profile,

            dependents=random.randint(0, self.config.max_dependents),

            job_stability = self.config.job_stability,
            health_factor = self.config.health_factor,

            is_bankrupt=False,

            last_income = self.config.initial_income,
            last_expenses = self.config.initial_expenses
        )

        return self._get_observation()

    def step(self, action: Action):
        self.state = step(self.state, action)
        reward = self._compute_reward()
        done = self._is_done()
        obs = self._get_observation()

        return obs, reward, done, {}

    def _get_observation(self):
        portfolio_value = (
            self.state.portfolio.equity +
            self.state.portfolio.debt +
            self.state.portfolio.cash
        )

        if self.state.goals:
            goal_progress = sum([g.progress for g in self.state.goals]) / len(self.state.goals)
        else:
            goal_progress = 0.0

        income_trend = self.state.income - self.state.last_income
        expense_trend = self.state.expenses - self.state.last_expenses

        obs = Observation(
            age=self.state.age,
            month=self.state.month,

            income=self.state.income,
            expenses=self.state.expenses,
            savings=self.state.savings,
            net_worth=self.state.net_worth,

            equity=self.state.portfolio.equity,
            debt=self.state.portfolio.debt,
            cash=self.state.portfolio.cash,

            loans=self.state.loans,
            goals=self.state.goals,

            risk_profile=self.state.risk_profile,
            dependents=self.state.dependents,

            job_stability=self.state.job_stability,
            health_factor=self.state.health_factor,

            is_bankrupt=self.state.is_bankrupt,

            portfolio_value=portfolio_value,
            goal_progress_summary=goal_progress,

            income_trend=income_trend,
            expense_trend=expense_trend
        )

        self.state.last_income = self.state.income
        self.state.last_expenses = self.state.expenses

        return obs

        if len(self.state.goals) > 0:
            avg_goal_progress = sum([g.progress for g in self.state.goals]) / len(self.state.goals)
        else:
            avg_goal_progress = 0.0

        return Observation(
            age=self.state.age,
            month=self.state.month,
            income=self.state.income,
            expenses=self.state.expenses,
            savings=self.state.savings,
            net_worth=self.state.net_worth,
            portfolio_value=portfolio_value,
            goal_progress_summary=avg_goal_progress,
            risk_profile=self.state.risk_profile,
            dependents=self.state.dependents,
            is_bankrupt=self.state.is_bankrupt,
            income_trend=0.0,
            expense_trend=0.0
        )

    def _compute_reward(self):
        return compute_reward(self.state)

    def _is_done(self):
        if self.state.is_bankrupt:
            return True
        if self.state.age >= 65:
            return True
        return False