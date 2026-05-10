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
        target_robot,
        llm_reason
    FROM event_summary
    ORDER BY id DESC
    LIMIT 300
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


df = load_data()

if df.empty:
    st.warning("아직 DB에 저장된 이벤트가 없습니다. Commander C를 실행한 뒤 다시 확인하세요.")
    st.stop()

# 컬럼이 없는 오래된 DB를 대비
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
    st.info("아직 LLM Reason이 없습니다.")
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
    st.info("현재 high risk 이벤트가 없습니다.")
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
    이 시스템은 원본 영상 스트림을 공유하지 않고, 각 로봇이 생성한 summary JSON만 Commander C에 전달한다.

    - 원본 영상 미공유
    - 의미 정보 중심 통신
    - 이벤트/위험도/좌표 기반 판단
    - Qwen 기반 LLM Mission Reason 생성
    - 다중 로봇 협업 구조
    """
)

st.caption("Auto-refresh: 2초마다 DB를 다시 읽어 최신 mission event를 표시합니다.")
