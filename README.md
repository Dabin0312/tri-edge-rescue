# Tri-Edge Rescue

클라우드 없는 온디바이스 멀티로봇 탐색·구조 AI 프로젝트

## 핵심 컨셉

본 프로젝트는 Robot A와 Robot B가 각자 로컬에서 상황을 판단하고, 원본 영상이 아닌 의미 정보(summary JSON)만 Commander C에 전달하는 구조를 구현한다.

Commander C는 각 로봇의 summary를 통합해 판단하고, 다시 각 로봇에게 task command를 전송한다.

핵심 슬로건:

> 영상을 보내지 않고, 의미를 보낸다.

## 현재 구현 상태

- Robot A summary publisher
- Robot B summary publisher
- Commander C summary subscriber
- Commander C decision logic
- SQLite DB logging
- Commander C task command publisher
- Robot A/B task command subscriber

## ROS2 Topic 구조

| Topic | Publisher | Subscriber | Description |
|---|---|---|---|
| `/robot_a/event_summary` | Robot A | Commander C | Robot A의 탐지/상황 summary |
| `/robot_b/event_summary` | Robot B | Commander C | Robot B의 탐지/상황 summary |
| `/robot_a/task_command` | Commander C | Robot A | Robot A에게 보내는 작업 명령 |
| `/robot_b/task_command` | Commander C | Robot B | Robot B에게 보내는 작업 명령 |

## Summary JSON 예시

```json
{
  "robot_id": "A",
  "timestamp": 1,
  "object": "hazard",
  "confidence": 0.91,
  "position": {
    "x": 4.2,
    "y": 1.7
  },
  "risk_score": 8,
  "event": "local_detection_summary",
  "last_command": "avoid_area"
}
