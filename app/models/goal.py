from pydantic import BaseModel

class Goal(BaseModel):
    name: str
    type: str
    target_amount: float
    priority: int
    years_left: int

    _progress: float = 0.0

    @property
    def progress(self):
        return self._progress