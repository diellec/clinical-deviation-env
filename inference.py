import os

from app.env import ClinicalEnv
from app.grader import grade_episode

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline-deterministic")

TASK_NAME = os.getenv("TASK_NAME", "all_tasks")
BENCHMARK = os.getenv("BENCHMARK", "clinical_deviation_env")


BASELINE_POLICIES = {
    "timing_deviation": [
        "inspect_case",
        "flag_deviation",
        "request_reason",
        "hold_processing",
        "close_case"
    ],
    "sample_mismatch": [
        "inspect_case",
        "flag_mismatch",
        "block_separation",
        "request_correct_child",
        "close_case"
    ],
    "hemolyzed_sample": [
        "inspect_case",
        "flag_quality_issue",
        "hold_storage",
        "request_supervisor_review",
        "close_case"
    ]
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


def run_case(env: ClinicalEnv, case_type: str):
    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task=case_type, env=BENCHMARK, model=MODEL_NAME)

    try:
        env.reset(case_type=case_type)

        for step_num, action in enumerate(BASELINE_POLICIES[case_type], start=1):
            result = env.step(action)

            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))
            error = result.get("error", None)

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
        success = score >= 0.99

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


def main():
    env = ClinicalEnv()
    for case_type in BASELINE_POLICIES:
        run_case(env, case_type)


if __name__ == "__main__":
    main()