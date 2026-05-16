#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TRI_EDGE_HOME="${TRI_EDGE_HOME:-$REPO_ROOT}"

cd "$REPO_ROOT/ros2_ws"

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "[Tri-Edge Rescue] Cleaning old Gazebo processes..."

pkill -x gzclient 2>/dev/null
pkill -x gzserver 2>/dev/null
pkill -x gazebo 2>/dev/null

sleep 2

echo "[Tri-Edge Rescue] Starting Gazebo rescue world..."
ros2 launch tri_edge_worlds rescue_world.launch.py
