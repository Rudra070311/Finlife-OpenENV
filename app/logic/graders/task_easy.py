from app.models.state import State

def grade_easy(state: State) -> float:
    score = 0.0

    if not state.is_bankrupt:
        score += 0.4

    if state.savings > state.expenses * 3:
        score += 0.3

    if state.net_worth > 0:
        score += 0.3

    return min(score, 1.0)