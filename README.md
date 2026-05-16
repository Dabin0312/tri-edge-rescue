# Tri-Edge Rescue

Cloud-free on-device multi-robot search and rescue AI project.

Tri-Edge Rescue validates a Gazebo/ROS2 rescue workflow where Robot A and Robot B summarize local field events, while Commander C receives only compact summary JSON and assigns missions. The core idea is to avoid sending raw video or heavy sensor streams to a central server. Instead, each robot shares lightweight semantic messages such as position, detected object, and risk score.

## Architecture

```text
Simulation PC
  - Gazebo rescue world
  - TurtleBot3 Burger x 2
  - /robot_a/odom, /robot_b/odom

Robot A Brain
  - subscribes: /robot_a/odom, /robot_a/task_command
  - publishes:  /robot_a/event_summary

Robot B Brain
  - subscribes: /robot_b/odom, /robot_b/task_command
  - publishes:  /robot_b/event_summary

Commander C
  - subscribes: /robot_a/event_summary, /robot_b/event_summary
  - publishes:  /robot_a/task_command, /robot_b/task_command
  - saves:      SQLite mission DB
  - uses:       Qwen2.5-0.5B-Instruct when available, deterministic fallback otherwise

Dashboard
  - visualizes: db/mission_events.db
  - exports:    reports/mission_report.md
```

## Implemented Features

- ROS2 Humble package layout
- Gazebo rescue world with walls, obstacles, victim, hazard zone, and safe checkpoint
- Robot A/B odometry-based event summary generation
- Commander C decision rules and task-command feedback
- Optional local Qwen mission reasoning with a no-crash fallback planner
- SQLite mission logging
- Streamlit dashboard
- Markdown mission report generator
- Jetson-oriented run scripts
- Smoke tests for planner fallback and report generation

## Project Structure

```text
tri-edge-rescue/
  ai/
  dashboard/
    app.py
    generate_report.py
  db/
  docs/
  logs/
  reports/
  ros2_ws/
    src/
      commander_c/
      robot_a_brain/
      robot_b_brain/
      tri_edge_worlds/
  scripts/
  tests/
  qwen_test.py
  requirements.txt
```

## System Requirements

The full demo expects an Ubuntu or Jetson environment with:

- ROS2 Humble
- Gazebo Classic with `gazebo_ros`
- TurtleBot3 Gazebo models
- Python 3.10 or later
- `colcon` build tools

On a ROS2 Humble machine, the usual packages are:

```bash
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-turtlebot3-gazebo python3-colcon-common-extensions
```

## Python Dependencies

```bash
python3 -m pip install -r requirements.txt
```

`torch` and `transformers` are only needed for the local Qwen model. The system still runs with deterministic mission reasoning when Qwen is disabled or unavailable.

## Runtime Environment

The scripts automatically set `TRI_EDGE_HOME` to the cloned repository root. When running commands manually, you can set:

```bash
export TRI_EDGE_HOME=~/tri-edge-rescue
export TRI_EDGE_DB_PATH=$TRI_EDGE_HOME/db/mission_events.db
export TRI_EDGE_ENABLE_QWEN=auto
```

To force the lightweight deterministic planner:

```bash
export TRI_EDGE_ENABLE_QWEN=0
```

## Build ROS2 Workspace

```bash
cd ~/tri-edge-rescue/ros2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## Demo Run

Terminal 1: Gazebo rescue world

```bash
~/tri-edge-rescue/scripts/run_gazebo_world.sh
```

Terminal 2: spawn Robot A/B

```bash
~/tri-edge-rescue/scripts/spawn_robots.sh
```

Terminal 3: Robot A/B brains and Commander C

```bash
cd ~/tri-edge-rescue/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch commander_c demo_system.launch.py
```

Terminal 4: dashboard

```bash
~/tri-edge-rescue/scripts/run_dashboard.sh
```

Open:

```text
http://localhost:8501
```

## Topic Structure

| Topic | Publisher | Subscriber | Description |
| --- | --- | --- | --- |
| `/robot_a/odom` | Gazebo | Robot A Brain | Robot A position |
| `/robot_b/odom` | Gazebo | Robot B Brain | Robot B position |
| `/robot_a/event_summary` | Robot A Brain | Commander C | Robot A local event summary |
| `/robot_b/event_summary` | Robot B Brain | Commander C | Robot B local event summary |
| `/robot_a/task_command` | Commander C | Robot A Brain | Task command for Robot A |
| `/robot_b/task_command` | Commander C | Robot B Brain | Task command for Robot B |

## Summary JSON

```json
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
```

## Task Command JSON

```json
{
  "target_robot": "A",
  "command": "avoid_area",
  "reason": "high_risk_detected",
  "risk_score": 8,
  "target_position": {
    "x": -3.54,
    "y": -3.60
  },
  "llm_reason": "Robot A should avoid_area because a high-risk hazard was detected near (-3.54, -3.60)."
}
```

## Decision Rules

| Condition | Decision | Command |
| --- | --- | --- |
| `risk_score >= 7` | High risk: avoid or replan route | `avoid_area` |
| `object == person` | Victim candidate: prioritize rescue target | `approach_victim` |
| `object == obstacle` | Obstacle: update map and avoid | `update_map_and_avoid` |
| otherwise | Normal: continue exploration | `continue_exploration` |

## Mission Report

```bash
cd ~/tri-edge-rescue
python3 dashboard/generate_report.py
```

Output:

```text
reports/mission_report.md
```

## Qwen Smoke Test

```bash
cd ~/tri-edge-rescue
TRI_EDGE_ENABLE_QWEN=0 python3 qwen_test.py
```

Use `TRI_EDGE_ENABLE_QWEN=auto` or `1` after the Qwen model is available locally.

## Jetson Deployment Plan

| Device | Role | Command |
| --- | --- | --- |
| Gazebo PC / Ubuntu VM | Simulation environment | `scripts/run_gazebo_world.sh` and `scripts/spawn_robots.sh` |
| Jetson A | Robot A Brain | `scripts/run_robot_a.sh` |
| Jetson B | Robot B Brain | `scripts/run_robot_b.sh` |
| Jetson C | Commander, DB, dashboard | `scripts/run_commander.sh`, `scripts/run_dashboard.sh` |

All devices should use the same network and `ROS_DOMAIN_ID`.

```bash
export ROS_DOMAIN_ID=7
```
