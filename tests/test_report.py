import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "dashboard"))

from generate_report import generate_report


def test_generate_report_contains_latest_command_and_reason():
    df = pd.DataFrame(
        [
            {
                "id": 1,
                "received_at": "2026-05-16T12:00:00",
                "robot_id": "A",
                "object": "hazard",
                "confidence": 0.95,
                "x": -3.2,
                "y": -3.0,
                "risk_score": 8,
                "decision": "HIGH RISK: avoid or replan route",
                "command": "avoid_area",
                "target_robot": "A",
                "llm_reason": "Robot A should avoid the high-risk hazard.",
            }
        ]
    )

    report = generate_report(df)

    assert "Tri-Edge Rescue Mission Report" in report
    assert "High-risk events: 1" in report
    assert "avoid_area" in report
    assert "Robot A should avoid" in report
