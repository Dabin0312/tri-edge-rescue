import os
import sqlite3
from datetime import datetime

import pandas as pd


def project_home():
    return os.path.expanduser(os.getenv("TRI_EDGE_HOME", "~/tri_edge_rescue"))


def mission_db_path():
    configured_path = os.getenv("TRI_EDGE_DB_PATH")
    if configured_path:
        return os.path.expanduser(configured_path)

    return os.path.join(project_home(), "db", "mission_events.db")


DB_PATH = mission_db_path()
REPORT_DIR = os.path.join(project_home(), "reports")


def load_data():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT
        id,
        received_at,
        robot_id,
        object,
        confidence,
        x,
        y,
        risk_score,
        decision,
        command,
        target_robot,
        llm_reason
    FROM event_summary
    ORDER BY id ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def generate_report(df):
    total_events = len(df)
    robot_a_events = int((df["robot_id"] == "A").sum())
    robot_b_events = int((df["robot_id"] == "B").sum())
    victim_events = int((df["object"] == "person").sum())
    obstacle_events = int((df["object"] == "obstacle").sum())
    hazard_events = int((df["object"] == "hazard").sum())
    high_risk_events = int((df["risk_score"] >= 7).sum())

    latest = df.iloc[-1]

    if high_risk_events > 0:
        mission_status = "CAUTION: High-risk events were detected."
    elif victim_events > 0:
        mission_status = "ACTIVE: Victim candidates were detected."
    else:
        mission_status = "NORMAL: Exploration proceeded without critical events."

    command_counts = df["command"].value_counts().to_dict()
    object_counts = df["object"].value_counts().to_dict()

    report = []
    report.append("# Tri-Edge Rescue Mission Report")
    report.append("")
    report.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    report.append("")
    report.append("## Mission Status")
    report.append("")
    report.append(mission_status)
    report.append("")
    report.append("## Event Summary")
    report.append("")
    report.append(f"- Total events: {total_events}")
    report.append(f"- Robot A events: {robot_a_events}")
    report.append(f"- Robot B events: {robot_b_events}")
    report.append(f"- Victim candidate events: {victim_events}")
    report.append(f"- Obstacle events: {obstacle_events}")
    report.append(f"- Hazard events: {hazard_events}")
    report.append(f"- High-risk events: {high_risk_events}")
    report.append("")
    report.append("## Latest Event")
    report.append("")
    report.append(f"- Event ID: {latest['id']}")
    report.append(f"- Time: {latest['received_at']}")
    report.append(f"- Robot: {latest['robot_id']}")
    report.append(f"- Object: {latest['object']}")
    report.append(f"- Position: ({latest['x']}, {latest['y']})")
    report.append(f"- Risk score: {latest['risk_score']}")
    report.append(f"- Decision: {latest['decision']}")
    report.append(f"- Command: {latest['command']}")
    if "llm_reason" in latest and latest["llm_reason"]:
        report.append(f"- Mission reason: {latest['llm_reason']}")
    report.append("")
    report.append("## Object Counts")
    report.append("")

    for obj, count in object_counts.items():
        report.append(f"- {obj}: {count}")

    report.append("")
    report.append("## Command Counts")
    report.append("")

    for command, count in command_counts.items():
        report.append(f"- {command}: {count}")

    report.append("")
    report.append("## On-Device Communication Value")
    report.append("")
    report.append(
        "This mission used summary JSON messages instead of sharing raw image streams. "
        "Each robot generated local semantic information such as detected object, position, "
        "risk score, and event type. Commander C integrated those summaries, saved them to a "
        "local database, and sent task commands back to each robot."
    )
    report.append("")
    report.append("Key value:")
    report.append("")
    report.append("- No raw image sharing")
    report.append("- Semantic-information-only communication")
    report.append("- Local DB-based mission logging")
    report.append("- Multi-robot command feedback loop")
    report.append("- On-device AI architecture readiness")

    return "\n".join(report)


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    df = load_data()

    if df.empty:
        print("No events found in DB.")
        return

    report_text = generate_report(df)
    output_path = os.path.join(REPORT_DIR, "mission_report.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"Mission report generated: {output_path}")


if __name__ == "__main__":
    main()
