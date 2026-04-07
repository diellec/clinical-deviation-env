import os

from app.env import ClinicalEnv
from app.grader import grade_episode

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline-deterministic")
HF_TOKEN = os.getenv("HF_TOKEN")

TASK_NAME = os.getenv("TASK_NAME", "all_tasks")
BENCHMARK = os.getenv("BENCHMARK", "clinical_deviation_env")

if not HF_TOKEN:
    raise EnvironmentError("HF_TOKEN environment variable is required.")


BASELINE_POLICIES = {
    "timing_deviation": [
        "inspect_case",
        "review_protocol",
        "flag_deviation",
        "place_hold",
        "request_reason",
        "record_reason:late_arrival",
        "close_case",
    ],
    "sample_mismatch": [
        "inspect_case",
        "review_protocol",
        "flag_deviation",
        "block_separation",
        "request_rescan",
        "record_disposition:traceability_restored",
        "close_case",
    ],
    "hemolyzed_sample": [
        "inspect_case",
        "review_protocol",
        "flag_deviation",
        "place_hold",
        "request_supervisor_review",
        "record_disposition:reject_sample",
        "close_case",
    ],
}


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str = None) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def run_case(env: ClinicalEnv, task_id: str):
    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    try:
        env.reset(case_type=task_id)

        for step_num, action in enumerate(BASELINE_POLICIES[task_id], start=1):
            result = env.step(action)

            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))
            error = result.get("observation", {}).get("last_action_error")

            rewards.append(reward)
            steps_taken = step_num

            log_step(
                step=step_num,
                action=action,
                reward=reward,
                done=done,
                error=error,
            )

            if done:
                break

        final_grade = grade_episode(env.state)
        score = max(0.0, min(1.0, float(final_grade["score"])))
        success = bool(final_grade.get("success", False))

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


def main():
    env = ClinicalEnv()

    if TASK_NAME != "all_tasks":
        if TASK_NAME not in BASELINE_POLICIES:
            raise ValueError(f"Unknown TASK_NAME: {TASK_NAME}")
        run_case(env, TASK_NAME)
        return

    for task_id in BASELINE_POLICIES:
        run_case(env, task_id)


if __name__ == "__main__":
    main()