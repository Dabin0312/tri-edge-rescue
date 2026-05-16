import os
import sqlite3

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh


def mission_db_path():
    configured_path = os.getenv("TRI_EDGE_DB_PATH")
    if configured_path:
        return os.path.expanduser(configured_path)

    project_home = os.getenv("TRI_EDGE_HOME", "~/tri_edge_rescue")
    return os.path.join(os.path.expanduser(project_home), "db", "mission_events.db")


DB_PATH = mission_db_path()

st.set_page_config(
    page_title="Tri-Edge Rescue Dashboard",
    layout="wide"
)

st.title("Tri-Edge Rescue Dashboard")
st.caption("On-Device Multi-Robot AI Mission Monitor")

st_autorefresh(interval=2000, key="dashboard_refresh")


@st.cache_data(ttl=2)
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()

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
    ORDER BY id DESC
    LIMIT 300
    """

    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    return df


df = load_data()

if df.empty:
    st.warning("No mission events have been saved yet. Run Commander C and check again.")
    st.code(DB_PATH, language="text")
    st.stop()

if "llm_reason" not in df.columns:
    df["llm_reason"] = "none"

latest_id = int(df["id"].max())
total_events = len(df)
high_risk_count = int((df["risk_score"] >= 7).sum())
victim_count = int((df["object"] == "person").sum())
obstacle_count = int((df["object"] == "obstacle").sum())
hazard_count = int((df["object"] == "hazard").sum())

robot_a_count = int((df["robot_id"] == "A").sum())
robot_b_count = int((df["robot_id"] == "B").sum())

latest_event = df.sort_values("id", ascending=False).iloc[0]
latest_command = latest_event.get("command", "none")
latest_robot = latest_event.get("robot_id", "unknown")
latest_risk = latest_event.get("risk_score", 0)
latest_llm_reason = latest_event.get("llm_reason", "none")

if high_risk_count > 0:
    mission_status = "CAUTION: High-risk events detected"
elif victim_count > 0:
    mission_status = "ACTIVE: Victim candidate detected"
else:
    mission_status = "NORMAL: Exploration in progress"

col1, col2, col3, col4 = st.columns(4)

col1.metric("Latest Event ID", latest_id)
col2.metric("Loaded Events", total_events)
col3.metric("High Risk Events", high_risk_count)
col4.metric("Victim Candidates", victim_count)

st.divider()
st.subheader("Mission Report")

report_col1, report_col2 = st.columns([1, 1])

with report_col1:
    st.markdown(
        f"""
        **Mission Status:** `{mission_status}`  
        **Latest Robot:** Robot `{latest_robot}`  
        **Latest Command:** `{latest_command}`  
        **Latest Risk Score:** `{latest_risk}`  
        """
    )

with report_col2:
    st.markdown(
        f"""
        **Robot A Events:** `{robot_a_count}`  
        **Robot B Events:** `{robot_b_count}`  
        **Obstacle Events:** `{obstacle_count}`  
        **Hazard Events:** `{hazard_count}`  
        """
    )

st.subheader("LLM Mission Reason")

if pd.isna(latest_llm_reason) or str(latest_llm_reason).strip() == "":
    st.info("No LLM reason has been generated yet.")
else:
    st.success(str(latest_llm_reason))

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("Recent Mission Events")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

with right:
    st.subheader("Robot Event Count")
    robot_counts = df["robot_id"].value_counts().reset_index()
    robot_counts.columns = ["robot_id", "count"]
    st.bar_chart(robot_counts, x="robot_id", y="count")

    st.subheader("Object Count")
    object_counts = df["object"].value_counts().reset_index()
    object_counts.columns = ["object", "count"]
    st.bar_chart(object_counts, x="object", y="count")

st.divider()
st.subheader("High Risk Events")

high_risk_df = df[df["risk_score"] >= 7]

if high_risk_df.empty:
    st.info("No high-risk events are currently stored.")
else:
    st.dataframe(
        high_risk_df[
            [
                "id",
                "received_at",
                "robot_id",
                "object",
                "x",
                "y",
                "risk_score",
                "command",
                "llm_reason"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.subheader("Latest Command by Robot")

latest_by_robot = (
    df.sort_values("id", ascending=False)
      .drop_duplicates("robot_id")
      [
          [
              "robot_id",
              "command",
              "decision",
              "llm_reason",
              "risk_score",
              "received_at"
          ]
      ]
)

st.dataframe(
    latest_by_robot,
    use_container_width=True,
    hide_index=True
)

st.divider()
st.subheader("Communication Value")

st.markdown(
    """
    This system does not share raw image streams. Each robot sends only a compact
    summary JSON to Commander C.

    - No raw image sharing
    - Semantic summary-only communication
    - Event, risk, and position-based decision making
    - Qwen-based mission reasoning when the local model is available
    - Multi-robot task feedback loop
    """
)

st.caption("Auto-refresh reads the mission DB every 2 seconds.")
