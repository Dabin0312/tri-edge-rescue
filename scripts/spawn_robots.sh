#!/bin/bash

source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger

echo "[Tri-Edge Rescue] Waiting for /spawn_entity service..."

until ros2 service list | grep -q "/spawn_entity"; do
  echo "Waiting for Gazebo spawn service..."
  sleep 2
done

echo "[Tri-Edge Rescue] Spawning Robot A..."
ros2 run gazebo_ros spawn_entity.py \
  -entity robot_a \
  -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf \
  -robot_namespace robot_a \
  -x -3.5 -y -3.5 -z 0.01 || true

sleep 3

echo "[Tri-Edge Rescue] Spawning Robot B..."
ros2 run gazebo_ros spawn_entity.py \
  -entity robot_b \
  -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf \
  -robot_namespace robot_b \
  -x 3.5 -y -3.5 -z 0.01 || true

sleep 3

echo "[Tri-Edge Rescue] Checking robot topics..."
ros2 topic list | grep robot

if ros2 topic list | grep -q "/robot_a/odom" && ros2 topic list | grep -q "/robot_b/odom"; then
  echo "[Tri-Edge Rescue] Robot A/B spawn verified successfully."
else
  echo "[Tri-Edge Rescue] Robot spawn verification failed. Check Gazebo."
fi
