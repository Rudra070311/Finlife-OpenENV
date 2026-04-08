from pydantic import BaseModel


class EnvConfig(BaseModel):
    max_steps: int = 600

    initial_age: int = 18
    initial_income: float = 20000.0
    initial_expenses: float = 15000.0
    initial_savings: float = 5000.0

    risk_profile: str = "moderate"

    job_stability: float = 0.8
    health_factor: float = 0.9

    max_dependents: int = 5

    enable_events: bool = True


class TrainConfig(BaseModel):
    episodes: int = 1
    verbose: bool = True


class Config(BaseModel):
    env: EnvConfig = EnvConfig()
    train: TrainConfig = TrainConfig()


config = Config()