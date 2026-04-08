from app.models.state import State, Goal
import random


def generate_goals(state: State):
    """
    Dynamically adds goals based on life stage.
    Runs every step but only adds if not already present.
    """
    existing_goal_names = [g.name for g in state.goals]

    if state.age == 25 and state.dependents == 0:
        state.dependents = random.randint(0, 5)

    if state.age >= 22 and "emergency_fund" not in existing_goal_names:
        state.goals.append(Goal(
            name="emergency_fund",
            type="emergency",
            target_amount=state.expenses * 6,
            priority=3,
            years_left=2
        ))

    if state.age >= 25 and "house_buy" not in existing_goal_names:
        state.goals.append(Goal(
            name="house_buy",
            type="house",
            target_amount=1500000,
            priority=2,
            years_left=10
        ))

    if state.age >= 30 and "house_emi_phase" not in existing_goal_names:
        state.goals.append(Goal(
            name="house_emi_phase",
            type="house",
            target_amount=0,
            priority=2,
            years_left=20
        ))

    if state.age >= 30 and state.dependents > 0:
        for i in range(state.dependents):
            name = f"child_edu_{i}"
            if name not in existing_goal_names:
                state.goals.append(Goal(
                    name=name,
                    type="education",
                    target_amount=800000,
                    priority=3,
                    years_left=15
                ))

    if state.age >= 40 and "retirement_corpus" not in existing_goal_names:
        state.goals.append(Goal(
            name="retirement_corpus",
            type="retirement",
            target_amount=10000000,
            priority=5,
            years_left=(65 - state.age)
        ))

    if state.age >= 60 and "retirement_use" not in existing_goal_names:
        state.goals.append(Goal(
            name="retirement_use",
            type="retirement",
            target_amount=0,
            priority=5,
            years_left=25
        ))


def update_goal_progress(state: State) -> None:
    for goal in state.goals:
        required = goal.target_amount

        if required <= 0:
            continue

        if goal.type == "retirement":
            base = state.portfolio.equity + state.portfolio.debt

        elif goal.type == "emergency":
            base = state.savings

        elif goal.type == "education":
            base = state.savings + state.portfolio.debt * 0.5

        elif goal.type == "house":
            base = state.savings + state.portfolio.equity * 0.3

        else:
            base = state.savings

        goal.current_amount = min(base / required * required, required) if required > 0 else 0
    
def compute_goal_penalty(state: State) -> float:
    """
    Penalty for missing deadlines.
    (Hook this into reward later)
    """

    penalty = 0.0

    for goal in state.goals:
        if goal.years_left <= 0 and goal.progress < 1.0:
            penalty -= 5 * goal.priority  # weighted penalty
        # Also penalty for goals approaching deadline with low progress
        elif goal.years_left <= 2 and goal.progress < 0.5:
            penalty -= 2 * goal.priority

    return penalty