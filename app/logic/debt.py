from app.models.state import State, Loan


def apply_loan_payments(state: State) -> State:
    updated_loans = []

    for loan in state.loans:
        if loan.remaining_months <= 0:
            continue

        monthly_interest = loan.amount * (loan.interest_rate / 12)
        principal_payment = loan.emi - monthly_interest

        if principal_payment < 0:
            principal_payment = 0

        loan.amount -= principal_payment
        loan.remaining_months -= 1

        state.savings -= loan.emi

        if loan.amount > 0:
            updated_loans.append(loan)

    state.loans = updated_loans
    return state


def add_loan(state: State, loan_amount: float) -> State:
    if loan_amount <= 0:
        return state

    interest_rate = 0.1
    tenure = 60

    monthly_rate = interest_rate / 12

    emi = loan_amount * (monthly_rate * (1 + monthly_rate) ** tenure) / ((1 + monthly_rate) ** tenure - 1)

    loan = Loan(
        amount=loan_amount,
        interest_rate=interest_rate,
        tenure_months=tenure,
        remaining_months=tenure,
        emi=emi
    )

    state.loans.append(loan)
    state.savings += loan_amount

    return state