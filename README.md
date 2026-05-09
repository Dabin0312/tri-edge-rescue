# Tri-Edge Rescue

클라우드 없는 온디바이스 멀티로봇 탐색·구조 AI 프로젝트

## 1. Project Overview

**Tri-Edge Rescue**는 재난·실험실 사고 환경을 가정한 온디바이스 멀티로봇 탐색·구조 AI 시스템이다.

본 프로젝트는 두 대의 로봇이 각자 현장에서 로컬 정보를 수집하고, 원본 영상이나 대용량 센서 데이터를 중앙으로 보내지 않고, 의미 정보(summary JSON)만 Commander C에 전달하는 구조를 구현한다.

Commander C는 Robot A/B의 summary를 통합해 위험도와 상황을 판단하고, 각 로봇에게 task command를 다시 전송한다.

핵심 슬로건:

> 영상을 보내지 않고, 의미를 보낸다.

---

## 2. Core Concept

기존 클라우드 기반 구조에서는 로봇의 카메라 영상이나 센서 데이터를 외부 서버로 전송해야 하므로 다음 문제가 발생할 수 있다.

- 네트워크 불안정 시 미션 중단
- 원본 영상 전송에 따른 민감정보 노출
- 다중 로봇 환경에서 높은 통신량
- 서버 왕복 지연으로 인한 느린 대응

Tri-Edge Rescue는 각 로봇이 로컬에서 의미 정보를 생성하고, 중앙 Commander는 이 summary만 받아 판단한다.

