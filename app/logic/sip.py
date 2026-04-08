from app.models.state import State
from app.models.action import Action

def apply_sip(state: State, action: Action) -> State:
    invest_amount = action.sip_amount
    if invest_amount <= 0:
        return state

    equity_invest = action.allocate_equity * action.sip_amount
    debt_invest = action.allocate_debt * action.sip_amount
    cash_invest = action.allocate_cash * action.sip_amount

    state.portfolio.equity += equity_invest
    state.portfolio.debt += debt_invest
    state.portfolio.cash += cash_invest
    
    state.savings -= action.sip_amount

    return state