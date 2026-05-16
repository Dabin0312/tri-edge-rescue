#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TRI_EDGE_HOME="${TRI_EDGE_HOME:-$REPO_ROOT}"

cd "$REPO_ROOT/ros2_ws"

source /opt/ros/humble/setup.bash
source install/setup.bash

echo "[Tri-Edge Rescue] Starting Robot A Brain..."
ros2 run robot_a_brain event_publisher