```text
Raw Image / Sensor Stream ❌
Semantic Summary JSON ✅

## 3. System Architecture
Gazebo Simulation PC / Ubuntu VM
  ├── Rescue world
  ├── Robot A spawn
  ├── Robot B spawn
  ├── /robot_a/odom
  ├── /robot_a/scan
  ├── /robot_b/odom
  └── /robot_b/scan

Robot A Brain
  ├── subscribe: /robot_a/odom
  ├── subscribe: /robot_a/task_command
  └── publish:   /robot_a/event_summary

Robot B Brain
  ├── subscribe: /robot_b/odom
  ├── subscribe: /robot_b/task_command
  └── publish:   /robot_b/event_summary

Commander C
  ├── subscribe: /robot_a/event_summary
  ├── subscribe: /robot_b/event_summary
  ├── publish:   /robot_a/task_command
  ├── publish:   /robot_b/task_command
  └── save:      SQLite mission DB

Dashboard
  └── visualize: mission_events.db

## 4. Current Implementation Status

현재 구현된 기능은 다음과 같다.

ROS2 Humble 기반 멀티노드 구조
Gazebo rescue world 구성
Gazebo 내 Robot A/B spawn
/robot_a/odom, /robot_b/odom 기반 실제 위치 수신
Robot A/B odom 기반 summary JSON 생성
Commander C summary 수신
위험도 기반 decision 생성
Commander C → Robot A/B task command 전송
Robot A/B task command 수신
SQLite DB mission logging
Streamlit dashboard
Mission report generator
Demo launch file

## 5. ROS2 Topic Structure
| Topic                    | Publisher     | Subscriber    | Description            |
| ------------------------ | ------------- | ------------- | ---------------------- |
| `/robot_a/odom`          | Gazebo        | Robot A Brain | Robot A의 실제 Gazebo 위치  |
| `/robot_b/odom`          | Gazebo        | Robot B Brain | Robot B의 실제 Gazebo 위치  |
| `/robot_a/scan`          | Gazebo        | Optional      | Robot A LiDAR scan     |
| `/robot_b/scan`          | Gazebo        | Optional      | Robot B LiDAR scan     |
| `/robot_a/event_summary` | Robot A Brain | Commander C   | Robot A의 의미 정보 summary |
| `/robot_b/event_summary` | Robot B Brain | Commander C   | Robot B의 의미 정보 summary |
| `/robot_a/task_command`  | Commander C   | Robot A Brain | Robot A에게 보내는 작업 명령    |
| `/robot_b/task_command`  | Commander C   | Robot B Brain | Robot B에게 보내는 작업 명령    |

## 6. Summary JSON Example
Robot A/B는 원본 영상이나 전체 센서 스트림 대신 다음과 같은 summary JSON만 Commander C에 전송한다.

{
  "robot_id": "A",
  "timestamp": 12,
  "object": "hazard",
  "confidence": 0.93,
  "position": {
    "x": -3.54,
    "y": -3.60
  },
  "risk_score": 8,
  "event": "gazebo_odom_based_summary",
  "last_command": "avoid_area"
}

## 7. Task Command JSON Example
Commander C는 summary를 바탕으로 각 로봇에게 명령을 다시 전송한다.

{
  "target_robot": "A",
  "command": "avoid_area",
  "reason": "high_risk_detected",
  "risk_score": 8,
  "target_position": {
    "x": -3.54,
    "y": -3.60
  }
}

## 8. Decision Rule

| Condition            | Decision                                   | Command                |
| -------------------- | ------------------------------------------ | ---------------------- |
| `risk_score >= 7`    | HIGH RISK: avoid or replan route           | `avoid_area`           |
| `object == person`   | VICTIM CANDIDATE: prioritize rescue target | `approach_victim`      |
| `object == obstacle` | OBSTACLE: update map and avoid             | `update_map_and_avoid` |
| otherwise            | NORMAL: continue exploration               | `continue_exploration` |

## 9. Project Structure

tri-edge-rescue/
├── ros2_ws/
│   └── src/
│       ├── robot_a_brain/
│       ├── robot_b_brain/
│       ├── commander_c/
│       └── tri_edge_worlds/
│           ├── worlds/
│           │   └── rescue_lab.world
│           └── launch/
│               └── rescue_world.launch.py
├── dashboard/
│   ├── app.py
│   └── generate_report.py
├── db/
│   └── mission_events.db
├── reports/
├── docs/
├── logs/
├── ai/
├── .gitignore
└── README.md

## 10. Gazebo Environment
Gazebo world는 재난·실험실 사고 환경을 단순화해 구성한다.

주요 요소:

| Object            | Meaning         |
| ----------------- | --------------- |
| Wall              | 실내 사고 환경        |
| Gray boxes        | 일반 장애물          |
| Blue cylinder     | 구조 대상 victim    |
| Red flat cylinder | 위험 구역 hazard    |
| Orange box        | blocked path    |
| Green cylinder    | safe checkpoint |
| Robot A           | Scout A         |
| Robot B           | Scout B         |


## 11. Build

cd ~/tri-edge-rescue/ros2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash

## 12. Demo Run

Terminal 1: Gazebo rescue world
cd ~/tri-edge-rescue/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch tri_edge_worlds rescue_world.launch.py
Terminal 2: Spawn Robot A/B
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger

ros2 run gazebo_ros spawn_entity.py \
  -entity robot_a \
  -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf \
  -robot_namespace robot_a \
  -x -3.5 -y -3.5 -z 0.01

ros2 run gazebo_ros spawn_entity.py \
  -entity robot_b \
  -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf \
  -robot_namespace robot_b \
  -x 3.5 -y -3.5 -z 0.01
Terminal 3: Run Robot A/B Brain + Commander C
cd ~/tri-edge-rescue/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch commander_c demo_system.launch.py
Terminal 4: Run Dashboard
cd ~/tri-edge-rescue
python3 -m streamlit run dashboard/app.py --server.address 0.0.0.0

Open browser:

http://localhost:8501


## 13. Check ROS2 Topics

source /opt/ros/humble/setup.bash
ros2 topic list

Expected topics:

/robot_a/cmd_vel
/robot_a/odom
/robot_a/scan
/robot_a/event_summary
/robot_a/task_command
/robot_b/cmd_vel
/robot_b/odom
/robot_b/scan
/robot_b/event_summary
/robot_b/task_command


## 14. Move Robot A/B Manually

Move Robot A:

ros2 topic pub /robot_a/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1}, angular: {z: 0.0}}" --rate 5

Stop Robot A:

ros2 topic pub /robot_a/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}" --once

Move Robot B:

ros2 topic pub /robot_b/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1}, angular: {z: 0.0}}" --rate 5

Stop Robot B:

ros2 topic pub /robot_b/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}" --once


15. SQLite DB

Commander C saves mission events to SQLite.

DB path:

~/tri-edge-rescue/db/mission_events.db

Check DB:

sqlite3 ~/tri-edge-rescue/db/mission_events.db
SELECT id, received_at, robot_id, object, risk_score, decision, command, target_robot
FROM event_summary
ORDER BY id DESC
LIMIT 10;

Exit:

.quit
16. Mission Report

Generate mission report:

cd ~/tri-edge-rescue
python3 dashboard/generate_report.py

Output:

reports/mission_report.md

17. Jetson Deployment Plan

최종적으로 Jetson Orin Nano 3대는 다음과 같이 배치한다.
| Device                | Role            | Run                           |
| --------------------- | --------------- | ----------------------------- |
| Gazebo PC / Ubuntu VM | Simulation PC   | Gazebo world, Robot A/B spawn |
| Jetson A              | Robot A Brain   | `robot_a_brain`               |
| Jetson B              | Robot B Brain   | `robot_b_brain`               |
| Jetson C              | Local Commander | `commander_c`, DB, dashboard  |

Jetson A:

cd ~/tri-edge-rescue/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run robot_a_brain event_publisher

Jetson B:

cd ~/tri-edge-rescue/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run robot_b_brain event_publisher

Jetson C:

cd ~/tri-edge-rescue/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run commander_c event_subscriber

Dashboard on Jetson C:

cd ~/tri-edge-rescue
python3 -m streamlit run dashboard/app.py --server.address 0.0.0.0


18. Network Setup for Jetson

모든 장비는 같은 네트워크에 있어야 한다.

Gazebo PC / Ubuntu VM
Jetson A
Jetson B
Jetson C
Control Desktop

권장 방식:

Same router / LAN
ROS_DOMAIN_ID 동일하게 설정

Set ROS domain:

echo "export ROS_DOMAIN_ID=7" >> ~/.bashrc
source ~/.bashrc

Check IP:

hostname -I

Check communication:

ping <target_ip>


