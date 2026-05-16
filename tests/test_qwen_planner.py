import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "ros2_ws" / "src" / "commander_c"))


def test_qwen_planner_fallback_reason():
    os.environ["TRI_EDGE_ENABLE_QWEN"] = "0"

    from commander_c.qwen_planner import QwenMissionPlanner

    planner = QwenMissionPlanner()
    reason = planner.generate_reason(
        robot_id="B",
        detected_object="hazard",
        risk_score=8,
        x=-3.2,
        y=-3.0,
        command="avoid_area",
    )

    assert "Robot B" in reason
    assert "avoid_area" in reason
    assert "high-risk" in reason
