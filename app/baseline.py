from app.env import ClinicalEnv
from app.grader import grade_episode


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


def run_case(env, case_type):
    print(f"\n=== Running case: {case_type} ===")
    state = env.reset(case_type=case_type)
    print("Initial state:")
    print(state)

    total_reward = 0
    done = False
    result = None

    for action in BASELINE_POLICIES[case_type]:
        result = env.step(action)
        total_reward += result["reward"]

        print(f"\nAction: {action}")
        print(f"Reward: {result['reward']}")
        print(f"Message: {result['message']}")
        print(f"Status: {result['state']['status']}")

        done = result["done"]
        if done:
            break

    final_grade = grade_episode(env.state)

    print(f"\nFinal status: {env.state['status']}")
    print(f"Total reward: {total_reward}")
    print(f"Done: {done}")
    print(f"Final graded score: {final_grade['score']}")
    print(f"Steps taken: {final_grade['steps_taken']}")


def main():
    env = ClinicalEnv()

    for case_type in BASELINE_POLICIES.keys():
        run_case(env, case_type)


if __name__ == "__main__":
    main()