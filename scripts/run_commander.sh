#!/bin/bash

cd ~/tri-edge-rescue/ros2_ws

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "[Tri-Edge Rescue] Starting Commander C with Qwen planner..."
ros2 run commander_c event_subscriber
