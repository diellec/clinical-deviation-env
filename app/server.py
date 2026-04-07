from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from app.env import ClinicalEnv
from app.tasks import TASKS
from app.grader import grade_episode
from app.models import ActionInput

app = FastAPI()
env = ClinicalEnv()


class ResetInput(BaseModel):
    case_type: Optional[str] = "timing_deviation"


@app.get("/")
def root():
    return {"message": "Clinical Deviation Environment is running."}


@app.get("/tasks")
def get_tasks():
    return {"tasks": TASKS}


@app.post("/reset")
def reset(reset_input: ResetInput = ResetInput()):
    return env.reset(case_type=reset_input.case_type)


@app.get("/state")
def state():
    return env.get_state()


@app.post("/step")
def step(action_input: ActionInput):
    return env.step(action_input.action)


@app.get("/grader")
def grader():
    if env.state is None:
        return {"error": "No active episode. Call /reset first."}
    return grade_episode(env.state)