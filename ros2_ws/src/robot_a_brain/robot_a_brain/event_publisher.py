import json
import math
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry


class RobotAEventPublisher(Node):
    def __init__(self):
        super().__init__('robot_a_event_publisher')

        self.publisher_ = self.create_publisher(String, '/robot_a/event_summary', 10)

        self.command_subscriber = self.create_subscription(
            String,
            '/robot_a/task_command',
            self.command_callback,
            10
        )

        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/robot_a/odom',
            self.odom_callback,
            10
        )

        self.timer = self.create_timer(1.0, self.publish_event)
        self.count = 0
        self.last_command = "none"

        self.current_x = 0.0
        self.current_y = 0.0
        self.has_odom = False

        self.hazard_position = (-3.2, -3.0)
        self.victim_position = (3.2, 3.1)
        self.obstacle_position = (0.0, 2.5)

        self.get_logger().info("Robot A Brain started. Using /robot_a/odom.")

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.has_odom = True

    def command_callback(self, msg):
        try:
            command = json.loads(msg.data)
            self.last_command = command.get("command", "unknown")
            self.get_logger().info(f"Robot A received command: {msg.data}")
        except json.JSONDecodeError:
            self.get_logger().error(f"Robot A received invalid command: {msg.data}")

    def distance_to(self, target):
        return math.sqrt((self.current_x - target[0]) ** 2 + (self.current_y - target[1]) ** 2)

    def infer_local_event(self):
        if not self.has_odom:
            return "unknown", 0.0, 1

        hazard_dist = self.distance_to(self.hazard_position)
        victim_dist = self.distance_to(self.victim_position)
        obstacle_dist = self.distance_to(self.obstacle_position)

        min_dist = min(hazard_dist, victim_dist, obstacle_dist)

        if min_dist == hazard_dist and hazard_dist < 2.5:
            return "hazard", round(random.uniform(0.85, 0.98), 2), 8
        elif min_dist == victim_dist and victim_dist < 2.5:
            return "person", round(random.uniform(0.82, 0.96), 2), 5
        elif min_dist == obstacle_dist and obstacle_dist < 2.0:
            return "obstacle", round(random.uniform(0.80, 0.95), 2), 4
        else:
            return "clear", round(random.uniform(0.70, 0.90), 2), 1

    def publish_event(self):
        self.count += 1
        detected_object, confidence, risk_score = self.infer_local_event()

        event = {
            "robot_id": "A",
            "timestamp": self.count,
            "object": detected_object,
            "confidence": confidence,
            "position": {
                "x": round(self.current_x, 2),
                "y": round(self.current_y, 2)
            },
            "risk_score": risk_score,
            "event": "gazebo_odom_based_summary",
            "last_command": self.last_command
        }

        msg = String()
        msg.data = json.dumps(event, ensure_ascii=False)
        self.publisher_.publish(msg)
        self.get_logger().info(f"Robot A summary published: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = RobotAEventPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
