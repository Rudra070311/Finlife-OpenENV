from app.models.state import State
from app.models.action import Action

from app.logic.actions import validate_action
from app.logic.sip import apply_sip
from app.logic.debt import apply_loan_payments, add_loan
from app.logic.goals import generate_goals, update_goal_progress

from app.simulator import apply_events


def step(state: State, action: Action) -> State:
    action = validate_action(state, action)

    new_month = state.month + 1
    new_age = state.age + 1 if new_month % 12 == 0 else state.age

    new_state = State(
        age=new_age,
        month=new_month,
        income=state.income,
        expenses=state.expenses,
        savings=state.savings,
        net_worth=state.net_worth,
        portfolio=state.portfolio,
        loans=list(state.loans),
        goals=list(state.goals),
        risk_profile=state.risk_profile,
        dependents=state.dependents,
        job_stability=state.job_stability,
        health_factor=state.health_factor,
        is_bankrupt=state.is_bankrupt
    )

    new_state.savings += new_state.income
    new_state.savings -= new_state.expenses

    new_state = apply_sip(new_state, action)

    new_state = apply_loan_payments(new_state)

    if action.take_loan:
        new_state = add_loan(new_state, action.loan_amount)

    new_state.savings -= action.spend_luxury

    new_state = apply_events(new_state)

    generate_goals(new_state)
    update_goal_progress(new_state)

    portfolio_value = (
        new_state.portfolio.equity +
        new_state.portfolio.debt +
        new_state.portfolio.cash
    )

    total_liabilities = sum([l.amount for l in new_state.loans])

    new_state.net_worth = new_state.savings + portfolio_value - total_liabilities

    if new_state.savings < -10000:
        new_state.is_bankrupt = True

    return new_state