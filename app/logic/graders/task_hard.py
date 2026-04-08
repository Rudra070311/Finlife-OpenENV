from app.models.state import State

def grade_hard(state: State) -> float:
    score = 0.0

    if not state.is_bankrupt:
        score += 0.2

    if state.age >= 60 and state.savings > 0:
        score += 0.2

    goal_progress = 0.0
    if state.goals:
        goal_progress = sum([g.progress for g in state.goals]) / len(state.goals)

    score += goal_progress * 0.3

    if state.net_worth > 2000000:
        score += 0.2

    if len(state.loans) == 0:
        score += 0.1

    return min(score, 1.0)