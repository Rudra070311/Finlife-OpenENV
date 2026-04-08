import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from app.config import Config

from app.environment import FinLifeEnv
from app.models.action import Action

from app.logic.graders import grade_easy, grade_medium, grade_hard
from app.reward import compute_reward


config = Config()

def policy(obs):
    return Action(
        sip_amount=obs.savings * 0.25,
        allocate_equity=0.6,
        allocate_debt=0.3,
        allocate_cash=0.1,
        spend_luxury=0.0,
        take_loan=False,
        loan_amount=0.0
    )


def run():
    env = FinLifeEnv(config=config.env)

    obs = env.reset()
    total_reward = 0.0
    action_history = []

    print("="*70)
    print("FINANCIAL LIFE SIMULATION STARTED")
    print("="*70)

    for step in range(config.env.max_steps):
        action = policy(obs)
        action_history.append(action)

        obs, reward, done, _ = env.step(action)
        total_reward += reward

        if config.train.verbose:
            print(f"\n{'='*70}")
            print(f"STEP {step} - Age {obs.age} years")
            print(f"{'='*70}")
            
            print("\n📊 CURRENT STATE:")
            print(f"  Savings:           ${round(obs.savings, 2):>15}")
            print(f"  Net Worth:         ${round(obs.net_worth, 2):>15}")
            print(f"  Step Reward:       {round(reward, 3):>15}")
            
            print("\n💰 ALLOCATION DECISIONS:")
            print(f"  SIP Amount:        ${round(action.sip_amount, 2):>15}")
            print(f"  Equity Allocation: {round(action.allocate_equity*100, 1):>14}%")
            print(f"  Debt Allocation:   {round(action.allocate_debt*100, 1):>14}%")
            print(f"  Cash Allocation:   {round(action.allocate_cash*100, 1):>14}%")
            print(f"  Luxury Spending:   {round(action.spend_luxury*100, 1):>14}%")
            
            loan_status = "YES" if action.take_loan else "NO"
            print(f"  Take Loan:         {loan_status:>15}")
            if action.take_loan:
                print(f"  Loan Amount:       ${round(action.loan_amount, 2):>15}")
            
            # Print other observation details if available
            if hasattr(obs, '__dict__'):
                print("\n📈 OTHER DETAILS:")
                for key, value in obs.__dict__.items():
                    if key not in ['savings', 'net_worth', 'age']:
                        if isinstance(value, float):
                            print(f"  {key:.<25} {round(value, 2):>15}")
                        else:
                            print(f"  {key:.<25} {str(value):>15}")

        if done:
            print(f"\n⏹️  Simulation ended at step {step}")
            break

    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Total Steps:       {step + 1:>15}")
    print(f"Total Reward:      {round(total_reward, 2):>15}")
    print(f"Final Age:         {obs.age:>15} years")
    print(f"Final Savings:     ${round(obs.savings, 2):>15}")
    print(f"Final Net Worth:   ${round(obs.net_worth, 2):>15}")

    print("\n🏆 PERFORMANCE SCORES:")
    print(f"  Easy:              {grade_easy(env.state):>14}")
    print(f"  Medium:            {grade_medium(env.state):>14}")
    print(f"  Hard:              {grade_hard(env.state):>14}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    run()