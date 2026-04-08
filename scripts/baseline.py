from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from app.environment import FinLifeEnv
from app.models.action import Action
from app.logic.graders import grade_easy, grade_medium, grade_hard

def policy(obs):
    sip = 0.0
    equity = 0.6
    debt = 0.3
    cash = 0.1
    luxury = 0.0
    take_loan = False
    loan_amount = 0.0

    if obs.savings < obs.expenses * 3:
        sip = obs.savings * 0.2
        equity, debt, cash = 0.2, 0.2, 0.6

    elif obs.savings < obs.expenses * 6:
        sip = obs.savings * 0.3
        equity, debt, cash = 0.4, 0.4, 0.2

    else:
        sip = obs.savings * 0.5

        if obs.age < 30:
            equity, debt, cash = 0.7, 0.2, 0.1
        elif obs.age < 50:
            equity, debt, cash = 0.6, 0.3, 0.1
        else:
            equity, debt, cash = 0.4, 0.5, 0.1

    if obs.savings > obs.expenses * 6:
        luxury = obs.income * 0.05

    if obs.savings < obs.expenses * 2 and obs.age < 35:
        take_loan = True
        loan_amount = obs.income * 6

    # Ensure all values are non-negative
    sip = max(0.0, min(sip, obs.savings))
    luxury = max(0.0, min(luxury, obs.savings - sip))

    return Action(
        sip_amount=sip,
        allocate_equity=equity,
        allocate_debt=debt,
        allocate_cash=cash,
        spend_luxury=luxury,
        take_loan=take_loan,
        loan_amount=loan_amount
    )


def run_episode():
    env = FinLifeEnv()
    obs = env.reset()

    total_reward = 0.0

    for step in range(600):
        action = policy(obs)

        obs, reward, done, _ = env.step(action)
        total_reward += reward

        print(f"\nStep {step}")
        print("Age:", obs.age)
        print("Savings:", round(obs.savings, 2))
        print("Income:", round(obs.income, 2))
        print("Net Worth:", round(obs.net_worth, 2))
        print("Reward:", round(reward, 3))

        if done:
            break

    print("\nTotal Reward:", round(total_reward, 2))

    print("\nFinal Scores:")
    print("Easy:", grade_easy(env.state))
    print("Medium:", grade_medium(env.state))
    print("Hard:", grade_hard(env.state))


if __name__ == "__main__":
    run_episode()