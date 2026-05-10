#!/bin/bash

cd ~/tri-edge-rescue/ros2_ws

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "[Tri-Edge Rescue] Starting Robot A Brain..."
ros2 run robot_a_brain event_publisher
