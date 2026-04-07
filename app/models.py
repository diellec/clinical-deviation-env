from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ActionInput(BaseModel):
    action: str


class Observation(BaseModel):
    case_id: str
    task_type: str
    study_id: str
    subject_id: str
    current_stage: str
    facts: Dict[str, Any]
    workflow: Dict[str, Any]
    allowed_actions: List[str]
    protocol_hint: Optional[str] = None
    last_action_error: Optional[str] = None


class State(BaseModel):
    case_id: str
    task_id: str
    difficulty: str
    status: str
    done: bool
    steps_taken: List[str]
    score: float
    observation: Observation
    grader_progress: Dict[str, bool]


class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    message: str
    score: float
    grader_progress: Dict[str, bool]


class Task(BaseModel):
    id: str
    name: str
    difficulty: str
    description: str
    objective: str
    key_risks: List[str]
    available_actions: List[str]