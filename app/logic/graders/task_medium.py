from app.models.state import State

def grade_medium(state: State) -> float:
    score = 0.0

    if not state.is_bankrupt:
        score += 0.3

    if state.savings >= state.expenses * 6:
        score += 0.2

    goal_progress = 0.0
    if state.goals:
        goal_progress = sum([g.progress for g in state.goals]) / len(state.goals)

    score += goal_progress * 0.3

    if state.net_worth > 500000:
        score += 0.2

    return min(score, 1.0)