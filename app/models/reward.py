from pydantic import BaseModel

class RewardWeights(BaseModel):
    survival: float = 1.0
    savings_positive: float = 1.0
    savings_negative: float = -2.0
    net_worth: float = 0.00001
    emergency_fund: float = 2.0
    high_emi_penalty: float = -3.0
    goal_progress: float = 5.0
    retirement_bonus: float = 10.0
    bankruptcy_penalty: float = -50.0