from pydantic import BaseModel

class TaskScores(BaseModel):
    survival: float
    stability: float
    growth: float
    goals: float
    debt_control: float
    retirement: float

    def overall(self) -> float:
        return (
            self.survival +
            self.stability +
            self.growth +
            self.goals +
            self.debt_control +
            self.retirement
        ) / 6.0