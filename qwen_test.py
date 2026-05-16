import sys
from pathlib import Path


repo_root = Path(__file__).resolve().parent
commander_src = repo_root / "ros2_ws" / "src" / "commander_c"
sys.path.insert(0, str(commander_src))

from commander_c.qwen_planner import QwenMissionPlanner


def main():
    planner = QwenMissionPlanner()
    reason = planner.generate_reason(
        robot_id="A",
        detected_object="hazard",
        risk_score=8,
        x=-3.5,
        y=-3.6,
        command="avoid_area"
    )
    print(reason)


if __name__ == "__main__":
    main()
