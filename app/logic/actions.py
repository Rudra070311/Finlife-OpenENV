from app.models.state import State
from app.models.action import Action


def validate_action(state: State, action: Action) -> Action:
    new_action = Action(**action.dict())

    new_action.sip_amount = max(new_action.sip_amount, 0)
    new_action.allocate_equity = max(new_action.allocate_equity, 0)
    new_action.allocate_debt = max(new_action.allocate_debt, 0)
    new_action.allocate_cash = max(new_action.allocate_cash, 0)
    new_action.spend_luxury = max(new_action.spend_luxury, 0)

    total_alloc = (
        new_action.allocate_equity +
        new_action.allocate_debt +
        new_action.allocate_cash
    )

    if total_alloc > 1.0:
        new_action.allocate_equity /= total_alloc
        new_action.allocate_debt /= total_alloc
        new_action.allocate_cash /= total_alloc

    if total_alloc == 0:
        new_action.allocate_cash = 1.0

    new_action.sip_amount = min(new_action.sip_amount, state.savings)

    max_luxury = state.income * 0.3
    new_action.spend_luxury = min(new_action.spend_luxury, max_luxury)

    total_spend = new_action.sip_amount + new_action.spend_luxury
    if total_spend > state.savings:
        scale = state.savings / total_spend
        new_action.sip_amount *= scale
        new_action.spend_luxury *= scale

    if new_action.take_loan:
        if new_action.loan_amount <= 0:
            new_action.take_loan = False
        else:
            max_loan = state.income * 12
            new_action.loan_amount = min(new_action.loan_amount, max_loan)

            estimated_emi = new_action.loan_amount / 60
            if estimated_emi > state.income * 0.5:
                new_action.take_loan = False
                new_action.loan_amount = 0.0

    return new_action