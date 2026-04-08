import random
from app.models.state import State, Portfolio


def apply_market_returns(state: State) -> State:
    equity_return = random.gauss(0.01, 0.05)
    debt_return = random.gauss(0.005, 0.01)

    new_equity = state.portfolio.equity * (1 + equity_return)
    new_debt = state.portfolio.debt * (1 + debt_return)

    state.portfolio = Portfolio(
        equity=max(new_equity, 0),
        debt=max(new_debt, 0),
        cash=max(state.portfolio.cash, 0)
    )

    return state


def apply_income_growth(state: State) -> State:
    if state.month % 12 == 0 and state.month > 0:
        growth = random.uniform(0.05, 0.15)
        state.income *= (1 + growth)
    return state


def apply_inflation(state: State) -> State:
    inflation = random.uniform(0.003, 0.01)
    state.expenses *= (1 + inflation)
    return state


def apply_events(state: State) -> State:
    state = apply_market_returns(state)
    state = apply_income_growth(state)
    state = apply_inflation(state)
    return state