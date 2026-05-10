#!/bin/bash

cd ~/tri-edge-rescue/ros2_ws

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "[Tri-Edge Rescue] Cleaning old Gazebo processes..."

pkill -x gzclient 2>/dev/null
pkill -x gzserver 2>/dev/null
pkill -x gazebo 2>/dev/null

sleep 2

echo "[Tri-Edge Rescue] Starting Gazebo rescue world..."
ros2 launch tri_edge_worlds rescue_world.launch.py
