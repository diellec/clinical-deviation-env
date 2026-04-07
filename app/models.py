from pydantic import BaseModel
from typing import List, Optional


class ActionInput(BaseModel):
    action: str


class State(BaseModel):
    case_id: str
    case_type: str
    activity: Optional[str]

    status: str
    steps_taken: List[str]
    available_actions: List[str]


class StepResponse(BaseModel):
    state: dict
    reward: float
    done: bool
    message: str


class Task(BaseModel):
    name: str
    description: str
    available_actions: List[str]