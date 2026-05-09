import os
import sqlite3

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh


st.set_page_config(
    page_title="Tri-Edge Rescue Dashboard",
    layout="wide"
)

st.title("Tri-Edge Rescue Dashboard")
st.caption("On-Device Multi-Robot AI Mission Monitor")

# Auto refresh every 2 seconds
st_autorefresh(interval=2000, key="dashboard_refresh")

DB_PATH = os.path.expanduser("~/tri_edge_rescue/db/mission_events.db")


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
        target_robot
    FROM event_summary
    ORDER BY id DESC
    LIMIT 200
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


df = load_data()

if df.empty:
    st.warning("아직 DB에 저장된 이벤트가 없습니다. Commander C를 실행한 뒤 다시 확인하세요.")
    st.stop()

latest_id = int(df["id"].max())
total_events = len(df)
high_risk_count = int((df["risk_score"] >= 7).sum())
victim_count = int((df["object"] == "person").sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Latest Event ID", latest_id)
col2.metric("Loaded Events", total_events)
col3.metric("High Risk Events", high_risk_count)
col4.metric("Victim Candidates", victim_count)

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
    st.info("현재 high risk 이벤트가 없습니다.")
else:
    st.dataframe(
        high_risk_df,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.subheader("Latest Command by Robot")

latest_by_robot = (
    df.sort_values("id", ascending=False)
      .drop_duplicates("robot_id")
      [["robot_id", "command", "decision", "risk_score", "received_at"]]
)

st.dataframe(
    latest_by_robot,
    use_container_width=True,
    hide_index=True
)

st.caption("Auto-refresh: 2초마다 DB를 다시 읽어 최신 mission event를 표시합니다.")
